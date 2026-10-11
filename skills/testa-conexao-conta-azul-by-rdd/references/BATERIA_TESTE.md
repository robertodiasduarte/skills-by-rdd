# Bateria de teste e critério de cor

Só ferramentas classificadas como **leitura** entram aqui (ver `CLASSIFICACAO_FERRAMENTAS.md`).
Cada chamada pede o mínimo: **1 registro** quando a ferramenta aceitar tamanho de página ou limite.

| Item | Como testar | Verde | Amarelo | Vermelho |
|---|---|---|---|---|
| MCP visível | Listar as ferramentas de um MCP identificado como da Conta Azul (o nome do servidor/conector ou da ferramenta cita a Conta Azul). Palavra de módulo sozinha não basta: outro ERP tem "vendas" também | Há ferramentas da Conta Azul e ao menos 1 é leitura | Há ferramentas, mas nenhuma é leitura | Nenhuma ferramenta da Conta Azul |
| Empresa conectada | Chamar a ferramenta **classificada como leitura** que devolve a conta conectada (ex.: `get_conta_conectada`, `obter_empresa`). Nome sem verbo de leitura (`me`, `empresa`) sai indeterminado e não é chamado: o item fica amarelo | Devolve o nome da empresa | Não há ferramenta de leitura para isso | Erro (traduzir pelo catálogo) |
| Pessoas | 1 chamada de leitura de clientes/fornecedores, limite 1 | Responde (contar registros) | Não há ferramenta de leitura do módulo | Erro (traduzir) |
| Financeiro | 1 chamada de leitura de contas a pagar ou a receber, limite 1 | Responde | Sem ferramenta de leitura | Erro |
| Vendas | 1 chamada de leitura de vendas, limite 1 | Responde | Sem ferramenta de leitura | Erro |
| Segurança | Resultado da classificação | Todas as ferramentas são leitura | Há indeterminadas | **Há escrita**: alerta; o teste continua só com leitura |

## O que mostrar do retorno

- **Só** o nome da empresa conectada e a **contagem** de registros de cada chamada.
- **Nunca** valores, CPF ou CNPJ de terceiros, nomes de clientes, descrição de lançamentos.
- Se a ferramenta devolver dados demais, resuma em "N registro(s) lido(s)".

## Ordem

1. Pré-requisitos (uma pergunta).
2. Descobrir e classificar as ferramentas.
3. Empresa conectada.
4. Pessoas, financeiro, vendas — só os módulos que tiverem ferramenta de leitura.
5. Relatório (modelo em `assets/relatorio.template.md`).

Erro em um item não interrompe os outros, exceto `http_401` ou `invalid_grant` na empresa conectada:
sem autorização válida, os demais itens ficam "não testado" e o relatório diz por quê.
