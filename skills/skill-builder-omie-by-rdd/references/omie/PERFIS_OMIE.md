# Perfis Omie — Operador e Conferidor

O MCP passa a resposta da Omie pelo contexto do modelo. Somar dentro do contexto é aritmética do modelo, e é aí que
número se corrompe. Por isso a skill gerada tem um de dois perfis.

## As perguntas (uma por mensagem, antes de nomear o perfil)

1. "Sua skill precisa somar, contar ou comparar valores de vários registros, ou só mostrar o que o Omie devolve?"
2. "Você roda Python no seu computador, por exemplo no Claude Code, com acesso à internet?"
3. "É uma empresa ou uma carteira de empresas?" (carteira ⇒ `omie_executar_em_varias`)
4. "No conector do Omie, `omie_executar` está como 'pedir aprovação'?" (só se houver escrita)

Contar registros pelo campo que a API informa (`nTotRegistros`) **não** é somar: serve aos dois perfis.

## Derivação (o modelo não escolhe)

| `mcp_disponivel` | precisa somar | Python com rede | Perfil |
|---|---|---|---|
| sim | sim | sim | **conferidor** |
| qualquer outro caso | | | **operador** |

Precisa somar mas não roda Python ⇒ operador, com a lacuna "totalização exige Claude Code" registrada no escopo.
Sem conector ⇒ operador + `pending: nao_exercida_contra_omie`.

## Registro

`perfil_omie.json` ao lado do escopo (modelo em `assets/omie/perfil_omie.template.json`):

```json
{"schema": 1, "totaliza": true, "executa_python_com_rede": true, "perfil": "conferidor",
 "multi_empresa": false, "aprovacao_por_ferramenta": "declarada_sim", "mcp_disponivel": true}
```

O escopo recebe em `restricoes` a linha que o lint calcula:

```bash
python3 "$SKILL_ROOT/scripts/lint_bundle_omie.py" --restricao perfil_omie.json
```

Mudar o perfil muda essa linha, que muda o escopo, que invalida a confirmação no `scope_gate.py`.
No escopo: `area` = `contabil`, `perfil_pedido` = `operacional`, `perfil_efetivo` = `C`, `periodo_calculo` =
`nao aplicavel` e `caminhos_calculo` vazio — somar registros não é cálculo profissional.

## O que cada perfil entrega

| | Operador | Conferidor |
|---|---|---|
| Onde roda | Claude com conector (web, desktop, Code); ChatGPT por texto, sem teste | Claude Code (ou outro ambiente com Python e rede) + conector |
| Arquivos `.py` | nenhum | `scripts/omie_num.py`, `tests/test_omie_num.py` (cópias exatas dos assets) |
| Pedido de soma | recusa literal: "Este perfil não totaliza registros. Para somar com conferência, gere o perfil Conferidor." | "Nunca some, conte ou compare valores de cabeça: todo total sai do `scripts/omie_num.py`." |
| Total na resposta | — | com a linha "Conferência: N registros lidos de N informados pela Omie · soma direta = soma por grupo." |
| Escrita | gate literal, se o escopo tiver escrita | não grava nada nesta versão (só leitura) |
