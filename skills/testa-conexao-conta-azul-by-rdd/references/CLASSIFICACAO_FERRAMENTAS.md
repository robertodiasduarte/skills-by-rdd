# Classificação das ferramentas: leitura, escrita ou indeterminada

Esta é a mesma regra do script `scripts/classificar_ferramentas.py`, escrita para ser aplicada à mão
quando o aplicativo não consegue executar o script. O resultado tem de ser o mesmo nos dois caminhos.

REGRA FAIL-CLOSED: só ferramentas classificadas como leitura são chamadas; escrita e indeterminada nunca são chamadas, nem como teste.

## Como ler o nome e a descrição

Leia o **nome** e a **descrição** separadamente (cada um tem as suas palavras), sempre nesta ordem:

1. **Antes de mexer no texto**, veja se ele tem um auxiliar de voz passiva — `é`, `são`, `foi`, `será`, `is`, `was`…
   (lista `AUXILIARES` abaixo). Leia **com acento**: `é` é verbo, `e` é conjunção e não conta.
2. Separe as palavras grudadas em camelCase: a troca de minúscula (ou número) para maiúscula separa
   (`listOrCreateCustomer` vira `list`, `Or`, `Create`, `Customer`), e uma sigla em maiúsculas se separa da palavra
   que começa logo depois dela (`GetOrUpdateHTTPStatus` vira `Get`, `Or`, `Update`, `HTTP`, `Status`).
3. Só então passe para minúsculas e tire os acentos, e quebre em palavras: tudo que não é letra ou número separa
   (`listar_contas_a_pagar` vira `listar`, `contas`, `a`, `pagar`).
4. Compare **palavra a palavra**, nunca um pedaço do meio: `ver` não casa `reverter`, `get` não casa `forget`.
   - **Radical** casa o começo da palavra: `atualiz` casa `atualiza`, `atualizar`, `atualizacao`.
   - **Exato** casa só a palavra inteira: `gera` casa `gera`, mas não `geral`.
   - O **particípio de um verbo exato** também é termo de escrita: de cada verbo exato terminado em `-ar` saem
     `-ado`, `-ada`, `-ados`, `-adas` (`gerar` → `gerado`, `geradas`); mais `pago(s)`/`pagas` e os da lista `PARTICIPIOS_EN`
     (`issued`, `paid`, `sent`…). Ele segue a mesma regra de isenção dos outros particípios.

## As regras, nesta ordem (a primeira que casar decide)

| Ordem | Se… | Então |
|---|---|---|
| 1 | alguma palavra do nome ou da descrição casa um termo de **escrita** | **escrita** |
| 2 | alguma palavra do nome ou da descrição começa por `baix` | **indeterminada** (na Conta Azul, dar baixa é quitar) |
| 3 | o **nome** tem conjunção depois da 1ª palavra (`listar_e_apagar`, `get_or_reset`) | **indeterminada** (duas ações num nome só) |
| 4 | alguma palavra do **nome** casa um termo de **leitura** | **leitura** |
| 5 | nada casou | **indeterminada** |

Duas exceções na regra 1, porque não são verbo:
- **Particípio** (`criado`, `emitidas`, `atualizados`) **conta como escrita**. Só é isento (adjetivo) quando TUDO vale:
  1. vem **colado depois de um substantivo do domínio, no mesmo trecho**: entre os dois só pode haver espaço ou `_`;
     qualquer outro sinal (ponto, vírgula, travessão, hífen, barra, aspas, parênteses, quebra de linha…) quebra a ligação (`notas emitidas`, `pagamentos realizados`, `clientes cadastrados`
     — lista `SUBSTANTIVOS_DO_DOMINIO` abaixo);
  2. o substantivo **e** o particípio estão no **plural** (`notas emitidas`); no singular (`cliente criado`) conta como
     escrita, porque costuma ser o resultado da própria operação;
  3. não é a 1ª palavra do nome;
  4. nome e descrição **juntos** não têm auxiliar (`é`, `são`, `foi`, `is`…) nem palavra de condição (`se`, `caso`,
     `quando`, `if`, `when`…), nem palavra que comece com `exist`, `inexist` ou `necessar`, nem `automaticamente`,
     `if missing`, `needed`;
  5. não está a até 2 palavras de `ou`/`or` (`criado ou atualizado` é upsert).
  Palavra da lista de termos **exatos** de escrita nunca é isenta (`liquida` termina em -ida, mas é verbo).
- `pagar` e `receber` logo depois de `a` são nome de conta **só** quando antes vem `conta(s)`, `título(s)`,
  `valor(es)`, `lançamento(s)`, `parcela(s)`, `saldo(s)` ou `total(is)` (`contas a pagar`). `começa a pagar` é verbo.

Em dúvida, a classe é **indeterminada**, e indeterminada não é chamada.

