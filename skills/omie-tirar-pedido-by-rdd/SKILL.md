---
name: omie-tirar-pedido-by-rdd
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: '1.0.0'
description: "Monta um pedido de venda no Omie a partir do cliente e dos itens ditados pela pessoa, mostra o pedido na tela e só o inclui depois de uma frase literal de confirmação, um pedido por vez, conferindo o resultado. Use quando a pessoa pedir para tirar, lançar, fazer ou criar um pedido de venda no Omie. Requer o conector MCP do Omie. Período de consulta: dados ao vivo no momento da execução; período de cálculo: não aplicável. Não fatura nem emite NF-e, não inutiliza, não cadastra cliente ou produto, não dá desconto, não altera nem exclui pedido e não soma valores de vários pedidos."
---

# Tirar pedido no Omie

## Quick start

Requer o conector MCP do Omie ligado e, no conector, `omie_executar` e `omie_executar_em_varias` em "pedir aprovação".
Começar por `omie_listar_apps` e perguntar a empresa quando houver mais de uma. Pedido típico: "tira um pedido para a
Padaria Sol: 10 caixas do produto 123 e 5 do 456, em 30/60". Resultado: o pedido incluído na etapa 10, com o número
e o status conferidos.

## Quando usar / Quando não usar

Usar para: incluir **um** pedido de venda por vez, ditado pela pessoa, para cliente e produtos que já existem no Omie.

Não usar, inclusive quando a pessoa insistir, inclusive "só desta vez":
- **faturar** o pedido ou emitir NF-e, e **inutilizar** numeração — o servidor da Omie não pede confirmação para essas ações; faça pelo Omie;
- cadastrar cliente ou produto que não foi encontrado;
- dar desconto, sugerir troca de produto ou outro preço além do que a pessoa disser;
- alterar, duplicar, trocar etapa ou excluir pedido existente;
- somar, totalizar ou comparar valores de vários pedidos (ver recusa abaixo);
- análise comercial, de margem ou de crédito do cliente.

## Dados necessários

| Dado | Origem | Se faltar |
|---|---|---|
| Empresa (`app_hash`) | `omie_listar_apps` | perguntar qual, se houver mais de uma |
| Cliente | CNPJ, razão social ou nome fantasia dito pela pessoa | perguntar |
| Itens | código, EAN ou descrição + quantidade; preço só se a pessoa disser | perguntar a quantidade |
| Condição de pagamento | pergunta | perguntar; nunca escolher |

## Procedimento passo a passo

1. `omie_listar_apps`; confirmar a empresa.
2. Cliente: `geral/clientes:ListarClientes` com `clientesFiltro` (`cnpj_cpf`, `razao_social` ou `nome_fantasia`), 5 por página. Mais de um ⇒ perguntar qual. Nenhum ⇒ dizer e parar.
3. Cada item: `estoque/resumo:ObterEstoqueProduto` com `xCodigo` (código, EAN ou descrição): código, descrição, preço (`nPrecoUnitario`) e saldo. Mais de um produto ⇒ perguntar qual. Se a pessoa disser outro preço, usar o dela.
4. Destacar, com o critério dito, item com quantidade maior que o saldo disponível. Não sugerir troca nem desconto.
5. Condição de pagamento: `geral/parcelas:ListarParcelas` para achar o código da condição que a pessoa disser.
6. Antes de incluir, `omie_descrever_operacao` para `produtos/pedido:IncluirPedido` e montar o `param` com os campos reais.
7. Seguir o gate abaixo. Incluir com `produtos/pedido:IncluirPedido`, etapa "10" (pedido). Incluir não emite nota, mas o pedido passa a existir no Omie.
8. Conferir com `produtos/pedido:ConsultarPedido` e responder com o número do pedido e o valor total **que a Omie devolveu**. A skill não soma os itens.

### Gate de escrita

1. **Validar** antes: chame a operação de validação da Omie quando existir; sem ela, confira cliente, itens e condição com as operações de leitura. Status diferente de "0" ou dado faltando ⇒ pare e mostre o motivo.
2. **Mostrar** o documento completo que será gravado (cliente, itens, quantidades, valores e condição).
3. Pedir a **frase literal** `CONFIRMO GRAVAR <tipo> <identificador>`. Qualquer outra resposta não autoriza.
4. **Um por vez**: uma frase por documento; lote exige uma frase para cada um.
5. Executar com `"confirmado": true` e **conferir o status** com a operação de consulta.
6. **Não repetir**: erro ou dúvida no status ⇒ pare e informe; nunca tente de novo sozinho.

Nesta skill a frase é `CONFIRMO GRAVAR PEDIDO <nome do cliente>`. No passo 2 do gate, mostrar cada item com quantidade
e preço unitário, sem total calculado pelo modelo.

Pré-requisito: no conector do Omie, `omie_executar` e `omie_executar_em_varias` em "pedir aprovação".

## Validações e checklist de qualidade

- [ ] Empresa informada em toda chamada.
- [ ] Toda operação usada consta em `manifest.json › operacoes`.
- [ ] Nenhuma inclusão sem a frase literal daquele pedido.
- [ ] Um pedido por frase; nenhum retry automático.
- [ ] Nenhum valor somado pelo modelo; o total vem do `ConsultarPedido`.
- [ ] Todo destaque diz o critério.

## Tratamento de exceções

| Situação | O que fazer |
|---|---|
| conector ausente | dizer que a skill precisa do conector do Omie e parar |
| cliente ou produto não encontrado | dizer e parar; não cadastrar |
| erro de campo obrigatório | `omie_descrever_operacao`, corrigir e mostrar o pedido de novo antes de pedir a frase |
| erro ao incluir | mostrar a mensagem da Omie e parar; conferir com `produtos/pedido:ConsultarPedido` se nada foi gravado; corrigido o dado, voltar ao passo 2 do gate (mostrar de novo e pedir nova frase) — nunca reenviar sozinho |
| "Too many requests" ou HTTP 425 | parar e informar (bloqueio de cerca de 30 minutos) |
| dado que a Omie não trouxe | `nao disponivel` |

## Examples

**Positivo (sintético).** "Tira um pedido para a Padaria Sol: 10 caixas do 123 em 30/60." → cliente, produto e
condição achados; pedido mostrado; após `CONFIRMO GRAVAR PEDIDO Padaria Sol`, inclusão na etapa 10 e número conferido.

**Contraexemplo.** "Já fatura também." → recusa de faturamento.

**Contraexemplo.** "Quanto deu o total dos pedidos de hoje?" → recusa de totalização.

## Texto canônico de recusa

- "Este perfil não totaliza registros. Para somar com conferência, gere o perfil Conferidor."
- "Faturar e inutilizar estão fora desta skill: o servidor da Omie não pede confirmação para essas ações. Faça pelo Omie."
- "Não cadastro cliente nem produto: confira o nome ou cadastre pelo Omie."
- "Dado necessário: nao disponivel. Não será substituído por uma suposição."

## Inventário do bundle

[Escopo confirmado](references/ESCOPO_CONFIRMADO.md) · [Como funciona](references/COMO_FUNCIONA.md) ·
[Manifesto](manifest.json) · [Histórico](CHANGELOG.md) · [Cenários](evals/cases.json).

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
