# Como funciona

O conector do Omie deixa o assistente de IA gravar direto na sua empresa, e não existe ambiente de teste: o pedido
incluído passa a existir na hora. Esta skill trata a gravação como um documento que você assina.

Ela acha o cliente, os produtos e a condição de pagamento que você ditou, mostra o pedido inteiro na tela e só inclui
depois que você escreve a frase `CONFIRMO GRAVAR PEDIDO <cliente>`. Um pedido por frase. Depois de incluir, ela
consulta o pedido na Omie e mostra o número e o total que a Omie devolveu — a skill não soma itens.

Se algo der errado ao gravar, ela mostra a mensagem da Omie e para: nunca tenta de novo sozinha, para não duplicar
pedido. Faturar (emitir a nota) fica fora: o servidor da Omie não pede confirmação para faturar.

Recomendação que vale mais que qualquer texto: no conector do Omie, deixe `omie_executar` em "pedir aprovação". Assim o
próprio aplicativo pergunta antes de cada gravação.
