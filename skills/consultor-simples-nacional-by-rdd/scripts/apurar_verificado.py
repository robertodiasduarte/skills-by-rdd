#!/usr/bin/env python3
"""Orquestra cálculo, verificação redundante, baseline oficial e hard-stop.

Nenhum status genérico de aprovação é emitido para entrada arbitrária.
A concordância engine/verify prova consistência de implementação, não correção normativa da tabela.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOLDENS=ROOT/"references"/"goldens"/"official_examples.json"
from engine import executar as engine_exec
from verify import executar as verify_exec
from validate_goldens import run_all as run_goldens, compare_expected

def cent(v): return Decimal(str(v)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
def close(a,b,tol=Decimal("0.000001")):
    try: return abs(Decimal(str(a))-Decimal(str(b)))<=tol
    except Exception: return a==b

def _cmp_dict(a,b,prefix,diffs,tol=Decimal("0.000001")):
    if set(a)!=set(b):
        diffs.append({"campo":prefix+".chaves","engine":sorted(a),"verify":sorted(b)}); return
    for k in sorted(a):
        pa=f"{prefix}.{k}"
        av,bv=a[k],b[k]
        if isinstance(av,dict) and isinstance(bv,dict): _cmp_dict(av,bv,pa,diffs,tol)
        elif isinstance(av,(int,float)) and isinstance(bv,(int,float)):
            tt=Decimal("0.005") if (".valores." in pa or pa.endswith(".total") or pa.endswith("total_das_calculado")) else tol
            if not close(av,bv,tt): diffs.append({"campo":pa,"engine":av,"verify":bv})
        elif av!=bv: diffs.append({"campo":pa,"engine":av,"verify":bv})

def comparar_resultados(engine,verify):
    diffs=[]
    for f in ("ano","modo","anexo"):
        if engine.get(f)!=verify.get(f): diffs.append({"campo":f,"engine":engine.get(f),"verify":verify.get(f)})
    if engine.get("modo")=="ordinario":
        for f in ("faixa","rbt12","rpa","receita_iss_retido","aliquota_nominal_pct","parcela_deduzir","aliquota_efetiva_pct"):
            if not close(engine.get(f),verify.get(f)): diffs.append({"campo":f,"engine":engine.get(f),"verify":verify.get(f)})
        for f in ("bases_por_tributo","percentuais_efetivos_pct","valores"):
            _cmp_dict(engine.get(f,{}),verify.get(f,{}),f,diffs)
        if cent(engine.get("total_das_calculado",0))!=cent(verify.get("total_das_calculado",0)):
            diffs.append({"campo":"total_das_calculado","engine":engine.get("total_das_calculado"),"verify":verify.get("total_das_calculado")})
    else:
        for f in ("mercado_interno","mercado_externo"):
            _cmp_dict(engine.get(f,{}),verify.get(f,{}),f,diffs)
        for f in ("rba_interno","rba_externo","sublimite"):
            if not close(engine.get(f),verify.get(f)): diffs.append({"campo":f,"engine":engine.get(f),"verify":verify.get(f)})
        if cent(engine.get("total_das_calculado",0))!=cent(verify.get("total_das_calculado",0)):
            diffs.append({"campo":"total_das_calculado","engine":engine.get("total_das_calculado"),"verify":verify.get("total_das_calculado")})
    return diffs

def match_golden(inp,result):
    data=json.loads(GOLDENS.read_text(encoding="utf-8"))
    for case in data["cases"]:
        if case.get("kind")!="das": continue
        if inp==case["input"]:
            return case,compare_expected(result,case["expected"])
    return None,[]

def main():
    if len(sys.argv)!=2: raise SystemExit('Uso: python3 "$SKILL_ROOT/scripts/apurar_verificado.py" <apuracao.json>')
    try: inp=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except Exception as ex:
        print(json.dumps({"status":"ERRO_ENTRADA","entrega_bloqueada":True,"erro":str(ex)},ensure_ascii=False)); return 2

    baseline=run_goldens()
    if not baseline.get("pass"):
        print(json.dumps({"status":"BASELINE_OFICIAL_FALHOU","entrega_bloqueada":True,"baseline":baseline},ensure_ascii=False,indent=2)); return 5
    try:
        eng=engine_exec(sys.argv[1]); ver=verify_exec(sys.argv[1])
    except (ValueError,TypeError,SystemExit,KeyError) as ex:
        print(json.dumps({"status":"MOTOR_OU_VERIFY_RECUSOU","entrega_bloqueada":True,"erro":str(ex)},ensure_ascii=False,indent=2)); return 4

    diffs=comparar_resultados(eng,ver)
    if diffs:
        print(json.dumps({"status":"DIVERGENCIA_ENGINE_VERIFY","entrega_bloqueada":True,
                          "divergencias":diffs,
                          "mensagem":"Hard-stop: divergência de implementação; nenhum número é entregue como resultado."},
                         ensure_ascii=False,indent=2)); return 6

    golden,gdiffs=match_golden(inp,eng)
    if golden is not None and gdiffs:
        print(json.dumps({"status":"GABARITO_OFICIAL_DIVERGIU","entrega_bloqueada":True,
                          "golden_id":golden["id"],"source":golden["source"],"divergencias":gdiffs},
                         ensure_ascii=False,indent=2)); return 7

    if golden is not None:
        status="GABARITO_OFICIAL_CONFERIDO"
        validacao={"golden_id":golden["id"],"conferido_por":golden["conferido_por"],
                   "fonte_do_gabarito":golden["fonte_do_gabarito"],"source":golden["source"],
                   "engine_verify_concordantes":True}
    else:
        status="CALCULO_DETERMINISTICO_SEM_GABARITO_ESPECIFICO"
        validacao={"engine_verify_concordantes":True,
                   "escopo_da_verificacao":"implementacao_e_precisao",
                   "validacao_normativa_especifica":False,
                   "baseline_oficial_global_ok":True,
                   "limite":"A mesma tabela normativa alimenta engine e verify. A concordância não certifica a correção normativa desta entrada específica."}

    print(json.dumps({"status":status,"entrega_bloqueada":False,"validacao":validacao,"resultado":eng},
                     ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
