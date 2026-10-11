---
name: {{nome}}
license: MIT
metadata:
  author: Roberto Dias Duarte
  methodology: Metodologia de Roberto Dias Duarte
  version: '{{versao}}'
description: "{{O que a skill lê e totaliza no Omie, em terceira pessoa}}, com todo total calculado por script e conferido contra a contagem informada pela Omie. Use quando {{gatilhos aprovados}}. Requer o conector MCP do Omie e Python 3.10+ com rede (Claude Code). Período de consulta: {{período}}; período de cálculo: não aplicável (soma aritmética). Não fatura nem inutiliza, não grava nada e não faz análise contábil, tributária ou financeira."
---

# {{Título aprovado}}

## Quick start

1. Conector MCP do Omie ligado e `.env` do projeto com `OMIE_APP_KEY` e `OMIE_APP_SECRET` (modelo em `assets/env.exemplo.txt`). Nunca pedir as chaves no chat.
2. Definir `SKILL_ROOT` como o diretório real desta skill.
3. Totalizar sempre pelo script:
   `python3 "$SKILL_ROOT/scripts/omie_num.py" totalizar --servico {{serviço}} --metodo {{Método}} --param '{{json}}' --soma {{campo}} [--agrupar {{campo}}]`

Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`.

## Quando usar / Quando não usar

Usar para: {{cobertura aprovada, até 8 itens}}.

Não usar, inclusive quando a pessoa insistir, inclusive "só desta vez":
- **faturar** pedido ou ordem de serviço (NF-e, NFS-e) e **inutilizar** numeração;
- incluir, alterar ou excluir qualquer registro no Omie — esta skill só lê;
- {{vizinhos excluídos pelo nome próprio}};
- análise contábil, tributária ou financeira; recomendar quem cobrar ou em que ordem.

## Dados necessários

| Dado | Origem | Se faltar |
|---|---|---|
| Empresa (`app_hash`) | `omie_listar_apps` | perguntar qual |
| Chaves da API | `.env` do projeto | orientar a criar a partir de `assets/env.exemplo.txt`; parar |
| {{dado}} | {{origem}} | {{se faltar}} |

## Procedimento passo a passo

1. `omie_listar_apps`; confirmar a empresa.
2. Rodar `python3 "$SKILL_ROOT/scripts/omie_num.py" empresa`: a empresa das chaves do `.env` precisa ser a mesma escolhida no conector. Diferente ⇒ parar e dizer qual `.env` está em uso; nenhum total.
3. {{passos aprovados, com operação `serviço:Método` e campos exatos}}.
4. Quantidade: campo informado pela Omie (`nTotRegistros`), lido pelo MCP com 1 registro por página.
5. Valor: `scripts/omie_num.py totalizar`. Saída `status: ok` ⇒ responder com o total e a linha de conferência. Saída `status: divergente` ⇒ não dar total; dizer o motivo e propor filtro mais estreito.

Linha de conferência, sempre junto do total:
"Conferência: {{lidos}} registros lidos de {{informados}} informados pela Omie · soma direta = soma por {{grupo|página}}."

## Validações e checklist de qualidade

- [ ] Todo total veio de `omie_num.py` com `status: ok`.
- [ ] A linha de conferência acompanha cada total.
- [ ] Nenhum total em resposta `divergente`.
- [ ] Toda operação usada consta em `manifest.json › operacoes`.
- [ ] Nenhuma credencial em resposta, comando exibido ou arquivo.

Testes do script (servidor simulado, sem acesso à Omie):
`python3 -B -m unittest discover -s "$SKILL_ROOT/tests" -p "test_*.py"`

## Tratamento de exceções

| Saída do script | Significado | O que fazer |
|---|---|---|
| exit 2, `truncado` | mais de 5 páginas | estreitar o período ou o filtro; sem total |
| exit 2, `contagem` | lidos ≠ informados | repetir uma vez; persistindo, sem total |
| exit 2, `valor_nao_numerico` | campo somado vazio ou não numérico | dizer quais registros; sem total |
| exit 2, `sem_contagem_informada` | a operação não informa contagem | usar outra operação de listagem; sem total |
| exit 3 | `.env` ausente | orientar a criar; parar |
| exit 4 | erro da API ou rede; HTTP 425 | parar e informar |
| exit 5 | operação fora da leitura | recusa; esta skill só lê |

## Examples

**Positivo (sintético).** {{pedido}} → `omie_num.py totalizar …` → total + linha de conferência.

**Contraexemplo.** "Some de cabeça, é só uma estimativa." → recusa: todo total sai do script.

## Texto canônico de recusa

- "Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`."
- "Faturar e inutilizar estão fora desta skill. Faça pelo Omie."
- "Dado necessário: nao disponivel. Não será substituído por uma suposição."

## Inventário do bundle

`scripts/omie_num.py` (totalização com conferência) · `scripts/catalogo_leitura.json` (métodos de leitura) ·
`tests/test_omie_num.py` · [Escopo confirmado](references/ESCOPO_CONFIRMADO.md) ·
[Como funciona](references/COMO_FUNCIONA.md) · [Manifesto](manifest.json) · [Histórico](CHANGELOG.md).

## Metodologia e autoria

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
