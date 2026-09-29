# Cálculo dos Anexos I a V
Use para alíquota nominal, parcela a deduzir, alíquota efetiva e DAS.
Primeiro classifique a atividade/anexo e o período. Depois use o apurador redundante somente em cenário ordinário suportado.
Fontes: LC 123/2006, Resolução CGSN 140/2018 e Manual PGDAS-D.


## Exportação de mercadorias no Anexo I

Quando houver mercado interno e exportação, não usar o modo ordinário. A V4.1 possui `modo=exportacao_anexo_i`, que mantém RBT12 e RPA separados para os dois mercados e reproduz o Exemplo 6 oficial. O modo é bloqueado se houver efeito de sublimite, ICMS-ST, monofásico ou início de atividade.
