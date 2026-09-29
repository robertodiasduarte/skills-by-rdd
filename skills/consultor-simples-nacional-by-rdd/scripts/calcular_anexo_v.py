#!/usr/bin/env python3
"""Para atividade JÁ confirmada como sujeita ao fator R, sugere III ou V e calcula o DAS.

Admite segregação de receita que sofreu retenção de ISS.
"""
import argparse, json
from simples_core import calcular_fator_r, calcular_anexo, parse_numero

ap=argparse.ArgumentParser()
ap.add_argument("--ano", type=int, required=True)
ap.add_argument("--mes", type=int, required=True, choices=range(1,13))
ap.add_argument("--rbt12", type=parse_numero, required=True)
ap.add_argument("--rpa", type=parse_numero, required=True)
ap.add_argument("--fs12", type=parse_numero, required=True)
ap.add_argument("--iss-retido", type=parse_numero, default=0.0,
                help="Receita do PA que sofreu retenção de ISS; não é o valor do imposto.")
args=ap.parse_args()
try:
    fr=calcular_fator_r(args.fs12,args.rbt12,args.ano,args.mes)
    anexo=fr["anexo_sugerido"]
    calc=calcular_anexo(anexo,args.rbt12,args.rpa,args.ano,receita_iss_retido=args.iss_retido)
    print(json.dumps({
        "fator_r":fr,
        "calculo":calc,
        "observacao":"Use o resultado somente depois de confirmar documentalmente que a atividade está sujeita ao fator R."
    },ensure_ascii=False,indent=2))
except ValueError as e:
    raise SystemExit(str(e))
