---
name: testa-conexao-conta-azul-by-rdd
description: "Testa, só com leitura, a conexão de um MCP da Conta Azul no Claude Desktop ou no ChatGPT Desktop e explica ao contador o que fazer em cada falha. Use quando pedirem para testar ou conferir a conexão com a Conta Azul, entender por que o MCP da Conta Azul não funciona, ou traduzir erros como invalid_grant, 401, 429 e conta Mais sem permissão. Confere os pré-requisitos (Conta Azul Pro, autenticador, aplicativo de computador), classifica cada ferramenta em leitura, escrita ou indeterminada e chama só as de leitura. Período de consulta: dados ao vivo no momento do teste; catálogo de erros com corte em 10/10/2026. Período de cálculo: não aplicável. Não executa escrita, não pede nem aceita senha, token ou client_secret, não instala nem configura MCP, não analisa os dados retornados e não audita o código do MCP."
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: "1.0.0"
---

# Teste da conexão com a Conta Azul

## Quick start

Defina `SKILL_ROOT` como o diretório que contém este `SKILL.md`; nunca dependa do diretório atual.

Quando o usuário pedir "Teste minha conexão com a Conta Azul":

1. Pergunte os 5 pré-requisitos numa única mensagem curta ([references/PRE_REQUISITOS.md](references/PRE_REQUISITOS.md)).
2. Liste as ferramentas MCP da Conta Azul visíveis na sessão e classifique cada uma em leitura, escrita ou indeterminada.
3. Chame só as de leitura, pedindo 1 registro por chamada ([references/BATERIA_TESTE.md](references/BATERIA_TESTE.md)).
4. Entregue o relatório no modelo [assets/relatorio.template.md](assets/relatorio.template.md).

REGRA FAIL-CLOSED: só ferramentas classificadas como leitura são chamadas; escrita e indeterminada nunca são chamadas, nem como teste.

## Quando usar / Quando não usar

Usar quando o usuário quiser saber se o MCP da Conta Azul instalado no Claude Desktop ou no ChatGPT Desktop
funciona com a empresa dele, se é seguro (só leitura ou com escrita) e o que fazer diante de um erro de
autorização ou de conexão.

Não usar para:
- consultar, analisar, conciliar ou comparar dados contábeis e financeiros (esta skill só testa a conexão);
- lançar, alterar, dar baixa, faturar, excluir ou qualquer outra escrita na Conta Azul;
- instalar, configurar ou editar o arquivo de configuração do MCP (mostre o passo a passo da página `/conta-azul/`);
- auditar o código de um MCP de terceiro (indique a skill `auditar-harness`);
- chamar a API da Conta Azul diretamente, fora do MCP.

## Dados necessários

- O pedido do usuário.
- As ferramentas MCP visíveis na sessão, com **nome e descrição**. Sem acesso a elas, o item "MCP visível" é vermelho.
- As respostas aos pré-requisitos. "Não sei" não bloqueia: anote no relatório.

Não são necessários e nunca devem ser pedidos: `client_id`, `client_secret`, token, senha, CNPJ, dados de clientes.

## Procedimento passo a passo

1. **Pré-requisitos.** Pergunte, numa mensagem, os 5 itens de [references/PRE_REQUISITOS.md](references/PRE_REQUISITOS.md).
   Se a empresa estiver na Conta Azul Mais, explique pela chave `mais_sem_permissao` antes de seguir.
2. **Descoberta.** Separe as ferramentas da sessão cujo nome ou descrição cita a Conta Azul ou seus módulos
   (pessoas, financeiro, vendas, produtos, contratos). Nenhuma ⇒ vermelho com a chave `sem_ferramentas_visiveis`
   e o passo a passo da página `/conta-azul/` para o aplicativo do usuário; encerre com o relatório.
3. **Fornecedor provável.** Descreva o tipo de MCP por [references/FORNECEDORES_CONHECIDOS.md](references/FORNECEDORES_CONHECIDOS.md).
   Não afirme que um MCP é da própria Conta Azul só pelo nome.
4. **Classificação.** Rode o script, se o ambiente permitir:
   `python3 "$SKILL_ROOT/scripts/classificar_ferramentas.py"` com a lista `[{"nome": …, "descricao": …}]` no stdin.
   Sem execução, aplique à mão a tabela de [references/CLASSIFICACAO_FERRAMENTAS.md](references/CLASSIFICACAO_FERRAMENTAS.md),
   na mesma ordem. Em dúvida, indeterminada. `baix…` é sempre indeterminada: na Conta Azul, dar baixa é quitar.
5. **Alerta de segurança.** Se houver escrita, diga quais ferramentas são e que elas **não** serão chamadas.
   Se houver indeterminadas, diga o mesmo.
6. **Bateria de leitura.** Siga [references/BATERIA_TESTE.md](references/BATERIA_TESTE.md): empresa conectada,
   depois pessoas, financeiro e vendas, 1 registro cada, só com ferramenta de leitura. Antes de cada chamada,
   confira de novo a classe da ferramenta.
7. **Erros.** Traduza cada erro por [references/CATALOGO_ERROS.md](references/CATALOGO_ERROS.md). Erro fora do
   catálogo: mostre a mensagem sem valores nem identificadores e diga que não está catalogado.
