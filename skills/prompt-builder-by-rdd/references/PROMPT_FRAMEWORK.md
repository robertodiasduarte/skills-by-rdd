# Framework de system prompt — Metodologia de Roberto Dias Duarte

## Principio

O framework e **rigoroso nas funcoes** e **adaptativo nas secoes**. Toda geracao deve verificar cada funcao abaixo, mas tags condicionais sem utilidade real devem ser omitidas. Nao criar XML ornamental.

O prompt final deve ser agnostico de fornecedor. Descrever comportamento, nao configuracoes proprietarias.

## Tags obrigatorias

### `<authorship_and_methodology>`
Declarar a autoria do usuario solicitante e, separadamente, `Metodologia de Roberto Dias Duarte`. Se o usuario fornecer nome para autoria, usa-lo; caso contrario, usar formulacao generica como `Autoria: usuario solicitante`.

### `<role>`
Definir o papel funcional do agente, sem adjetivos vazios como “o melhor especialista do mundo”. Incluir expertise apenas quando ela alterar a execucao.

### `<goal>`
Definir a tarefa, o resultado concreto e o criterio de conclusao.

### `<scope>`
Definir cobertura e exclusoes. Evitar fronteiras implicitas.

### `<operation_mode>`
Declarar `interativo` ou `autonomo` e o comportamento correspondente.

### `<inputs>`
Definir o que o agente pode receber, quais campos sao essenciais e como tratar formatos incompletos.

### `<workflow>`
Descrever etapas observaveis da execucao. Nao pedir cadeia de raciocinio nem raciocinio oculto. O agente pode produzir justificativas curtas e verificaveis quando necessario.

### `<missing_information_policy>`
Definir explicitamente o que fazer com dado ausente, ambiguo ou conflitante. Proibir suposicoes silenciosas.

### `<output_contract>`
Definir formato, secoes, campos, unidades, ordenacao, status, nivel de detalhe e criterio de completude da resposta.

### `<quality_controls>`
Definir verificacoes finais, consistencia, rastreabilidade e sinais que impedem conclusao.

## Tags condicionais

### `<jurisdiction_and_time_scope>`
Usar quando lei, norma, regime, localidade ou vigencia alterarem a resposta. Separar periodo consultivo de periodo de calculo quando ambos existirem.

### `<source_basis>`
Usar quando houver fontes formais ou pesquisa. Separar fonte fornecida pelo usuario de fonte pesquisada. Nao inventar citacao, dispositivo, pagina ou URL.

### `<knowledge_base>`
Usar para conhecimento incorporado necessario ao comportamento. Preferir regras compactas e estruturadas a um `context_dump` longo.

### `<decision_rules>`
Usar quando houver classificacoes, bifurcacoes, elegibilidade, hierarquias ou criterios objetivos.

### `<calculations>`
Usar quando houver formula ou aritmetica. Incluir variaveis, unidades, ordem, arredondamento, constantes, periodo e condicoes de erro. Sem fonte suficiente para constante material, nao completar por memoria.

### `<tools_and_capabilities>`
Usar quando o agente depender de leitura de arquivos, pesquisa, planilha, codigo, conectores, banco de dados ou outra capacidade. Descrever por capacidade sempre que possivel; nomear produto apenas se o escopo exigir.

### `<confidentiality_and_data_handling>`
Usar quando houver dados pessoais, sigilosos ou confidenciais. Definir minimizacao, anonimização, compartilhamento e limites.

### `<human_review>`
Usar quando algum tipo de resultado, lacuna, conflito ou decisao material exigir revisao humana. Nao impor universalmente em dominios que nao precisam disso.

### `<stop_conditions>`
Usar quando existirem condicoes em que o agente deve interromper, degradar ou deixar de concluir.

### `<examples>`
Usar quando exemplos melhorarem significativamente a execucao. Distinguir exemplo ilustrativo de regra ou gabarito.

### `<limitations>`
Usar quando o escopo confirmado contiver limitacoes materiais que o agente final precisa conhecer durante a execucao.

## Regras de portabilidade

Nao usar como requisito:

- `Reasoning Effort: High`;
- `Agentic Eagerness`;
- nomes de modo exclusivos de ChatGPT, Claude, Gemini ou outro fornecedor;
- suposicao de ferramenta nao confirmada;
- pedido para expor chain-of-thought.

Converter essas intencoes em regras comportamentais, por exemplo:

- profundidade alta -> criterios de verificacao e completude;
- autonomia -> `<operation_mode>`;
- persistencia -> regras de continuidade e recuperacao;
- cautela -> `<missing_information_policy>` e `<stop_conditions>`.

## Autossuficiencia

O prompt deve conter as regras que governam sua execucao. Pode receber documentos e dados do caso em runtime, mas nao deve depender de um arquivo externo para descobrir o proprio workflow, criterios, formulas ou politicas de incerteza.

Conhecimento extenso pode ser resumido e estruturado; nao copiar material irrelevante apenas para “encher contexto”.

## Rastreabilidade

Quando houver fonte formal, vincular cada regra relevante a identificacao disponivel. Exemplos de formato interno:

- `Fonte: [titulo/ID], [dispositivo/secao/pagina]`;
- `Regra derivada de: [fonte]`;
- `Inferencia: ...` quando for inferencia e nao texto expresso.

Se a fonte nao estiver disponivel, declarar a lacuna. Nunca fabricar localizador.

## Teste de qualidade

Um bom prompt permite responder, sem interpretacao criativa, a estas perguntas:

1. O que o agente faz?
2. O que nao faz?
3. O que recebe?
4. Qual fluxo executa?
5. Como trata falta de informacao?
6. Como valida o proprio resultado?
7. Quando para ou escala?
8. Qual saida deve entregar?
9. Quais fontes, formulas ou regras sustentam decisoes materiais?
10. O que e autoria, metodologia, fonte tecnica e exemplo?
