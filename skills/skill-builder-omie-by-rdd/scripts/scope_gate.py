#!/usr/bin/env python3
"""Read-only scope/approval consistency gate. Python 3.10+, standard library.

The host must supply authentic user-message evidence. This program cannot
authenticate a person or stop an LLM from bypassing the protocol.
Numeric limits below are engineering limits, not professional-domain constants.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_JSON_BYTES = 4 * 1024 * 1024  # Local defensive cap for extended metadata.
MAX_RDD_BYTES = 4000  # RDD documentation §4.4, seven-field scope projection.
MAX_ITEMS = 8         # RDD documentation §4.4.
MAX_ITEM_CHARS = 120  # RDD documentation §4.4.
NA = "nao disponivel"
SCOPE_KEYS = {
    "id", "revisao", "nome", "area", "tema", "objetivo", "publico", "jurisdicao",
    "cobre", "recusa", "periodo_consulta", "periodo_calculo", "entradas", "saidas",
    "perfil_pedido", "processo_normativo", "perfil_efetivo", "politica_internet",
    "ferramentas", "revisao_humana", "criterios_aceite", "materiais", "lacunas",
    "restricoes", "caminhos_calculo",
}
MATERIAL_KEYS = {
    "id", "slot", "path", "sha256", "status", "titulo", "fonte", "localizador",
    "periodo", "papel", "conferido_por", "fonte_do_gabarito",
}
APPROVAL_KEYS = {
    "origem", "escopo_id", "revisao", "sha256_escopo", "texto",
    "apos_apresentacao", "mensagem_id",
}

class GateError(ValueError):
    """Safe, non-sensitive error code."""

def require(condition: bool, code: str) -> None:
    if not condition:
        raise GateError(code)

def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "JSON_CHAVE_DUPLICADA")
        result[key] = value
    return result

def reject_constant(_: str) -> None:
    raise GateError("JSON_CONSTANTE_INVALIDA")

def read_json(path: Path) -> dict:
    require(path.stat().st_size <= MAX_JSON_BYTES, "JSON_MUITO_GRANDE")
    result = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=no_duplicates,
        parse_constant=reject_constant,
    )
    require(isinstance(result, dict), "JSON_DEVE_SER_OBJETO")
    return result

def digest(scope: dict) -> str:
    raw = json.dumps(
        scope, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def filled(value: object) -> bool:
    return text(value) and value.strip().casefold() != NA

def safe_material(root: Path, rel: str) -> Path:
    require(text(rel), "CAMINHO_VAZIO")
    require("\x00" not in rel and "\\" not in rel and ":" not in rel,
            "CAMINHO_INSEGURO")
    parts = rel.split("/")
    require(not rel.startswith("/") and all(p not in ("", ".", "..") for p in parts),
            "CAMINHO_INSEGURO")
    base = root.resolve(strict=True)
    target = base.joinpath(*parts)
    walk = base
    for part in parts:
        walk = walk / part
        require(not walk.is_symlink(), "LINK_SIMBOLICO_RECUSADO")
    resolved = target.resolve(strict=True)
    require(resolved.is_relative_to(base) and resolved.is_file(), "CAMINHO_INSEGURO")
    return resolved

def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            h.update(block)
    return h.hexdigest()

def derive_profile(scope: dict) -> str:
    usable = [m for m in scope["materiais"] if m["status"] == "utilizavel"]
    base = any(m["slot"] == "base" for m in usable)
    normative = scope["processo_normativo"] and any(
        m["slot"] in {"norma", "tabela", "regra"} for m in usable
    )
    request = scope["perfil_pedido"]
    if request == "operacional":
        return "C"
    if request == "consulta":
        return "B" if base else "C"
    if request == "calcula":
        return "A" if normative else "C"
    if request == "ambas":
        return "AB" if base and normative else ("A" if normative else ("B" if base else "C"))
    raise GateError("PERFIL_PEDIDO_INVALIDO")

def validate_scope(scope: dict, material_root: Path | None = None) -> None:
    require(isinstance(scope, dict) and set(scope) == SCOPE_KEYS, "CAMPOS_ESCOPO_INVALIDOS")
    require(text(scope["id"]) and bool(re.fullmatch(r"[A-Za-z0-9_-]{1,40}", scope["id"])),
            "ID_INVALIDO")
    require(type(scope["revisao"]) is int and scope["revisao"] >= 1, "REVISAO_INVALIDA")
    require(text(scope["nome"]) and len(scope["nome"]) <= 64
            and bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", scope["nome"]))
            and not ({"claude", "anthropic"} & set(scope["nome"].split("-"))),
            "NOME_INVALIDO")
    require(scope["area"] in {"contabil", "tributario", "trabalhista", "juridico"},
            "AREA_INVALIDA")
    for key in ("tema", "objetivo", "publico", "jurisdicao", "revisao_humana"):
        require(filled(scope[key]), "DEFINICAO_ESSENCIAL_AUSENTE")
    for key in ("periodo_consulta", "periodo_calculo"):
        require(text(scope[key]), "PERIODO_AUSENTE")
    for key in ("cobre", "recusa", "entradas", "saidas", "ferramentas",
                "criterios_aceite", "lacunas", "restricoes", "caminhos_calculo"):
        require(isinstance(scope[key], list) and all(filled(v) for v in scope[key]),
                "LISTA_INVALIDA")
        require(len(scope[key]) == len(set(scope[key])), "ITEM_DUPLICADO")
    for key in ("cobre", "recusa", "entradas", "saidas", "criterios_aceite"):
        require(bool(scope[key]), "LISTA_ESSENCIAL_VAZIA")
    for key in ("cobre", "recusa"):
        require(len(scope[key]) <= MAX_ITEMS
                and all(len(v) <= MAX_ITEM_CHARS for v in scope[key]),
                "FRONTEIRA_FORA_LIMITE")
    require(type(scope["processo_normativo"]) is bool, "PROCESSO_NORMATIVO_INVALIDO")
    require(scope["perfil_pedido"] in {"operacional", "consulta", "calcula", "ambas"},
            "PERFIL_PEDIDO_INVALIDO")
    require(scope["perfil_efetivo"] in {"A", "B", "AB", "C"}, "PERFIL_EFETIVO_INVALIDO")
    require(scope["politica_internet"] in {
        "sem_pesquisa", "somente_com_autorizacao", "fontes_oficiais_autorizadas"
    }, "POLITICA_INTERNET_INVALIDA")
    require(isinstance(scope["materiais"], list), "MATERIAIS_INVALIDOS")
    ids, paths = set(), set()
    for material in scope["materiais"]:
        require(isinstance(material, dict) and set(material) == MATERIAL_KEYS,
                "CAMPOS_MATERIAL_INVALIDOS")
        require(all(text(v) for v in material.values()), "CAMPO_MATERIAL_VAZIO")
        require(material["id"] not in ids, "MATERIAL_ID_DUPLICADO")
        ids.add(material["id"])
        require(material["slot"] in {"norma", "tabela", "caso", "regra", "base"},
                "SLOT_INVALIDO")
        require(material["status"] in {"utilizavel", "pendente"}, "STATUS_MATERIAL_INVALIDO")
        if material["path"] == NA:
            require(material["status"] == "pendente" and material["sha256"] == NA,
                    "MATERIAL_AUSENTE_NAO_PODE_SER_UTILIZAVEL")
            continue
        require(material_root is not None, "RAIZ_MATERIAIS_NECESSARIA")
        require(material["path"].casefold() not in paths, "CAMINHO_MATERIAL_DUPLICADO")
        paths.add(material["path"].casefold())
        require(bool(re.fullmatch(r"[0-9a-f]{64}", material["sha256"])), "HASH_INVALIDO")
        actual = safe_material(material_root, material["path"])
        require(actual.stat().st_size > 0, "MATERIAL_VAZIO")
        require(file_hash(actual) == material["sha256"], "MATERIAL_ALTERADO")
        if material["status"] == "utilizavel" and material["slot"] == "base":
            require(actual.suffix.lower() == ".md", "BASE_EXIGE_MARKDOWN")
            actual.read_text(encoding="utf-8")  # Require readable UTF-8 text.
    effective = derive_profile(scope)
    require(scope["perfil_efetivo"] == effective, "PERFIL_DIVERGENTE")
    if effective in {"A", "AB"}:
        require(filled(scope["periodo_calculo"])
                and scope["periodo_calculo"] != "nao aplicavel",
                "PERIODO_CALCULO_NECESSARIO")
        require(bool(scope["caminhos_calculo"]), "CAMINHOS_CALCULO_NECESSARIOS")
    else:
        require(not scope["caminhos_calculo"]
                and scope["periodo_calculo"] == "nao aplicavel",
                "CALCULO_FORA_DO_PERFIL")
    if effective in {"B", "AB"}:
        require(filled(scope["periodo_consulta"])
                and scope["periodo_consulta"] != "nao aplicavel",
                "PERIODO_CONSULTA_NECESSARIO")
    projection = {k: scope[k] for k in (
        "area", "tema", "cobre", "recusa", "periodo_consulta", "periodo_calculo", "publico"
    )}
    require(len(json.dumps(projection, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
            <= MAX_RDD_BYTES, "ESCOPO_RDD_MUITO_GRANDE")

def confirmation_text(scope: dict) -> str:
    return f"CONFIRMO O ESCOPO {scope['id']} V{scope['revisao']} E AUTORIZO GERAR A SKILL."

def challenge(scope: dict, material_root: Path | None = None) -> dict:
    validate_scope(scope, material_root)
    return {
        "status": "AGUARDANDO_CONFIRMACAO", "geracao_autorizada": False,
        "escopo_id": scope["id"], "revisao": scope["revisao"],
        "sha256_escopo": digest(scope), "frase_confirmacao": confirmation_text(scope),
        "perfil_efetivo": scope["perfil_efetivo"],
        "aviso": "Apresentar o resumo integral e aguardar uma nova mensagem do usuario.",
    }

def check_approval(scope: dict, approval: dict, material_root: Path | None = None) -> dict:
    validate_scope(scope, material_root)
    require(isinstance(approval, dict) and set(approval) == APPROVAL_KEYS,
            "CAMPOS_CONFIRMACAO_INVALIDOS")
    require(approval["origem"] == "usuario", "ORIGEM_NAO_USUARIO")
    require(approval["apos_apresentacao"] is True, "CONFIRMACAO_ANTERIOR_AO_RESUMO")
    require(filled(approval["mensagem_id"]), "EVIDENCIA_MENSAGEM_AUSENTE")
    require(approval["escopo_id"] == scope["id"]
            and type(approval["revisao"]) is int
            and approval["revisao"] == scope["revisao"], "VERSAO_NAO_CONFIRMADA")
    require(approval["sha256_escopo"] == digest(scope), "ESCOPO_ALTERADO")
    require(isinstance(approval["texto"], str)
            and approval["texto"].strip() == confirmation_text(scope),
            "TEXTO_CONFIRMACAO_INVALIDO")
    return {
        "status": "ESCOPO_CONFIRMADO", "geracao_autorizada": True,
        "sha256_escopo": digest(scope), "perfil_efetivo": scope["perfil_efetivo"],
        "limite": "Consistencia do registro; autoria e captura da mensagem dependem do host.",
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "check"])
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--material-root", type=Path)
    args = parser.parse_args(argv)
    try:
        scope = read_json(args.scope)
        if args.action == "prepare":
            result = challenge(scope, args.material_root)
        else:
            require(args.approval is not None, "CONFIRMACAO_AUSENTE")
            result = check_approval(scope, read_json(args.approval), args.material_root)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (GateError, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        error = str(exc) if isinstance(exc, GateError) else "ENTRADA_INVALIDA_OU_INACESSIVEL"
        print(json.dumps({
            "status": "BLOQUEADO", "geracao_autorizada": False, "erro": error,
        }, ensure_ascii=False, sort_keys=True))
        return 2

if __name__ == "__main__":
    sys.exit(main())