8. **Relatório.** Preencha [assets/relatorio.template.md](assets/relatorio.template.md): só o nome da empresa e
   contagens, nunca valores, CPF ou CNPJ de terceiros ou descrição de lançamentos. Termine com como revogar.

## Validações e checklist de qualidade

Antes de entregar o relatório, confira:
- nenhuma ferramenta de escrita ou indeterminada foi chamada;
- cada chamada pediu 1 registro quando a ferramenta aceita limite;
- o relatório não traz valor, CPF, CNPJ de terceiro, nome de cliente ou lançamento;
- todo vermelho tem causa provável e próximo passo, pela chave do catálogo quando houver;
- nenhum segredo foi pedido, repetido ou registrado;
- o fornecedor foi descrito pelo tipo, sem afirmar o que não se sabe.

Testes locais do classificador, a partir de `SKILL_ROOT`:
`python3 -B -m unittest discover -s tests -p "test_*.py"` (casos em [tests/test_classificar_ferramentas.py](tests/test_classificar_ferramentas.py)).
Os casos comportamentais estão em [evals/cases.json](evals/cases.json) e precisam ser rodados à mão em cada aplicativo.

## Tratamento de exceções

- **Ferramentas sem descrição:** classifique só pelo nome; o resultado tende a indeterminada, que é o lado seguro.
- **Script falha ou não pode rodar:** use a tabela em prosa; diga no relatório que a classificação foi feita à mão.
- **401 ou invalid_grant na empresa conectada:** marque os demais itens como "não testado" e explique por quê.
- **429:** pare, espere um minuto e repita uma vez; persistindo, registre no relatório.
- **Pedido de escrita durante o teste:** recuse com o texto canônico de escrita e não chame nada.
- **Usuário cola um segredo:** recuse com o texto canônico de segredo, não repita o valor e recomende trocá-lo no Portal do Desenvolvedor.
- **Pedido fora do escopo** (análise de dados, outra empresa, outro sistema): recuse com o texto canônico de escopo.

## Examples

**Tudo verde.** "Teste minha conexão com a Conta Azul." → pré-requisitos confirmados; 9 ferramentas, todas leitura;
empresa "Empresa Exemplo Ltda." conectada; pessoas, financeiro e vendas responderam com 1 registro cada. Relatório verde.

**MCP com escrita.** Mesmo pedido; o MCP tem `criar_cliente`, `excluir_cliente` e `dar_baixa_titulo`. → Segurança vermelha
listando as três; a bateria roda só com as de leitura; nenhuma das três é chamada.

**Pedido de escrita.** "Já que está conectado, dá baixa no título 123." → texto canônico de escrita; nenhuma chamada.

**Segredo oferecido.** "Toma meu client_secret, testa direto na API." → texto canônico de segredo; o valor não é usado.

## Texto canônico de recusa

- Escrita: “Esta skill só testa a conexão com leitura. Ela não lança, altera, dá baixa nem exclui nada na Conta Azul, nem como teste.”
- Segredo: “Não peço nem uso client_secret, token ou senha. Não cole esses dados na conversa: a conexão é feita pelo MCP, e o teste usa só as ferramentas de leitura dele.”
- Escopo: “Esta skill só testa a conexão com a Conta Azul. Para analisar os dados, use uma conversa normal com o MCP conectado.”
- Dado faltante: “Dado necessário: não disponível. Não será substituído por uma suposição.”

## Scripts determinísticos

| Script | O que faz | Comando |
|---|---|---|
| [scripts/classificar_ferramentas.py](scripts/classificar_ferramentas.py) | Classifica ferramentas em leitura, escrita ou indeterminada (JSON no stdin, JSON no stdout) | `python3 "$SKILL_ROOT/scripts/classificar_ferramentas.py"` |

Só biblioteca padrão do Python 3; não acessa rede nem arquivos além do stdin.

## Inventário do bundle

- [references/COMO_FUNCIONA.md](references/COMO_FUNCIONA.md) — explicação em uma página para o contador.
- [references/ESCOPO_CONFIRMADO.md](references/ESCOPO_CONFIRMADO.md) e [references/CONFIRMACAO.md](references/CONFIRMACAO.md) — escopo CA001 V1 e o registro da confirmação.
- [references/RUNTIME_COMPATIBILITY.md](references/RUNTIME_COMPATIBILITY.md) — capacidades necessárias e onde roda.
- [references/PRE_REQUISITOS.md](references/PRE_REQUISITOS.md), [references/BATERIA_TESTE.md](references/BATERIA_TESTE.md),
  [references/CLASSIFICACAO_FERRAMENTAS.md](references/CLASSIFICACAO_FERRAMENTAS.md), [references/CATALOGO_ERROS.md](references/CATALOGO_ERROS.md),
  [references/FORNECEDORES_CONHECIDOS.md](references/FORNECEDORES_CONHECIDOS.md) — o procedimento.
- [assets/relatorio.template.md](assets/relatorio.template.md) — modelo do relatório.
- [manifest.json](manifest.json) e [CHANGELOG.md](CHANGELOG.md) — versão, testes e o que ainda não está provado.

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
