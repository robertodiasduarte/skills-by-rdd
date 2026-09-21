# Notas de migracao

## Origem

A linhagem comecou em `prompt-builder`, que produzia prompts em XML e possuia integracao SDD. A versao 3.0 removeu SDD, adicionou brainstorm, gate, portabilidade, seguranca e suporte global, mas manteve XML como estrutura principal e uma ideia ampla de autossuficiencia.

## Versao 4.0 - mudanca de arquitetura

A versao 4.0 preserva a governanca da 3.0 e altera o framework de geracao para **contract-first + data-delimited + evidence-driven**.

### Preservado

- brainstorm progressivo;
- gate de escopo versionado;
- um unico system prompt como artefato principal;
- autoria do usuario e metodologia RDD separadas;
- pesquisa somente com autorizacao;
- seguranca documental;
- cinco gavetas RDD;
- relatorio externo de fontes, lacunas e limitacoes;
- ausencia de chain-of-thought solicitado.

### Alterado

- XML deixou de ser envelope principal obrigatorio;
- Markdown/secoes textuais viraram estrutura padrao do contrato;
- XML passou a ser preferido como delimitador de dados, documentos e exemplos;
- autossuficiencia passou a significar contrato de comportamento completo, nao copia integral de corpus;
- evidencia e prioridade de fontes passaram a ser componentes explicitos quando pertinentes;
- autonomia passou a distinguir cobertura de julgamento;
- regra de nao expandir escopo foi fortalecida;
- estados fechados e tabelas de decisao passaram a ser preferidos quando reduzem variancia;
- calculos materiais passaram a exigir definicao de mecanismo de validacao quando disponivel;
- recomendacoes de configuracao proprietaria, quando uteis, ficam apenas no relatorio externo;
- testes passaram a incluir estabilidade do prompt produzido.

### Continua removido

- toda integracao SDD;
- `ReasoningSteps` como convite a raciocinio interno exposto;
- `context_dump` monolitico como arquitetura padrao;
- configuracoes proprietarias dentro do prompt portatil;
- anatomia fixa com secoes vazias ou ornamentais.
