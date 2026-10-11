#!/usr/bin/env python3
"""Herança vigiada entre skills do catálogo (HERANCA.json).

Cada zip precisa ser autossuficiente, então uma skill-filha leva cópias dos
arquivos que herda. Este verificador impede que a cópia derive em silêncio:

  copia     o arquivo da filha e o da origem têm o mesmo sha256 declarado;
            a origem_versao bate com manifest.json da skill de origem.
  derivado  o arquivo foi adaptado de uma origem; com "externa": true a origem
            está fora deste repositório e só é conferida por quem a tem (o
            gate local da plataforma). Aqui: o sha256 do próprio arquivo bate
            com o declarado (editar sem atualizar a herança reprova) e a
            âncora de "diferencas" existe.

E reprova cópia não declarada: arquivo da filha byte-idêntico a um arquivo das
skills que ela declara como origem, sem entrada no HERANCA.json.

Hashes no HERANCA.json: sha256 em 8 grupos de 8 hex separados por hifen.

Uso: python3 scripts/heranca-check.py [--repo DIR]
Saída: 0 ok · 2 divergência · 64 HERANCA.json inválido.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

LIXO = {"__pycache__", ".DS_Store"}
CAMPOS_COPIA = {"arquivo", "modo", "origem", "origem_versao", "sha256"}
CAMPOS_DERIVADO = {"arquivo", "modo", "externa", "origem", "sha256_origem", "sha256", "diferencas"}


class Invalido(ValueError):
    pass


def sem_duplicata(pares):
    saida = {}
    for chave, valor in pares:
        if chave in saida:
            raise Invalido(f"chave duplicada: {chave}")
        saida[chave] = valor
    return saida


def recusar_constante(nome):
    raise Invalido(f"constante não finita: {nome}")


def ler_json(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"),
                      object_pairs_hook=sem_duplicata, parse_constant=recusar_constante)


def sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def sha_declarado(valor: str) -> str:
    """sha256 em grupos de 8 separados por hifen: hex corrido pode ter 11 digitos
    seguidos e reprovar o padrao de CPF do publish-check.sh por acaso."""
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9a-f]{8}(-[0-9a-f]{8}){7}", valor):
        raise Invalido(f"sha256 fora do formato xxxxxxxx-…-xxxxxxxx: {valor!r}")
    return valor.replace("-", "")


def arquivos(raiz: Path):
    for caminho in sorted(raiz.rglob("*")):
        rel = caminho.relative_to(raiz)
        if caminho.is_file() and not (set(rel.parts) & LIXO) and caminho.suffix != ".pyc":
            yield caminho


def raiz_da_skill(repo: Path, origem: str) -> Path:
    partes = Path(origem).parts
    if len(partes) < 3 or partes[0] != "skills" or ".." in partes:
        raise Invalido(f"origem fora de skills/<nome>/: {origem}")
    return repo / partes[0] / partes[1]


def versao_manifest(raiz_skill: Path) -> str:
    try:
        return str(ler_json(raiz_skill / "manifest.json").get("version", ""))
    except (OSError, ValueError):
        return ""


def ancora_existe(filha: Path, diferencas: str) -> bool:
    arquivo, _, ancora = diferencas.partition("#")
    alvo = filha / arquivo
    if not alvo.is_file():
        return False
    if not ancora:
        return True
    texto = alvo.read_text(encoding="utf-8")
    return f'id="{ancora}"' in texto or f"<a id=\"{ancora}\">" in texto or f"{{#{ancora}}}" in texto


def validar_itens(dados: dict) -> list[dict]:
    if set(dados) != {"schema", "itens"} or dados["schema"] != 1 or not isinstance(dados["itens"], list):
        raise Invalido("HERANCA.json fora do schema 1")
    vistos = set()
    for item in dados["itens"]:
        if not isinstance(item, dict) or item.get("modo") not in {"copia", "derivado"}:
            raise Invalido("item sem modo válido")
        esperado = CAMPOS_COPIA if item["modo"] == "copia" else CAMPOS_DERIVADO
        if set(item) != esperado:
            raise Invalido(f"campos inválidos em {item.get('arquivo')}")
        if item["arquivo"] in vistos or ".." in Path(item["arquivo"]).parts:
            raise Invalido(f"arquivo repetido ou inseguro: {item['arquivo']}")
        vistos.add(item["arquivo"])
    return dados["itens"]


def checar(repo: Path) -> list[str]:
    erros = []
    for heranca in sorted((repo / "skills").glob("*/HERANCA.json")):
        filha = heranca.parent
        if not (filha / "SKILL.md").is_file():
            continue
        itens = validar_itens(ler_json(heranca))
        origens = {raiz_da_skill(repo, it["origem"]) for it in itens if it["modo"] == "copia"}
        shas_origem = {sha(f) for o in origens if o.is_dir() for f in arquivos(o)}
        declarados = set()
        for it in itens:
            alvo = filha / it["arquivo"]
            declarados.add(it["arquivo"])
            if not alvo.is_file():
                erros.append(f"{filha.name}:{it['arquivo']}:ausente")
                continue
            if it["modo"] == "copia":
                origem = repo / it["origem"]
                if sha(alvo) != sha_declarado(it["sha256"]):
                    erros.append(f"{filha.name}:{it['arquivo']}:copia_alterada")
                if not origem.is_file() or sha(origem) != sha_declarado(it["sha256"]):
                    erros.append(f"{filha.name}:{it['arquivo']}:origem_mudou")
                if it["origem_versao"] != versao_manifest(raiz_da_skill(repo, it["origem"])):
                    erros.append(f"{filha.name}:{it['arquivo']}:versao_desatualizada")
            else:
                sha_declarado(it["sha256_origem"])
                if sha(alvo) != sha_declarado(it["sha256"]):
                    erros.append(f"{filha.name}:{it['arquivo']}:derivado_alterado")
                if not ancora_existe(filha, it["diferencas"]):
                    erros.append(f"{filha.name}:{it['arquivo']}:diferencas_sem_ancora")
        for caminho in arquivos(filha):
            rel = caminho.relative_to(filha).as_posix()
            if rel not in declarados and rel != "HERANCA.json" and sha(caminho) in shas_origem:
                erros.append(f"{filha.name}:{rel}:copia_nao_declarada")
    return erros


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        erros = checar(args.repo.resolve())
    except (Invalido, ValueError, KeyError, TypeError) as exc:
        print(f"HERANCA INVALIDA: {exc}")
        return 64
    for erro in erros:
        print(f"FAIL {erro}")
    if erros:
        print(f"Herança vigiada: {len(erros)} divergência(s). Recopie da origem e atualize sha256/origem_versao.")
        return 2
    total = len(list((args.repo / "skills").glob("*/HERANCA.json")))
    print(f"PASS: herança vigiada em {total} skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
