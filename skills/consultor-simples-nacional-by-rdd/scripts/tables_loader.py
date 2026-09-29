#!/usr/bin/env python3
"""Carregador único das tabelas normativas locais do Simples Nacional.

Fail-closed: se não houver tabela exatamente para o ano solicitado, o cálculo é recusado.
Não acessa rede. Biblioteca padrão apenas.
"""
from __future__ import annotations
import json
from pathlib import Path

def carregar_tabelas(ano: int) -> dict:
    if not isinstance(ano, int):
        raise ValueError("Ano deve ser inteiro.")
    root = Path(__file__).resolve().parents[1]
    caminho = root / "references" / "tabelas" / str(ano) / "anexos.json"
    if not caminho.exists():
        base = root / "references" / "tabelas"
        anos = sorted(p.name for p in base.iterdir() if p.is_dir() and p.name.isdigit()) if base.exists() else []
        raise ValueError(
            f"Sem tabela validada para {ano}. Anos disponíveis: {', '.join(anos) or 'nenhum'}. "
            "Este cálculo não está disponível para o período solicitado."
        )
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Tabela normativa inválida para {ano}: JSON linha {e.lineno}: {e.msg}") from e

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ano", type=int, required=True)
    args = ap.parse_args()
    print(json.dumps(carregar_tabelas(args.ano), ensure_ascii=False, indent=2))
