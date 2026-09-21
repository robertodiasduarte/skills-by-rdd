# Escopo confirmado - PB-RDD-001 V2

Status: confirmado pelo usuario apos apresentacao do resumo versionado.

## Objetivo

Atualizar a **Prompt Builder by RDD** para a versao 4.0, mantendo brainstorm, gate e governanca, mas alterando o framework central de `XML-first` para **contract-first + data-delimited + evidence-driven**.

## Publico

Principalmente profissionais e equipes, sem restricao de dominio. A skill atende contabilidade, tributario, trabalhista, juridico, marketing, vendas, RH, tecnologia, educacao, operacoes e outros contextos.

## Jurisdicao e idioma

Cobertura global. Quando jurisdicao, autoridade, regime ou vigencia alterarem o comportamento do prompt, esses elementos devem ser definidos no brainstorm.

Usar por padrao o idioma do usuario.

## Cobertura aprovada

1. Brainstorm progressivo, uma pergunta principal por vez.
2. Um unico `system prompt` como artefato principal.
3. Estrutura principal em Markdown/secoes textuais; XML ou delimitadores equivalentes para dados, documentos, exemplos e payloads quando uteis.
4. Filosofia de contrato: resultado, contexto, limites, criterio de pronto e verificacao; sem roteiro de raciocinio interno.
5. Modo de operacao `interativo` ou `autonomo`, com autonomia na cobertura e cerca no julgamento.
6. Contrato de evidencia e prioridade de fontes quando o processo exigir.
7. Estados fechados e tabelas de decisao quando reduzirem variancia.
8. Separacao entre julgamento do LLM e validacao numerica deterministica quando houver numeros materiais.
9. Cinco gavetas RDD quando pertinentes: Lei/norma, Tabela, Caso, Conta/regra e Base.
10. Pesquisa externa somente com autorizacao expressa.
11. Relatorio externo curto com fontes, lacunas, limitacoes, validacao e recomendacoes de deployment quando pertinentes.

## Exclusoes aprovadas

1. Sem SDD.
2. Sem arquitetura multiagente obrigatoria.
3. Sem dependencia de fornecedor de IA.
4. Sem XML obrigatorio como envelope principal.
5. Sem pesquisa silenciosa.
6. Sem invencao de leis, numeros, fontes, regras, evidencias ou capacidades.
7. Sem transformar exemplos nao validados em norma.
8. Sem exigir exposicao de raciocinio interno.
9. Sem expansao silenciosa de escopo ou "dourar o ouro".
10. Sem afirmar conferencia numerica externa quando ela nao ocorreu.
11. Sem gerar antes do gate de confirmacao.

## Materiais usados na concepcao

- `prompt-builder.zip`, versao anterior, usado como base de migracao.
- Dois exemplos de prompts contabeis fornecidos em conversa, usados apenas como referencia de estrutura, profundidade e comportamento.
- Documento fornecido pelo usuario `Melhores praticas comuns - Fable e Astra para prompts contabeis`, usado para revisar a arquitetura contract-first, evidencia, delimitacao de dados, estados, verificacao numerica e estabilidade.

Os exemplos contabeis nao sao gabaritos normativos e seu conteudo profissional nao e presumido como validado.

## Materiais ausentes

Caso real/gabarito profissional validado: `nao_disponivel`.

A ausencia nao bloqueia a skill. Casos sinteticos podem ser usados para teste comportamental, desde que rotulados como sinteticos e nunca tratados como prova normativa.

## Regras aprovadas

- O prompt final deve ser autossuficiente quanto ao contrato de comportamento, nao necessariamente quanto a um corpus extenso.
- Instrucoes e regras devem ser separadas de dados, documentos e exemplos.
- XML pode ser usado como delimitador de dados, mas nao e estrutura principal obrigatoria.
- A autoria do prompt gerado pertence ao usuario.
- A metodologia deve ser identificada separadamente como `Metodologia de Roberto Dias Duarte`.
- No modo interativo, dado essencial ausente gera pergunta minima ao usuario.
- No modo autonomo, dado essencial ausente e registrado sem suposicao; o restante seguro continua sendo processado.
- Falta de evidencia nao deve virar julgamento definitivo por plausibilidade.
- O agente nao deve ampliar o escopo por iniciativa propria.
- Quando houver conflito de fontes, a prioridade deve ser explicitamente definida para o processo.
- Quando houver estados, preferir enums fechados e criterio de pronto observavel.
- Para numeros materiais, definir formula, responsavel pela aritmetica e mecanismo de validacao quando disponivel.
- Configuracoes proprietarias de fornecedor ficam fora do prompt portatil e podem aparecer apenas no relatorio externo quando pertinentes.
- Quando houver dados pessoais ou confidenciais, emitir alerta de seguranca antes de incentivar novos uploads sensiveis.

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
- framework contract-first, sem XML principal obrigatorio;
- dados de runtime delimitados quando pertinente;
- evidencia, prioridade, estados e criterio de pronto incorporados quando aplicaveis;
- calculos materiais sem alegacao de validacao inexistente;
- parametros proprietarios fora do prompt portatil;
- um unico prompt + relatorio externo;
- gate explicito antes da geracao;
- autoria do prompt atribuida ao usuario;
- pesquisa e seguranca conforme regras acima;
- casos de avaliacao positivos e negativos incluidos;
- pacote final validado localmente e entregue como `skill.zip`.
