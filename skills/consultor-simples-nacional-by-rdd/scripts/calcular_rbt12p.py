#!/usr/bin/env python3
"""Calcula RBT12 proporcionalizada (RBT12p) nos 12 primeiros meses de atividade.

Aceita pontuação brasileira sem quebrar a lista:
  --receita-atual "20.000,00"
  --receitas-anteriores "10.000,00; 12.500,50; 8.000,00"

Para listas com vírgula decimal, use ponto e vírgula entre os meses.
"""
from __future__ import annotations
import argparse, json
from simples_core import carregar_tabelas, parse_numero, parse_lista_numeros, validar_valor

def calcular_rbt12p(receita_atual, receitas_anteriores, ano: int) -> dict:
    carregar_tabelas(int(ano))
    atual = parse_numero(receita_atual)
    anteriores = (
        parse_lista_numeros(receitas_anteriores)
        if isinstance(receitas_anteriores, str)
        else [parse_numero(x) for x in receitas_anteriores]
    )
    validar_valor("receita atual", atual)
    if len(anteriores) > 11:
        raise ValueError("Informe no máximo 11 meses anteriores.")
    for x in anteriores:
        validar_valor("receita anterior", x)
    if not anteriores:
        rbt12p = atual * 12
        criterio = "primeiro mês: receita do próprio PA × 12"
    else:
        rbt12p = (sum(anteriores)/len(anteriores))*12
        criterio = f"meses 2 a 12: média dos {len(anteriores)} meses anteriores ao PA × 12"
    return {
        "rbt12p": rbt12p,
        "criterio": criterio,
        "receita_atual": atual,
        "receitas_anteriores": anteriores,
        "periodo_regras": "2018-2026",
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--ano", type=int, required=True)
    ap.add_argument("--receita-atual", required=True)
    ap.add_argument("--receitas-anteriores", default="")
    args=ap.parse_args()
    try:
        print(json.dumps(calcular_rbt12p(args.receita_atual,args.receitas_anteriores,args.ano), ensure_ascii=False, indent=2))
        return 0
    except (ValueError,TypeError) as e:
        raise SystemExit(str(e))

if __name__ == "__main__":
    raise SystemExit(main())
