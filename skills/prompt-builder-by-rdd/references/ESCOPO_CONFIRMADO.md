# Escopo confirmado — PB-RDD-001 V1

Status: confirmado pelo usuario apos apresentacao do resumo versionado.

## Objetivo

Criar uma nova versao independente da antiga `prompt-builder`, denominada **Prompt Builder by RDD**, para construir um unico `system prompt` profissional por meio de brainstorm progressivo, coleta de materiais, consolidacao de escopo, confirmacao explicita, geracao e validacao.

## Publico

Principalmente profissionais e equipes. Uso frequente esperado nas areas contabil, tributaria, trabalhista e juridica, mas sem restricao de dominio. A skill tambem deve atender marketing, vendas, RH, tecnologia, educacao, operacoes e outros contextos.

## Jurisdicao e idioma

Cobertura global. Quando jurisdicao, autoridade, regime ou vigencia alterarem o comportamento do prompt, esses elementos devem ser definidos no brainstorm.

Usar por padrao o idioma do usuario.

## Cobertura aprovada

1. Brainstorm progressivo, uma pergunta principal por vez.
2. Um unico `system prompt` como artefato principal.
3. Framework XML semantico, rigoroso nas funcoes e adaptativo nas secoes.
4. Modo de operacao obrigatoriamente definido como `interativo` ou `autonomo`.
5. Coleta das cinco gavetas RDD quando pertinentes: Lei/norma, Tabela, Caso, Conta/regra e Base.
6. Pesquisa externa somente com autorizacao expressa.
7. Tratamento adicional de jurisdicao, vigencia, calculos, fontes, seguranca e revisao quando o dominio exigir.
8. Relatorio externo curto com fontes, lacunas, limitacoes e validacao.

## Exclusoes aprovadas

1. Sem SDD.
2. Sem arquitetura multiagente obrigatoria.
3. Sem dependencia de um fornecedor de IA.
4. Sem pesquisa silenciosa.
5. Sem invencao de leis, numeros, fontes, regras ou capacidades.
6. Sem transformar exemplos nao validados em norma.
7. Sem exigir exposicao de raciocinio interno.
8. Sem gerar antes do gate de confirmacao.

## Materiais usados na concepcao

- Arquivo `prompt-builder.zip`, versao anterior, usado como base de migracao.
- Dois exemplos de prompts contabeis fornecidos em conversa, usados apenas como referencia de estrutura, profundidade e comportamento.

Os exemplos contabeis **nao** sao gabaritos normativos e seu conteudo profissional nao e presumido como validado.

## Materiais ausentes

Caso real/gabarito profissional validado: `nao_disponivel`.

A ausencia nao bloqueia a skill. Casos sinteticos podem ser usados para teste comportamental, desde que rotulados como sinteticos e nunca tratados como prova normativa.

## Regras aprovadas

- O prompt final deve ser autossuficiente quanto as regras de execucao.
- Tags XML nao aplicaveis podem ser omitidas.
- A autoria do prompt gerado pertence ao usuario.
- A metodologia deve ser identificada separadamente como `Metodologia de Roberto Dias Duarte`.
- No modo interativo, dado essencial ausente gera pergunta minima ao usuario.
- No modo autonomo, dado essencial ausente e registrado sem suposicao e, quando material, encaminhado para revisao humana.
- Lacunas nao bloqueiam automaticamente a geracao, mas devem ser expostas com impacto.
- Quando houver fundamentos formais, o prompt deve orientar sua indicacao quando pertinente, sem inventar citacoes.
- Quando houver dados pessoais ou confidenciais, a skill deve emitir alerta de seguranca antes de incentivar novos uploads sensiveis.

## Seguranca

O alerta deve recomendar que o usuario avalie ambiente empresarial/organizacional adequado ao risco e controles pertinentes, como SOC 2, ISO 27001/27701, DPA, retencao, uso de dados para treinamento, criptografia, controle de acesso, SSO/MFA, residencia de dados e legislacao aplicavel. Nenhuma certificacao isolada deve ser apresentada como garantia de conformidade.

## Pesquisa

Desativada por padrao. Quando autorizada, diferenciar fonte pesquisada de material fornecido e nao enviar acervo privado a terceiros.

## Perfil efetivo

Meta-operacional. A skill constroi prompts; nao executa diretamente calculos, pareceres, analises profissionais ou outras tarefas do processo descrito.

## Criterios de aceite

- pacote instalavel com `SKILL.md` valido;
- nome `prompt-builder-by-rdd` e display name `Prompt Builder by RDD`;
- ausencia completa de integracao SDD;
- framework sem parametros proprietarios como `Reasoning Effort`;
- um unico prompt + relatorio externo;
- gate explicito antes da geracao;
- autoria do prompt atribuida ao usuario;
- pesquisa e seguranca conforme regras acima;
- casos de avaliacao positivos e negativos incluidos;
- pacote final validado localmente e entregue como `skill.zip`.
