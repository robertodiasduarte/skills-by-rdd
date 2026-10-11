#!/usr/bin/env python3
"""Lint de dominio Omie sobre uma skill gerada (roda DEPOIS do lint_bundle.py).

Le o bundle, nao executa nada dele. Python 3.10+, biblioteca padrao.

Classifica cada operacao com a MESMA barreira dupla do omie_num.py: leitura so se
constar como leitura do servico em catalogo_leitura.json E passar na regra de nome
(importada do proprio omie_num.py). Todo o resto e escrita; deprecated e servico fora
do catalogo sao recusados.

Uso:
  lint_bundle_omie.py --root PACOTE [--perfil operador|conferidor]
                      [--perfil-arquivo perfil_omie.json --escopo escopo.json]
  lint_bundle_omie.py --restricao perfil_omie.json   # imprime a linha para escopo.restricoes

Saida JSON no stdout; exit 0 aprovado · 2 reprovado · 64 uso incorreto.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets" / "omie"

_spec = importlib.util.spec_from_file_location("omie_num", ASSETS / "omie_num.py")
omie_num = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(omie_num)

RECUSA_OPERADOR = "Este perfil não totaliza registros. Para somar com conferência, gere o perfil Conferidor."
PROIBE_SOMA = "Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`."
LINHA_CONFERENCIA = ("registros lidos de", "informados pela Omie")
MESMA_EMPRESA = "a empresa das chaves do `.env` precisa ser a mesma escolhida no conector"
PASSOS_GATE = ("validar", "mostrar", "frase literal", "um por vez", "conferir o status", "não repetir")
PREREQ_APROVACAO = "pedir aprovação"
CONFIRMADO = '"confirmado": true'
CAMPOS_PERFIL = {"schema", "totaliza", "executa_python_com_rede", "perfil", "multi_empresa",
                 "aprovacao_por_ferramenta", "mcp_disponivel"}
APROVACAO = {"declarada_sim", "declarada_nao", "nao_perguntado"}
OPERACAO_RE = re.compile(r"\b([a-z]+/[a-z0-9-]+):([A-Z][A-Za-z0-9]+)\b")
# Verbo de escrita em CamelCase citado solto, mesmo fora do catálogo (achado R1 do 2º revisor, rodada 7).
VERBO_ESCRITA_RE = re.compile(r"\b(?:Incluir|Alterar|Excluir|Lancar|Cancelar|Concluir|Baixar|Faturar|Inutilizar|Upsert|"
                              r"Associar|Trocar|Devolver|Gerar|Ativar|Suspender|Conciliar|Duplicar|Adicionar|Reabrir|Estornar)"
                              r"[A-Z][A-Za-z0-9]*\b")
OP_JSON_RE = re.compile(r"[\"']op[\"']\s*:\s*[\"']([A-Za-z][A-Za-z0-9]*)[\"']")
FISCAL_RE = re.compile(r"(Faturar|Inutilizar)")
RADICAL_FISCAL_RE = re.compile(r"fatur|inutiliz", re.I)
NAO_USAR_RE = re.compile(r"^\s*n[ãa]o usar", re.I)
TITULO_QUANDO_USAR = "## Quando usar / Quando não usar"
# Os mesmos binários que o lint_bundle.py herdado aceita (só dentro de assets/); todo o resto tem de ser UTF-8.
BINARIOS_PERMITIDOS = {".pdf", ".xlsx", ".docx", ".pptx", ".png", ".jpg", ".jpeg"}


class Uso(ValueError):
    pass


def sem_duplicata(pares):
    out = {}
    for k, v in pares:
        if k in out:
            raise ValueError(f"chave duplicada: {k}")
        out[k] = v
    return out


def ler_json(caminho: Path):
    return json.loads(caminho.read_text(encoding="utf-8"), object_pairs_hook=sem_duplicata,
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))


def sha_canonico(dados: dict) -> str:
    raw = json.dumps(dados, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def restricao(perfil: dict) -> str:
    # Hash em 8 grupos de 8: hex corrido pode ter 11 digitos seguidos e casar com o padrao de CPF
    # de varredores de conteudo (o publish-check.sh do catalogo reprovou por isso).
    h = sha_canonico(perfil)
    return f"perfil_omie:{perfil.get('perfil')} sha256:{'-'.join(h[i:i + 8] for i in range(0, 64, 8))}"


def perfil_derivado(p: dict) -> str:
    if p.get("mcp_disponivel") is True and p.get("totaliza") is True and p.get("executa_python_com_rede") is True:
        return "conferidor"
    return "operador"


def checar_perfil(perfil: dict, escopo: dict) -> list[str]:
    erros = []
    tipos_ok = (set(perfil) == CAMPOS_PERFIL and perfil.get("schema") == 1
                and all(isinstance(perfil.get(k), bool) for k in
                        ("totaliza", "executa_python_com_rede", "multi_empresa", "mcp_disponivel"))
                and perfil.get("perfil") in {"operador", "conferidor"}
                and perfil.get("aprovacao_por_ferramenta") in APROVACAO)
    if not tipos_ok:
        return ["PERFIL_CAMPOS_INVALIDOS"]
    if perfil["perfil"] != perfil_derivado(perfil):
        erros.append("PERFIL_NAO_DERIVADO")
    if restricao(perfil) not in escopo.get("restricoes", []):
        erros.append("PERFIL_FORA_DO_ESCOPO")
    return erros


def metodos_do_catalogo(catalogo: dict) -> set[str]:
    return {m for e in catalogo.values() for m in [*e.get("leitura", []), *e.get("bloqueados", {})]}


def classificar(catalogo: dict, call: str, op: str) -> str:
    if call not in catalogo:
        return "fora_do_catalogo"
    entrada = catalogo[call]
    if entrada.get("bloqueados", {}).get(op) == "deprecated":
        return "deprecated"
    if op in entrada.get("leitura", []) and omie_num.name_rule_allows(op):
        return "leitura"
    return "escrita"


def gate_de_escrita_ok(texto: str) -> bool:
    bloco = re.search(r"^### Gate de escrita\s*$(.*?)(?=^#{2,3} |\Z)", texto, re.M | re.S)
    if not bloco:
        return False
    itens = re.findall(r"^\s*(\d+)\.\s+(.+)$", bloco.group(1), re.M)
    if [n for n, _ in itens[:6]] != [str(i) for i in range(1, 7)]:
        return False
    return all(chave in item.casefold() for chave, (_, item) in zip(PASSOS_GATE, itens[:6]))


# Cópias exatas dos assets: citam nomes de métodos em listas de política/catálogo, não instruem o modelo.
# Só saem da varredura se forem byte a byte iguais ao asset (divergente já reprova em OMIE_NUM_DIVERGENTE).
COPIAS_DOS_ASSETS = {"scripts/omie_num.py": "omie_num.py",
                     "scripts/catalogo_leitura.json": "catalogo_leitura.json",
                     "tests/test_omie_num.py": "test_omie_num.py"}


def textos(raiz: Path) -> tuple[str, list[str]]:
    """Texto de TODO arquivo do pacote: qualquer arquivo pode instruir o modelo (achado AT-004 do avaliador:
    escrita num assets/roteiro.md citado pelo SKILL.md passava). Fica de fora só o manifest.json (é a própria
    declaração) e as cópias exatas dos assets. Arquivo que não é UTF-8 válido sem byte nulo (UTF-16, latin-1…)
    não é pulado como binário: volta na 2ª lista, salvo binário permitido em assets/ (achado h7, ciclo 2)."""
    partes, nao_utf8 = [], []
    for p in sorted(raiz.rglob("*")):
        rel = p.relative_to(raiz)
        if not p.is_file() or {"__pycache__", ".git"} & set(rel.parts) or rel.as_posix() == "manifest.json":
            continue
        dados = p.read_bytes()
        asset = COPIAS_DOS_ASSETS.get(rel.as_posix())
        if asset and dados == (ASSETS / asset).read_bytes():
            continue
        try:
            texto = dados.decode("utf-8")
        except UnicodeDecodeError:
            texto = None
        if texto is not None and "\0" not in texto:
            partes.append(texto)
        elif not (rel.parts[0] == "assets" and p.suffix.lower() in BINARIOS_PERMITIDOS):
            nao_utf8.append(rel.as_posix())
    return "\n".join(partes), nao_utf8


def fronteira_fiscal(skill: str) -> list[str]:
    """Faturar/inutilizar só contam como fronteira DENTRO da lista que vem logo abaixo da 1ª linha iniciada por
    "Não usar" em "## Quando usar / Quando não usar" (itens "- " contíguos + continuações indentadas). Radical
    fiscal em qualquer outro ponto da seção — a própria linha "Não usar", "Usar para", parênteses, depois da
    lista — reprova: a regra posicional anterior foi derrotada duas vezes (achados c3/c4, ciclo 2)."""
    blocos = [m.group(1) for m in re.finditer(rf"^{re.escape(TITULO_QUANDO_USAR)}\s*$(.*?)(?=^## |\Z)",
                                              skill, re.M | re.S)]
    if not blocos:
        return ["FRONTEIRA_FISCAL_AUSENTE"]
    linhas = blocos[0].split("\n")
    lista: list[int] = []
    inicio = next((i for i, linha in enumerate(linhas) if NAO_USAR_RE.match(linha)), None)
    if inicio is not None:
        for i in range(inicio + 1, len(linhas)):
            linha = linhas[i]
            if linha.startswith("- ") or (lista and linha[:1] in {" ", "\t"} and linha.strip()):
                lista.append(i)
            else:
                break
    dentro = "\n".join(linhas[i] for i in lista).casefold()
    fora = "\n".join([*(linhas[i] for i in range(len(linhas)) if i not in lista), *blocos[1:]])
    erros = []
    if "fatur" not in dentro or "inutiliz" not in dentro:
        erros.append("FRONTEIRA_FISCAL_AUSENTE")
    if RADICAL_FISCAL_RE.search(fora):
        erros.append("FRONTEIRA_FISCAL_FORA_DA_LISTA")
    return erros


def versao_frontmatter(skill: str) -> str | None:
    m = re.match(r"\A---\n(.*?)\n---", skill, re.S)
    if not m:
        return None
    v = re.search(r"^  version:\s*['\"]?([^'\"\n]+)['\"]?\s*$", m.group(1), re.M)
    return v.group(1).strip() if v else None


def lint(raiz: Path, perfil: str | None, catalogo: dict) -> list[str]:
    erros = []
    skill_path, manifest_path = raiz / "SKILL.md", raiz / "manifest.json"
    if not skill_path.is_file() or not manifest_path.is_file():
        return ["SKILL_OU_MANIFEST_AUSENTE"]
    tudo, nao_utf8 = textos(raiz)
    if nao_utf8:
        erros.append("TEXTO_NAO_UTF8")
        if "SKILL.md" in nao_utf8:
            return erros
    skill = skill_path.read_text(encoding="utf-8")
    manifest = ler_json(manifest_path)

    if versao_frontmatter(skill) != manifest.get("version"):
        erros.append("VERSAO_AUSENTE_OU_DIVERGENTE")
    if "## Metodologia e autoria" not in skill or "Esta skill foi construída com a metodologia de Roberto Dias Duarte." not in skill:
        erros.append("ATRIBUICAO_AUSENTE")
    perfil_manifest = manifest.get("perfil_omie")
    if perfil_manifest not in {"operador", "conferidor"}:
        erros.append("PERFIL_MANIFEST_INVALIDO")
    elif perfil and perfil != perfil_manifest:
        erros.append("PERFIL_DIVERGENTE_DO_MANIFEST")
    perfil = perfil or perfil_manifest

    operacoes = manifest.get("operacoes")
    if not isinstance(operacoes, list) or not operacoes or not all(
            isinstance(o, dict) and set(o) == {"call", "op"} for o in operacoes):
        return sorted(set(erros + ["OPERACOES_NAO_DECLARADAS_NO_MANIFEST"]))
    declaradas = {(o["call"], o["op"]) for o in operacoes}
    if {(c, o) for c, o in OPERACAO_RE.findall(tudo)} - declaradas:
        erros.append("OPERACAO_NAO_DECLARADA")
    # Método citado só pelo nome (sem "serviço:"): qualquer nome de método do catálogo no texto precisa ser de
    # uma operação declarada — senão uma gravação escapa do gate de escrita (achado R3 da review pós-build).
    metodos_declarados = {o for _, o in declaradas}
    if any(re.search(rf"\b{re.escape(m)}\b", tudo) for m in metodos_do_catalogo(catalogo) - metodos_declarados):
        erros.append("OPERACAO_NAO_DECLARADA")
    # Forma JSON ("op": "Metodo"): vale para QUALQUER nome, inclusive fora do catálogo (achado R1 da rodada 2).
    if set(OP_JSON_RE.findall(tudo)) - metodos_declarados:
        erros.append("OPERACAO_NAO_DECLARADA")
    if set(VERBO_ESCRITA_RE.findall(tudo)) - metodos_declarados:
        erros.append("OPERACAO_NAO_DECLARADA")

    classes = {(c, o): classificar(catalogo, c, o) for c, o in declaradas}
    if "deprecated" in classes.values():
        erros.append("OPERACAO_DEPRECATED")
    if "fora_do_catalogo" in classes.values():
        erros.append("OPERACAO_FORA_DO_CATALOGO")
    if any(FISCAL_RE.search(o) for _, o in declaradas):
        erros.append("FATURAR_NO_ESCOPO")
    tem_escrita = "escrita" in classes.values()

    erros += fronteira_fiscal(skill)
    if tem_escrita:
        if not gate_de_escrita_ok(skill):
            erros.append("ESCRITA_SEM_GATE")
        if CONFIRMADO not in tudo:
            erros.append("ESCRITA_SEM_CONFIRMADO")
        if PREREQ_APROVACAO not in tudo.casefold() or "omie_executar" not in tudo:
            erros.append("PREREQ_APROVACAO_AUSENTE")
    elif CONFIRMADO in tudo:
        erros.append("CONFIRMADO_SEM_ESCRITA")

    scripts = sorted(p.relative_to(raiz).as_posix() for p in raiz.rglob("*.py")
                     if "__pycache__" not in p.parts)
    if perfil == "operador":
        if scripts:
            erros.append("PERFIL_OPERADOR_COM_SCRIPT")
        if RECUSA_OPERADOR not in skill:
            erros.append("RECUSA_TOTALIZACAO_AUSENTE")
        if "conector MCP Omie" not in manifest.get("requisitos", []):
            erros.append("REQUISITOS_INCOMPLETOS")
    elif perfil == "conferidor":
        if tem_escrita:
            erros.append("CONFERIDOR_COM_ESCRITA")
        for rel in ("scripts/omie_num.py", "scripts/catalogo_leitura.json", "tests/test_omie_num.py", "assets/env.exemplo.txt"):
            if not (raiz / rel).is_file():
                erros.append("CONFERIDOR_SEM_SCRIPT")
        if set(scripts) - {"scripts/omie_num.py", "tests/test_omie_num.py"}:
            erros.append("SCRIPT_FORA_DO_PERFIL")
        for rel, asset in (("scripts/omie_num.py", "omie_num.py"),
                           ("scripts/catalogo_leitura.json", "catalogo_leitura.json"),
                           ("tests/test_omie_num.py", "test_omie_num.py")):
            alvo = raiz / rel
            if alvo.is_file() and alvo.read_bytes() != (ASSETS / asset).read_bytes():
                erros.append("OMIE_NUM_DIVERGENTE")
        if PROIBE_SOMA not in skill:
            erros.append("SOMA_PELO_MODELO_NAO_PROIBIDA")
        if not all(p in skill for p in LINHA_CONFERENCIA):
            erros.append("CONFERENCIA_LITERAL_AUSENTE")
        if MESMA_EMPRESA not in skill or "omie_num.py\" empresa" not in skill:
            erros.append("CONFERIDOR_SEM_CONFERENCIA_DE_EMPRESA")
        if ("geral/empresas", "ListarEmpresas") not in declaradas:
            # O `omie_num.py empresa` lê essa operação: o manifest declara tudo o que a skill executa.
            erros.append("CONFERIDOR_SEM_OPERACAO_DE_EMPRESA")
        reqs = manifest.get("requisitos", [])
        if "conector MCP Omie" not in reqs or not any("Python" in r for r in reqs):
            erros.append("REQUISITOS_INCOMPLETOS")

    pending = manifest.get("pending", [])
    exercida = (raiz / "evidencias" / "exercida.md").is_file()
    if not exercida and "nao_exercida_contra_omie" not in pending:
        erros.append("PENDING_NAO_EXERCIDA_AUSENTE")
    if exercida and "nao_exercida_contra_omie" in pending:
        erros.append("PENDING_CONTRADIZ_EVIDENCIA")
    return sorted(set(erros))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path)
    parser.add_argument("--perfil", choices=["operador", "conferidor"])
    parser.add_argument("--perfil-arquivo", type=Path)
    parser.add_argument("--escopo", type=Path)
    parser.add_argument("--restricao", type=Path)
    parser.add_argument("--catalogo", type=Path, default=ASSETS / "catalogo_leitura.json")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 64
    try:
        if args.restricao:
            print(restricao(ler_json(args.restricao)))
            return 0
        if not args.root and not args.perfil_arquivo:
            raise Uso("informe --root e/ou --perfil-arquivo com --escopo")
        erros = []
        perfil = args.perfil
        if args.perfil_arquivo:
            if not args.escopo:
                raise Uso("--perfil-arquivo exige --escopo")
            sidecar = ler_json(args.perfil_arquivo)
            erros += checar_perfil(sidecar, ler_json(args.escopo))
            # O perfil confirmado no escopo manda: o bundle entregue tem de ser desse perfil (achado R1 da review).
            if perfil and perfil != sidecar.get("perfil"):
                erros.append("PERFIL_DIVERGENTE_DO_ESCOPO")
            perfil = sidecar.get("perfil")
        if args.root:
            erros += lint(args.root, perfil, ler_json(args.catalogo)["servicos"])
    except Uso as exc:
        print(json.dumps({"erro_uso": str(exc)}, ensure_ascii=False))
        return 64
    except (OSError, ValueError, TypeError, KeyError) as exc:
        erros = [f"ENTRADA_INVALIDA:{type(exc).__name__}"]
    erros = sorted(set(erros))
    print(json.dumps({"pass": not erros, "errors": erros,
                      "scope": "dominio_omie; complementa lint_bundle.py, nao prova conduta do modelo"},
                     ensure_ascii=False, sort_keys=True))
    return 0 if not erros else 2


if __name__ == "__main__":
    sys.exit(main())
