# Experimentação e medição proporcional à decisão

Leia para desenhar ou avaliar testes de campanha, fluxo, oferta, evento ou produto. Base: [M05, M08, M19–M22](fontes.md). Cartões, exemplos e fórmulas abaixo são síntese operacional; não certificados de validade estatística.

## Escolher o método pela pergunta

| Incerteza | Método inicial possível | O que permite aprender | Limite |
| --- | --- | --- | --- |
| Contexto/necessidade | Entrevista de episódio e observação | Circunstâncias, alternativas, critérios | Não estima conversão ou prevalência sozinha |
| Compreensão/esforço | Tarefa em protótipo ou processo | Onde entende, erra, precisa de ajuda | Não comprova demanda paga |
| Capacidade de entregar | Piloto manual com escopo real | Tempo, dependência, falha, custo | Operação pequena pode não escalar |
| Disposição a pagar | Oferta transparente/compromisso real | Aceitação nas condições apresentadas | Amostra e condições limitam generalização |
| Efeito de uma mudança | A/B aleatório com instrumentação | Diferença estimada entre condições | Requer unidade, volume e desenho adequados |
| Efeito total de mensagens/mídia | Controle sem a ação de marketing | Incremento em relação ao controle | Confira exceções e exposição por outros canais |

Comparar dois anúncios testa variantes; não demonstra necessariamente o efeito de anunciar versus não anunciar. Comparar dois meses ou pessoas que escolheram participar de um evento não cria controle equivalente.

## Cartão de teste antes de executar

Adapte a Test Card (M19): hipótese, método, medida e limiar de sucesso. Acrescente detalhes suficientes para a hipótese atual:

- **Decisão e mecanismo:** o que será escolhido e por que a mudança deve melhorar o resultado.
- **Público/fase e elegibilidade:** quem entra, por qual sinal definido antes da exposição.
- **Mudança e comparação:** o que varia e o que permanece equivalente.
- **Unidade:** pessoa, oportunidade ou organização, conforme interação entre participantes e forma de entrega. Preserve identificação consistente; não faça a mesma pessoa receber ambas as condições inadvertidamente.
- **Métrica principal:** resultado relevante, evento, numerador, denominador, origem dos dados e janela de maturação.
- **Limites:** custo, esforço, reclamação, cancelamento ou falha de entrega que não pode piorar além do critério acordado.
- **Volume e duração:** histórico disponível, efeito mínimo útil, amostra necessária quando quantitativo e ciclo observado. Sem dados para dimensionar, marque o teste como exploratório.
- **Regra de decisão:** continuar, ajustar, parar ou declarar inconclusivo; defina o que cada resultado autoriza concluir.

Hipótese ilustrativa: um resumo claro de responsabilidades pode melhorar a compreensão do serviço. Uma tarefa de compreensão testa isso diretamente; perguntar a uma persona sintética se gostou, ou medir só clique no anúncio, não responde à mesma pergunta.

## Definir a métrica sem esconder o denominador

Taxa de conversão = unidades únicas que completam o evento na janela ÷ unidades elegíveis definidas no desenho. Em um experimento, análise principal deve preservar a atribuição aos grupos; condicionar apenas a quem abriu/clicou depois do envio pode criar grupos incomparáveis.

Para A/B com taxas `pT` e `pC`: diferença absoluta = `pT − pC`; diferença relativa = `(pT − pC) / pC`, se `pC` não for zero. Informe tamanho dos grupos e incerteza. Exemplo puramente aritmético: 10% para 12% representa +2 pontos percentuais ou +20% relativo; sem desenho e amostra, isso não demonstra causalidade ou significância.

Não confunda eventos repetidos com pessoas únicas, receita de pipeline com recebimento, receita com margem, ou resultado atribuído com incremental. Frequência, atividade e conversão podem ter denominadores diferentes; registre o utilizado.

## Integridade do teste quantitativo

M21 destaca hipótese, métricas, poder e unidade de aleatorização. Faça planejamento de amostra a partir de taxa/variabilidade histórica e efeito mínimo relevante quando houver condições; não adote número universal de participantes. Em vendas B2B, membros da mesma empresa podem afetar uns aos outros, exigindo unidade organizacional e análise apropriada.

M22 trata desvio entre proporção prevista e observada dos grupos. Não exija igualdade exata: avalie desvios relevantes com diagnóstico apropriado. Investigue perdas, duplicidades, filtros, entregabilidade e cruzamento de grupos antes de interpretar diferença como efeito. Interrompa conclusão se dados essenciais estiverem comprometidos.

Defina janela considerando o tempo até o resultado e não encerre um teste de horizonte fixo só quando o painel fica favorável. Monitoramento sequencial exige método previsto para isso. Muitas métricas/variantes e recortes após ver resultados aumentam o risco de achados ocasionais; trate exploração posterior como hipótese para confirmação. Esses controles são recomendações de síntese, não implementação de uma plataforma estatística nesta skill.

## Aprender e atualizar o perfil

Adapte a Learning Card (M20): hipótese testada, observação, interpretação e ação. Acrescente limitações, casos divergentes e se o resultado sustentou a decisão no contexto estudado. “Inconclusivo” não significa “não funciona” nem “funciona”.

Registre a evidência do teste separadamente da hipótese anterior. Atualize apenas conclusões afetadas. Um piloto positivo não valida todos os canais, fases e condições comerciais; um A/B negativo de redação não refuta automaticamente a necessidade do cliente.
