#!/usr/bin/env python3
"""Verificador redundante com implementação independente e Decimal.

Não importa engine.py nem simples_core.py. Compartilha somente tables_loader.py, portanto
a independência é de implementação/precisão, não de fonte normativa. Para entradas que
coincidem com exemplos oficiais, a validação externa é feita por official_examples.json.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP, getcontext
import json,re,sys
from pathlib import Path
from tables_loader import carregar_tabelas

getcontext().prec=34
QUALS={"exportacao","sublimite","icms_st","monofasico_pis_cofins","inicio_atividade"}
BASE={"competencia","modo","anexo","qualificacoes"}
ORD={"rbt12","rpa","receita_iss_retido"}
EXT={"rbt12_interno","rbt12_externo","rpa_interno","rpa_externo","rba_interno","rba_externo","sublimite"}
ALLOWED=BASE|ORD|EXT

def D(v):
    if isinstance(v,(int,float,Decimal)): return Decimal(str(v))
    s=str(v).strip().replace("R$","").replace(" ","")
    if "." in s and "," in s:
        s=s.replace(".","").replace(",",".") if s.rfind(",")>s.rfind(".") else s.replace(",","")
    elif "," in s: s=s.replace(",",".")
    return Decimal(s)

def cent(v): return D(v).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)

def _load(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj,dict): raise ValueError("Entrada deve ser objeto JSON.")
    if set(obj)-ALLOWED: raise ValueError("Campos não permitidos.")
    if BASE-set(obj): raise ValueError("Campos obrigatórios ausentes.")
    m=re.fullmatch(r"(20\d{2})-(0[1-9]|1[0-2])",str(obj["competencia"]))
    if not m: raise ValueError("competencia inválida.")
    obj["_ano"]=int(m.group(1)); obj["anexo"]=str(obj["anexo"]).upper()
    if obj["modo"] not in {"ordinario","exportacao_anexo_i"}: raise ValueError("modo inválido.")
    if obj["anexo"] not in {"I","II","III","IV","V"}: raise ValueError("anexo inválido.")
    if not isinstance(obj["qualificacoes"],dict) or set(obj["qualificacoes"])!=QUALS: raise ValueError("qualificacoes inválidas.")
    return obj

def faixa(rbt,limites):
    if rbt<=0: raise ValueError("RBT12 deve ser positivo.")
    for i,lim in enumerate(limites,1):
        if rbt<=D(lim): return i
    raise ValueError("RBT12 excede limite do motor.")

def taxas(data,anexo,f,ef):
    chave=f"{anexo}-{f}"
    alt=data.get("iss_redistribuicao",{}).get(chave); th=data.get("iss_thresholds",{}).get(chave)
    if alt and th is not None and ef>D(th):
        out={k:(ef-D("0.05"))*(D(v)/D("100")) for k,v in alt.items()}; out["ISS"]=D("0.05"); return out
    return {k:ef*D(v)/D("100") for k,v in data["anexos"][anexo]["partilhas"][f-1].items()}

def segmento_i(data,rbt,rpa,exporta):
    f=faixa(rbt,data["limites_rbt12"]); tab=data["anexos"]["I"]
    nom=D(tab["aliquotas"][f-1]); pd=D(tab["deducoes"][f-1]); ef=nom/D("100")-pd/rbt
    tx=taxas(data,"I",f,ef)
    if exporta:
        for t in ("COFINS","PIS","ICMS"):
            if t in tx: tx[t]=D("0")
    vals={t:cent(rpa*v) for t,v in tx.items()}
    return {"faixa":f,"rbt12":float(rbt),"rpa":float(rpa),"aliquota_nominal_pct":float(nom),
            "parcela_deduzir":float(pd),"aliquota_efetiva_pct":float(ef*D("100")),
            "percentuais_efetivos_pct":{t:float(v*D("100")) for t,v in tx.items()},
            "valores":{t:float(v) for t,v in vals.items()},"total":float(sum(vals.values(),D("0")))}

def _ordinario(e,data):
    if any(bool(e["qualificacoes"][k]) for k in QUALS): raise ValueError("Cenário qualificado não suportado no modo ordinário.")
    rbt=D(e["rbt12"]); rpa=D(e["rpa"]); ret=D(e.get("receita_iss_retido",0))
    if rpa<0 or ret<0 or ret>rpa: raise ValueError("RPA/ISS retido inválidos.")
    f=faixa(rbt,data["limites_rbt12"]); tab=data["anexos"][e["anexo"]]
    nom=D(tab["aliquotas"][f-1]); pd=D(tab["deducoes"][f-1]); ef=nom/D("100")-pd/rbt
    tx=taxas(data,e["anexo"],f,ef); bases={k:rpa for k in tx}
    if "ISS" in bases: bases["ISS"]=rpa-ret
    vals={k:bases[k]*v for k,v in tx.items()}
    return {"periodo_regras":"2018-2026","ano":e["_ano"],"modo":"ordinario","anexo":e["anexo"],"faixa":f,
            "rbt12":float(rbt),"rpa":float(rpa),"receita_iss_retido":float(ret),
            "aliquota_nominal_pct":float(nom),"parcela_deduzir":float(pd),"aliquota_efetiva_pct":float(ef*D("100")),
            "bases_por_tributo":{k:float(v) for k,v in bases.items()},
            "percentuais_efetivos_pct":{k:float(v*D("100")) for k,v in tx.items()},
            "valores":{k:float(v) for k,v in vals.items()},"total_das_calculado":float(sum(vals.values(),D("0")))}

def _export(e,data):
    if e["anexo"]!="I" or not e["qualificacoes"]["exportacao"]: raise ValueError("Modo exportação exige Anexo I e exportacao=true.")
    if any(bool(e["qualificacoes"][k]) for k in ("icms_st","monofasico_pis_cofins","inicio_atividade")): raise ValueError("Qualificação não suportada.")
    vals={k:D(e[k]) for k in EXT}
    if e["qualificacoes"]["sublimite"] or vals["rba_interno"]>vals["sublimite"] or vals["rba_externo"]>vals["sublimite"]:
        raise ValueError("Efeito de sublimite não suportado.")
    mi=segmento_i(data,vals["rbt12_interno"],vals["rpa_interno"],False)
    me=segmento_i(data,vals["rbt12_externo"],vals["rpa_externo"],True)
    return {"periodo_regras":"2018-2026","ano":e["_ano"],"modo":"exportacao_anexo_i","anexo":"I",
            "mercado_interno":mi,"mercado_externo":me,"rba_interno":float(vals["rba_interno"]),
            "rba_externo":float(vals["rba_externo"]),"sublimite":float(vals["sublimite"]),
            "total_das_calculado":float(cent(D(str(mi["total"]))+D(str(me["total"])))),
            "verificacao":{"tipo_independencia":"implementacao_independente_decimal","fonte_tabela":"mesmo tables_loader"}}

def executar(path):
    e=_load(path); data=carregar_tabelas(e["_ano"])
    return _ordinario(e,data) if e["modo"]=="ordinario" else _export(e,data)

def main():
    if len(sys.argv)!=2: raise SystemExit('Uso: python3 "$SKILL_ROOT/scripts/verify.py" <apuracao.json>')
    try: out=executar(sys.argv[1])
    except Exception as ex:
        print(json.dumps({"status":"ERRO","entrega_bloqueada":True,"erro":str(ex)},ensure_ascii=False)); return 2
    print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
