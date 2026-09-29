#!/usr/bin/env python3
"""Calcula fator R; não decide sozinho se a atividade está sujeita ao fator R."""
import argparse,json
from simples_core import calcular_fator_r,parse_numero
ap=argparse.ArgumentParser()
ap.add_argument("--ano",type=int,required=True)
ap.add_argument("--mes",type=int,required=True,choices=range(1,13))
ap.add_argument("--fs12",type=parse_numero,required=True)
ap.add_argument("--rbt12",type=parse_numero,required=True)
args=ap.parse_args()
try:
    print(json.dumps(calcular_fator_r(args.fs12,args.rbt12,args.ano,args.mes),ensure_ascii=False,indent=2))
except ValueError as e:
    raise SystemExit(str(e))
