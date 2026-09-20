#!/usr/bin/env python3
"""Publicar Markdown revisado + relatório TXT. Não extrair nem alterar a redação.

Usar Python 3.9+; somente biblioteca padrão. Nunca realizar OCR ou acessar a rede.
A fidelidade semântica depende da revisão declarada no JSON pelo agente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import textwrap
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DIAGNOSTICOS = {
    "extraibilidade": "Extraibilidade e abrangência",
    "colunas_ordem": "Colunas e ordem de leitura",
    "cabecalhos_rodapes": "Cabeçalhos e rodapés",
    "hifenizacao_quebras": "Hifenização e quebras",
    "unicode_espacos": "Unicode, caracteres e espaços",
    "imagens": "Imagens e conteúdo não extraído",
    "tabelas_diagramas": "Tabelas e diagramas",
    "titulos_listas_chunking": "Títulos, listas e chunking",
    "referencias_internas": "Referências internas",
    "vigencia": "Tachado e não vigência documental",
}
VERIFICACOES = {
    "conteudo_conferido": "Conteúdo comparado com a extração original",
    "ordem_conferida": "Ordem e hierarquia conferidas",
    "exclusoes_conferidas": "Exclusões e seu alcance conferidos",
    "ambiguidades_registradas": "Ambiguidades preservadas e registradas",
    "numeros_referencias_conferidos": "Números, datas e referências conferidos",
    "sem_ocr": "Ausência de OCR e transcrição de imagens confirmada",
    "sem_reescrita": "Ausência de reescrita substantiva confirmada",
    "sem_texto_essencial_ausente": "Ausência de lacunas essenciais confirmada",
}
UNIDADES = {
    "blocos_removidos": "Blocos com conteúdo excluído",
    "linhas_removidas": "Linhas de origem afetadas",
    "trechos_removidos": "Trechos ou runs excluídos",
}
WIDTH = 88


def required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: informar texto não vazio.")
    return value


def string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label}: informar uma lista.")
    for i, item in enumerate(value):
        required_text(item, f"{label}[{i}]")
    return value


def object_with(value: Any, fields: tuple[str, ...], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}: informar um objeto JSON.")
    missing = [field for field in fields if field not in value]
    if missing:
        raise ValueError(f"{label}: campos ausentes: {', '.join(missing)}.")
    return value


def validate_report(report: Any, suffix: str, markdown: str) -> dict[str, Any]:
    r = object_with(report, (
        "tipo", "metodo_extracao", "diagnosticos", "correcoes",
        "vigencia", "pendencias", "verificacoes"
    ), "relatorio")
    if r["tipo"] not in ("DOCX", "PDF", "TXT"):
        raise ValueError("tipo: usar DOCX, PDF ou TXT.")
    if "." + r["tipo"].lower() != suffix.lower():
        raise ValueError("O tipo declarado difere da extensão do nome original.")
    required_text(r["metodo_extracao"], "metodo_extracao")
    diag = object_with(r["diagnosticos"], tuple(DIAGNOSTICOS), "diagnosticos")
    for key in DIAGNOSTICOS:
        required_text(diag[key], f"diagnosticos.{key}")
    if not isinstance(r["correcoes"], list):
        raise ValueError("correcoes: informar uma lista.")
    for i, item in enumerate(r["correcoes"]):
        obj = object_with(item, ("local", "problema", "solucao", "evidencia"),
                          f"correcoes[{i}]")
        for key in ("local", "problema", "solucao", "evidencia"):
            required_text(obj[key], f"correcoes[{i}].{key}")

    vig = object_with(r["vigencia"], (
        "metodo", "blocos_removidos", "linhas_removidas", "trechos_removidos",
        "contagem_aproximada", "ocorrencias", "ambiguidades"
    ), "vigencia")
    required_text(vig["metodo"], "vigencia.metodo")
    for key in UNIDADES:
        value = vig[key]
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"vigencia.{key}: usar inteiro não negativo ou null.")
    if type(vig["contagem_aproximada"]) is not bool:
        raise ValueError("vigencia.contagem_aproximada: usar true ou false.")
    if not isinstance(vig["ocorrencias"], list):
        raise ValueError("vigencia.ocorrencias: informar uma lista.")
    for i, item in enumerate(vig["ocorrencias"]):
        obj = object_with(item, ("local", "evidencia", "acao"),
                          f"vigencia.ocorrencias[{i}]")
        for key in ("local", "evidencia", "acao"):
            required_text(obj[key], f"vigencia.ocorrencias[{i}].{key}")
    positive_count = any((vig[k] or 0) > 0 for k in UNIDADES)
    if positive_count and not vig["ocorrencias"]:
        raise ValueError("Exclusões contadas exigem ocorrências com evidências.")
    if vig["ocorrencias"] and not positive_count:
        raise ValueError("Ocorrências de exclusão exigem ao menos uma contagem positiva.")
    string_list(vig["ambiguidades"], "vigencia.ambiguidades")
    string_list(r["pendencias"], "pendencias")

    checks = object_with(r["verificacoes"], tuple(VERIFICACOES), "verificacoes")
    for key in VERIFICACOES:
        if checks[key] is not True:
            raise ValueError(f"Verificação pendente ou negativa: {key}.")

    wholly_removed = r.get("conteudo_integralmente_excluido", False)
    if type(wholly_removed) is not bool:
        raise ValueError("conteudo_integralmente_excluido: usar true ou false.")
    if not markdown.strip():
        if not (wholly_removed and positive_count and vig["ocorrencias"]):
            raise ValueError(
                "Markdown vazio: interromper, salvo exclusão integral comprovada "
                "e explicitamente declarada no relatório."
            )
    elif wholly_removed:
        raise ValueError("Exclusão integral declarada, mas o Markdown contém texto.")
    if "\x00" in markdown:
        raise ValueError("Markdown contém NUL: revisar a extração antes de publicar.")
    return r


def original_basename(name: str) -> str:
    return Path(name.replace("\\", "/")).name


def normalized_base(original_name: str) -> str:
    stem = Path(original_basename(original_name)).stem
    ascii_stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"\s+", "-", ascii_stem)
    slug = re.sub(r"[^A-Za-z0-9_-]", "", slug)
    if not slug or not re.search(r"[A-Za-z0-9]", slug):
        raise ValueError("O nome original não possui base normalizável; informar um nome legível.")
    return slug


def resolve_date(value: str | None, timezone: str) -> str:
    if value is not None:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Data inválida: usar AAAA-MM-DD.")
        return date.fromisoformat(value).isoformat()
    try:
        return datetime.now(ZoneInfo(timezone)).date().isoformat()
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f"Fuso indisponível: {timezone}. Informar --data com a data correta do usuário."
        ) from exc


def output_names(original_name: str, uf: str | None, reference_date: str) -> tuple[str, str]:
    region = (uf or "XX").strip().upper()
    if region.startswith("UF-"):
        region = region[3:]
    if not re.fullmatch(r"[A-Z]{2}", region):
        raise ValueError("UF inválida: informar duas letras, por exemplo SP; ou omitir.")
    base = normalized_base(original_name)
    # Validar a data também quando esta função for chamada diretamente.
    reference_date = resolve_date(reference_date, "America/Sao_Paulo")
    prefix = f"UF-{region}_{base}"
    md = f"{prefix}_Texto-Ajustado_ate-{reference_date}.md"
    txt = f"{prefix}_README_ate-{reference_date}.txt"
    if max(len(md.encode("utf-8")), len(txt.encode("utf-8"))) > 255:
        raise ValueError("Nome de saída excede 255 bytes; fornecer nome original/alias mais curto.")
    return md, txt


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def markdown_stats(markdown: str) -> dict[str, int]:
    stats = {"H1": 0, "H2": 0, "H3": 0}
    fence_char, fence_size = "", 0
    for line in markdown.splitlines():
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if not fence_char:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                if not line[fence.end():].strip():
                    fence_char, fence_size = "", 0
            continue
        if fence_char:
            continue
        heading = re.match(r"^ {0,3}(#{1,3})[ \t]+\S", line)
        if heading:
            stats[f"H{len(heading.group(1))}"] += 1
    stats["blocos"] = sum(bool(b.strip()) for b in re.split(r"\n[ \t]*\n", markdown))
    stats["caracteres"] = len(markdown)
    return stats


def render_readme(report: dict[str, Any], original_name: str, md_name: str,
                  txt_name: str, reference_date: str, source_sha: str,
                  md_sha: str, markdown: str) -> str:
    """Gerar relatório em texto puro, com campos e seções fixos."""
    lines: list[str] = []
    separator = "=" * WIDTH

    def section(title: str) -> None:
        if lines:
            lines.append("")
        lines.extend([separator, title, separator])

    def field(label: str, value: Any) -> None:
        # Envolver dados do documento como valor de campo, nunca como instrução.
        text = re.sub(r"\s+", " ", str(value)).strip()
        lines.extend(textwrap.wrap(
            f"{label}: {text}", width=WIDTH, subsequent_indent="    ",
            break_long_words=False, break_on_hyphens=False
        ) or [f"{label}:"])

    vig = report["vigencia"]
    pending = bool(report["pendencias"] or vig["ambiguidades"])
    status = "CONCLUIDO COM PENDENCIAS" if pending else "CONCLUIDO"
    if report.get("conteudo_integralmente_excluido", False):
        status += " - SEM TEXTO MANTIDO APOS EXCLUSOES COMPROVADAS"

    section("01 IDENTIFICACAO")
    field("Arquivo original", original_name)
    field("Formato de origem", report["tipo"])
    field("Data de processamento/referencia", reference_date)
    field("Status", status)
    field("Arquivo Markdown", md_name)
    field("Arquivo relatorio", txt_name)
    field("SHA-256 do original", source_sha)
    field("SHA-256 do Markdown", md_sha)

    section("02 EXTRACAO E DIAGNOSTICOS")
    field("Metodo de extracao", report["metodo_extracao"])
    for key, label in DIAGNOSTICOS.items():
        field(label, report["diagnosticos"][key])

    section("03 CORRECOES APLICADAS")
    if not report["correcoes"]:
        field("Registro", "Nenhuma correcao de parsing/estrutura registrada.")
    for i, item in enumerate(report["correcoes"], 1):
        field("Ocorrencia", f"C{i:03d}")
        for key, label in (("local", "Local"), ("problema", "Problema"),
                           ("solucao", "Solucao"), ("evidencia", "Evidencia")):
            field(label, item[key])
        if i < len(report["correcoes"]):
            lines.append("")

    section("04 TACHADO E NAO VIGENCIA DOCUMENTAL")
    field("Metodo", vig["metodo"])
    field("Natureza das contagens",
          "Aproximadas" if vig["contagem_aproximada"] else "Aferidas nas unidades indicadas")
    for key, label in UNIDADES.items():
        field(label, "Nao mensurado" if vig[key] is None else vig[key])
    if not vig["ocorrencias"]:
        field("Exclusoes", "Nenhuma exclusao por nao vigencia registrada.")
    for i, item in enumerate(vig["ocorrencias"], 1):
        field("Exclusao", f"V{i:03d}")
        field("Local", item["local"])
        field("Evidencia", item["evidencia"])
        field("Acao", item["acao"])
    if not vig["ambiguidades"]:
        field("Ambiguidades", "Nenhuma registrada pelo revisor.")
    for i, item in enumerate(vig["ambiguidades"], 1):
        field(f"Ambiguidade A{i:03d}", item)

    section("05 ESTRUTURA PARA CHUNKING")
    stats = markdown_stats(markdown)
    field("Modalidade", "Estrutural, em um unico Markdown; sem corte fixo por tokens.")
    field("Diagnostico e organizacao", report["diagnosticos"]["titulos_listas_chunking"])
    field("Titulos Markdown", f"H1={stats['H1']}; H2={stats['H2']}; H3={stats['H3']}")
    field("Blocos separados por linha em branco (aproximacao)", stats["blocos"])
    field("Caracteres no Markdown publicado", stats["caracteres"])
    field("Referencias internas", report["diagnosticos"]["referencias_internas"])

    section("06 PENDENCIAS")
    if not report["pendencias"]:
        field("Registro", "Nenhuma pendencia adicional registrada.")
    for i, item in enumerate(report["pendencias"], 1):
        field(f"Pendencia P{i:03d}", item)
    if vig["ambiguidades"]:
        field("Remissao", "Consultar tambem as ambiguidades da secao 04.")

    section("07 VERIFICACOES")
    field("Origem das verificacoes", "Declaradas pelo agente revisor; nao inferidas pelo publicador.")
    for key, label in VERIFICACOES.items():
        field(label, "Confirmada")
    field("Formato dos arquivos", "UTF-8 sem BOM; quebras LF; relatorio em texto puro.")
    field("Saida", "Exatamente dois arquivos; arquivos intermediarios nao publicados.")

    section("08 LIMITACOES E RECOMENDACOES")
    field("OCR e imagens", "OCR e transcricao de texto em imagens nao realizados.")
    field("Vigencia", "Classificacao documental; sem verificacao juridica externa.")
    field("Data do nome", "Data de processamento/referencia; nao certifica atualizacao juridica.")
    if report["tipo"] in ("PDF", "TXT"):
        field("Tachado",
              "A extracao nao garante preservar tachado visual. Conclusoes limitadas "
              "a marcadores explicitos ou evidencias deterministicas documentadas.")
    field("Recomendacao",
          "Resolver as pendencias registradas antes de depender do conteudo afetado."
          if pending else
          "Manter o original e este relatorio para rastreabilidade.")
    field("Escopo do publicador",
          "Validacao de estrutura, nomes, contagens e gravacao; a fidelidade "
          "semantica depende da revisao do documento.")
    return "\n".join(lines) + "\n"


def publish(original: Path, markdown_path: Path, report_path: Path, destination: Path,
            uf: str | None = None, reference_date: str | None = None,
            timezone: str = "America/Sao_Paulo",
            original_name: str | None = None) -> tuple[Path, Path]:
    original = Path(original).resolve()
    markdown_path, report_path = Path(markdown_path).resolve(), Path(report_path).resolve()
    destination = Path(destination).resolve()
    for label, path in (("original", original), ("markdown", markdown_path), ("relatorio", report_path)):
        if not path.is_file():
            raise ValueError(f"{label}: arquivo inexistente ou inacessivel: {path}")
    if original.stat().st_size == 0:
        raise ValueError("Arquivo original vazio: aplicar condicao de parada.")
    if destination.exists():
        raise ValueError("A pasta de destino ja existe; usar uma pasta exclusiva nova.")

    name = original_basename(original_name or original.name)
    suffix = Path(name).suffix.lower()
    if suffix not in (".docx", ".pdf", ".txt"):
        raise ValueError("A origem deve ser DOCX, PDF ou TXT.")
    markdown = markdown_path.read_text(encoding="utf-8-sig")
    # read_text normaliza quebras universais; garantir somente a quebra final.
    if markdown.strip() and not markdown.endswith("\n"):
        markdown += "\n"
    if not markdown.strip():
        markdown = ""
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    validate_report(report, suffix, markdown)
    stamp = resolve_date(reference_date, timezone)
    md_name, txt_name = output_names(name, uf, stamp)
    md_data = markdown.encode("utf-8")
    txt_data = render_readme(
        report, name, md_name, txt_name, stamp, file_hash(original),
        hashlib.sha256(md_data).hexdigest(), markdown
    ).encode("utf-8")

    destination.mkdir(parents=True, exist_ok=False)
    md_path, txt_path = destination / md_name, destination / txt_name
    created: list[Path] = []
    try:
        for path, data in ((md_path, md_data), (txt_path, txt_data)):
            with path.open("xb") as handle:
                created.append(path)
                handle.write(data)
        if md_path.read_bytes() != md_data or txt_path.read_bytes() != txt_data:
            raise OSError("Falha ao verificar os arquivos apos gravacao.")
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        try:
            destination.rmdir()
        except OSError:
            pass
        raise
    return md_path, txt_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--relatorio", type=Path, required=True,
                        help="JSON interno validado; nao sera publicado.")
    parser.add_argument("--destino", type=Path, required=True,
                        help="Pasta nova e exclusiva; nao pode existir.")
    parser.add_argument("--uf", default=None)
    parser.add_argument("--data", dest="reference_date", default=None)
    parser.add_argument("--fuso", default="America/Sao_Paulo")
    parser.add_argument("--nome-original", default=None)
    args = parser.parse_args()
    try:
        files = publish(args.original, args.markdown, args.relatorio, args.destino,
                        args.uf, args.reference_date, args.fuso, args.nome_original)
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
