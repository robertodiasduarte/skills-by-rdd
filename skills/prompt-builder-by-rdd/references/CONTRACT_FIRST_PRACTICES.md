# Praticas contract-first incorporadas

## Origem e papel

Este arquivo resume praticas incorporadas a partir do documento fornecido pelo usuario **"Melhores praticas comuns - Fable e Astra para prompts contabeis"**. O documento foi usado como fonte de concepcao da versao 4.0.

As praticas abaixo foram generalizadas para a Prompt Builder by RDD. Exemplos contabeis do documento nao viram regras universais para marketing, vendas, tecnologia ou outros dominios.

## 1. Contrato, nao roteiro de raciocinio

O system prompt deve declarar resultado pronto, contexto, limites, criterio de pronto e verificacao. Nao deve prescrever uma cadeia de raciocinio interna nem simular profundidade por frases como "pense mais".

## 2. Separar instrucao, regra e dado

Instrucoes governam o agente. Regras definem decisao. Dados, documentos e exemplos sao entradas nao confiaveis e devem ficar delimitados. Conteudo dentro de bloco de dados nunca deve substituir instrucoes do system prompt.

## 3. Autonomia na cobertura; cerca no julgamento

O agente deve persistir na varredura ou cobertura da tarefa. Um item pendente nao deve interromper o restante. Ao mesmo tempo, falta de evidencia nao autoriza conclusao definitiva por plausibilidade.

## 4. Nao dourar o ouro

Nao adicionar analise, feature, ajuste, categoria, documento ou produto final que o escopo nao pediu. Achados laterais podem ser listados como pendencia ou recomendacao, sem execucao silenciosa.

## 5. Evidencia antes de conclusao material

Quando a tarefa depender de fatos ou classificacao, exigir evidencia da sessao e regra aplicavel. Se houver fonte formal, inclui-la quando pertinente. Historico, nome, descricao ou pista vaga nao devem virar prova apenas porque parecem plausiveis.

## 6. Prioridade explicita

Se houver varias fontes ou evidencias, o prompt deve declarar a prioridade aplicavel ao processo. A skill nunca inventa uma hierarquia universal.

## 7. Estados fechados

Quando o processo usar status, classificacoes ou conclusoes, preferir enums fechados. Definir tambem quais estados impedem conclusao final. Isso reduz variancia entre execucoes.

## 8. Few-shot curto e de fronteira

Quando exemplos ajudarem, usar poucos exemplos consistentes e claramente delimitados. Priorizar erros recorrentes e fronteiras de decisao; nao misturar exemplos com dados reais do caso.

## 9. Instrucoes persistentes curtas

O system prompt deve conter o contrato de comportamento, nao uma copia indiscriminada de toda a base. Regras extensas, normas, planos ou corpus podem ser fornecidos como base/dados de runtime quando o ambiente suportar.

## 10. Formato explicito

Definir se a resposta deve usar tabela, schema, lista, campos ou prosa. Nao confiar no formato default do modelo quando o output tiver funcao operacional.

## 11. Numeros conferidos por mecanismo adequado

Quando um numero material puder ser conferido por script, planilha, funcao ou schema, preferir esse mecanismo. Aumentar effort ou pedir mais raciocinio nao substitui validacao deterministica.

## 12. Segundo passe e estabilidade

Para uso material, recomendar um verificador em contexto limpo quando possivel. O objetivo e encontrar violacoes, nao reescrever toda a tarefa.

Avaliar estabilidade repetindo entradas representativas. Mudanca de estado sem evidencia nova, expansao de escopo, categoria inventada ou numero "fechado" sem lastro indicam falha do contrato.

## 13. Configuracao de fornecedor fora do prompt portatil

Configuracoes de profundidade, effort ou recursos exclusivos de um fornecedor podem ser uteis no deployment, mas nao devem contaminar o system prompt portatil. Registrar recomendacoes especificas somente no relatorio externo quando o ambiente-alvo for conhecido.
