# Manual da Compensação

<!-- Sumário gerado para navegação; não integra o texto oficial da fonte. -->
## Sumário de navegação
- Manual da Compensação
- Sumário
- 1 - Introdução
- 1.1 - Apresentação do aplicativo
- 1.2 - Objetivos do aplicativo
- 1.3 - A quem se destina
- 2 - Requisitos tecnológicos
- 3 - Acesso ao aplicativo de compensação
- 4 - Funcionalidades do aplicativo de compensação
- 4.1 - Compensar
- 4.2 - Consulta compensações
- 4.3 - Cancelamento de compensação


Versão - Março de 2024

## Sumário

- [1 - Introdução](#1---introdução)
  - [1.1 - Apresentação do aplicativo](#11---apresentação-do-aplicativo)
  - [1.2 - Objetivos do aplicativo](#12---objetivos-do-aplicativo)
  - [1.3 - A quem se destina](#13---a-quem-se-destina)
- [2 - Requisitos tecnológicos](#2---requisitos-tecnológicos)
- [3 - Acesso ao aplicativo de compensação](#3---acesso-ao-aplicativo-de-compensação)
- [4 - Funcionalidades do aplicativo de compensação](#4---funcionalidades-do-aplicativo-de-compensação)
  - [4.1 - Compensar](#41---compensar)
  - [4.2 - Consulta compensações](#42---consulta-compensações)
  - [4.3 - Cancelamento de compensação](#43---cancelamento-de-compensação)
- [5 - Emissão de DAS após compensação](#5---emissão-de-das-após-compensação)

## 1 - Introdução

### 1.1 - Apresentação do aplicativo

O aplicativo "Compensação a Pedido" é um sistema eletrônico para a realização de compensação de pagamentos recolhidos indevidamente ou em montante superior ao devido, relativos a créditos apurados no Simples Nacional, com débitos também apurados no Simples Nacional, para com o mesmo ente federado, e relativos ao mesmo tributo, de acordo com o disposto na Lei Complementar nº 123, de 14 de dezembro de 2006 (e alterações) e na Resolução CGSN nº 140, de 2018.

O aplicativo está disponível no portal do Simples Nacional, menu **Simples Serviços > Restituição e Compensação > Compensação a Pedido**, podendo ser acessado por meio de código de acesso ou certificado digital:

https://www8.receita.fazenda.gov.br/SimplesNacional/controleAcesso/Autentica.aspx?id=36

### 1.2 - Objetivos do aplicativo

- Compensar créditos apurados no Simples Nacional com débitos também apurados no Simples Nacional, para com o mesmo ente federado, e relativos ao mesmo tributo;
- Consultar as compensações efetuadas, com a opção de imprimir o extrato da compensação;
- Cancelar as compensações efetuadas.

### 1.3 - A quem se destina

O aplicativo se destina às Microempresas (ME) ou Empresas de Pequeno Porte (EPP) optantes pelo Simples Nacional.

**ATENÇÃO!**

Empresa não optante pelo Simples Nacional, que já foi optante pelo regime e possui valores passíveis de compensação, pode utilizar o aplicativo para compensar créditos com débitos, ambos apurados no Simples Nacional.

O aplicativo não permite a compensação de valores apurados no regime Simei.

## 2 - Requisitos tecnológicos

O sistema está habilitado para os seguintes navegadores: Internet Explorer 9.0 (versões acima devem estar com modo de compatibilidade ativo: teclar Control+F5 ou acionar o menu **Ferramentas -> Opções da Internet**) e navegadores baseados no Mozilla 5.0 (Firefox 2.0 e Netscape 8.0) ou versões posteriores.

## 3 - Acesso ao aplicativo de compensação

O aplicativo pode ser acessado pelo Portal do Simples Nacional ou pelo e-CAC.

Portal do Simples Nacional: https://www8.receita.fazenda.gov.br/SimplesNacional/Default.aspx

e-CAC: https://cav.receita.fazenda.gov.br/autenticacao/login/index

Para acessar pelo Portal do Simples Nacional, clique na imagem que indica os serviços do Simples Nacional.

Em seguida, efetue o login com CNPJ, CPF do responsável e Código de Acesso.

**IMPORTANTE!**

Para gerar o código de acesso usado no Portal do Simples Nacional, acesse:

http://www8.receita.fazenda.gov.br/SimplesNacional/controleAcesso/GeraCodigo.aspx

Clique em **Restituição e Compensação > Compensação a Pedido**.

## 4 - Funcionalidades do aplicativo de compensação

O aplicativo "Compensação a Pedido" possui três funcionalidades: **Compensar**, **Consulta Compensações** e **Cancelamento de Compensação**.

### 4.1 - Compensar

Esta função permite ao contribuinte realizar a compensação de pagamentos recolhidos indevidamente ou em montante superior ao devido (créditos apurados no Simples Nacional) com débitos também apurados no Simples Nacional, para com o mesmo ente federado, e relativos ao mesmo tributo (tributo de mesma espécie e natureza).

Ou seja:

- a compensação de cada um dos tributos da União somente poderá ser realizada com o respectivo tributo pago indevidamente ou a maior;
- a compensação do ICMS somente poderá ser realizada com esse imposto no âmbito do respectivo ente federado;
- a compensação do ISS somente poderá ser realizada com esse imposto no âmbito do respectivo ente federado;
- caso a compensação não tenha sido realizada pelos motivos acima expostos, é exibida a mensagem: "Compensação não efetuada. Só é possível compensar tributos da mesma espécie. Ex. IRPJ com IRPJ; ICMS de SP com ICMS de SP".

Para realizar a compensação, o contribuinte deve informar o período de apuração (PA) do crédito.

O sistema retorna apenas os pagamentos de Simples Nacional, com valores disponíveis, que tenham sido arrecadados em um período inferior a 5 anos da data atual.

Caso não exista pagamento de Simples Nacional com valor disponível para o PA, é exibida a mensagem "Não há pagamentos com valores disponíveis nesse PA".

Caso exista pagamento com valores disponíveis, o aplicativo exibe os dados do pagamento recolhido indevidamente ou a maior.

**ATENÇÃO!**

Caso o pagamento indevido ou a maior tenha sido recolhido por meio de DAS de parcelamento ou DAS de cobrança, deve ser informado o PA do débito abrangido por ele, e não o PA impresso no DAS.

Os débitos abrangidos pelo DAS podem ser consultados no demonstrativo de pagamentos do aplicativo de parcelamento.

Exemplo:

- DAS de parcela de 01/2020, com vencimento em 31/01/2020, pago em duplicidade, amortizou os débitos dos PA 01, 02 e 03/2019;
- Ao realizar a compensação, o contribuinte deverá informar cada um dos PA (01, 02 e 03/2019);
- Não deve, portanto, informar o PA do DAS da parcela (01/2020).

Ao clicar sobre o número do DAS, são exibidos os detalhes do pagamento.

Ao confirmar a utilização do pagamento, o aplicativo apresenta a lista de débitos passíveis de compensação.

É permitido selecionar apenas um PA (débito). Se após a compensação restar saldo do pagamento, deve-se realizar nova compensação.

O contribuinte seleciona o PA do débito e clica em **Utilizar Débito**. São exibidos os dados do débito e os dados do pagamento.

Nesta tela, o débito e o pagamento são exibidos em valor original. A atualização dos valores do crédito com juros e do débito com multa e juros de mora é feita apenas quando efetuada a compensação.

Ao clicar em **Compensar**, é exibida mensagem de confirmação. Se o contribuinte confirmar, o aplicativo apresenta tela com os dados do débito e os dados do pagamento.

O "Saldo Após Compensação" apresenta o débito (Dados do Débito) e o crédito (Dados do Pagamento), tributo a tributo, depois de realizada a compensação.

No caso em tela, estavam disponíveis valores de ICMS/SP, INSS e IPI. No PA selecionado, havia débito de ICMS/SP e INSS, dentre outros tributos.

Os valores de ICMS/SP e INSS foram compensados. O crédito de IPI não foi utilizado, pois não havia débito deste tributo no PA. Os débitos dos demais tributos do PA não foram amortizados, pois não havia crédito correspondente no pagamento.

O valor utilizado corresponde ao valor do pagamento que foi utilizado nessa compensação. Valor amortizado corresponde ao valor principal do débito amortizado pela compensação.

O crédito utilizado na compensação é corrigido pela taxa SELIC acumulada a partir do mês seguinte ao pagamento, mais 1% no mês da compensação. Já o débito compensado é corrigido pela mesma taxa a partir do mês seguinte ao vencimento, mais multa de 0,33% ao dia, limitada a 20% após o 60º dia.

### 4.2 - Consulta compensações

Essa funcionalidade permite a consulta e impressão do extrato das compensações a pedido efetuadas pelo contribuinte.

Ao acessar **Consulta Compensações**, o aplicativo apresenta os dados das compensações realizadas.

Ao clicar no ícone da impressora, é exibido o extrato da compensação, que pode ser impresso pelo contribuinte.

### 4.3 - Cancelamento de compensação

Essa funcionalidade permite o cancelamento de uma compensação a pedido efetuada pelo contribuinte.

Ao acessar **Cancelamento de Compensação**, o aplicativo apresenta os dados das compensações realizadas.

O contribuinte seleciona a compensação que deseja cancelar e, depois de confirmar, o aplicativo exibe a mensagem "Compensação cancelada com sucesso".

Após o cancelamento, o pagamento que havia sido utilizado fica disponível para ser usado em outra compensação ou ser objeto de um pedido de restituição.

**ATENÇÃO!**

O aplicativo não permite cancelar uma compensação cujo débito compensado esteja próximo ao prazo de prescrição.

Por outro lado, caso o crédito esteja prescrito, no momento do cancelamento, será exibida a mensagem: "O crédito do(s) DAS [Nº do DAS] já está prescrito e não poderá mais ser utilizado após a efetivação desta operação. Deseja continuar?"

## 5 - Emissão de DAS após compensação

Se após a compensação restar saldo devedor, a empresa deverá gerar o DAS da diferença da seguinte forma.

**Compensação com débito vencido:** gerar DAS Cobrança no PGDAS-D 2018 na opção **Débitos**.

A funcionalidade **Débitos > Consultar/Gerar DAS** identifica o saldo devedor do débito que está em cobrança na RFB (não inclui débitos já enviados para inscrição em dívida ativa, que devem ser recolhidos separadamente), considerando todas as amortizações que o débito possa ter sofrido ao longo do tempo, como pagamentos, compensações ou parcelamentos.

Nessa funcionalidade, o DAS (denominado DAS Cobrança) será gerado com o valor correto, deduzido o valor já compensado.

**Compensação com débito a vencer:** gerar DAS Avulso no aplicativo **Emissão de DAS Avulso** no Portal do Simples Nacional.

Para identificar o saldo devedor de cada tributo, ente a ente (por exemplo, ISS - São Paulo/SP), após a compensação, a ser informado no aplicativo DAS Avulso, o contribuinte deverá:

1. Obter os valores devidos por tributo e por ente antes da compensação: no PGDAS-D 2018, na opção **Declaração Mensal > Consultar Declarações**, clicar em **Extrato** da operação **Geração de DAS**, campo 6.1 (caso o DAS não tenha sido gerado, utilizar a opção **Declaração Mensal > Gerar DAS**);
2. Deduzir os valores compensados para cada tributo/ente: no aplicativo **Compensação a Pedido**, na opção **Consulta Compensações**, o valor compensado é apresentado no campo **Valor Amortizado**.

**ATENÇÃO!**

A geração do DAS Avulso é de inteira responsabilidade do contribuinte.

As informações da compensação **NÃO** aparecem no extrato do DAS do PGDAS-D (**Declaração Mensal > Consultar Declarações**) e devem ser consultadas no próprio aplicativo **Compensação a Pedido**.
