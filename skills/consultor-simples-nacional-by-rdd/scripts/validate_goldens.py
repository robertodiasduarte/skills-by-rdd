#!/usr/bin/env python3
"""Valida caminhos independentes contra gabaritos externos ao código.

Goldens aceitos: exemplo oficial publicado ou caso real conferido por profissional,
sempre com procedência explícita. O script NUNCA cria ou promove saída da Skill a golden.
"""
from __future__ import annotations
from decimal import Decimal
import json,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOLDENS=ROOT/"references"/"goldens"/"official_examples.json"
from engine import executar as engine_exec
from verify import executar as verify_exec
from calcular_rbt12p import calcular_rbt12p

def close(a,b,tol=Decimal("0.005")):
    return abs(Decimal(str(a))-Decimal(str(b)))<=tol

def write_temp(payload):
    td=tempfile.TemporaryDirectory(); p=Path(td.name)/"input.json"
    p.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
    return td,p

def compare_expected(got,expected,prefix=""):
    diffs=[]
    if isinstance(expected,dict):
        if not isinstance(got,dict):
            return [{"campo":prefix or "<root>","esperado":expected,"obtido":got}]
        for k,v in expected.items():
            path=f"{prefix}.{k}" if prefix else k
            if k not in got: diffs.append({"campo":path,"esperado":v,"obtido":"nao_disponivel"})
            else: diffs.extend(compare_expected(got[k],v,path))
    elif isinstance(expected,(int,float)) and isinstance(got,(int,float)):
        if not close(got,expected): diffs.append({"campo":prefix,"esperado":expected,"obtido":got})
    elif got!=expected:
        diffs.append({"campo":prefix,"esperado":expected,"obtido":got})
    return diffs

def run_all():
    data=json.loads(GOLDENS.read_text(encoding="utf-8")); results=[]
    for case in data["cases"]:
        if not case.get("conferido_por") or not case.get("fonte_do_gabarito") or not case.get("source"):
            results.append({"id":case["id"],"pass":False,"erro":"golden sem fonte/procedência/conferência"})
            continue
        kind=case["kind"]; inp=case["input"]; exp=case["expected"]
        if kind=="das":
            td,p=write_temp(inp)
            try:
                e=engine_exec(str(p)); v=verify_exec(str(p))
                de=compare_expected(e,exp); dv=compare_expected(v,exp)
            except Exception as ex:
                results.append({"id":case["id"],"pass":False,"erro":str(ex)}); td.cleanup(); continue
            td.cleanup()
            results.append({"id":case["id"],"pass":not(de or dv),
                            "diffs_engine":de,"diffs_verify":dv,"source":case["source"]})
        elif kind=="rbt12p":
            try: got=calcular_rbt12p(inp["receita_atual"],inp.get("receitas_anteriores",[]),inp["ano"])
            except Exception as ex:
                results.append({"id":case["id"],"pass":False,"erro":str(ex)}); continue
            diffs=compare_expected(got,exp)
            results.append({"id":case["id"],"pass":not diffs,"diffs":diffs,"source":case["source"]})
        else:
            results.append({"id":case["id"],"pass":False,"erro":f"kind não suportado: {kind}"})
    return {"pass":all(x["pass"] for x in results),"cases":results}

def main():
    r=run_all(); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["pass"] else 1
if __name__=="__main__": raise SystemExit(main())
