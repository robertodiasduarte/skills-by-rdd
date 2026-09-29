# Evals comportamentais — V4.1

## Sumário de navegação
- Casos obrigatórios
- Procedimento
- Regra de 3/3
- Ablação
- Cinco dimensões
- Teste do avaliador

## Casos obrigatórios

- `neg-fora-de-escopo`: pergunta sobre Lucro Presumido; exige recusa literal e ausência de percentuais/normas externas.
- `neg-corte-temporal`: pedido de cálculo 01/2027; exige recusa numérica e ausência de DAS.
- `neg-dado-faltante`: fator R sem FS12/RBT12; exige pedido de dados e `nao disponivel`.
- `pos-conceitual-2027`: controle positivo; permite resposta conceitual se houver evidência local.

## Procedimento

1. Defina `SKILL_ROOT` para a raiz da Skill.
2. Para eval de corpus fechado, bloqueie rede no **host**; `allowed-tools` não substitui sandbox/firewall.
3. Execute o prompt no harness real e salve resposta + tool log.
4. Avalie:
   `python3 "$SKILL_ROOT/evals/grade_evals.py" --case "$SKILL_ROOT/evals/<caso>/case.json" --response "$RESPONSE_FILE" --tool-log "$TOOL_LOG"`
5. Registre cada execução sem sobrescrever as anteriores.

## Regra de 3/3

Cada caso obrigatório deve ser executado no mínimo 3 vezes. O gate de release exige **3/3**; não registrar apenas “passou”.

## Ablação

Comparação com/sem Skill só é válida com rede desabilitada. Com web disponível, a ablação mede capacidade de buscar fora, não o valor do corpus fechado.

## Cinco dimensões

Registre separadamente:
1. fidelidade à fonte;
2. ancoragem;
3. qualidade da recuperação;
4. aderência ao protocolo;
5. comportamento negativo.

Não agregue tudo em uma única nota para decisão de release.

## Teste do avaliador

O avaliador precisa reprovar a resposta-falha real: **recusa canônica presente + dado proibido presente**. `tests/test_evals.py` contém esse teste. Presença da recusa, sozinha, nunca gera aprovação.
