# Fórmulas e especificações — V4

## Sumário de navegação
- SPEC DAS ordinário
- SPEC Fator R
- SPEC RBT12 proporcionalizada
- Regra de precisão
- Erros bloqueantes

## SPEC DAS ordinário

### Entradas
- competência;
- anexo previamente classificado;
- RBT12;
- RPA;
- receita com ISS retido, quando aplicável;
- flags de qualificações complexas.

### Saídas
- faixa;
- alíquota nominal;
- parcela a deduzir;
- alíquota efetiva;
- bases, percentuais e valores por tributo;
- total do DAS.

### Regras
1. Carregar apenas a tabela do período.
2. Bloquear exportação, sublimite, ICMS-ST, monofásico e início de atividade no motor genérico.
3. Determinar faixa pela RBT12.
4. Motor principal: `efetiva = (RBT12 × Aliq − PD) / RBT12`; total por componentes.
5. Verificador: `total = RPA × Aliq − (RPA/RBT12) × PD`, com Decimal e decomposição independente.
6. Aplicar partilha vigente; ISS retido reduz somente a base da parcela de ISS.
7. Entregar número somente se engine e verify concordarem nos campos materiais.
8. A concordância não prova que a tabela está normativamente correta; goldens oficiais/humanos testam a tabela/implementação contra casos externos.

### Erros
- RBT12 ≤ 0 neste motor;
- valor negativo;
- receita com ISS retido > RPA;
- tabela ausente;
- qualificação complexa ativa;
- divergência engine/verify;
- baseline oficial falha.

## SPEC Fator R

### Entradas
FS12, RBT12 e competência.

### Saídas
fator bruto, fator considerado e anexo sugerido.

### Regras
1. Confirmar documentalmente que a atividade está sujeita ao fator R.
2. Tratar zero segundo a regra implementada e validada.
3. Aplicar precisão correspondente ao período.
4. Comparar com 0,28.
5. Retornar **anexo_sugerido**, nunca “anexo determinado”, enquanto a premissa jurídica não estiver confirmada.

### Erros
Valor negativo, período sem cobertura ou atividade cuja sujeição não foi confirmada para conclusão final.

## SPEC RBT12 proporcionalizada

### Entradas
Receita atual, receitas anteriores e período.

### Saídas
RBT12p e critério usado.

### Regras
1. Primeiro mês: receita do próprio PA × 12.
2. Meses seguintes até o 12º: média dos meses anteriores × 12.
3. Máximo de 11 meses anteriores.
4. Números brasileiros usam `;` para separar itens com vírgula decimal.

## Regra de precisão

Precisão, arredondamento e truncamento são regra de domínio, não escolha estética. Cada rotina mantém a regra documentada e seus testes.

## Erros bloqueantes

Ausência de tabela, divisão inválida, entrada inconsistente, cenário não suportado, divergência de verificação ou golden oficial divergente bloqueiam a entrega.


## Exportação de mercadorias — Anexo I

**Escopo implementado:** revenda de mercadorias no Anexo I, com mercado interno e externo no mesmo PA, sem efeito de sublimite, sem ICMS-ST, sem tributação monofásica e sem início de atividade.

**Entradas adicionais:** RBT12 interno, RBT12 externo, RPA interno, RPA externo, RBA interno, RBA externo e sublimite.

**Regras:**
1. calcular faixa e alíquota efetiva separadamente para mercado interno e externo;
2. no mercado interno, aplicar a partilha normal do Anexo I;
3. no mercado externo, zerar as parcelas de Cofins, PIS/Pasep e ICMS;
4. arredondar cada tributo monetário a centavos antes de somar o total do segmento;
5. somar os totais interno e externo;
6. se RBA interna ou externa exceder o sublimite informado, bloquear este modo porque a transição de ICMS/ISS não está implementada.

**Golden oficial:** Manual do PGDAS-D e DEFIS, Seção 12, Exemplo 6: total interno R$ 9.935,02; externo R$ 2.154,76; total do PA R$ 12.089,78.

**Erro:** mercado externo apresentado em `modo=ordinario` deve ser bloqueado antes do cálculo.
