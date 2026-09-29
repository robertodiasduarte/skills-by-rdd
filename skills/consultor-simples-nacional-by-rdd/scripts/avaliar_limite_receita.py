#!/usr/bin/env python3
"""Avalia, de forma didática, excesso do limite anual do Simples (R$ 4,8 milhões) para PA 2018-2026."""
import argparse, json
from simples_core import validar_ano, validar_valor, parse_numero

ap=argparse.ArgumentParser()
ap.add_argument("--ano", type=int, required=True)
ap.add_argument("--rba-atual", type=parse_numero, required=True)
ap.add_argument("--tipo", choices=["mercado_interno","exportacao"], default="mercado_interno")
ap.add_argument("--inicio-atividade", action="store_true")
ap.add_argument("--meses-atividade-ano", type=int)
args=ap.parse_args()
try:
    validar_ano(args.ano); validar_valor("RBA",args.rba_atual)
    if args.inicio_atividade:
        if not args.meses_atividade_ano or not (1<=args.meses_atividade_ano<=12):
            raise ValueError("Em início de atividade, informe --meses-atividade-ano entre 1 e 12.")
        limite=400_000.0*args.meses_atividade_ano
    else:
        limite=4_800_000.0
    pct_excesso=(args.rba_atual/limite-1) if args.rba_atual>limite else 0.0
    if args.rba_atual<=limite:
        efeito="sem exclusão por este limite"
    elif args.inicio_atividade and args.rba_atual>limite*1.20:
        efeito="exclusão com efeitos retroativos ao início da atividade"
    elif args.rba_atual>limite*1.20:
        efeito="exclusão a partir do mês subsequente ao excesso superior a 20%"
    else:
        efeito="exclusão a partir do ano-calendário subsequente"
    print(json.dumps({
        "tipo_receita":args.tipo,"limite_aplicado":limite,"rba":args.rba_atual,
        "excesso_pct":pct_excesso*100,"classificacao":efeito,
        "observacao":"Mercado interno e exportação têm limites adicionais próprios; avalie cada bloco de receita separadamente e confirme o fato gerador/data do excesso."
    }, ensure_ascii=False, indent=2))
except ValueError as e:
    raise SystemExit(str(e))
