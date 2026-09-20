# Notas de migracao da versao anterior

## Origem

A versao anterior se chamava `prompt-builder` e produzia um prompt em XML. Ela continha regras uteis de contrato de saida, dados faltantes, verificacao e formulas, alem de uma integracao SDD especifica.

## Preservado e ampliado

- contrato de saida definido antes de escrever detalhes;
- regras explicitas para contexto ausente;
- formulas estruturadas quando houver calculo;
- verificacao e completude;
- isolamento de material de referencia;
- recuperacao diante de resultado vazio;
- remocao de redundancia;
- uso de XML semantico.

## Removido

- toda integracao SDD;
- qualquer dependencia de workflow SDD;
- `Reasoning Effort`, `Agentic Eagerness` e configuracoes similares;
- `ReasoningSteps` como convite a raciocinio interno exposto;
- `context_dump` monolitico como bloco generico;
- suposicao de que um prompt complexo deve seguir anatomia fixa mesmo quando secoes nao se aplicam.

## Adicionado

- brainstorm obrigatorio e progressivo;
- cinco gavetas RDD para materiais;
- escopo versionado;
- confirmacao explicita antes da geracao;
- modo `interativo` ou `autonomo` obrigatorio;
- autoria do prompt atribuida ao usuario;
- metodologia RDD separada da autoria e das fontes;
- suporte global e multidominio;
- pesquisa externa somente com autorizacao;
- alerta de confidencialidade e seguranca;
- relatorio externo de fontes, lacunas e limitacoes;
- testes comportamentais positivos e negativos.
