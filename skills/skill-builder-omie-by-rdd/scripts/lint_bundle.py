#!/usr/bin/env python3
"""Read-only portable bundle lint, not the official RDD validator.

Supports a deliberately restricted YAML frontmatter: one-line scalar strings and
an optional one-level metadata mapping. Uses standard library only; no execution.
Limits: RDD documentation §§3, 4.4, 6 and 7; stricter body <500 from §3.1.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REQUIRED_HEADINGS = [
    "## Quick start", "## Quando usar / Quando não usar", "## Dados necessários",
    "## Procedimento passo a passo", "## Validações e checklist de qualidade",
    "## Tratamento de exceções", "## Examples",
]
MAX_FILES = 120
MAX_BYTES = 25 * 1024 * 1024
TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".py", ".sh", ".sql", ".html", ".toml", ".svg"}
ASSET_EXTENSIONS = {".pdf", ".xlsx", ".docx", ".pptx", ".png", ".jpg", ".jpeg"}
PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:scripts|references|assets|evals|tests|agents)/[A-Za-z0-9_./-]+")
SECRET_PATTERNS = [
    re.compile(r"sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=]{24,}"),
]

def scalar(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('"'):
        value = json.loads(raw)
        if not isinstance(value, str):
            raise ValueError("Escalar nao textual")
        return value
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    if not raw or raw in {"|", ">", "true", "false", "null", "~"} or raw[0] in "[{":
        raise ValueError("Fora do subconjunto YAML")
    return raw

def frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)(.*)\Z", text, re.S)
    if not match:
        raise ValueError("Frontmatter ausente")
    data, in_metadata = {}, False
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and in_metadata:
            key, sep, value = line.strip().partition(":")
            if not sep or key in data["metadata"]:
                raise ValueError("Metadata invalido")
            data["metadata"][key] = scalar(value)
            continue
        if line[0].isspace():
            raise ValueError("Indentacao fora do subconjunto")
        key, sep, value = line.partition(":")
        if not sep or key in data or key not in ALLOWED:
            raise ValueError("Chave invalida ou duplicada")
        in_metadata = key == "metadata"
        if in_metadata:
            if value.strip():
                raise ValueError("Metadata exige mapa em bloco")
            data[key] = {}
        else:
            data[key] = scalar(value)
    return data, match.group(2)

def lint(root: Path) -> dict:
    errors = []
    if not root.is_dir() or root.is_symlink():
        return {"pass": False, "errors": ["RAIZ_INVALIDA"], "files": 0}
    files, seen = [], set()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append("LINK_SIMBOLICO")
            continue
        if not path.is_file():
            continue
        files.append(path)
        low = rel.casefold()
        if low in seen:
            errors.append("PATH_DUPLICADO_CASE_INSENSITIVE")
        seen.add(low)
        if any(part in {"", ".", "..", ".git", "__pycache__", "__MACOSX"} for part in rel.split("/")) or "\\" in rel or ":" in rel:
            errors.append("PATH_INSEGURO_OU_LIXO")
        if path.name in {".DS_Store", "Thumbs.db"} or path.name.startswith("._"):
            errors.append("LIXO_DE_ARQUIVADOR")
        suffix = path.suffix.lower()
        is_asset = rel.startswith("assets/")
        if suffix not in TEXT_EXTENSIONS and not (is_asset and suffix in ASSET_EXTENSIONS):
            errors.append("EXTENSAO_NAO_PERMITIDA")
        if path.stat().st_size == 0:
            errors.append("ARQUIVO_VAZIO")
        if suffix in TEXT_EXTENSIONS:
            try:
                content = path.read_text(encoding="utf-8")
                if "\x00" in content:
                    errors.append("BYTE_NULO_EM_TEXTO")
                if any(pattern.search(content) for pattern in SECRET_PATTERNS):
                    errors.append("POSSIVEL_CREDENCIAL")
            except UnicodeError:
                errors.append("TEXTO_NAO_UTF8")
    if len(files) > MAX_FILES:
        errors.append("ARQUIVOS_EXCEDIDOS")
    if sum(p.stat().st_size for p in files) > MAX_BYTES:
        errors.append("TAMANHO_EXCEDIDO")
    skill = root / "SKILL.md"
    if not skill.is_file() or skill.is_symlink():
        errors.append("SKILL_AUSENTE")
    else:
        try:
            text = skill.read_text(encoding="utf-8")
            data, body = frontmatter(text)
            name, description = data.get("name"), data.get("description")
            if (not isinstance(name, str) or len(name) > 64
                or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
                or name != root.name
                or {"anthropic", "claude"} & set(name.split("-"))):
                errors.append("NOME_INVALIDO")
            if (not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024
                or "<" in description or ">" in description):
                errors.append("DESCRIPTION_INVALIDA")
            if "compatibility" in data and not 1 <= len(data["compatibility"]) <= 500:
                errors.append("COMPATIBILITY_INVALIDA")
            if len(body.splitlines()) >= 500:
                errors.append("CORPO_EXCEDE_LIMITE")
            lines = body.splitlines()
            title = next((line for line in lines if line.strip()), "")
            if not title.startswith("# ") or title.startswith("## "):
                errors.append("TITULO_AUSENTE")
            positions = []
            for heading in REQUIRED_HEADINGS:
                if lines.count(heading) != 1:
                    errors.append("SECAO_AUSENTE_OU_DUPLICADA")
                else:
                    positions.append(lines.index(heading))
            if positions != sorted(positions):
                errors.append("SECOES_FORA_DE_ORDEM")
            refs = set(PATH_RE.findall(body))
            for ref in refs:
                if ref.endswith("/"):
                    continue
                parts = ref.split("/")
                if any(p in {".", "..", ""} for p in parts):
                    errors.append("REFERENCIA_INSEGURA")
                elif not (root / ref).exists():
                    errors.append("REFERENCIA_INEXISTENTE")
            # Also handle Markdown links to root files and relative paths.
            for link in re.findall(r"\]\(([^)\s]+)\)", body):
                target = link.split("#", 1)[0]
                if not target or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                    continue
                if target.startswith("/") or ".." in target.split("/"):
                    errors.append("REFERENCIA_INSEGURA")
                elif not (root / target).exists():
                    errors.append("REFERENCIA_INEXISTENTE")
            for path in files:
                rel = path.relative_to(root).as_posix()
                if rel.startswith("scripts/") and rel not in refs:
                    errors.append("SCRIPT_NAO_CITADO")
        except (ValueError, TypeError, UnicodeError):
            errors.append("FRONTMATTER_FORA_DO_SUBCONJUNTO_OU_TEXTO_INVALIDO")
    return {
        "pass": not errors, "errors": sorted(set(errors)), "files": len(files),
        "scope": "estrutura_basica; nao substitui validacao RDD, normativa ou comportamental",
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = lint(args.root)
    except (OSError, ValueError, RecursionError):
        result = {"pass": False, "errors": ["ARQUIVOS_INACESSIVEIS"], "files": 0}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["pass"] else 2

if __name__ == "__main__":
    sys.exit(main())
