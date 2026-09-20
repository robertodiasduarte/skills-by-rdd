# Template adaptativo de saída

Usar este esqueleto como referencia. Manter as tags obrigatorias e remover tags condicionais que nao agreguem funcao real. Substituir todos os colchetes antes da entrega.

```xml
<system_prompt>
  <authorship_and_methodology>
    <authorship>[usuario solicitante ou nome informado]</authorship>
    <methodology>Metodologia de Roberto Dias Duarte</methodology>
  </authorship_and_methodology>

  <role>
    [papel funcional do agente]
  </role>

  <goal>
    [tarefa, resultado concreto e criterio de conclusao]
  </goal>

  <scope>
    <included>[cobertura]</included>
    <excluded>[exclusoes]</excluded>
  </scope>

  <!-- Condicional -->
  <jurisdiction_and_time_scope>
    [jurisdicao, autoridade, periodo consultivo e/ou periodo de calculo]
  </jurisdiction_and_time_scope>

  <operation_mode>
    <mode>[interativo | autonomo]</mode>
    <behavior>[regra correspondente]</behavior>
  </operation_mode>

  <inputs>
    [entradas aceitas, campos essenciais e premissas permitidas]
  </inputs>

  <!-- Condicionais -->
  <source_basis>[fontes e politica de fundamentacao]</source_basis>
  <knowledge_base>[conhecimento incorporado necessario]</knowledge_base>
  <decision_rules>[regras de decisao]</decision_rules>
  <calculations>[formulas, unidades, arredondamento e constantes]</calculations>
  <tools_and_capabilities>[capacidades realmente disponiveis]</tools_and_capabilities>
  <confidentiality_and_data_handling>[regras de dados]</confidentiality_and_data_handling>

  <workflow>
    [etapas observaveis, sem solicitar cadeia de raciocinio]
  </workflow>

  <missing_information_policy>
    [comportamento para ausencia, ambiguidade e conflito]
  </missing_information_policy>

  <!-- Condicionais -->
  <human_review>[pontos que exigem revisao]</human_review>
  <stop_conditions>[quando interromper, degradar ou nao concluir]</stop_conditions>
  <examples>[exemplos ilustrativos claramente rotulados]</examples>
  <limitations>[limitacoes materiais conhecidas]</limitations>

  <quality_controls>
    [verificacoes antes de concluir]
  </quality_controls>

  <output_contract>
    [formato final, secoes, campos, status, unidades e completude]
  </output_contract>
</system_prompt>
```

## Relatorio externo

Depois do bloco XML, entregar um relatorio curto fora do prompt:

```text
Relatorio de geracao
- Fontes fornecidas pelo usuario: ...
- Fontes pesquisadas com autorizacao: ...
- Lacunas: ...
- Limitacoes: ...
- Validacao realizada: ...
```

Nao inserir esse relatorio dentro de `<system_prompt>`.
