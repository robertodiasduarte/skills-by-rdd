#!/usr/bin/env python3
"""Valida um Markdown preparado ANTES de enviá-lo à plataforma RDD.

Mesmas regras do degrau 0 do servidor (`_shared/md-canonico.ts`): o que reprova aqui
reprova lá. Rodar isto é obrigatório no fluxo da skill — o servidor NUNCA vê o documento
original, então este é o único ponto em que uma extração ruim pode ser barrada.

Uso:
    python scripts/validar.py CAMINHO.md

Saída: JSON em stdout.
Exit: 0 = pronto para enviar (pode ter warnings) · 1 = uso incorreto · 2 = reprovado.

Sem dependências externas: só a biblioteca padrão.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024  # espelha consultor-prep-criar/logic.ts

RE_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
RE_FRONTMATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
RE_CABECALHO_MAPA = re.compile(
    r"^#\s+Mapa Sem[âa]ntico\s*\(\s*[ÍI]ndice de Remiss[õo]es por Tema\s*\)",
    re.IGNORECASE | re.MULTILINE,
)
RE_ANCORA = re.compile(
    r"(^|\n)\s*(T[ÍI]TULO\s+[IVXLCDM]|CAP[ÍI]TULO\s+[IVXLCDM]|Se[çc][ãa]o\s+[IVXLCDM]"
    r"|Art\.\s*\d|§\s*\d|Par[áa]grafo\s+[úu]nico)",
    re.IGNORECASE,
)
RE_PERGUNTA = re.compile(r"^(?:\d{1,3}\s*[).:]|Pergunta:)\s*(.{8,}?\?)\s*$", re.IGNORECASE)

# Um .md achatado (PDF extraído sem preservar linhas) é tecnicamente válido e produz uma base
# INÚTIL: a Resolução CGSN 140 extraída sem PyMuPDF virou 331 KB em 106 linhas com 1 "Art.".
# Como o servidor não vê o original, este é o único ponto em que isso pode ser barrado.
MIN_LINHAS_POR_10KB = 8
MIN_ANCORAS_POR_100KB = 5


def separar_frontmatter(md: str) -> tuple[dict[str, str], str]:
    m = RE_FRONTMATTER.match(md)
    if not m:
        return {}, md
    fm: dict[str, str] = {}
    for linha in m.group(1).split("\n"):
        kv = re.match(r"^([a-z_]+):\s*(.*)$", linha, re.IGNORECASE)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip("\"'")
    return fm, md[m.end():]


def contar_perguntas(corpo: str) -> int:
    return sum(1 for l in corpo.split("\n") if RE_PERGUNTA.match(l.strip()))


def validar(caminho: Path) -> tuple[dict, int]:
    erros: list[str] = []
    avisos: list[str] = []

    if caminho.suffix.lower() != ".md":
        return {"status": "erro", "erros": ["a plataforma recebe só Markdown (.md)"], "avisos": []}, 2

    try:
        bruto = caminho.read_bytes()
    except OSError as exc:
        return {"status": "erro", "erros": [f"não consegui ler o arquivo: {exc}"], "avisos": []}, 2

    if len(bruto) > MAX_BYTES:
        erros.append(f"{len(bruto) // 1048576} MB excede o limite de 8 MB — divida o documento")

    try:
        md = bruto.decode("utf-8")
    except UnicodeDecodeError:
        return {"status": "erro", "erros": ["o arquivo não está em UTF-8"], "avisos": []}, 2

    frontmatter, corpo = separar_frontmatter(md)
    if not corpo.strip():
        return {"status": "erro", "erros": ["arquivo vazio"], "avisos": []}, 2

    eh_mapa = bool(RE_CABECALHO_MAPA.search(corpo))
    if eh_mapa:
        erros.append(
            "isto é um Mapa Semântico (índice), não um documento — envie-o junto do "
            "Texto-Ajustado que ele descreve, nunca sozinho"
        )
        return {"status": "erro", "papel": "mapa", "erros": erros, "avisos": avisos}, 2

    headings = RE_HEADING.findall(corpo)
    tem_ancora = bool(RE_ANCORA.search(corpo))
    perguntas = contar_perguntas(corpo)
    if not headings and not tem_ancora and perguntas < 3:
        erros.append(
            "não achei títulos (#), artigos (Art./§) nem perguntas numeradas — "
            "rode a skill no modo parse antes de enviar"
        )

    # Achatamento: muitos bytes em poucas linhas = extração que perdeu as quebras.
    # ⛔ Só faz sentido acima de 20 KB: documento curto e legítimo tem poucas linhas por
    #    construção, e reprovar MD bom é pior do que deixar passar um ruim (o aluno fica
    #    sem saída e o suporte herda o problema).
    linhas_uteis = [l for l in corpo.split("\n") if l.strip()]
    kb = len(bruto) // 10240
    if len(bruto) > 20480 and len(linhas_uteis) < kb * MIN_LINHAS_POR_10KB:
        erros.append(
            f"o texto parece achatado ({len(linhas_uteis)} linhas para "
            f"{len(bruto) // 1024} KB) — a extração perdeu as quebras de linha. "
            "Rode a skill num ambiente com PyMuPDF ou converta o PDF antes"
        )
    if len(bruto) > 100 * 1024:
        ancoras = len(RE_ANCORA.findall(corpo))
        por_100kb = ancoras / (len(bruto) / (100 * 1024))
        if tem_ancora and por_100kb < MIN_ANCORAS_POR_100KB:
            erros.append(
                f"só {ancoras} âncoras normativas em {len(bruto) // 1024} KB — "
                "a estrutura do documento não sobreviveu à extração"
            )

    if not frontmatter.get("rdd_base"):
        avisos.append("sem_frontmatter: aceito nesta versão; a v2.1 da skill grava rdd_base: 1")

    status = "erro" if erros else "ok"
    saida = {
        "status": status,
        "papel": "documento",
        "arquivo": caminho.name,
        "stats": {
            "bytes": len(bruto),
            "linhas": len(linhas_uteis),
            "headings": len(headings),
            "tem_ancora_normativa": tem_ancora,
            "perguntas_faq": perguntas,
        },
        "erros": erros,
        "avisos": avisos,
    }
    return saida, (2 if erros else 0)


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "erro", "erros": ["uso: validar.py CAMINHO.md"]}, ensure_ascii=False))
        return 1
    saida, code = validar(Path(sys.argv[1]))
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
