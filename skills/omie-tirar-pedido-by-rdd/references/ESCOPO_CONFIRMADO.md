# Escopo confirmado

Escopo **OMIE-PED V2** · sha256 do escopo `65e4271b-86a3a3bf-abc5c908-8f356d80-6a303826-d6804b50-672c53b4-498cc901` · confirmado em 10/10/2026 com a frase
`CONFIRMO O ESCOPO OMIE-PED V2 E AUTORIZO GERAR A SKILL.`. Gerada pela `skill-builder-omie-by-rdd` 1.0.0.

**Perfil Omie:** Operador — a skill não precisa somar valores de vários registros; ela grava um pedido por vez com o gate de escrita.

**Objetivo:** montar o pedido de venda ditado pela pessoa, mostrar na tela e incluir no Omie só depois da frase literal de confirmação.

**Público:** dono ou vendedor de empresa que usa o Omie, ou o contador que opera por ela. **Revisão humana:** a pessoa confere o pedido montado antes da frase literal.

**Cobre:**
- achar o cliente por CNPJ, razão social ou nome fantasia
- achar produtos, preço e saldo
- achar a condição de pagamento
- incluir o pedido na etapa 10 com o gate de escrita
- conferir o pedido incluído

**Não cobre:**
- faturar o pedido ou emitir NF-e
- inutilizar numeração
- cadastrar cliente ou produto
- dar desconto ou sugerir troca de produto
- alterar ou excluir pedido existente
- somar valores de vários pedidos

**Entradas:**
- empresa (app_hash)
- cliente
- itens com quantidade e, se houver, preço
- condição de pagamento

**Saídas:**
- pedido montado na tela
- número do pedido incluído
- status conferido

**Período de consulta:** dados ao vivo no momento da execução. **Período de cálculo:** nao aplicavel.

**Critérios de aceite:**
- nenhuma inclusão sem a frase CONFIRMO GRAVAR PEDIDO <cliente>
- um pedido por frase
- status conferido depois de incluir
- faturar recusado

**Lacunas declaradas:**
- o total do pedido mostrado na tela é o que a própria Omie devolve ao montar; a skill não soma itens
