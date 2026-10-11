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
Prefixo "re"/"des" + termo de escrita também é escrita ("reemite", "desconcilia", "refatura"), salvo as exceções.
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
    "efetu", "realiz", "process", "aplic", "atribu", "reenvi", "desconect", "notific", "prorrog", "reagend",
    "inser", "contabiliz", "recalcul", "provision", "deposit", "sobrescrev", "repass", "compens",
    "creat", "updat", "insert", "upsert", "modif", "writ", "submit", "approv", "generat", "upload", "sync",
    "register", "authoriz", "attach", "archiv", "revok", "reconcil", "activat", "deactivat", "refund",
    "merg", "restor", "settl", "overwrit", "push", "destroy", "purg", "eras", "chang", "replac", "renam", "assign", "enabl", "disabl",
    "reopen", "schedul", "trigger", "execut", "publish", "renew", "rotat", "invalidat", "unlink", "disconnect",
    # Avaliador ciclo 2: verbos cuja forma sem prefixo é substantivo ambíguo ("classificação", "configuração").
    "reclassific", "redefin", "reconfigur", "reexport", "retific", "deslig", "relig", "desfaz", "desfez", "desfeit",
    "escrev", "append", "migrat",
    # Avaliador ciclo 3.
    "inutiliz", "suspend", "rejeit", "reject", "renegoci", "unsubscrib", "subscrib",
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
    "save", "saves", "store", "stores", "book", "books", "sign", "signs",
    "assina", "assinar", "assine", "assinou", "rateia", "ratear", "rateie", "rateou", "posta", "postar", "postou",
    "drop", "drops", "clear", "clears", "reset", "resets", "move", "moves", "apply", "applies", "close", "closes",
    "run", "runs", "complete", "completes", "finalize", "finalizes", "charge", "charges",
    # Avaliador ciclo 2. Só as formas verbais: "publicação" e "configurações" continuam leitura.
    "publicar", "publica", "publique", "publicou", "configurar", "configura", "configure", "configurou", "configures",
    "migrar", "migra", "migre", "migrou", "unificar", "unifica", "unifique", "unificou", "unify", "unifies",
    # Avaliador ciclo 3. Fora de propósito, porque a forma é também substantivo: "reserva", "copia", "emails", "start".
    "manifestar", "manifesta", "manifeste", "manifestou", "protestar", "protesta", "proteste", "protestou",
    "negativar", "negativa", "negative", "negativou", "creditar", "credita", "credite", "creditou",
    "debitar", "debita", "debite", "debitou", "conceder", "concede", "concedeu", "abater", "abate", "abateu",
    "reservar", "reservou", "copiar", "copiou", "movimentar", "movimenta", "movimente", "movimentou",
    "associar", "associa", "associe", "associou", "classificar", "classifica", "classifique", "classificou",
    "categorizar", "categoriza", "categorize", "categorizou", "categorizes", "efetivar", "efetiva", "efetive",
    "efetivou", "aceitar", "aceita", "aceite", "aceitou", "recusar", "recusa", "recuse", "recusou",
    "iniciar", "inicia", "inicie", "iniciou", "mover", "movem", "moveu",
    "lock", "locks", "fix", "fixes", "ship", "ships", "starts",
    # Em inglês, forma exata: o radical pegaria o substantivo ("termination", "notifications", "refresh token").
    "adjust", "adjusts", "notify", "notifies", "terminate", "terminates", "amend", "amends", "invite", "invites",
    "increment", "increments", "fulfill", "fulfills", "refreshes",
)
# Particípio dos verbos que só existem como forma exata (review rodada 9, auditor A1): "boleto gerado", "bills are
# paid". PT: derivado de cada infinitivo -ar da lista; EN: lista explícita (irregulares não se derivam).
PARTICIPIOS_EN = (
    "issued", "marked", "paid", "sent", "booked", "signed", "charged", "closed", "moved", "applied", "dropped",
    "cleared", "ran", "added", "posted", "patched", "saved", "stored", "pushed", "voided", "blocked", "released",
    "completed", "finalized",
)
PARTICIPIOS_IRREGULARES_PT = ("pago", "pagos", "pagas")
# Prefixo + termo de escrita = escrita (avaliador ciclo 2: "reemite", "desconcilia", "refatura", "reprocessa" saíam
# leitura). O resto da palavra precisa de 3 letras ou mais. Exceções: palavras de leitura que o prefixo pegaria.
PREFIXOS_DE_ESCRITA = ("re", "des")
EXCECOES_DE_PREFIXO = ("descobre", "remark", "remarks")
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
    # "_" separa: auxiliar dentro de nome snake_case também conta (review rodada 7, A2).
    s = unicodedata.normalize("NFC", _separar_camel(texto).lower())
    return any(t in AUXILIARES for t in re.findall(r"[^\W_]+", s))


