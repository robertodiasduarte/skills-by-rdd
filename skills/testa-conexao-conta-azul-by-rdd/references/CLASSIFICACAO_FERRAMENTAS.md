# Classificação das ferramentas: leitura, escrita ou indeterminada

Esta é a mesma regra do script `scripts/classificar_ferramentas.py`, escrita para ser aplicada à mão
quando o aplicativo não consegue executar o script. O resultado tem de ser o mesmo nos dois caminhos.

REGRA FAIL-CLOSED: só ferramentas classificadas como leitura são chamadas; escrita e indeterminada nunca são chamadas, nem como teste.

## Como ler o nome e a descrição

1. Junte o **nome** e a **descrição** da ferramenta, em minúsculas e sem acento.
2. Quebre em palavras: tudo que não é letra ou número separa (`listar_contas_a_pagar` vira `listar`, `contas`, `a`, `pagar`).
3. Compare **palavra a palavra**, nunca um pedaço do meio: `ver` não casa `reverter`, `get` não casa `forget`.
   - **Radical** casa o começo da palavra: `atualiz` casa `atualiza`, `atualizar`, `atualizacao`.
   - **Exato** casa só a palavra inteira: `gera` casa `gera`, mas não `geral`.

## As regras, nesta ordem (a primeira que casar decide)

| Ordem | Se… | Então |
|---|---|---|
| 1 | alguma palavra do nome ou da descrição casa um termo de **escrita** | **escrita** |
| 2 | alguma palavra do nome ou da descrição começa por `baix` | **indeterminada** (na Conta Azul, dar baixa é quitar) |
| 3 | alguma palavra do **nome** casa um termo de **leitura** | **leitura** |
| 4 | nada casou | **indeterminada** |

Duas exceções na regra 1, porque não são verbo:
- **Particípio que funciona como adjetivo** (`emitidas`, `cancelados`, `realizados`) não conta como escrita.
  Ele **conta** (é verbo) quando: é a **primeira** palavra do nome; vem logo depois de um auxiliar
  (`é criado`, `são removidos`, `is created` — voz passiva); ou o texto fala em criar sob condição
  (`se não existir`, `automaticamente`, `if missing`). Os auxiliares e os marcadores estão nas listas abaixo.
- `pagar` e `receber` logo depois de `a` são nome de conta (`contas a pagar`), não o verbo.

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
    "restor"
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
    "ative",
    "ativou",
    "inativar",
    "inative",
    "desativar",
    "desative",
    "add",
    "adds",
    "set",
    "sets",
    "put",
    "puts",
    "post",
    "posts",
    "patch",
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
    "releases"
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
    "fetch",
    "read"
  ],
  "EXATOS_LEITURA": [
    "get",
    "find",
    "ver",
    "show",
    "view"
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
    "e",
    "sera",
    "serao",
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
    "absent"
  ]
}
```
<!-- LISTAS:FIM -->

## Limites conhecidos

- Ferramenta de leitura com palavra de escrita na descrição (“Lista notas por data de **emissão**”) sai
  como escrita e não é testada. É o lado seguro: perde-se cobertura, nunca se escreve no ERP.
- Nome sem nenhum verbo conhecido (`conta_azul_status`) sai indeterminado, mesmo que só leia.
- "e" também é conjunção: em "notas emitidas **e** canceladas", `canceladas` conta como escrita. Lado seguro.
- Nenhuma lista de palavras é completa. Um verbo de escrita que não está nas listas, num nome que também tem
  verbo de leitura, sai como leitura. Por isso a bateria pede **1 registro** e nenhum parâmetro de criação, e o
  relatório lista todas as ferramentas chamadas: confira a lista antes de usar o MCP no dia a dia.
