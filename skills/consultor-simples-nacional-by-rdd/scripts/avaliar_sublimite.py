#!/usr/bin/env python3
"""Avalia efeito de excesso do sublimite de ICMS/ISS para PA 2018-2026."""
import argparse, json
from simples_core import validar_ano, validar_valor, parse_numero

ap=argparse.ArgumentParser()
ap.add_argument("--ano", type=int, required=True)
ap.add_argument("--rba-atual", type=parse_numero, required=True)
ap.add_argument("--sublimite", type=parse_numero, required=True, help="Ex.: 1800000 ou 3600000")
ap.add_argument("--rbaa", type=parse_numero, help="Receita do ano-calendário anterior, se aplicável")
ap.add_argument("--tipo", choices=["mercado_interno","exportacao"], default="mercado_interno")
ap.add_argument("--inicio-atividade", action="store_true")
ap.add_argument("--meses-atividade-ano", type=int)
args=ap.parse_args()
try:
    validar_ano(args.ano); validar_valor("RBA",args.rba_atual); validar_valor("sublimite",args.sublimite,False)
    if args.rbaa is not None: validar_valor("RBAA",args.rbaa)
    if args.inicio_atividade:
        if not args.meses_atividade_ano or not (1<=args.meses_atividade_ano<=12):
            raise ValueError("Em início de atividade, informe --meses-atividade-ano entre 1 e 12.")
        limite=(args.sublimite/12.0)*args.meses_atividade_ano
    else:
        limite=args.sublimite
    eventos=[]
    if args.rbaa is not None and args.rbaa>args.sublimite:
        eventos.append("RBAA acima do sublimite: ICMS/ISS impedidos no Simples desde o início do ano corrente.")
    if args.rba_atual<=limite:
        atual="sem novo impedimento por excesso no ano corrente"
    elif args.inicio_atividade and args.rba_atual>limite*1.20:
        atual="excesso >20% no ano de início: impedimento retroativo ao início da atividade"
    elif args.rba_atual>limite*1.20:
        atual="excesso >20%: impedimento a partir do mês seguinte"
    else:
        atual="excesso até 20%: impedimento a partir do ano seguinte"
    eventos.append(atual)
    print(json.dumps({
        "tipo_receita":args.tipo,"sublimite_anual_informado":args.sublimite,
        "sublimite_aplicado_ao_ano":limite,"rba_atual":args.rba_atual,"rbaa":args.rbaa,
        "resultado":eventos,
        "observacao":"O valor do sublimite aplicável deve ser confirmado para a UF/ano. Mercado interno e exportação são avaliados separadamente."
    }, ensure_ascii=False, indent=2))
except ValueError as e:
    raise SystemExit(str(e))
