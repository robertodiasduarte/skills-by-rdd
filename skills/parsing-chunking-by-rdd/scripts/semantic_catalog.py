#!/usr/bin/env python3
"""
Build a deterministic structural catalog from an adjusted normative Markdown file.

No network access. No package installation. Stdlib only.
Prints JSON to stdout. Exit code 2 indicates a stop condition.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ARTICLE_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?Art\.?\s*(\d+[A-Za-z]?(?:-[A-Za-z0-9]+)?)[º°]?(?:\s*[.\-–—:]|\s|$)",
    re.IGNORECASE,
)
PARAGRAPH_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(§\s*\d+[º°]?(?:-[A-Za-z0-9]+)?|Par[aá]grafo\s+[uú]nico)\b",
    re.IGNORECASE,
)
INCISO_RE = re.compile(r"^\s*(?:#{1,6}\s*)?([IVXLCDM]+)\s*[-–—.)]\s+", re.IGNORECASE)
ALINEA_RE = re.compile(r"^\s*(?:#{1,6}\s*)?([a-z])\)\s+", re.IGNORECASE)
ANNEX_RE = re.compile(r"\bAnexo\s+([IVXLCDM]+|\d+[A-Za-z]?|[A-Z])\b", re.IGNORECASE)
TABLE_RE = re.compile(r"\bTabela\s+([IVXLCDM]+|\d+[A-Za-z]?|[A-Z])\b", re.IGNORECASE)
SECTIONAL_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(T[ÍI]TULO|CAP[ÍI]TULO|SE[CÇ][ÃA]O|SUBSE[CÇ][ÃA]O)\b",
    re.IGNORECASE,
)
TRANSITION_RE = re.compile(
    r"\b(vig[eê]ncia|revoga(?:do|da|ção|ções)|produ[cç][aã]o\s+de\s+efeitos|"
    r"disposi[cç][oõ]es?\s+transit[oó]rias?|entra\s+em\s+vigor|vetado|sem\s+efic[aá]cia)\b",
    re.IGNORECASE,
)

MAX_CONTEXT = 360


@dataclass
class Heading:
    level: int
    title: str
    line: int


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def context_for(lines: list[str], index: int) -> str:
    parts: list[str] = []
    for j in range(index, min(index + 3, len(lines))):
        value = compact(lines[j])
        if value:
            parts.append(value)
        if len(" ".join(parts)) >= MAX_CONTEXT:
            break
    value = " ".join(parts)
    if len(value) > MAX_CONTEXT:
        value = value[: MAX_CONTEXT - 1].rstrip() + "…"
    return value


def normalize_article(token: str) -> str:
    token = token.strip()
    return f"Art. {token}"


def normalize_paragraph(token: str) -> str:
    token = compact(token).rstrip(".")
    if token.lower().startswith("par"):
        return "Parágrafo único"
    token = re.sub(r"\s+", " ", token)
    return token


def unique_append(items: list[dict], seen: set[tuple], item: dict, key: tuple) -> None:
    if key not in seen:
        seen.add(key)
        items.append(item)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Adjusted Markdown source")
    args = parser.parse_args()

    source = Path(args.source)
    result = {
        "status": "stop",
        "source": source.name,
        "stop_condition": None,
        "warnings": [],
        "stats": {},
        "headings": [],
        "units": [],
        "annexes": [],
        "tables": [],
        "signals": [],
    }

    if source.suffix.lower() != ".md":
        result["stop_condition"] = "A entrada do modo semantic deve ser um arquivo .md."
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    try:
        text = read_text(source)
    except Exception as exc:
        result["stop_condition"] = f"Não foi possível abrir o Markdown: {exc}"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    if not text.strip() or len(compact(text)) < 120:
        result["stop_condition"] = "Markdown vazio ou sem conteúdo textual suficiente."
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    lines = text.splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    table_lines = [ln for ln in nonempty if ln.lstrip().startswith("|") and ln.count("|") >= 2]
    table_ratio = len(table_lines) / max(1, len(nonempty))

    headings: list[Heading] = []
    heading_stack: list[Heading] = []
    units: list[dict] = []
    annexes: list[dict] = []
    tables: list[dict] = []
    signals: list[dict] = []
    seen_units: set[tuple] = set()
    seen_annexes: set[tuple] = set()
    seen_tables: set[tuple] = set()
    seen_signals: set[tuple] = set()

    current_article: str | None = None

    for i, raw in enumerate(lines):
        line_no = i + 1
        line = raw.strip()
        if not line:
            continue

        hm = HEADING_RE.match(line)
        if hm:
            heading = Heading(len(hm.group(1)), compact(hm.group(2)), line_no)
            headings.append(heading)
            heading_stack = [h for h in heading_stack if h.level < heading.level]
            heading_stack.append(heading)

        heading_path = " > ".join(h.title for h in heading_stack)
        ctx = context_for(lines, i)

        am = ARTICLE_RE.match(line)
        if am:
            current_article = normalize_article(am.group(1))
            unique_append(
                units,
                seen_units,
                {
                    "kind": "article",
                    "canonical": current_article,
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("article", current_article),
            )

        pm = PARAGRAPH_RE.match(line)
        if pm:
            paragraph = normalize_paragraph(pm.group(1))
            canonical = f"{current_article}, {paragraph}" if current_article else paragraph
            unique_append(
                units,
                seen_units,
                {
                    "kind": "paragraph",
                    "canonical": canonical,
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("paragraph", canonical, line_no),
            )

        im = INCISO_RE.match(line)
        if im:
            inciso = im.group(1).upper()
            canonical = f"{current_article}, Inciso {inciso}" if current_article else f"Inciso {inciso}"
            unique_append(
                units,
                seen_units,
                {
                    "kind": "inciso",
                    "canonical": canonical,
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("inciso", canonical, line_no),
            )

        alm = ALINEA_RE.match(line)
        if alm:
            alinea = alm.group(1).lower()
            canonical = f"{current_article}, alínea {alinea}" if current_article else f"alínea {alinea}"
            unique_append(
                units,
                seen_units,
                {
                    "kind": "alinea",
                    "canonical": canonical,
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("alinea", canonical, line_no),
            )

        if SECTIONAL_RE.match(line) and not hm:
            unique_append(
                units,
                seen_units,
                {
                    "kind": "section",
                    "canonical": compact(line),
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("section", compact(line), line_no),
            )

        # Register annex/table occurrences; dedupe by identifier while retaining first context.
        for m in ANNEX_RE.finditer(line):
            identifier = m.group(1).upper()
            unique_append(
                annexes,
                seen_annexes,
                {
                    "identifier": identifier,
                    "canonical": f"Anexo {identifier}",
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("annex", identifier),
            )

        for m in TABLE_RE.finditer(line):
            identifier = m.group(1).upper()
            unique_append(
                tables,
                seen_tables,
                {
                    "identifier": identifier,
                    "canonical": f"Tabela {identifier}",
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                ("table", identifier),
            )

        if TRANSITION_RE.search(line):
            key = (line_no, compact(line)[:160])
            unique_append(
                signals,
                seen_signals,
                {
                    "line": line_no,
                    "heading_path": heading_path,
                    "context": ctx,
                },
                key,
            )

    # Add headings as structural units only when they are not merely article headings.
    for h in headings:
        if not ARTICLE_RE.match(h.title):
            unique_append(
                units,
                seen_units,
                {
                    "kind": "heading",
                    "canonical": h.title,
                    "line": h.line,
                    "heading_path": h.title,
                    "context": h.title,
                },
                ("heading", h.level, h.title),
            )

    stats = {
        "characters": len(text),
        "lines": len(lines),
        "nonempty_lines": len(nonempty),
        "headings": len(headings),
        "articles": sum(1 for u in units if u["kind"] == "article"),
        "paragraphs": sum(1 for u in units if u["kind"] == "paragraph"),
        "incisos": sum(1 for u in units if u["kind"] == "inciso"),
        "alineas": sum(1 for u in units if u["kind"] == "alinea"),
        "annexes": len(annexes),
        "tables": len(tables),
        "transition_signals": len(signals),
        "table_line_ratio": round(table_ratio, 4),
    }
    result["stats"] = stats
    result["headings"] = [h.__dict__ for h in headings]
    result["units"] = sorted(units, key=lambda x: (x["line"], x["kind"], x["canonical"]))
    result["annexes"] = annexes
    result["tables"] = tables
    result["signals"] = signals

    referential_count = (
        stats["articles"]
        + stats["paragraphs"]
        + stats["incisos"]
        + stats["annexes"]
        + stats["tables"]
        + stats["headings"]
    )

    if stats["headings"] == 0 and referential_count == 0:
        result["stop_condition"] = (
            "Não há headings nem unidades normativas confiáveis para construir remissões."
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    if table_ratio >= 0.65 and stats["articles"] == 0 and stats["headings"] < 3:
        result["stop_condition"] = (
            "Conteúdo predominantemente tabular sem referências textuais suficientes; "
            "o mapeamento semântico ficaria especulativo."
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    if stats["articles"] == 0:
        result["warnings"].append(
            "Nenhum artigo iniciado por 'Art.' foi identificado; usar headings/anexos/tabelas "
            "como referências somente quando forem citáveis e inequívocos."
        )

    if stats["characters"] < 6000 or stats["articles"] < 10:
        result["warnings"].append(
            "Documento curto ou com poucas unidades; menos de 20 temas pode ser apropriado, "
            "desde que justificado no README."
        )

    result["status"] = "ok"
    result["stop_condition"] = None
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
