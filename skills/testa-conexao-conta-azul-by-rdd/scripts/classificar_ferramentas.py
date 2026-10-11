#!/usr/bin/env python3
"""Classifica ferramentas MCP em leitura, escrita ou indeterminada. Determinístico, só biblioteca padrão.

Entrada (stdin): JSON com uma lista de {"nome": "...", "descricao": "..."}.
Saída (stdout): JSON com uma lista de {"nome", "classe", "motivo"}, na mesma ordem.

As listas e a ordem das regras são as de references/CLASSIFICACAO_FERRAMENTAS.md
(o teste de paridade em tests/ compara as duas fontes).

Regras, nesta ordem:
  1. Um token do nome ou da descrição casa um termo de escrita            -> escrita
  2. Um token do nome ou da descrição começa por "baix" (baixa = quitação) -> indeterminada
  3. Um token do NOME casa um termo de leitura                            -> leitura
  4. Qualquer outro caso                                                  -> indeterminada

Casamento POR TOKEN, nunca por pedaço de palavra: "ver" não casa "reverter".
Radical casa o início do token ("atualiz" casa "atualiza", "atualizacao"); exato casa só o token inteiro.
Particípio adjetivo ("notas emitidas") não conta como verbo de escrita, exceto: no 1º token do nome; depois de
auxiliar ("é criado", "is created" — voz passiva); ou se o texto fala em criar sob condição ("se não existir",
"automaticamente", "if missing").
"a pagar" e "a receber" são nome de conta ("contas a pagar"), não verbo.
"""
import json
import re
import sys
import unicodedata

RADICAIS_ESCRITA = (
    "cria", "crie", "cadastr", "inclu", "edit", "atualiz", "alter", "exclu", "delet", "remov",
    "cancel", "emit", "emiss", "quit", "revert", "revers", "convert", "convers", "envi", "adicion",
    "estorn", "aprov", "confirm", "transmit", "salv", "grav", "import", "duplic", "reabr", "fech",
    "marc", "sincron", "autoriz", "anex", "revog", "anul", "bloque", "liber", "reembols", "transfer",
    "mescl", "restaur",
    "creat", "updat", "insert", "upsert", "modif", "writ", "submit", "approv", "generat", "upload", "sync",
    "register", "authoriz", "attach", "archiv", "revok", "reconcil", "activat", "deactivat", "refund",
    "merg", "restor",
)
EXATOS_ESCRITA = (
    "gera", "gerar", "gere", "gerou", "geram", "geracao",
    "pagar", "paga", "pague", "pagou",
    "registrar", "registra", "registre", "registrou",
    "lancar", "lanca", "lance", "lancou",
    "faturar", "fatura", "fature", "faturou",
    "arquivar", "arquiva", "arquive", "arquivou",
    "liquidar", "liquide", "liquidou",
    "conciliar", "concilia", "concilie", "conciliou",
    "ativar", "ative", "ativou", "inativar", "inative", "desativar", "desative",
    "add", "adds", "set", "sets", "put", "puts", "post", "posts", "patch", "patches", "send", "sends",
    "pay", "pays", "issue", "issues", "mark", "marks", "void", "voids", "block", "blocks", "release", "releases",
)
RADICAIS_LEITURA = ("list", "busc", "consult", "obte", "obti", "detalh", "pesquis", "mostr", "exib", "search", "fetch", "read")
EXATOS_LEITURA = ("get", "find", "ver", "show", "view")
RADICAL_INDETERMINADO = "baix"
SUFIXOS_PARTICIPIO = ("ado", "ada", "ados", "adas", "ido", "ida", "idos", "idas")
NOME_DE_CONTA = ("pagar", "receber")
# Particípio depois de auxiliar é voz passiva ("um novo cliente é criado"): verbo, não adjetivo.
AUXILIARES = ("e", "sera", "serao", "sao", "foi", "foram", "fica", "ficam", "sendo", "ser", "seja", "sejam",
              "is", "are", "was", "were", "be", "been", "being", "gets")
# Descrição que fala em criar sob condição ("se não existir", "automaticamente", "if missing"):
# nenhum particípio dela é isento.
MARCADORES_CONDICIONAIS = ("automaticamente", "automatically", "missing", "absent")


def tokens(texto):
    s = unicodedata.normalize("NFKD", (texto or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", s)


def _escrita(tok):
    return tok in EXATOS_ESCRITA or any(tok.startswith(r) for r in RADICAIS_ESCRITA)


def _leitura(tok):
    return tok in EXATOS_LEITURA or any(tok.startswith(r) for r in RADICAIS_LEITURA)


def _condicional(toks):
    if any(t in MARCADORES_CONDICIONAIS for t in toks):
        return True
    return any(a in ("nao", "not") and b.startswith("exist") for a, b in zip(toks, toks[1:]))


def _conta_como_verbo(toks, i, primeiro_do_nome):
    tok = toks[i]
    if (not primeiro_do_nome and tok.endswith(SUFIXOS_PARTICIPIO)
            and not (i > 0 and toks[i - 1] in AUXILIARES) and not _condicional(toks)):
        return False
    if tok in NOME_DE_CONTA and i > 0 and toks[i - 1] == "a":
        return False
    return True


def classificar(nome, descricao=""):
    tn, td = tokens(nome), tokens(descricao)
    for toks, eh_nome in ((tn, True), (td, False)):
        for i, tok in enumerate(toks):
            if _escrita(tok) and _conta_como_verbo(toks, i, eh_nome and i == 0):
                return "escrita", f"termo de escrita: {tok}"
    for tok in tn + td:
        if tok.startswith(RADICAL_INDETERMINADO):
            return "indeterminada", f"'{tok}': baixa na Conta Azul é quitação"
    for tok in tn:
        if _leitura(tok):
            return "leitura", f"termo de leitura no nome: {tok}"
    return "indeterminada", "nenhum termo conhecido"


def main():
    try:
        itens = json.load(sys.stdin)
        if not isinstance(itens, list) or not all(
                isinstance(i, dict) and isinstance(i.get("nome"), str)
                and (i.get("descricao") is None or isinstance(i.get("descricao"), str)) for i in itens):
            raise ValueError("esperada uma lista de objetos com 'nome' (texto) e 'descricao' (texto, opcional)")
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"erro": f"entrada inválida: {e}"}, ensure_ascii=False))
        return 2
    saida = []
    for i in itens:
        classe, motivo = classificar(i["nome"], i.get("descricao") or "")
        saida.append({"nome": i["nome"], "classe": classe, "motivo": motivo})
    print(json.dumps(saida, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
