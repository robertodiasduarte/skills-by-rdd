---
name: {{nome}}
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: '{{versao}}'
description: "{{O que a skill faz no Omie, em terceira pessoa}}. Use quando {{gatilhos aprovados, com as palavras que a pessoa usa}}. Requer o conector MCP do Omie. Período de consulta: {{dados ao vivo no momento da execução | período pedido}}; período de cálculo: não aplicável. Não soma valores de vários registros, não fatura nem inutiliza e não faz análise contábil, tributária ou financeira."
---

# {{Título aprovado}}

## Quick start

Requer o conector MCP do Omie ligado. Começar por `omie_listar_apps` e perguntar a empresa quando houver mais de uma.
{{Uma ou duas linhas com o pedido típico e o que a skill devolve.}}

## Quando usar / Quando não usar

Usar para: {{cobertura aprovada, até 8 itens}}.

Não usar, inclusive quando a pessoa insistir, inclusive "só desta vez":
- **faturar** pedido ou ordem de serviço (NF-e, NFS-e) e **inutilizar** numeração — o servidor da Omie não pede confirmação para essas ações; faça pelo Omie;
- somar, totalizar ou comparar valores de vários registros — este perfil não soma (ver recusa abaixo);
- {{vizinhos excluídos pelo nome próprio}};
- análise contábil, tributária ou financeira, recomendação de cobrança, compra ou desconto.

## Dados necessários

| Dado | Origem | Se faltar |
|---|---|---|
| Empresa (`app_hash`) | `omie_listar_apps` | perguntar qual, se houver mais de uma |
| {{dado}} | {{pergunta ou operação de leitura}} | {{perguntar · nao disponivel}} |

## Procedimento passo a passo

1. `omie_listar_apps`; confirmar a empresa.
2. {{passos aprovados, cada um com a operação no formato `serviço:Método` e os campos exatos}}.
3. Quantidades vêm do campo que a Omie informa (`nTotRegistros`, `total_de_registros`), nunca de contagem feita pelo modelo.

<!-- Bloco abaixo SÓ quando o escopo aprovado tem escrita. Sem escrita, apagar até o fim do gate. -->
### Gate de escrita

1. **Validar** antes: chame a operação de validação da Omie quando existir; sem ela, confira cliente, itens e condição com as operações de leitura. Status diferente de "0" ou dado faltando ⇒ pare e mostre o motivo.
2. **Mostrar** o documento completo que será gravado (cliente, itens, quantidades, valores e condição).
3. Pedir a **frase literal** `CONFIRMO GRAVAR <tipo> <identificador>`. Qualquer outra resposta não autoriza.
4. **Um por vez**: uma frase por documento; lote exige uma frase para cada um.
5. Executar com `"confirmado": true` e **conferir o status** com a operação de consulta.
6. **Não repetir**: erro ou dúvida no status ⇒ pare e informe; nunca tente de novo sozinho.

Pré-requisito: no conector do Omie, `omie_executar` e `omie_executar_em_varias` em "pedir aprovação".
<!-- fim do bloco de escrita -->

## Validações e checklist de qualidade

- [ ] Empresa informada em toda chamada.
- [ ] Toda operação usada consta em `manifest.json › operacoes`.
- [ ] Nenhum valor somado pelo modelo.
- [ ] Todo destaque diz o critério.
- [ ] Resposta com empresa, operação, filtros, período e horário da consulta.

## Tratamento de exceções

| Situação | O que fazer |
|---|---|
| conector ausente | dizer que a skill precisa do conector do Omie e parar |
| erro de campo obrigatório na leitura | `omie_descrever_operacao`, corrigir e repetir uma vez |
| erro ao gravar | mostrar a mensagem da Omie e parar; corrigido o dado, voltar ao passo 2 do gate (mostrar de novo e pedir nova frase) — nunca reenviar sozinho |
| "Too many requests" ou HTTP 425 | parar e informar (bloqueio de cerca de 30 minutos) |
| lista vazia | dizer o período e o filtro usados; não é erro |
| dado que a Omie não trouxe | `nao disponivel` |

## Examples

**Positivo (sintético).** {{pedido}} → {{operações e resposta}}.

**Contraexemplo.** "Quanto dá o total em aberto?" → recusa de totalização e oferta de contar pelo `nTotRegistros`.

## Texto canônico de recusa

- "Este perfil não totaliza registros. Para somar com conferência, gere o perfil Conferidor."
- "Faturar e inutilizar estão fora desta skill: o servidor da Omie não pede confirmação para essas ações. Faça pelo Omie."
- "Dado necessário: nao disponivel. Não será substituído por uma suposição."

## Inventário do bundle

[Escopo confirmado](references/ESCOPO_CONFIRMADO.md) · [Como funciona](references/COMO_FUNCIONA.md) ·
[Manifesto](manifest.json) · [Histórico](CHANGELOG.md) · [Cenários](evals/cases.json).

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
