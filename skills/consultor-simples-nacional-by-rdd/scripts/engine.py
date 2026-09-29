#!/usr/bin/env python3
"""Motor principal de cálculo normativo.

Suporta:
- modo=ordinario: Anexos I a V, sem qualificações complexas;
- modo=exportacao_anexo_i: revenda de mercadorias com mercado interno e exportação,
  desde que não haja efeito de sublimite, ST, monofásico ou início de atividade.

Entrada por arquivo JSON; saída determinística em stdout. Offline e stdlib-only.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
import json, re, sys
from pathlib import Path
from simples_core import calcular_anexo, aliquota_efetiva, componentes_efetivos, parse_numero

QUALS={"exportacao","sublimite","icms_st","monofasico_pis_cofins","inicio_atividade"}
BASE={"competencia","modo","anexo","qualificacoes"}
ORD={"rbt12","rpa","receita_iss_retido"}
EXT={"rbt12_interno","rbt12_externo","rpa_interno","rpa_externo","rba_interno","rba_externo","sublimite"}
ALLOWED=BASE|ORD|EXT

def moeda(v: float) -> float:
    return float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def _load(path: str) -> dict:
    p=Path(path)
    try:
        obj=json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Arquivo de apuração não encontrado: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON inválido em {path}, linha {e.lineno}: {e.msg}")
    if not isinstance(obj,dict): raise SystemExit("A entrada deve ser objeto JSON.")
    extras=set(obj)-ALLOWED
    if extras: raise SystemExit("Campos não permitidos: "+", ".join(sorted(extras)))
    faltantes=BASE-set(obj)
    if faltantes: raise SystemExit("Campos obrigatórios ausentes: "+", ".join(sorted(faltantes)))
    m=re.fullmatch(r"(20\d{2})-(0[1-9]|1[0-2])",str(obj["competencia"]))
    if not m: raise SystemExit("competencia deve seguir AAAA-MM.")
    obj["_ano"]=int(m.group(1))
    obj["anexo"]=str(obj["anexo"]).upper()
    obj["modo"]=str(obj["modo"])
    if obj["anexo"] not in {"I","II","III","IV","V"}: raise SystemExit("anexo deve ser I, II, III, IV ou V.")
    if obj["modo"] not in {"ordinario","exportacao_anexo_i"}: raise SystemExit("modo inválido.")
    q=obj["qualificacoes"]
    if not isinstance(q,dict) or set(q)!=QUALS: raise SystemExit("qualificacoes deve conter exatamente as cinco flags previstas.")
    return obj

def _ordinario(e: dict) -> dict:
    q=e["qualificacoes"]
    ativos=[k for k in sorted(QUALS) if bool(q[k])]
    if ativos:
        raise ValueError("Cenário não suportado pelo modo ordinário: "+", ".join(ativos)+". Use modo/rotina específica.")
    for k in ("rbt12","rpa"):
        if k not in e: raise ValueError(f"Campo obrigatório ausente no modo ordinário: {k}")
    r=calcular_anexo(e["anexo"],parse_numero(e["rbt12"]),parse_numero(e["rpa"]),e["_ano"],
                     receita_iss_retido=parse_numero(e.get("receita_iss_retido",0)))
    r["modo"]="ordinario"
    return r

def _segmento_anexo_i(ano: int, rbt12: float, rpa: float, exportacao: bool) -> dict:
    faixa, nominal, pd, efetiva=aliquota_efetiva("I",rbt12,ano)
    taxas=componentes_efetivos("I",faixa,efetiva,ano)
    if exportacao:
        # Manual PGDAS-D, Exemplo 6: na revenda de mercadorias para o exterior
        # não incidem Cofins, PIS/Pasep e ICMS.
        for t in ("COFINS","PIS","ICMS"):
            if t in taxas: taxas[t]=0.0
    valores={t:moeda(rpa*taxa) for t,taxa in taxas.items()}
    return {
        "faixa":faixa,
        "rbt12":rbt12,
        "rpa":rpa,
        "aliquota_nominal_pct":nominal,
        "parcela_deduzir":pd,
        "aliquota_efetiva_pct":efetiva*100.0,
        "percentuais_efetivos_pct":{t:v*100.0 for t,v in taxas.items()},
        "valores":valores,
        "total":moeda(sum(valores.values()))
    }

def _exportacao_anexo_i(e: dict) -> dict:
    if e["anexo"]!="I": raise ValueError("modo exportacao_anexo_i exige anexo I.")
    q=e["qualificacoes"]
    if not q["exportacao"]: raise ValueError("modo exportacao_anexo_i exige qualificacoes.exportacao=true.")
    if any(bool(q[k]) for k in ("icms_st","monofasico_pis_cofins","inicio_atividade")):
        raise ValueError("Exportação Anexo I com ST, monofásico ou início de atividade não é suportada por este motor.")
    req=EXT
    falt=[k for k in sorted(req) if k not in e]
    if falt: raise ValueError("Campos obrigatórios ausentes no modo exportação: "+", ".join(falt))
    rbt_i=parse_numero(e["rbt12_interno"]); rbt_e=parse_numero(e["rbt12_externo"])
    rpa_i=parse_numero(e["rpa_interno"]); rpa_e=parse_numero(e["rpa_externo"])
    rba_i=parse_numero(e["rba_interno"]); rba_e=parse_numero(e["rba_externo"])
    sub=parse_numero(e["sublimite"])
    if min(rbt_i,rbt_e,sub)<=0 or min(rpa_i,rpa_e,rba_i,rba_e)<0:
        raise ValueError("Valores de exportação inválidos.")
    if q["sublimite"] or rba_i>sub or rba_e>sub:
        raise ValueError("Efeito de sublimite detectado/indicado; este modo não calcula a transição de ICMS/ISS.")
    interno=_segmento_anexo_i(e["_ano"],rbt_i,rpa_i,False)
    externo=_segmento_anexo_i(e["_ano"],rbt_e,rpa_e,True)
    return {
        "periodo_regras":"2018-2026","ano":e["_ano"],"modo":"exportacao_anexo_i","anexo":"I",
        "mercado_interno":interno,"mercado_externo":externo,
        "rba_interno":rba_i,"rba_externo":rba_e,"sublimite":sub,
        "total_das_calculado":moeda(interno["total"]+externo["total"]),
        "avisos":["Mercado interno e externo usam RBT12/RPA separados. Exportação do Anexo I zera Cofins, PIS/Pasep e ICMS neste modo."]
    }

def executar(path: str) -> dict:
    e=_load(path)
    return _ordinario(e) if e["modo"]=="ordinario" else _exportacao_anexo_i(e)

def main() -> int:
    if len(sys.argv)!=2:
        raise SystemExit('Uso: python3 "$SKILL_ROOT/scripts/engine.py" <apuracao.json>')
    try: result=executar(sys.argv[1])
    except (ValueError,TypeError) as ex:
        print(json.dumps({"status":"ERRO","entrega_bloqueada":True,"erro":str(ex)},ensure_ascii=False))
        return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
