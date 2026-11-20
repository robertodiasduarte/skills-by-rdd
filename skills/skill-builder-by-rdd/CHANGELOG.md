# Histórico

## 1.2.0 — 20/11/2026

A skill gerada pertence ao usuário: autor e licença passam a ser perguntados no
brainstorm e registrados no resumo do escopo e no registro de brainstorm, em vez de fixados em
Roberto Dias Duarte e MIT. O crédito à metodologia (`metadata.methodology` e a seção
`## Metodologia e autoria`) continua por padrão, aparece no resumo do escopo e pode
ser removido a pedido. A descrição passa a declarar isso.
A própria meta-skill continua MIT, de autoria de Roberto Dias Duarte.
Os 15 cenários de conversa saem do pacote distribuído e passam a morar no
repositório em pasta `evals` do repositório, arquivo `skill-builder-by-rdd/cases.json`: eles citam frases de
injeção como casos de teste, e o pacote não precisa delas para funcionar.
Nenhum script ou teste mudou.

## 1.1.2 — 10/10/2026

"Quando não usar" passa a nomear a `skill-builder-omie-by-rdd`: skill que opera o ERP
Omie pelo MCP oficial é gerada pela filha especializada, não por esta meta-skill.
Acrescenta o cenário negativo `neg-omie-mcp-vai-para-filha` (15 cenários). Nenhum
script, teste, referência ou modelo mudou.

## 1.1.1 — 20/09/2026

Renomeia a meta-skill para **Skill Builder by RDD**. O identificador técnico passa a
ser `skill-builder-by-rdd`, a pasta raiz do bundle acompanha o novo identificador e
o nome de exibição do adaptador OpenAI também é atualizado. As regras de autoria,
licença MIT e atribuição da metodologia de Roberto Dias Duarte permanecem inalteradas.

## 1.1.0 — 20/09/2026

Adiciona `metadata.author: Roberto Dias Duarte` e `license: MIT` à meta-skill e torna
obrigatória a mesma identificação em toda skill-filha gerada. Registra também
`metadata.methodology: Metodologia de Roberto Dias Duarte` e exige no corpo de cada
skill gerada a declaração literal: “Esta skill foi construída com a metodologia de
Roberto Dias Duarte.”

## 1.0.0 — 20/09/2026

Meta-skill inicial derivada da documentação RDD fornecida pelo usuário.
Inclui entrevista progressiva, cinco gavetas, exemplos e contraexemplos,
escopo versionado, confirmação obrigatória, perfis e regras de cálculo verificado.
Acrescenta modos de execução por capacidades, gate local de consistência, lint básico,
modelos, testes locais e cenários comportamentais ainda não executados em provedores.

As diferenças em relação ao padrão RDD estão declaradas em references/RASTREABILIDADE.md.