def tokens(texto):
    s = unicodedata.normalize("NFKD", _separar_camel(texto).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", s)


def tokens_e_fronteiras(texto):
    """Tokens e, para cada um, se ele abre um trecho novo. Trecho = só letras, números, espaço e `_`: QUALQUER
    outro sinal (ponto, vírgula, travessão, hífen, barra, aspas, parênteses, quebra de linha…) separa.
    A isenção de particípio exige o substantivo no MESMO trecho (review rodadas 6 e 7, codex: o ponto e depois
    o travessão colavam `clientes` + `criado`; lista de sinais vira regra por exclusão)."""
    # Sem marcas combinantes ANTES de separar: em NFD o acento (U+0327, U+0301…) não é \w e cortaria "lança" em
    # "lanc" + "a" (review rodada 9, codex). Acento sai aqui de qualquer jeito: tokens() compara sem acento.
    s = unicodedata.normalize("NFKD", texto or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    toks, fronteiras = [], []
    for trecho in re.split(r"[^\w \t]+", s):
        for k, t in enumerate(tokens(trecho)):
            toks.append(t)
            fronteiras.append(k == 0)
    return toks, fronteiras


PARTICIPIOS_DE_EXATOS = frozenset(
    [v[:-2] + suf for v in EXATOS_ESCRITA if v.endswith("ar") and len(v) > 3 for suf in ("ado", "ada", "ados", "adas")]
    + list(PARTICIPIOS_IRREGULARES_PT) + list(PARTICIPIOS_EN)
)


def _sem_prefixo(tok):
    """O resto da palavra depois de cada prefixo de escrita que ela tem (vazio se é exceção ou o resto é curto)."""
    if tok in EXCECOES_DE_PREFIXO:
        return []
    return [tok[len(p):] for p in PREFIXOS_DE_ESCRITA if tok.startswith(p) and len(tok) - len(p) >= 3]


def _exato_de_escrita(tok):
    return tok in EXATOS_ESCRITA or any(_exato_de_escrita(r) for r in _sem_prefixo(tok))


def _escrita(tok):
    if tok in EXATOS_ESCRITA or tok in PARTICIPIOS_DE_EXATOS or any(tok.startswith(r) for r in RADICAIS_ESCRITA):
        return True
    return any(_escrita(r) for r in _sem_prefixo(tok))


def _leitura(tok):
    return tok in EXATOS_LEITURA or any(tok.startswith(r) for r in RADICAIS_LEITURA)


def _condicional(toks):
    return any(t in MARCADORES_CONDICIONAIS or t in PALAVRAS_DE_CONDICAO or t.startswith(RADICAIS_CONDICIONAIS)
               for t in toks)


def _conta_como_verbo(toks, i, primeiro_do_nome, tem_auxiliar, condicional, fronteiras):
    tok = toks[i]
    vizinhos = toks[max(0, i - 2):i] + toks[i + 1:i + 3]
    # Auxiliar em qualquer posição do texto = voz passiva (review rodadas 2 e 4, codex): sem janela de distância.
    # Forma EXATA da lista é verbo por definição: nunca isentar como particípio ("liquida" termina em -ida;
    # review rodada 3, codex). Vale também com prefixo ("reliquida"; avaliador ciclo 2).
    if (not primeiro_do_nome and not _exato_de_escrita(tok) and (tok.endswith(SUFIXOS_PARTICIPIO) or tok in PARTICIPIOS_DE_EXATOS)
            and i > 0 and not fronteiras[i] and toks[i - 1] in SUBSTANTIVOS_DO_DOMINIO
            # Plural nos dois (review rodada 7, A3): listagem descreve "notas emitidas"; "cliente criado" no
            # singular costuma ser o resultado da própria operação.
            and tok.endswith("s") and toks[i - 1].endswith("s")
            and not tem_auxiliar and not condicional
            and not any(v in CONJUNCOES_ALTERNATIVA for v in vizinhos)):
        return False
    if tok in NOME_DE_CONTA and i > 1 and toks[i - 1] == "a" and toks[i - 2] in ANTES_DE_NOME_DE_CONTA:
        return False
    return True


def classificar(nome, descricao=""):
    # Uma forma canônica na entrada: NFC e NFD do mesmo texto têm de dar a mesma classe.
    nome = unicodedata.normalize("NFC", nome or "")
    descricao = unicodedata.normalize("NFC", descricao or "")
    (tn, fn), (td, fd) = tokens_e_fronteiras(nome), tokens_e_fronteiras(descricao)
    # Auxiliar e condição valem para nome e descrição JUNTOS (review rodada 5, A2: paridade com a prosa).
    aux = _tem_auxiliar(f"{nome} {descricao}")
    cond = _condicional(tn + td)
    for toks, fr, eh_nome in ((tn, fn, True), (td, fd, False)):
        for i, tok in enumerate(toks):
            if _escrita(tok) and _conta_como_verbo(toks, i, eh_nome and i == 0, aux, cond, fr):
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