## Exemplos

| Ferramenta | Classe | Por quê |
|---|---|---|
| `listar_clientes` — “Lista os clientes e cria um novo se não existir” | escrita | `cria` na descrição |
| `reverter_conciliacao` | escrita | `reverter`; o `ver` no meio não conta |
| `baixar_xml_nfe` | indeterminada | `baix` |
| `listar_contas_a_pagar` | leitura | `a pagar` é nome de conta |
| `listar_notas` — “Lista as notas emitidas” | leitura | `emitidas` é adjetivo |
| `listar_clientes` — “se o CPF não existir, um novo cliente é criado” | escrita | `é criado` é voz passiva |
| `verificar_status` | indeterminada | `ver` só casa a palavra inteira |

## Listas (fonte única; o teste compara com o script)

<!-- LISTAS:INICIO -->
```json
{
  "RADICAIS_ESCRITA": [
    "cria",
    "crie",
    "cadastr",
    "inclu",
    "edit",
    "atualiz",
    "alter",
    "exclu",
    "delet",
    "remov",
    "cancel",
    "emit",
    "emiss",
    "quit",
    "revert",
    "revers",
    "convert",
    "convers",
    "envi",
    "adicion",
    "estorn",
    "aprov",
    "confirm",
    "transmit",
    "salv",
    "grav",
    "import",
    "duplic",
    "reabr",
    "fech",
    "marc",
    "sincron",
    "autoriz",
    "anex",
    "revog",
    "anul",
    "bloque",
    "liber",
    "reembols",
    "transfer",
    "mescl",
    "restaur",
    "apag",
    "destru",
    "limp",
    "substitu",
    "renov",
    "encerr",
    "finaliz",
    "conclu",
    "dispar",
    "vincul",
    "desvincul",
    "habilit",
    "desabilit",
    "ajust",
    "corrig",
    "execut",
    "efetu",
    "realiz",
    "process",
    "aplic",
    "atribu",
    "reenvi",
    "desconect",
    "notific",
    "prorrog",
    "reagend",
    "inser",
    "contabiliz",
    "recalcul",
    "provision",
    "deposit",
    "sobrescrev",
    "repass",
    "compens",
    "creat",
    "updat",
    "insert",
    "upsert",
    "modif",
    "writ",
    "submit",
    "approv",
    "generat",
    "upload",
    "sync",
    "register",
    "authoriz",
    "attach",
    "archiv",
    "revok",
    "reconcil",
    "activat",
    "deactivat",
    "refund",
    "merg",
    "restor",
    "settl",
    "overwrit",
    "push",
    "destroy",
    "purg",
    "eras",
    "chang",
    "replac",
    "renam",
    "assign",
    "enabl",
    "disabl",
    "reopen",
    "schedul",
    "trigger",
    "execut",
    "publish",
    "renew",
    "rotat",
    "invalidat",
    "unlink",
    "disconnect"
  ],
  "EXATOS_ESCRITA": [
    "gera",
    "gerar",
    "gere",
    "gerou",
    "geram",
    "geracao",
    "pagar",
    "paga",
    "pague",
    "pagou",
    "registrar",
    "registra",
    "registre",
    "registrou",
    "lancar",
    "lanca",
    "lance",
    "lancou",
    "faturar",
    "fatura",
    "fature",
    "faturou",
    "arquivar",
    "arquiva",
    "arquive",
    "arquivou",
    "liquidar",
    "liquide",
    "liquidou",
    "conciliar",
    "concilia",
    "concilie",
    "conciliou",
    "ativar",
    "ativa",
    "ative",
    "ativou",
    "inativar",
    "inativa",
    "inative",
    "inativou",
    "desativar",
    "desativa",
    "desative",
    "desativou",
    "liquida",
    "zerar",
    "zera",
    "zere",
    "zerou",
    "trocar",
    "troca",
    "troque",
    "trocou",
    "agendar",
    "agenda",
    "agende",
    "agendou",
    "cobrar",
    "cobra",
    "cobre",
    "cobrou",
    "add",
    "adds",
    "set",
    "sets",
    "put",
    "puts",
    "post",
    "posts",
    "patch",
    "patches",
    "send",
    "sends",
    "pay",
    "pays",
    "issue",
    "issues",
    "mark",
    "marks",
    "void",
    "voids",
    "block",
    "blocks",
    "release",
    "releases",
    "save",
    "saves",
    "store",
    "stores",
    "book",
    "books",
    "sign",
    "signs",
    "assina",
    "assinar",
    "assine",
    "assinou",
    "rateia",
    "ratear",
    "rateie",
    "rateou",
    "posta",
    "postar",
    "postou",
    "drop",
    "drops",
    "clear",
    "clears",
    "reset",
    "resets",
    "move",
    "moves",
    "apply",
    "applies",
    "close",
    "closes",
    "run",
    "runs",
    "complete",
    "completes",
    "finalize",
    "finalizes",
    "charge",
    "charges"
  ],
  "RADICAIS_LEITURA": [
    "list",
    "busc",
    "consult",
    "obte",
    "obti",
    "detalh",
    "pesquis",
    "mostr",
    "exib",
    "search",
    "fetch"
  ],
  "EXATOS_LEITURA": [
    "get",
    "find",
    "ver",
    "show",
    "view",
    "read",
    "reads"
  ],
  "RADICAL_INDETERMINADO": "baix",
  "SUFIXOS_PARTICIPIO": [
    "ado",
    "ada",
    "ados",
    "adas",
    "ido",
    "ida",
    "idos",
    "idas"
  ],
  "NOME_DE_CONTA": [
    "pagar",
    "receber"
  ],
  "AUXILIARES": [
    "é",
    "será",
    "serão",
    "sera",
    "serao",
    "são",
    "sao",
    "foi",
    "foram",
    "fica",
    "ficam",
    "sendo",
    "ser",
    "seja",
    "sejam",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "gets"
  ],
  "MARCADORES_CONDICIONAIS": [
    "automaticamente",
    "automatically",
    "missing",
    "absent",
    "needed",
    "preciso"
  ],
  "RADICAIS_CONDICIONAIS": [
    "exist",
    "inexist",
    "necessar"
  ],
  "PALAVRAS_DE_CONDICAO": [
    "se",
    "caso",
    "quando",
    "senao",
    "contrario",
    "if",
    "when",
    "unless",
    "otherwise"
  ],
  "SUBSTANTIVOS_DO_DOMINIO": [
    "nota",
    "notas",
    "titulo",
    "titulos",
    "conta",
    "contas",
    "venda",
    "vendas",
    "pedido",
    "pedidos",
    "cliente",
    "clientes",
    "fornecedor",
    "fornecedores",
    "lancamento",
    "lancamentos",
    "pagamento",
    "pagamentos",
    "recebimento",
    "recebimentos",
    "parcela",
    "parcelas",
    "boleto",
    "boletos",
    "cobranca",
    "cobrancas",
    "fatura",
    "faturas",
    "produto",
    "produtos",
    "servico",
    "servicos",
    "contrato",
    "contratos",
    "documento",
    "documentos",
    "registro",
    "registros",
    "orcamento",
    "orcamentos"
  ],
  "CONJUNCOES_ALTERNATIVA": [
    "ou",
    "or"
  ],
  "CONJUNCOES_NO_NOME": [
    "e",
    "ou",
    "and",
    "or"
  ],
  "ANTES_DE_NOME_DE_CONTA": [
    "conta",
    "contas",
    "titulo",
    "titulos",
    "valor",
    "valores",
    "lancamento",
    "lancamentos",
    "parcela",
    "parcelas",
    "saldo",
    "saldos",
    "total",
    "totais"
  ],
  "PARTICIPIOS_EN": [
    "issued",
    "marked",
    "paid",
    "sent",
    "booked",
    "signed",
    "charged",
    "closed",
    "moved",
    "applied",
    "dropped",
    "cleared",
    "ran",
    "added",
    "posted",
    "patched",
    "saved",
    "stored",
    "pushed",
    "voided",
    "blocked",
    "released",
    "completed",
    "finalized"
  ],
  "PARTICIPIOS_IRREGULARES_PT": [
    "pago",
    "pagos",
    "pagas"
  ]
}
```
<!-- LISTAS:FIM -->

## Limites conhecidos

- Ferramenta de leitura com palavra de escrita na descrição (“Lista notas por data de **emissão**”) sai
  como escrita e não é testada. É o lado seguro: perde-se cobertura, nunca se escreve no ERP.
- Nome sem nenhum verbo conhecido (`conta_azul_status`) sai indeterminado, mesmo que só leia.
- `ativa`, `liquida`, `agenda`, `cobra`, `troca` contam como verbo mesmo quando são adjetivo ou substantivo
  ("conta ativa", "a agenda do dia"): lado seguro.
- `fatura` sozinho conta como verbo ("Lista e **fatura** as vendas"): "a fatura do cliente" também sai escrita. Lado seguro.
- Texto com auxiliar em qualquer lugar ("as notas **são** emitidas e listadas") faz todo particípio dele contar como escrita. Lado seguro.
- `devolve` fica de fora de propósito: em API quer dizer "retorna" (leitura).
- Nenhuma lista de palavras é completa. Um verbo de escrita que não está nas listas, num nome que também tem
  verbo de leitura, sai como leitura. Por isso a bateria pede **1 registro** e nenhum parâmetro de criação, e o
  relatório lista todas as ferramentas chamadas: confira a lista antes de usar o MCP no dia a dia.
