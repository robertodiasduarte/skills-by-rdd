# Como funciona a Prompt Builder by RDD

A skill transforma uma ideia, processo ou conjunto de materiais em um `system prompt` profissional. Ela nao comeca escrevendo o prompt: primeiro reduz ambiguidade e fecha um contrato observavel.

## Fluxo

1. **Descoberta:** entende tarefa, contexto, resultado e criterio de pronto.
2. **Coleta:** pede somente materiais relevantes e identifica lacunas.
3. **Contrato:** define autonomia, evidencia, prioridade, estados, numeros e limites quando aplicaveis.
4. **Consolidacao:** apresenta um escopo versionado e legivel.
5. **Confirmacao:** aguarda autorizacao explicita do usuario.
6. **Geracao:** constroi um unico system prompt contract-first, portatil e enxuto.
7. **Validacao:** verifica evidencia, estabilidade, escopo, dados, numeros e contrato de saida.
8. **Entrega:** fornece o prompt e um relatorio externo curto.

## Diferencial do metodo

O metodo separa coisas que prompts fracos costumam misturar:

- instrucao que governa o agente;
- regra que define decisao;
- evidencia ou fonte que sustenta a regra;
- dado variavel do caso;
- exemplo que ilustra comportamento;
- saida que o agente precisa produzir.

Tambem separa autonomia de cobertura de autonomia de julgamento. O agente pode continuar o lote sem abandonar itens claros, mas nao converte ausencia de evidencia em conclusao definitiva.

## Estrutura do prompt

As instrucoes ficam normalmente em Markdown ou secoes textuais claras. XML ou delimitadores equivalentes sao usados quando melhoram a separacao de dados, documentos e exemplos.

O prompt deve conter o contrato de comportamento. Corpus, normas e bases extensas nao precisam ser copiados integralmente quando puderem ser fornecidos como base ou dados de runtime.

## Uso em areas diferentes

Em marketing, o brainstorm pode concentrar publico, posicionamento, canais, evidencia do briefing, tom e criterios de campanha.

Em uma tarefa tributaria, pode acrescentar jurisdicao, vigencia, normas, prioridade de fontes, tabelas, formulas, arredondamento e mecanismo de validacao.

Em contabilidade, pode definir evidencia minima, estados fechados, regra de continuidade do lote e separacao entre julgamento do LLM e aritmetica conferida.

A arquitetura e a mesma; o rigor adicional aparece somente quando o dominio exige.
