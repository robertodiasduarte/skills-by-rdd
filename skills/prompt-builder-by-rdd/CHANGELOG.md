# Changelog

## 4.0.0 - 2026-09-21

- Alterada a arquitetura central de `XML-first` para `contract-first + data-delimited + evidence-driven`.
- Markdown/secoes textuais passaram a ser a estrutura principal recomendada do system prompt.
- XML passou a ser usado preferencialmente como delimitador de dados, documentos, exemplos e payloads.
- Redefinida autossuficiencia: contrato de comportamento completo sem obrigacao de copiar corpus extenso para o system prompt.
- Adicionado contrato de evidencia e prioridade de fontes quando pertinente.
- Refinada autonomia em `cobertura` versus `julgamento`, permitindo continuar lotes sem concluir itens sem evidencia.
- Adicionada regra explicita de nao expandir o escopo ou "dourar o ouro".
- Adicionados estados fechados e tabelas de decisao como mecanismos preferenciais quando reduzem variancia.
- Adicionada politica de calculo material com separacao entre julgamento do LLM e validacao deterministica quando disponivel.
- Configuracoes proprietarias de fornecedor passaram a ser permitidas somente como recomendacoes externas de deployment, nunca dentro do prompt portatil.
- Adicionada recomendacao opcional de segundo passe em contexto limpo para tarefas materiais.
- Ampliados os cenarios de avaliacao de 10 para 18, incluindo qualidade e estabilidade dos prompts produzidos.
- Incorporado como fonte de concepcao o documento fornecido pelo usuario `Melhores praticas comuns - Fable e Astra para prompts contabeis`.

## 3.0.0 - 2026-09-20

- Renomeada a skill para `prompt-builder-by-rdd` / **Prompt Builder by RDD**.
- Removida integralmente a integracao SDD.
- Ampliado o escopo para qualquer dominio, mantendo controles adicionais quando houver regulacao, calculo, jurisdicao ou dados sensiveis.
- Adicionado brainstorm progressivo com uma pergunta principal por vez.
- Adicionado gate de escopo versionado e confirmacao explicita antes da geracao.
- Adicionados modos `interativo` e `autonomo`.
- Criado framework XML semantico na versao 3.0.
- Separada autoria do usuario da `Metodologia de Roberto Dias Duarte`.
- Adicionadas politica de pesquisa, rastreabilidade de fontes e seguranca documental.
- Adicionado relatorio externo de fontes, lacunas e limitacoes.
