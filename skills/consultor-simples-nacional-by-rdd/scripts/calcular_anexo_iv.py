#!/usr/bin/env python3
"""Calcula o Anexo IV para PA 2018-2026, com segregação opcional de receita com ISS retido."""
import argparse, json
from simples_core import calcular_anexo, parse_numero

ap=argparse.ArgumentParser()
ap.add_argument("--ano", type=int, required=True)
ap.add_argument("--rbt12", type=parse_numero, required=True)
ap.add_argument("--rpa", type=parse_numero, required=True)
ap.add_argument("--iss-retido", type=parse_numero, default=0.0,
                help="Receita do PA que sofreu retenção de ISS; não é o valor do imposto retido.")
args=ap.parse_args()
try:
    r=calcular_anexo("IV", args.rbt12, args.rpa, args.ano, receita_iss_retido=args.iss_retido)
    r["observacao"]="CPP patronal do Anexo IV é externa ao DAS e não está incluída neste cálculo."
    print(json.dumps(r, ensure_ascii=False, indent=2))
except ValueError as e:
    raise SystemExit(str(e))
