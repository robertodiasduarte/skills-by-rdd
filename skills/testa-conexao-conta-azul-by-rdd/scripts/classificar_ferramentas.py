#!/usr/bin/env python3
"""Classifica ferramentas MCP em leitura, escrita ou indeterminada. Determinístico, só biblioteca padrão.

Entrada (stdin): JSON com uma lista de {"nome": "...", "descricao": "..."}.
Saída (stdout): JSON com uma lista de {"nome", "classe", "motivo"}, na mesma ordem.

As listas e a ordem das regras são as de references/CLASSIFICACAO_FERRAMENTAS.md
(o teste de paridade em tests/ compara as duas fontes).

Regras, nesta ordem:
  1. Um token do nome ou da descrição casa um termo de escrita            -> escrita
  2. Um token do nome ou da descrição começa por "baix" (baixa = quitação) -> indeterminada
  3. O NOME tem conjunção depois da 1ª palavra (listar_e_…, get_or_…)    -> indeterminada
  4. Um token do NOME casa um termo de leitura                            -> leitura
  5. Qualquer outro caso                                                  -> indeterminada

Casamento POR TOKEN, nunca por pedaço de palavra: "ver" não casa "reverter".
Radical casa o início do token ("atualiz" casa "atualiza", "atualizacao"); exato casa só o token inteiro.
Nome e descrição são quebrados também em camelCase ("listOrCreateCustomer" = list, or, create, customer).
Particípio ("criado", "emitidas") conta como verbo de escrita. Só é isento (adjetivo) quando TUDO vale: vem colado
depois de um substantivo do domínio ("notas emitidas", "pagamentos realizados"); não é o 1º token do nome; nome e
descrição juntos não têm auxiliar ("é criado", "is created") nem palavra de condição ("se", "caso", "quando", "if");
não está a até 2 palavras de "ou"/"or" ("criado ou atualizado" — upsert);
ou se o texto fala em criar sob condição ("se não existir", "automaticamente", "if missing").
Nome composto com conjunção ("listar_e_apagar", "get_or_reset") nunca é leitura: sai indeterminada se nenhum
termo de escrita casou.
"a pagar" e "a receber" só são nome de conta logo depois de "contas", "títulos", "valores"…; "começa a pagar" é verbo.
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
    "mescl", "restaur", "apag", "destru", "limp", "substitu", "renov", "encerr", "finaliz", "conclu",
    "dispar", "vincul", "desvincul", "habilit", "desabilit", "ajust", "corrig", "execut",
    "creat", "updat", "insert", "upsert", "modif", "writ", "submit", "approv", "generat", "upload", "sync",
    "register", "authoriz", "attach", "archiv", "revok", "reconcil", "activat", "deactivat", "refund",
    "merg", "restor", "destroy", "purg", "eras", "chang", "replac", "renam", "assign", "enabl", "disabl",
    "reopen", "schedul", "trigger", "execut", "publish", "renew", "rotat", "invalidat", "unlink", "disconnect",
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
    "ativar", "ativa", "ative", "ativou", "inativar", "inativa", "inative", "inativou",
    "desativar", "desativa", "desative", "desativou", "liquida",
    "zerar", "zera", "zere", "zerou", "trocar", "troca", "troque", "trocou",
    "agendar", "agenda", "agende", "agendou", "cobrar", "cobra", "cobre", "cobrou",
    "add", "adds", "set", "sets", "put", "puts", "post", "posts", "patch", "patches", "send", "sends",
    "pay", "pays", "issue", "issues", "mark", "marks", "void", "voids", "block", "blocks", "release", "releases",
    "drop", "drops", "clear", "clears", "reset", "resets", "move", "moves", "apply", "applies", "close", "closes",
    "run", "runs", "complete", "completes", "finalize", "finalizes", "charge", "charges",
)
RADICAIS_LEITURA = ("list", "busc", "consult", "obte", "obti", "detalh", "pesquis", "mostr", "exib", "search", "fetch")
# "read" é exato: como radical casava "readd" (re-add) e "readjust" (review rodada 4, auditor).
EXATOS_LEITURA = ("get", "find", "ver", "show", "view", "read", "reads")
RADICAL_INDETERMINADO = "baix"
SUFIXOS_PARTICIPIO = ("ado", "ada", "ados", "adas", "ido", "ida", "idos", "idas")
NOME_DE_CONTA = ("pagar", "receber")
# "a pagar" só é nome de conta depois de um destes substantivos ("contas a pagar"); "começa a pagar" é verbo.
ANTES_DE_NOME_DE_CONTA = ("conta", "contas", "titulo", "titulos", "valor", "valores", "lancamento", "lancamentos",
                          "parcela", "parcelas", "saldo", "saldos", "total", "totais")
# Texto com auxiliar em QUALQUER posição tem voz passiva ("um novo cliente é criado", "é, quando necessário,
# atualizado"): nenhum particípio dele é isento. Lidos com acento: "é" (verbo) não é "e" (conjunção).
AUXILIARES = ("é", "será", "serão", "sera", "serao", "são", "sao", "foi", "foram", "fica", "ficam", "sendo", "ser",
              "seja", "sejam", "is", "are", "was", "were", "be", "been", "being", "gets")
# Descrição que fala em criar sob condição ("se não existir", "automaticamente", "if missing"):
# nenhum particípio dela é isento.
MARCADORES_CONDICIONAIS = ("automaticamente", "automatically", "missing", "absent", "needed", "preciso")
# Radicais de condição: "caso inexistente", "se não existir", "doesn't exist", "quando necessário".
RADICAIS_CONDICIONAIS = ("exist", "inexist", "necessar")
# Palavra de condição em qualquer lugar do texto: nenhum particípio é isento ("criado quando não encontrado").
PALAVRAS_DE_CONDICAO = ("se", "caso", "quando", "senao", "contrario", "if", "when", "unless", "otherwise")
# Particípio só é adjetivo COLADO depois de um destes substantivos ("notas emitidas", "pagamentos realizados").
# Lista de permissão (review rodada 5): a isenção deixou de ser a regra e virou a exceção estreita.
SUBSTANTIVOS_DO_DOMINIO = (
    "nota", "notas", "titulo", "titulos", "conta", "contas", "venda", "vendas", "pedido", "pedidos",
    "cliente", "clientes", "fornecedor", "fornecedores", "lancamento", "lancamentos", "pagamento", "pagamentos",
    "recebimento", "recebimentos", "parcela", "parcelas", "boleto", "boletos", "cobranca", "cobrancas",
    "fatura", "faturas", "produto", "produtos", "servico", "servicos", "contrato", "contratos",
    "documento", "documentos", "registro", "registros", "orcamento", "orcamentos",
)
# Particípio a até 2 palavras de "ou"/"or" = alternativa de ação ("criado ou atualizado": upsert), não adjetivo.
CONJUNCOES_ALTERNATIVA = ("ou", "or")
# Nome composto com conjunção ("listar_e_apagar", "get_or_reset") junta duas ações: nunca é leitura, mesmo
# que o 2º verbo não esteja nas listas (fecha a classe "verbo de escrita fora da lista" no nome).
CONJUNCOES_NO_NOME = ("e", "ou", "and", "or")


def _separar_camel(texto):
    # listOrCreateCustomer -> list Or Create Customer; HTTPStatus -> HTTP Status (review rodada 4, codex).
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", texto or "")
    return re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)


def _tem_auxiliar(texto):
    # NFC antes de procurar: "é" decomposto (e + acento combinante) viraria "e" e passaria (review rodada 5, codex).
    s = unicodedata.normalize("NFC", _separar_camel(texto).lower())
    return any(t in AUXILIARES for t in re.findall(r"\w+", s))


def tokens(texto):
    s = unicodedata.normalize("NFKD", _separar_camel(texto).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", s)


def _escrita(tok):
    return tok in EXATOS_ESCRITA or any(tok.startswith(r) for r in RADICAIS_ESCRITA)


def _leitura(tok):
    return tok in EXATOS_LEITURA or any(tok.startswith(r) for r in RADICAIS_LEITURA)


def _condicional(toks):
    return any(t in MARCADORES_CONDICIONAIS or t in PALAVRAS_DE_CONDICAO or t.startswith(RADICAIS_CONDICIONAIS)
               for t in toks)


def _conta_como_verbo(toks, i, primeiro_do_nome, tem_auxiliar, condicional):
    tok = toks[i]
    vizinhos = toks[max(0, i - 2):i] + toks[i + 1:i + 3]
    # Auxiliar em qualquer posição do texto = voz passiva (review rodadas 2 e 4, codex): sem janela de distância.
    # Forma EXATA da lista é verbo por definição: nunca isentar como particípio ("liquida" termina em -ida;
    # review rodada 3, codex).
    if (not primeiro_do_nome and tok not in EXATOS_ESCRITA and tok.endswith(SUFIXOS_PARTICIPIO)
            and i > 0 and toks[i - 1] in SUBSTANTIVOS_DO_DOMINIO
            and not tem_auxiliar and not condicional
            and not any(v in CONJUNCOES_ALTERNATIVA for v in vizinhos)):
        return False
    if tok in NOME_DE_CONTA and i > 1 and toks[i - 1] == "a" and toks[i - 2] in ANTES_DE_NOME_DE_CONTA:
        return False
    return True


def classificar(nome, descricao=""):
    tn, td = tokens(nome), tokens(descricao)
    # Auxiliar e condição valem para nome e descrição JUNTOS (review rodada 5, A2: paridade com a prosa).
    aux = _tem_auxiliar(f"{nome} {descricao}")
    cond = _condicional(tn + td)
    for toks, eh_nome in ((tn, True), (td, False)):
        for i, tok in enumerate(toks):
            if _escrita(tok) and _conta_como_verbo(toks, i, eh_nome and i == 0, aux, cond):
                return "escrita", f"termo de escrita: {tok}"
    for tok in tn + td:
        if tok.startswith(RADICAL_INDETERMINADO):
            return "indeterminada", f"'{tok}': baixa na Conta Azul é quitação"
    if any(tok in CONJUNCOES_NO_NOME for tok in tn[1:]):
        return "indeterminada", "nome composto (duas ações): não é leitura"
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
