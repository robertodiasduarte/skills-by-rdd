# Changelog — testa-conexao-conta-azul-by-rdd

## 1.0.0 — 2026-10-11

- Primeira versão, gerada pelo skill-builder-by-rdd a partir do escopo CA001 V2 (perfil C, operacional).
- Antes de qualquer chamada, mostra a lista das ferramentas de leitura e espera o ok do usuário (escopo V2).
- Classificação de ferramentas MCP em leitura, escrita ou indeterminada por palavra inteira ou radical, nunca por
  pedaço de palavra; verbo de escrita na descrição vence o nome; `baix…` sempre indeterminada; regra fail-closed.
- Prefixo `re`/`des` + termo de escrita conta como escrita (`reemite`, `desconcilia`, `refatura`), com exceções
  listadas (`descobre`); `recebe` e `links` ficam de fora de propósito ("contas a receber", "links de pagamento").
- Mais 70 formas verbais de escrita (suspende, inutiliza, protesta, credita, debita, refreshes…). A confirmação passa a
  avisar que a lista de palavras não prova "só leitura" e pede para o usuário ler a descrição de cada ferramenta.
- Bateria só de leitura (empresa conectada; pessoas, financeiro e vendas com 1 registro).
- Catálogo com 8 erros conhecidos, conferidos em 10/10/2026.
- Casos comportamentais E1–E8 escritos; execução nos aplicativos pendente (ver manifest.json).
