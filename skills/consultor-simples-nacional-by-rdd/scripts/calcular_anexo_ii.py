#!/usr/bin/env python3
"""Calcula Anexo II para PA 2018-2026."""
import argparse, json
from simples_core import calcular_anexo, parse_numero
ap=argparse.ArgumentParser()
ap.add_argument("--ano",type=int,required=True)
ap.add_argument("--rbt12",type=parse_numero,required=True)
ap.add_argument("--rpa",type=parse_numero,required=True)
args=ap.parse_args()
try:
    r=calcular_anexo("II",args.rbt12,args.rpa,args.ano)
    r["observacao"]="Segregações específicas de ICMS/PIS/Cofins exigem rotina apropriada."
    print(json.dumps(r,ensure_ascii=False,indent=2))
except ValueError as e:
    raise SystemExit(str(e))
