---
name: omie-atrasos-conferidos-by-rdd
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: '1.0.0'
description: "Mostra os títulos atrasados de uma empresa no Omie, a receber e a pagar, em três faixas de atraso (até 30, de 31 a 90 e mais de 90 dias), com a quantidade informada pela Omie e o valor em aberto somado por script e conferido contra a contagem da Omie. Use quando a pessoa perguntar o que está atrasado, vencido ou em aberto no Omie, quanto soma o atraso ou como está a inadimplência por idade. Requer o conector MCP do Omie e Python 3.10+ com rede (Claude Code). Período de consulta: dados ao vivo no momento da execução; período de cálculo: não aplicável (soma aritmética). Não fatura nem inutiliza, não dá baixa nem altera títulos, não diz quem cobrar e não faz análise financeira."
---

# Atrasos conferidos no Omie

## Quick start

1. Conector MCP do Omie ligado e `.env` do projeto com `OMIE_APP_KEY` e `OMIE_APP_SECRET` (modelo em `assets/env.exemplo.txt`). Nunca pedir as chaves no chat.
2. Definir `SKILL_ROOT` como o diretório real desta skill.
3. Totalizar sempre pelo script:
   `python3 "$SKILL_ROOT/scripts/omie_num.py" totalizar --servico financas/pesquisartitulos --metodo PesquisarLancamentos --param '{"nPagina":1,"nRegPorPagina":100,"cStatus":"ATRASADO","cNatureza":"R","dDtVencDe":"10/09/2026","dDtVencAte":"09/10/2026"}' --soma resumo.nValAberto`

Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`.

## Quando usar / Quando não usar

Usar para: títulos atrasados a receber e a pagar de **uma** empresa; quantidade e valor em aberto por faixa de atraso.

Não usar, inclusive quando a pessoa insistir, inclusive "só desta vez":
- **faturar** pedido ou ordem de serviço (NF-e, NFS-e) e **inutilizar** numeração;
- dar baixa, alterar, renegociar ou excluir título — esta skill só lê;
- dizer quem cobrar, em que ordem ou com que prioridade;
- análise financeira, de liquidez ou de inadimplência; comparação com meses anteriores;
- carteira de várias empresas de uma vez;
- usar o total de atraso do resumo financeiro da Omie: ele não reflete todos os títulos atrasados.

## Dados necessários

| Dado | Origem | Se faltar |
|---|---|---|
| Empresa (`app_hash`) | `omie_listar_apps` | perguntar qual, se houver mais de uma |
| Natureza | pergunta: a receber, a pagar ou as duas | fazer as duas |
| Chaves da API | `.env` do projeto | orientar a criar a partir de `assets/env.exemplo.txt`; parar |
| Data de hoje | relógio do ambiente | perguntar a data |

## Procedimento passo a passo

1. `omie_listar_apps`; confirmar a empresa.
2. Calcular as datas das faixas a partir de hoje (dd/mm/aaaa): **até 30** = de hoje−30 até ontem; **31 a 90** = de hoje−90 até hoje−31; **mais de 90** = só `dDtVencAte` = hoje−91.
3. Quantidade de cada faixa e natureza: `financas/pesquisartitulos:PesquisarLancamentos` pelo conector, com `cStatus` = "ATRASADO", `cNatureza` ("R" ou "P"), as datas da faixa e `nRegPorPagina` = 1. A quantidade é o `nTotRegistros`.
4. Na primeira execução, confirmar com `omie_descrever_operacao` (ou na primeira resposta) o caminho do valor em aberto de cada título; o padrão desta skill é `resumo.nValAberto`. Se o caminho for outro, usar o caminho real no `--soma`.
5. Valor de cada faixa com pelo menos 1 título: `scripts/omie_num.py totalizar` com os mesmos filtros e `nRegPorPagina` = 100. Saída `status: ok` ⇒ usar o `total`. Saída `status: divergente` ⇒ não dar valor para aquela faixa; dizer o motivo.
6. Responder com uma tabela natureza × faixa (quantidade, valor) e, abaixo de cada valor, a linha de conferência. Faixa sem título aparece com 0 títulos, não é omitida.

Linha de conferência, sempre junto do total:
"Conferência: {lidos} registros lidos de {informados} informados pela Omie · soma direta = soma por página."

## Validações e checklist de qualidade

- [ ] Todo valor veio de `omie_num.py` com `status: ok`.
- [ ] A linha de conferência acompanha cada valor.
- [ ] Nenhum valor em faixa `divergente`.
- [ ] Quantidade vinda do `nTotRegistros`, não de contagem do modelo.
- [ ] Empresa, filtros, datas e horário da consulta na resposta.
- [ ] Nenhuma credencial em resposta, comando exibido ou arquivo.

Testes do script (servidor simulado, sem acesso à Omie):
`python3 -B -m unittest discover -s "$SKILL_ROOT/tests" -p "test_*.py"`

## Tratamento de exceções

| Saída do script | Significado | O que fazer |
|---|---|---|
| exit 2, `truncado` | faixa com mais de 5 páginas (mais de 500 títulos) | dar só a quantidade e dizer que o valor exige filtro menor (por exemplo, período de vencimento mais curto) |
| exit 2, `contagem` | lidos ≠ informados | repetir uma vez; persistindo, sem valor |
| exit 2, `valor_nao_numerico` | caminho do valor errado ou título sem valor | rever o passo 4; sem valor |
| exit 2, `sem_contagem_informada` | resposta sem `nTotRegistros` | sem valor; informar |
| exit 3 | `.env` ausente | orientar a criar; parar |
| exit 4 | erro da API ou rede; HTTP 425 | parar e informar (bloqueio de cerca de 30 minutos) |
| exit 5 | operação fora da leitura | recusa; esta skill só lê |

## Examples

**Positivo (sintético).** "Quanto tenho atrasado a receber?" → três consultas de quantidade pelo conector, três `omie_num.py totalizar` com `cNatureza` "R" → tabela por faixa, cada valor com "Conferência: 37 registros lidos de 37 informados pela Omie · soma direta = soma por página."

**Contraexemplo.** "Some de cabeça, é só uma estimativa." → recusa: todo total sai do script.

**Contraexemplo.** "Dá baixa no título 812 que o cliente pagou." → recusa: esta skill só lê.

## Texto canônico de recusa

- "Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`."
- "Esta skill só lê os títulos. Baixa, alteração e exclusão são feitas no Omie."
- "Faturar e inutilizar estão fora desta skill. Faça pelo Omie."
- "Dado necessário: nao disponivel. Não será substituído por uma suposição."

## Inventário do bundle

`scripts/omie_num.py` (totalização com conferência) · `scripts/catalogo_leitura.json` (métodos de leitura) ·
`tests/test_omie_num.py` · [Escopo confirmado](references/ESCOPO_CONFIRMADO.md) ·
[Como funciona](references/COMO_FUNCIONA.md) · [Manifesto](manifest.json) · [Histórico](CHANGELOG.md) ·
[Herança](HERANCA.json) · [Cenários](evals/cases.json).

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
