#!/usr/bin/env python3
"""
Validate a semantic map and its plain-text README against the adjusted Markdown source.

Stdlib only. Prints JSON to stdout.
Exit 0 when no blocking errors are found; exit 1 on validation errors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

TOPIC_RE = re.compile(r"^### Tema:\s*(.+?)\s*$", re.MULTILINE)
TAXONOMY_RE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$", re.MULTILINE)
REL_RE = re.compile(r"^\s*-\s*\[\[Tema:\s*(.+?)\s*\]\]\s*$", re.MULTILINE)
ARTICLE_TOKEN_RE = re.compile(r"\bArt\.?\s*(\d+[A-Za-z]?(?:-[A-Za-z0-9]+)?)[º°]?\b", re.IGNORECASE)
ANNEX_TOKEN_RE = re.compile(r"\bAnexo\s+([IVXLCDM]+|\d+[A-Za-z]?|[A-Z])\b", re.IGNORECASE)
TABLE_TOKEN_RE = re.compile(r"\bTabela\s+([IVXLCDM]+|\d+[A-Za-z]?|[A-Z])\b", re.IGNORECASE)
PARAGRAPH_TOKEN_RE = re.compile(r"§\s*(\d+[º°]?(?:-[A-Za-z0-9]+)?)", re.IGNORECASE)
APPROX_RE = re.compile(r"LOCALIZACAO\s+APROXIMADA", re.IGNORECASE)
INCISO_TOKEN_RE = re.compile(r"\bInciso\s+([IVXLCDM]+)\b", re.IGNORECASE)

MAP_SECTIONS = [
    "# Mapa Semântico (Índice de Remissões por Tema)",
    "## Metadados",
    "## Taxonomia de Temas",
    "## Entradas por Tema",
    "## Índice de Anexos e Tabelas",
]

TOPIC_FIELDS = [
    "**Perguntas típicas**",
    "**Onde está na norma**",
    "**Regras principais**",
    "**Exceções e condições**",
    "**Relacionados**",
    "**Vigência/versão**",
]

README_MARKERS = [
    "RELATORIO - MAPA SEMANTICO / INDICE DE REMISSOES",
    "ARQUIVO DE ORIGEM:",
    "ESCOPO:",
    "ESTATISTICAS:",
    "CRITERIOS E REGRAS:",
    "LIMITACOES / PENDENCIAS:",
    "ARQUIVOS GERADOS:",
    "FIM",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def norm_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalized_ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()


def section_between(text: str, start: str, next_markers: list[str]) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        return ""
    body_start = start_idx + len(start)
    ends = [text.find(marker, body_start) for marker in next_markers]
    ends = [x for x in ends if x >= 0]
    end_idx = min(ends) if ends else len(text)
    return text[body_start:end_idx]


def topic_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(TOPIC_RE.finditer(text))
    blocks: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find(
            "## Índice de Anexos e Tabelas", start
        )
        if end < 0:
            end = len(text)
        blocks.append((norm_name(m.group(1)), text[start:end]))
    return blocks


def questions_count(block: str) -> int:
    section = section_between(
        block,
        "**Perguntas típicas**",
        [
            "**Onde está na norma**",
            "**Regras principais**",
            "**Exceções e condições**",
            "**Relacionados**",
            "**Vigência/versão**",
        ],
    )
    return len(re.findall(r"^\s*\d+\.\s+\S", section, re.MULTILINE))


def relations_for(block: str) -> set[str]:
    section = section_between(
        block,
        "**Relacionados**",
        ["**Vigência/versão**"],
    )
    return {norm_name(x) for x in REL_RE.findall(section)}


def refs_section(block: str) -> str:
    return section_between(
        block,
        "**Onde está na norma**",
        [
            "**Regras principais**",
            "**Exceções e condições**",
            "**Relacionados**",
            "**Vigência/versão**",
        ],
    )


def article_scopes(source: str) -> dict[str, set[str]]:
    """Sub-âncoras (§/inciso) que existem DENTRO de cada artigo.

    ⛔ FIX R2 (review adversarial 2026-09-11, provado por execução): `source_tokens` devolve
       conjuntos GLOBAIS independentes, e a validação testava cada token sozinho. Uma fonte com
       "Art. 1º/§ 1º" e "Art. 2º/§ 2º" aceitava um mapa citando "Art. 1º, § 2º" — localização que
       não existe. Aqui a associação artigo→sub-âncora é preservada.
    """
    scopes: dict[str, set[str]] = {}
    atual: str | None = None
    for linha in source.split("\n"):
        t = linha.strip()
        m = re.match(r"^Art\.?\s*(\d+[A-Za-z]?(?:-[A-Za-z0-9]+)?)[º°]?", t, re.IGNORECASE)
        if m:
            atual = m.group(1).upper()
            scopes.setdefault(atual, set())
            continue
        if atual is None:
            continue
        for mp in PARAGRAPH_TOKEN_RE.finditer(t):
            scopes[atual].add("§" + mp.group(1).upper().replace("°", "º"))
        mi = re.match(r"^([IVXLCDM]+)\s*[-–—.)]\s+", t, re.IGNORECASE)
        if mi:
            scopes[atual].add(mi.group(1).upper())
    return scopes


def source_tokens(source: str) -> tuple[set[str], set[str], set[str], set[str], set[str]]:
    arts = {m.group(1).upper() for m in ARTICLE_TOKEN_RE.finditer(source)}
    anns = {m.group(1).upper() for m in ANNEX_TOKEN_RE.finditer(source)}
    tabs = {m.group(1).upper() for m in TABLE_TOKEN_RE.finditer(source)}
    paras = {m.group(1).upper().replace("°", "º") for m in PARAGRAPH_TOKEN_RE.finditer(source)}
    incisos = {m.group(1).upper() for m in INCISO_TOKEN_RE.finditer(source)}
    # Incisos in normative bodies are commonly written only as "I -", "II -", etc.
    incisos.update(
        m.group(1).upper()
        for m in re.finditer(r"^\s*([IVXLCDM]+)\s*[-–—.)]\s+", source, re.MULTILINE | re.IGNORECASE)
    )
    return arts, anns, tabs, paras, incisos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("map")
    parser.add_argument("readme")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    paths = [Path(args.source), Path(args.map), Path(args.readme)]
    for path in paths:
        if not path.exists():
            errors.append(f"Arquivo inexistente: {path}")
    if errors:
        print(json.dumps({"status": "error", "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
        return 1

    try:
        source = read(paths[0])
        map_text = read(paths[1])
        readme = read(paths[2])
    except Exception as exc:
        print(json.dumps({"status": "error", "errors": [f"Falha de leitura: {exc}"], "warnings": []}, ensure_ascii=False, indent=2))
        return 1

    if paths[0].suffix.lower() != ".md":
        errors.append("A fonte deve ser .md.")
    if paths[1].suffix.lower() != ".md":
        errors.append("O mapa deve ser .md.")
    if paths[2].suffix.lower() != ".txt":
        errors.append("O relatório deve ser .txt.")

    positions = []
    for marker in MAP_SECTIONS:
        idx = map_text.find(marker)
        if idx < 0:
            errors.append(f"Seção obrigatória ausente no mapa: {marker}")
        positions.append(idx)
    present_positions = [p for p in positions if p >= 0]
    if len(present_positions) == len(MAP_SECTIONS) and positions != sorted(positions):
        errors.append("As seções principais do mapa estão fora da ordem obrigatória.")

    taxonomy_section = section_between(
        map_text,
        "## Taxonomia de Temas",
        ["## Entradas por Tema"],
    )
    taxonomy = [norm_name(x) for x in TAXONOMY_RE.findall(taxonomy_section)]
    blocks = topic_blocks(map_text)
    block_names = [name for name, _ in blocks]

    if not blocks:
        errors.append("Nenhum bloco '### Tema:' foi encontrado.")

    if len(set(block_names)) != len(block_names):
        errors.append("Há nomes de temas duplicados.")

    if taxonomy and taxonomy != block_names:
        # Strict order equality improves stable retrieval and predictability.
        errors.append("A Taxonomia de Temas não coincide, na mesma ordem, com os blocos '### Tema:'.")

    theme_count = len(block_names)
    source_article_count = len({m.group(1).upper() for m in ARTICLE_TOKEN_RE.finditer(source)})
    short_source = len(source) < 6000 or source_article_count < 10

    if theme_count > 80:
        errors.append(f"Taxonomia possui {theme_count} temas; o máximo é 80.")
    if theme_count < 20 and not short_source:
        errors.append(
            f"Taxonomia possui {theme_count} temas em documento que não parece curto; esperado 20–80."
        )
    if theme_count < 20 and short_source:
        warnings.append(
            f"Taxonomia com {theme_count} temas aceita porque a fonte parece curta; justificar no README."
        )

    block_map = {name: block for name, block in blocks}
    relation_map: dict[str, set[str]] = {}

    for name, block in blocks:
        for field in TOPIC_FIELDS:
            if field not in block:
                errors.append(f"Tema '{name}' sem campo obrigatório: {field}")

        qn = questions_count(block)
        if qn < 2 or qn > 5:
            errors.append(f"Tema '{name}' possui {qn} perguntas típicas; esperado 2–5.")

        rels = relations_for(block)
        relation_map[name] = rels
        if name in rels:
            warnings.append(f"Tema '{name}' possui autorrelação.")

    for src, targets in relation_map.items():
        for target in targets:
            if target not in block_map:
                errors.append(f"Tema '{src}' referencia tema inexistente '{target}'.")
                continue
            if src not in relation_map.get(target, set()):
                errors.append(f"Relação unilateral: '{src}' -> '{target}' sem relação reversa.")

    src_arts, src_anns, src_tabs, src_paras, src_incisos = source_tokens(source)
    scopes = article_scopes(source)

    for name, block in blocks:
        refs = refs_section(block)
        approx = "LOCALIZACAO APROXIMADA" in normalized_ascii(refs).upper() or "LOCALIZACAO APROXIMADA" in refs.upper()

        # ⛔ FIX A1 (review adversarial 2026-09-11, provado por execução): a cláusula
        #    `and not approx` suprimia TODOS os erros de ausência do tema — bastava escrever
        #    "LOCALIZACAO APROXIMADA" para um "Art. 999" inexistente sair `status: ok`, exit 0,
        #    contrariando a regra "não inventar referência" do próprio SKILL.md.
        #    A âncora de MAIOR NÍVEL (o artigo) é obrigatória COM ou SEM o marcador; a
        #    aproximação só dispensa os níveis mais profundos (§/inciso).
        for m in ARTICLE_TOKEN_RE.finditer(refs):
            token = m.group(1).upper()
            if token not in src_arts:
                errors.append(f"Tema '{name}' cita Art. {token}, ausente da fonte.")

        for m in ANNEX_TOKEN_RE.finditer(refs):
            token = m.group(1).upper()
            if token not in src_anns:
                errors.append(f"Tema '{name}' cita Anexo {token}, ausente da fonte.")

        for m in TABLE_TOKEN_RE.finditer(refs):
            token = m.group(1).upper()
            if token not in src_tabs:
                errors.append(f"Tema '{name}' cita Tabela {token}, ausente da fonte.")

        # ⛔ FIX R2: o par (artigo, §/inciso) tem de coexistir no MESMO artigo.
        for linha in refs.split("\n"):
            t = linha.strip()
            if not t or APPROX_RE.search(normalized_ascii(t).upper()):
                continue
            ma = ARTICLE_TOKEN_RE.search(t)
            if not ma:
                continue
            art = ma.group(1).upper()
            if art not in scopes:
                continue
            for mp in PARAGRAPH_TOKEN_RE.finditer(t):
                alvo = "§" + mp.group(1).upper().replace("°", "º")
                if alvo not in scopes[art]:
                    errors.append(
                        f"Tema '{name}' cita Art. {art}, {alvo} — esse dispositivo não pertence a esse artigo na fonte."
                    )

        for m in PARAGRAPH_TOKEN_RE.finditer(refs):
            token = m.group(1).upper().replace("°", "º")
            if token not in src_paras and not approx:
                errors.append(f"Tema '{name}' cita § {token}, ausente da fonte.")

        for m in INCISO_TOKEN_RE.finditer(refs):
            token = m.group(1).upper()
            if token not in src_incisos and not approx:
                errors.append(f"Tema '{name}' cita Inciso {token}, ausente da fonte.")

    annex_index = section_between(map_text, "## Índice de Anexos e Tabelas", [])
    for ann in sorted(src_anns):
        if not re.search(rf"\bAnexo\s*:?\s*{re.escape(ann)}\b", annex_index, re.IGNORECASE):
            warnings.append(f"Anexo {ann} aparece na fonte, mas não foi localizado no índice final.")
    for tab in sorted(src_tabs):
        if not re.search(rf"\bTabela\s*:?\s*{re.escape(tab)}\b", annex_index, re.IGNORECASE):
            warnings.append(f"Tabela {tab} aparece na fonte, mas não foi localizada no índice final.")

    for marker in README_MARKERS:
        if marker not in readme:
            errors.append(f"Marcador obrigatório ausente no README: {marker}")

    # Check the declared count when present.
    m_count = re.search(r"Temas criados:\s*(\d+)", readme)
    if m_count and int(m_count.group(1)) != theme_count:
        errors.append(
            f"README declara {m_count.group(1)} temas, mas o mapa contém {theme_count}."
        )

    long_lines = [i + 1 for i, line in enumerate(readme.splitlines()) if len(line) > 120]
    if long_lines:
        warnings.append(
            "README contém linhas acima de 120 caracteres: "
            + ", ".join(map(str, long_lines[:10]))
            + ("..." if len(long_lines) > 10 else "")
        )

    # Heuristic: semantic map should not reproduce unusually long source paragraphs verbatim.
    source_paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", source)]
    for paragraph in source_paragraphs:
        if len(paragraph) >= 500 and paragraph in map_text:
            warnings.append(
                "Possível reprodução integral de trecho longo da norma no mapa; resumir e referenciar."
            )
            break

    status = "ok" if not errors else "error"
    output = {
        "status": status,
        "stats": {
            "themes": theme_count,
            "directed_relations": sum(len(v) for v in relation_map.values()),
            "source_articles": len(src_arts),
            "source_annexes": len(src_anns),
            "source_tables": len(src_tabs),
        },
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
