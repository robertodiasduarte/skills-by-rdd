#!/usr/bin/env python3
"""
Processa DOCX, PDF ou TXT para um Markdown ajustado e um README TXT rígido.

Princípios:
- Sem OCR.
- Sem reescrita editorial.
- Remoção de não vigência apenas quando objetiva.
- Saída bem-sucedida: exatamente dois arquivos finais (.md e .txt).
- Somente biblioteca padrão para DOCX/TXT; PDF usa backend local já instalado
  (PyMuPDF/fitz, pypdf ou PyPDF2), sem downloads ou instalação em runtime.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import math
import re
import statistics
import sys
import unicodedata
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

SUPPORTED = {".docx", ".pdf", ".txt"}
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
STOP_EXIT = 2

LEGAL_HEADING_PATTERNS = [
    (1, re.compile(r"^\s*T[ÍI]TULO\b", re.I)),
    (2, re.compile(r"^\s*CAP[ÍI]TULO\b", re.I)),
    (3, re.compile(r"^\s*(?:SE[CÇ][AÃ]O|SUBSE[CÇ][AÃ]O)\b", re.I)),
]
STRUCTURAL_RE = re.compile(
    r"^\s*(?:"
    r"#{1,6}\s+|"
    r"[-*•]\s+|"
    r"\d+[.)]\s+|"
    r"[IVXLCDM]+[.)]\s+|"
    r"[A-Za-z]\)\s+|"
    r"Art\.?\s*\d|"
    r"§\s*\d|"
    r"Par[aá]grafo\s+[uú]nico|"
    r"Inciso\s+[IVXLCDM]+"
    r")",
    re.I,
)
STANDALONE_NONVIGENT_RE = re.compile(
    r"^\s*[\[(]?\s*(?:REVOGAD[OA]S?|VETAD[OA]S?|SEM\s+EFIC[AÁ]CIA)\s*[\])]?\s*[.;:]?\s*$",
    re.I,
)
NONVIGENT_ANY_RE = re.compile(
    r"(?:REVOGAD[OA]S?|VETAD[OA]S?|SEM\s+EFIC[AÁ]CIA)",
    re.I,
)
REVISION_SIGNAL_RE = re.compile(
    r"(?:reda[cç][aã]o\s+dada|inclu[ií]d[oa]|produ[cç][aã]o\s+de\s+efeitos|"
    r"nova\s+reda[cç][aã]o|alterad[oa]\s+por)",
    re.I,
)
CROSSREF_RE = re.compile(
    r"\b(?:ver\s+acima|conforme\s+(?:o\s+)?item\s+anterior|como\s+acima|"
    r"nos\s+termos\s+acima)\b",
    re.I,
)

class StopProcessing(RuntimeError):
    pass

def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"

def parse_on_off(el: ET.Element | None) -> bool:
    if el is None:
        return False
    val = el.get(qn("val"))
    if val is None:
        return True
    return str(val).strip().lower() not in {"0", "false", "off", "none", "no"}

def normalize_text(text: str) -> tuple[str, int]:
    nb = text.count("\u00a0") + text.count("\u202f")
    text = text.replace("\u00a0", " ").replace("\u202f", " ")
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text, nb

def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

def normalize_base_name(path: Path) -> str:
    base = strip_accents(path.stem)
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"[^A-Za-z0-9_-]+", "", base)
    base = re.sub(r"-{2,}", "-", base).strip("-_")
    return base or "documento"

def normalize_uf(raw: str | None) -> str:
    if not raw:
        return "UF-XX"
    uf = strip_accents(raw).upper().strip()
    uf = re.sub(r"^UF-", "", uf)
    if not re.fullmatch(r"[A-Z]{2}", uf):
        raise StopProcessing("UF inválida. Use duas letras, por exemplo SP.")
    return f"UF-{uf}"

def normalize_date(raw: str | None) -> str:
    if not raw:
        return dt.date.today().isoformat()
    try:
        return dt.date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise StopProcessing("Data inválida. Use AAAA-MM-DD.") from exc

def is_heading_line(line: str) -> int | None:
    clean = line.strip()
    if not clean or len(clean) > 180:
        return None
    for level, pattern in LEGAL_HEADING_PATTERNS:
        if pattern.search(clean):
            return level
    # Heurística geral, conservadora: texto curto todo em maiúsculas e com letras.
    letters = [c for c in clean if c.isalpha()]
    if len(letters) >= 4 and all(c.isupper() for c in letters):
        return 2
    return None

def dehyphenate_physical_lines(lines: list[str], stats: dict) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            # Somente hífen ASCII no fim físico de linha, palavra alfabética >=3,
            # continuação iniciando por minúscula. Não tocar em listas/estruturas.
            m = re.search(r"([A-Za-zÀ-ÖØ-öø-ÿ]{3,})-$", cur.rstrip())
            n = re.match(r"^\s*([a-zà-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ]*)", nxt)
            if m and n and not STRUCTURAL_RE.match(nxt):
                joined = cur.rstrip()[:-1] + nxt.lstrip()
                out.append(joined)
                stats["dehyphenations"] += 1
                i += 2
                continue
        out.append(cur)
        i += 1
    return out

def remove_explicit_nonvigent_lines(lines: list[str], stats: dict, ambiguities: list[str]) -> list[str]:
    out = []
    for line in lines:
        s = line.strip()
        if s and STANDALONE_NONVIGENT_RE.fullmatch(s):
            stats["nonvigent_removed"] += 1
            continue
        if s and NONVIGENT_ANY_RE.search(s):
            ambiguities.append(f"Marcador de não vigência com texto substantivo mantido: {s[:180]}")
        out.append(line)
    return out

def reflow_lines(lines: list[str], stats: dict, ambiguities: list[str]) -> list[str]:
    lines = dehyphenate_physical_lines(lines, stats)
    paragraphs: list[str] = []
    buf: list[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return
        text = " ".join(x.strip() for x in buf if x.strip())
        text = re.sub(r"\s{2,}", " ", text).strip()
        if text:
            paragraphs.extend(split_long_paragraph(text, stats, ambiguities))
        buf = []

    for raw in lines:
        line = raw.strip()
        if not line:
            flush()
            if paragraphs and paragraphs[-1] != "":
                paragraphs.append("")
            continue
        level = is_heading_line(line)
        if level:
            flush()
            paragraphs.append("#" * level + " " + line)
            paragraphs.append("")
            continue
        if STRUCTURAL_RE.match(line):
            flush()
            paragraphs.append(line)
            paragraphs.append("")
            continue
        if REVISION_SIGNAL_RE.search(line):
            ambiguities.append(f"Sinal de redação histórica/alteração requer revisão conservadora: {line[:180]}")
        if CROSSREF_RE.search(line):
            ambiguities.append(f"Referência interna não resolvida automaticamente: {line[:180]}")
        # Se não há quebra em branco, juntar linhas físicas corridas.
        buf.append(line)

    flush()
    # reduzir múltiplas linhas vazias
    compact: list[str] = []
    for item in paragraphs:
        if item == "" and compact and compact[-1] == "":
            continue
        compact.append(item)
    while compact and compact[-1] == "":
        compact.pop()
    return compact

def split_long_paragraph(text: str, stats: dict, ambiguities: list[str]) -> list[str]:
    max_chars = 1800
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?;:])\s+(?=[A-ZÀ-ÖØ-Þ§])", text)
    if len(sentences) <= 1:
        ambiguities.append(
            f"Parágrafo longo ({len(text)} caracteres) mantido por falta de fronteira segura."
        )
        return [text]
    chunks: list[str] = []
    cur = ""
    for sent in sentences:
        candidate = sent if not cur else cur + " " + sent
        if cur and len(candidate) > max_chars:
            chunks.append(cur)
            cur = sent
        else:
            cur = candidate
    if cur:
        chunks.append(cur)
    if len(chunks) > 1:
        stats["long_paragraph_splits"] += len(chunks) - 1
    return chunks

def markdown_from_lines(lines: list[str], stats: dict, ambiguities: list[str]) -> str:
    normed = []
    for line in lines:
        n, nb = normalize_text(line)
        stats["nbsp_normalized"] += nb
        normed.extend(n.split("\n"))
    normed = remove_explicit_nonvigent_lines(normed, stats, ambiguities)
    items = reflow_lines(normed, stats, ambiguities)
    return "\n".join(items).strip() + "\n"

def style_heading_level(style: str | None) -> int | None:
    if not style:
        return None
    s = strip_accents(style).lower().replace("_", " ").strip()
    if s in {"title", "titulo"}:
        return 1
    m = re.search(r"(?:heading|titulo)\s*([1-6])", s)
    if m:
        return min(3, int(m.group(1)))
    return None

def read_run_text(run: ET.Element) -> str:
    parts: list[str] = []
    for node in run.iter():
        if node.tag == qn("t"):
            parts.append(node.text or "")
        elif node.tag == qn("tab"):
            parts.append("\t")
        elif node.tag in {qn("br"), qn("cr")}:
            parts.append("\n")
    return "".join(parts)

def extract_docx(path: Path, stats: dict, ambiguities: list[str]) -> tuple[str, dict]:
    meta = {
        "text_extractable": "SIM",
        "multicolumn": "NA",
        "possible_images": "NAO",
        "tables": 0,
        "method": "DOCX por atributo OOXML w:strike/w:dstrike",
        "format_notes": [],
    }
    try:
        zf = zipfile.ZipFile(path)
    except Exception as exc:
        raise StopProcessing(f"DOCX não pode ser aberto: {exc}") from exc
    with zf:
        try:
            xml = zf.read("word/document.xml")
        except KeyError as exc:
            raise StopProcessing("DOCX inválido: word/document.xml ausente.") from exc
        try:
            root = ET.fromstring(xml)
        except ET.ParseError as exc:
            raise StopProcessing("DOCX inválido: XML principal corrompido.") from exc

        body = root.find("w:body", NS)
        if body is None:
            raise StopProcessing("DOCX inválido: corpo do documento ausente.")

        out: list[str] = []
        image_count = 0

        def paragraph_text(p: ET.Element) -> tuple[str, str | None, bool]:
            nonlocal image_count
            ppr = p.find("w:pPr", NS)
            style = None
            is_list = False
            if ppr is not None:
                pstyle = ppr.find("w:pStyle", NS)
                if pstyle is not None:
                    style = pstyle.get(qn("val"))
                if ppr.find("w:numPr", NS) is not None:
                    is_list = True
            text_parts: list[str] = []
            for run in p.iter(qn("r")):
                rpr = run.find("w:rPr", NS)
                struck = False
                if rpr is not None:
                    struck = parse_on_off(rpr.find("w:strike", NS)) or parse_on_off(rpr.find("w:dstrike", NS))
                t = read_run_text(run)
                if struck:
                    if t.strip():
                        stats["struck_runs_removed"] += 1
                        stats["nonvigent_removed"] += 1
                    continue
                text_parts.append(t)
            drawings = len(list(p.iter(qn("drawing")))) + len(list(p.iter(qn("pict"))))
            image_count += drawings
            text = "".join(text_parts)
            text, nb = normalize_text(text)
            stats["nbsp_normalized"] += nb
            return text.strip(), style, is_list

        def table_to_text(tbl: ET.Element) -> list[str]:
            rows: list[list[str]] = []
            for tr in tbl.findall("w:tr", NS):
                cells: list[str] = []
                for tc in tr.findall("w:tc", NS):
                    paras: list[str] = []
                    for p in tc.findall(".//w:p", NS):
                        t, _, _ = paragraph_text(p)
                        if t:
                            paras.append(t)
                    cells.append(" ".join(paras).strip())
                if cells:
                    rows.append(cells)
            meta["tables"] += 1
            if not rows:
                return []
            widths = {len(r) for r in rows}
            # Não inventar cabeçalho de tabela. Manter linhas com separador visual simples.
            if len(widths) != 1:
                ambiguities.append("Tabela DOCX irregular linearizada como texto por linha; revisar semântica.")
            else:
                ambiguities.append("Tabela DOCX preservada como linhas de células; não convertida para tabela Markdown sem cabeçalho confiável.")
            return [" | ".join(c for c in row) for row in rows]

        for child in list(body):
            if child.tag == qn("p"):
                text, style, is_list = paragraph_text(child)
                if not text:
                    continue
                level = style_heading_level(style)
                if level:
                    out.append("#" * level + " " + text)
                    out.append("")
                elif is_list:
                    # Preservar o item sem inventar índice: marcador neutro.
                    out.append("- " + text)
                    out.append("")
                else:
                    # aplicar heading legal somente se evidente
                    legal = is_heading_line(text)
                    if legal:
                        out.append("#" * legal + " " + text)
                    else:
                        out.append(text)
                    out.append("")
            elif child.tag == qn("tbl"):
                rows = table_to_text(child)
                if rows:
                    out.extend(rows)
                    out.append("")

        image_count += len(list(root.iter(qn("drawing")))) + len(list(root.iter(qn("pict"))))
        # O cálculo acima pode contar novamente; o objetivo é apenas presença.
        if image_count:
            meta["possible_images"] = "SIM"
            meta["format_notes"].append(
                "Imagens/desenhos detectados no DOCX; conteúdo interno não foi lido nem submetido a OCR."
            )
        if any(name.startswith("word/header") or name.startswith("word/footer") for name in zf.namelist()):
            meta["format_notes"].append(
                "Cabeçalhos/rodapés DOCX foram excluídos do corpo processado; revisar se continham conteúdo substantivo."
            )

    text = "\n".join(out).strip()
    if len(re.sub(r"\s+", "", text)) < 20:
        raise StopProcessing("DOCX sem conteúdo textual suficiente no corpo.")
    # Evitar novo reflow agressivo: DOCX já fornece parágrafos estruturados.
    lines = text.splitlines()
    lines = remove_explicit_nonvigent_lines(lines, stats, ambiguities)
    final_lines: list[str] = []
    for line in lines:
        if line.startswith("#") or line.startswith("- "):
            final_lines.append(line)
            continue
        if REVISION_SIGNAL_RE.search(line):
            ambiguities.append(f"Sinal de redação histórica/alteração mantido para revisão: {line[:180]}")
        if CROSSREF_RE.search(line):
            ambiguities.append(f"Referência interna não resolvida automaticamente: {line[:180]}")
        if len(line) > 1800:
            parts = split_long_paragraph(line, stats, ambiguities)
            final_lines.extend(parts)
        else:
            final_lines.append(line)
    # compactar vazios
    compact = []
    for x in final_lines:
        if x == "" and compact and compact[-1] == "":
            continue
        compact.append(x)
    return "\n".join(compact).strip() + "\n", meta

def _norm_repeat(s: str) -> str:
    s, _ = normalize_text(s)
    s = re.sub(r"\d+", "#", s.strip().lower())
    s = re.sub(r"\s+", " ", s)
    return s[:240]

def _detect_multicolumn(blocks: list[tuple], page_width: float) -> bool:
    candidates = []
    for b in blocks:
        x0, y0, x1, y1, text = b[:5]
        width = max(0.0, x1 - x0)
        if not str(text).strip() or width > 0.68 * page_width:
            continue
        candidates.append((x0, y0, x1, y1, text))
    if len(candidates) < 6:
        return False
    left = [b for b in candidates if ((b[0] + b[2]) / 2) < 0.45 * page_width]
    right = [b for b in candidates if ((b[0] + b[2]) / 2) > 0.55 * page_width]
    if len(left) < 2 or len(right) < 2:
        return False
    if len(left) / len(candidates) < 0.28 or len(right) / len(candidates) < 0.28:
        return False
    overlaps = 0
    for l in left:
        for r in right:
            top = max(l[1], r[1])
            bottom = min(l[3], r[3])
            if bottom - top > 10:
                overlaps += 1
                if overlaps >= 2:
                    return True
    return False

def _detect_multicolumn_words(words: list[tuple], page_width: float) -> bool:
    """Detectar coluna dupla mesmo quando PyMuPDF funde ambas no mesmo bloco."""
    if len(words) < 12:
        return False
    # Agrupar palavras por linha visual usando proximidade do centro Y.
    ordered = sorted(words, key=lambda w: ((float(w[1]) + float(w[3])) / 2, float(w[0])))
    clusters: list[list[tuple]] = []
    for w in ordered:
        yc = (float(w[1]) + float(w[3])) / 2
        if not clusters:
            clusters.append([w])
            continue
        prev_y = sum((float(x[1]) + float(x[3])) / 2 for x in clusters[-1]) / len(clusters[-1])
        if abs(yc - prev_y) <= 2.5:
            clusters[-1].append(w)
        else:
            clusters.append([w])

    gap_midpoints: list[float] = []
    min_gap = max(55.0, 0.11 * page_width)
    for cluster in clusters:
        ws = sorted(cluster, key=lambda w: float(w[0]))
        if len(ws) < 4:
            continue
        best_gap = 0.0
        best_mid = None
        for a, b in zip(ws, ws[1:]):
            gap = float(b[0]) - float(a[2])
            if gap > best_gap:
                best_gap = gap
                best_mid = (float(a[2]) + float(b[0])) / 2
        if best_mid is None or best_gap < min_gap:
            continue
        left_words = [w for w in ws if float(w[2]) <= best_mid]
        right_words = [w for w in ws if float(w[0]) >= best_mid]
        if len(left_words) >= 2 and len(right_words) >= 2:
            gap_midpoints.append(best_mid)

    if len(gap_midpoints) < 3:
        return False
    med = statistics.median(gap_midpoints)
    aligned = [g for g in gap_midpoints if abs(g - med) <= 0.08 * page_width]
    return len(aligned) >= 3 and 0.32 * page_width <= med <= 0.68 * page_width

def extract_pdf_fitz(path: Path, stats: dict, ambiguities: list[str]):
    import fitz  # type: ignore

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise StopProcessing(f"PDF não pode ser aberto: {exc}") from exc
    if doc.page_count == 0:
        raise StopProcessing("PDF sem páginas.")

    pages = []
    top_candidates: list[str] = []
    bottom_candidates: list[str] = []
    multicol_pages = []
    image_blocks = 0

    for i in range(doc.page_count):
        page = doc.load_page(i)
        raw_blocks = page.get_text("blocks")
        text_blocks = []
        for b in raw_blocks:
            # PyMuPDF blocks: x0,y0,x1,y1,text,block_no,block_type
            btype = b[6] if len(b) > 6 else 0
            if btype == 1:
                image_blocks += 1
                continue
            text = str(b[4]) if len(b) > 4 else ""
            if text.strip():
                text_blocks.append((float(b[0]), float(b[1]), float(b[2]), float(b[3]), text))
        words = page.get_text("words")
        if _detect_multicolumn(text_blocks, float(page.rect.width)) or _detect_multicolumn_words(words, float(page.rect.width)):
            multicol_pages.append(i + 1)

        top = [b for b in text_blocks if b[1] <= 0.08 * page.rect.height]
        bottom = [b for b in text_blocks if b[3] >= 0.92 * page.rect.height]
        for b in top:
            top_candidates.append(_norm_repeat(b[4]))
        for b in bottom:
            bottom_candidates.append(_norm_repeat(b[4]))
        pages.append((page.rect.width, page.rect.height, text_blocks))

    if multicol_pages:
        raise StopProcessing(
            "PDF multi-coluna detectado com alto risco de ordem incorreta "
            f"(páginas: {', '.join(map(str, multicol_pages[:12]))}). "
            "Forneça versão linear DOCX/MD/TXT ou PDF de coluna única."
        )

    threshold = max(2, math.ceil(doc.page_count * 0.6))
    top_counts = collections.Counter(c for c in top_candidates if len(c) >= 4)
    bottom_counts = collections.Counter(c for c in bottom_candidates if len(c) >= 4)
    repeated_top = {k for k, v in top_counts.items() if v >= threshold}
    repeated_bottom = {k for k, v in bottom_counts.items() if v >= threshold}

    page_texts = []
    chars_per_page = []
    for width, height, blocks in pages:
        kept = []
        for b in sorted(blocks, key=lambda x: (x[1], x[0])):
            x0, y0, x1, y1, text = b
            norm = _norm_repeat(text)
            if y0 <= 0.08 * height and norm in repeated_top:
                stats["headers_footers_removed"] += 1
                continue
            if y1 >= 0.92 * height and norm in repeated_bottom:
                stats["headers_footers_removed"] += 1
                continue
            kept.append(text)
        ptxt = "\n".join(kept).strip()
        page_texts.append(ptxt)
        chars_per_page.append(len(re.sub(r"\s+", "", ptxt)))

    total_chars = sum(chars_per_page)
    median_chars = statistics.median(chars_per_page) if chars_per_page else 0
    if total_chars < 80 or median_chars < 15:
        raise StopProcessing("PDF com extração textual essencialmente vazia; provável scan/imagem. OCR é proibido.")

    meta = {
        "text_extractable": "SIM",
        "multicolumn": "NAO",
        "possible_images": "SIM" if image_blocks else "NAO",
        "tables": 0,
        "method": "PDF por heurística textual conservadora; sem inferência visual de tachado",
        "format_notes": [],
    }
    if image_blocks:
        meta["format_notes"].append(
            "Blocos de imagem detectados no PDF; conteúdo interno não foi lido nem submetido a OCR."
        )
    if repeated_top or repeated_bottom:
        meta["format_notes"].append("Cabeçalhos/rodapés repetitivos removidos por repetição determinística.")
    return "\n\n".join(page_texts), meta

def extract_pdf_text_backend(path: Path, stats: dict, ambiguities: list[str]):
    # Fallback sem coordenadas; não permite diagnóstico forte de colunas.
    PdfReader = None
    backend = None
    try:
        from pypdf import PdfReader as PR  # type: ignore
        PdfReader, backend = PR, "pypdf"
    except Exception:
        try:
            from PyPDF2 import PdfReader as PR  # type: ignore
            PdfReader, backend = PR, "PyPDF2"
        except Exception as exc:
            raise StopProcessing(
                "Nenhum extrator textual de PDF offline disponível (fitz/pypdf/PyPDF2)."
            ) from exc
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise StopProcessing(f"PDF não pode ser aberto: {exc}") from exc
    if not getattr(reader, "pages", None):
        raise StopProcessing("PDF sem páginas.")
    page_texts = []
    for page in reader.pages:
        try:
            page_texts.append((page.extract_text() or "").strip())
        except Exception:
            page_texts.append("")
    chars = [len(re.sub(r"\s+", "", t)) for t in page_texts]
    if sum(chars) < 80 or statistics.median(chars or [0]) < 15:
        raise StopProcessing("PDF com extração textual essencialmente vazia; provável scan/imagem. OCR é proibido.")

    # Remoção conservadora de primeira/última linha repetida.
    firsts, lasts = [], []
    split_pages = []
    for t in page_texts:
        ls = [x.strip() for x in t.splitlines() if x.strip()]
        split_pages.append(ls)
        if ls:
            firsts.append(_norm_repeat(ls[0]))
            lasts.append(_norm_repeat(ls[-1]))
    threshold = max(2, math.ceil(len(page_texts) * 0.6))
    rep_first = {k for k, v in collections.Counter(firsts).items() if v >= threshold and len(k) >= 4}
    rep_last = {k for k, v in collections.Counter(lasts).items() if v >= threshold and len(k) >= 4}
    cleaned = []
    for ls in split_pages:
        if ls and _norm_repeat(ls[0]) in rep_first:
            ls = ls[1:]
            stats["headers_footers_removed"] += 1
        if ls and _norm_repeat(ls[-1]) in rep_last:
            ls = ls[:-1]
            stats["headers_footers_removed"] += 1
        cleaned.append("\n".join(ls))
    ambiguities.append(
        f"PDF extraído com backend {backend} sem coordenadas; diagnóstico de multicoluna limitado."
    )
    meta = {
        "text_extractable": "SIM",
        "multicolumn": "AMBIGUO",
        "possible_images": "NA",
        "tables": 0,
        "method": "PDF por heurística textual conservadora; sem inferência visual de tachado",
        "format_notes": [
            "Backend sem coordenadas: validar colunas/layout com ferramenta PDF nativa, se disponível."
        ],
    }
    return "\n\n".join(cleaned), meta

def extract_pdf(path: Path, stats: dict, ambiguities: list[str]) -> tuple[str, dict]:
    try:
        return extract_pdf_fitz(path, stats, ambiguities)
    except ImportError:
        return extract_pdf_text_backend(path, stats, ambiguities)

def extract_txt(path: Path, stats: dict, ambiguities: list[str]) -> tuple[str, dict]:
    try:
        raw = path.read_bytes()
    except Exception as exc:
        raise StopProcessing(f"TXT não pode ser lido: {exc}") from exc
    encoding = "utf-8"
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Fallback explícito e registrado.
        text = raw.decode("latin-1")
        encoding = "latin-1"
        ambiguities.append("TXT não era UTF-8; aplicado fallback latin-1.")
    if len(re.sub(r"\s+", "", text)) < 20:
        raise StopProcessing("TXT sem conteúdo textual suficiente.")
    meta = {
        "text_extractable": "SIM",
        "multicolumn": "NA",
        "possible_images": "NA",
        "tables": 0,
        "method": "TXT por marcadores textuais explícitos de não vigência",
        "format_notes": [f"Codificação lida como {encoding}."],
    }
    return text, meta

def make_markdown(path: Path, stats: dict, ambiguities: list[str]) -> tuple[str, dict]:
    ext = path.suffix.lower()
    if ext == ".docx":
        return extract_docx(path, stats, ambiguities)
    if ext == ".pdf":
        raw, meta = extract_pdf(path, stats, ambiguities)
        return markdown_from_lines(raw.splitlines(), stats, ambiguities), meta
    if ext == ".txt":
        raw, meta = extract_txt(path, stats, ambiguities)
        return markdown_from_lines(raw.splitlines(), stats, ambiguities), meta
    raise StopProcessing(f"Extensão não suportada: {ext or '(sem extensão)'}.")

def list_or_none(items: list[str]) -> list[str]:
    return items if items else ["NENHUMA"]

def build_readme(
    source: Path,
    ext: str,
    process_date: str,
    uf_label: str,
    meta: dict,
    stats: dict,
    ambiguities: list[str],
    md_name: str,
    readme_name: str,
) -> str:
    changes: list[str] = []
    if stats["nbsp_normalized"]:
        changes.append(f"NBSP/espaços especiais normalizados: {stats['nbsp_normalized']}.")
    if stats["dehyphenations"]:
        changes.append(f"Quebras hifenizadas inequivocas reunidas: {stats['dehyphenations']}.")
    if stats["headers_footers_removed"]:
        changes.append(f"Blocos/linhas repetitivos de cabecalho/rodape removidos: {stats['headers_footers_removed']}.")
    if stats["long_paragraph_splits"]:
        changes.append(f"Divisoes estruturais de paragrafos longos em fronteiras seguras: {stats['long_paragraph_splits']}.")
    if stats["struck_runs_removed"]:
        changes.append(f"Runs DOCX tachados removidos: {stats['struck_runs_removed']}.")
    if stats["nonvigent_removed"] and not stats["struck_runs_removed"]:
        changes.append(f"Linhas com marcador textual inequivoco de nao vigencia removidas: {stats['nonvigent_removed']}.")
    for note in meta.get("format_notes", []):
        changes.append(note)

    vigency_ambiguities = [
        item for item in ambiguities
        if item.startswith("Marcador de não vigência")
        or item.startswith("Sinal de redação histórica/alteração")
    ]
    status = "OK_COM_ALERTAS" if ambiguities or meta.get("format_notes") else "OK"
    lines = [
        "RELATORIO DE PARSING E CHUNKING",
        "================================",
        f"ARQUIVO_ORIGEM: {source.name}",
        f"TIPO: {ext.upper().lstrip('.')}",
        f"DATA_PROCESSAMENTO: {process_date}",
        f"UF: {uf_label}",
        f"STATUS: {status}",
        "",
        "DIAGNOSTICO",
        "-----------",
        f"TEXTO_EXTRAIVEL: {meta.get('text_extractable', 'NA')}",
        f"MULTICOLUNA: {meta.get('multicolumn', 'NA')}",
        f"IMAGENS_RELEVANTES_POSSIVEIS: {meta.get('possible_images', 'NA')}",
        f"TABELAS_DETECTADAS: {meta.get('tables', 0)}",
        "",
        "ALTERACOES_APLICADAS",
        "--------------------",
    ]
    for item in list_or_none(changes):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "VIGENCIA",
        "--------",
        f"METODO_DETECCAO: {meta.get('method', 'NA')}",
        f"BLOCOS_OU_LINHAS_REMOVIDOS: {stats['nonvigent_removed']}",
        f"CASOS_AMBIGUOS_MANTIDOS: {len(vigency_ambiguities)}",
    ])
    if vigency_ambiguities:
        for item in vigency_ambiguities:
            # README ASCII-ish where feasible; preserve substantive original snippets.
            lines.append(f"- {item}")
    else:
        lines.append("- NENHUM")
    lines.extend([
        "",
        "PENDENCIAS_E_LIMITACOES",
        "-----------------------",
    ])
    pending = []
    if meta.get("possible_images") == "SIM":
        pending.append("Conteudo em imagens nao foi lido; OCR nao foi aplicado.")
    if meta.get("multicolumn") == "AMBIGUO":
        pending.append("Diagnostico de multicoluna limitado pelo backend de extracao.")
    pending.extend(ambiguities)
    for item in list_or_none(pending):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "SAIDAS",
        "------",
        f"MARKDOWN: {md_name}",
        f"RELATORIO: {readme_name}",
        "",
    ])
    return "\n".join(lines)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preparar DOCX/PDF/TXT para parsing e chunking sem OCR."
    )
    parser.add_argument("input", help="Arquivo DOCX, PDF ou TXT.")
    parser.add_argument("--output-dir", required=True, help="Diretorio de saida.")
    parser.add_argument("--uf", help="UF em duas letras, por exemplo SP.")
    parser.add_argument("--date", help="Data AAAA-MM-DD; padrao: data atual.")
    args = parser.parse_args(argv)

    source = Path(args.input).expanduser()
    try:
        if not source.exists() or not source.is_file():
            raise StopProcessing("Arquivo de entrada não existe ou não é arquivo.")
        ext = source.suffix.lower()
        if ext not in SUPPORTED:
            raise StopProcessing("Formato não suportado. Use DOCX, PDF ou TXT.")
        uf_label = normalize_uf(args.uf)
        process_date = normalize_date(args.date)

        stats = {
            "nbsp_normalized": 0,
            "dehyphenations": 0,
            "headers_footers_removed": 0,
            "long_paragraph_splits": 0,
            "struck_runs_removed": 0,
            "nonvigent_removed": 0,
        }
        ambiguities: list[str] = []

        markdown, meta = make_markdown(source, stats, ambiguities)
        if len(re.sub(r"\s+", "", markdown)) < 20:
            raise StopProcessing("Conteúdo resultante insuficiente após processamento.")

        outdir = Path(args.output_dir).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)
        base = normalize_base_name(source)
        md_name = f"{uf_label}_{base}_Texto-Ajustado_ate-{process_date}.md"
        readme_name = f"{uf_label}_{base}_README_ate-{process_date}.txt"
        md_path = outdir / md_name
        readme_path = outdir / readme_name

        # Escrever somente os dois artefatos finais.
        md_path.write_text(markdown, encoding="utf-8")
        readme = build_readme(
            source, ext, process_date, uf_label, meta, stats, ambiguities, md_name, readme_name
        )
        readme_path.write_text(readme, encoding="utf-8")

        payload = {
            "status": "ok",
            "files": [str(md_path), str(readme_path)],
            "warnings": ambiguities,
            "stats": stats,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except StopProcessing as exc:
        print(json.dumps({"status": "stop", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return STOP_EXIT
    except Exception as exc:
        print(
            json.dumps(
                {"status": "error", "reason": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
