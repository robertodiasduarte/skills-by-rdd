# Protocolo de brainstorm progressivo

## Objetivo

Conduzir uma entrevista curta por turno ate que exista informacao suficiente para consolidar um escopo verificavel. O usuario nao precisa conhecer engenharia de prompts.

## Regra de interacao

Fazer uma pergunta principal por mensagem. Admitir ate dois esclarecimentos do mesmo assunto somente quando forem necessarios para evitar ambiguidade imediata. Nunca repetir pergunta ja respondida.

A cada resposta, atualizar internamente quatro estados:

- `informado`: declarado pelo usuario;
- `comprovado`: sustentado por material utilizavel;
- `proposto`: sugestao estrutural ainda nao confirmada;
- `nao_disponivel`: ausencia reconhecida.

Nao tratar `nao_disponivel` como zero, nao aplicavel ou consentimento.

## Ordem adaptativa

A ordem abaixo e uma referencia, nao um questionario rigido:

1. processo/tarefa e resultado concreto;
2. publico e contexto de uso;
3. dominio e fronteiras;
4. entrada e saida;
5. modo `interativo` ou `autonomo`;
6. jurisdicao e periodos, se alterarem o comportamento;
7. regras, excecoes e proibicoes;
8. materiais existentes;
9. ferramentas/capacidades do agente final;
10. pesquisa externa;
11. criterios de aceite e revisao;
12. lacunas e riscos.

Se o usuario ja trouxer varios desses itens, pular diretamente para o maior vazio remanescente.

## Cinco gavetas RDD

Solicitar apenas as gavetas pertinentes:

### Lei/norma
Leis, regulamentos, normas tecnicas, politicas, contratos, instrumentos coletivos, standards ou regras formais. Registrar jurisdicao, autoridade, versao/vigencia e localizador quando disponiveis.

### Tabela
Faixas, taxas, limites, calendarios, indices, matrizes, tabelas de preco ou outras constantes versionadas. Registrar unidade, periodo, fonte e arredondamento quando pertinente.

### Caso
Exemplo positivo, entrada/saida desejada, contraexemplo, caso real anonimizado ou caso sintetico. Distinguir exemplo de estilo de gabarito profissional validado.

### Conta/regra
Formula, memoria de calculo, algoritmo, sequencia decisoria, ordem de operacoes, excecoes, arredondamento e criterios de validacao.

### Base
POP, manual, guia, playbook, FAQ, corpus, politica interna ou material de referencia.

## Exemplos e contraexemplos

Se nao houver caso real, registrar `nao_disponivel`. Nao bloquear a geracao apenas por isso.

Pode propor casos sinteticos para testar estrutura e comportamento, mas rotula-los como sinteticos e nunca usa-los como prova normativa ou profissional.

Contraexemplos tipicos:

- prompt vago ou ambiguo;
- objetivo sem criterio de conclusao;
- saida indefinida;
- regra misturada com exemplo;
- fonte inventada;
- dados faltantes preenchidos por suposicao;
- configuracao dependente de fornecedor;
- excesso de texto sem contrato operacional;
- ausencia de condicao de parada;
- prompt que expande o escopo silenciosamente.

## Modo de operacao

Perguntar obrigatoriamente se o prompt final operara de modo `interativo` ou `autonomo`.

**Interativo:** falta essencial -> perguntar somente o minimo necessario.

**Autonomo:** falta essencial -> registrar insuficiencia, nao inventar e encaminhar ponto material para revisao humana; continuar apenas no que for seguro.

## Sensibilidade e confidencialidade

Se a conversa indicar dados pessoais ou confidenciais, emitir o alerta definido em `SOURCE_AND_SECURITY.md` antes de incentivar o envio de novos documentos sensiveis.

## Fechamento do brainstorm

Consolidar um escopo versionado com ID e revisao. O resumo deve conter, conforme aplicavel:

- objetivo;
- publico;
- dominio e interfaces;
- jurisdicao;
- periodo consultivo;
- periodo de calculo;
- cobertura;
- exclusoes;
- entradas;
- saida;
- modo de operacao;
- materiais utilizados e ausentes;
- regras e premissas;
- ferramentas;
- pesquisa;
- seguranca;
- revisao humana;
- testes;
- limitacoes.

Em seguida pedir a frase:

`CONFIRMO O ESCOPO <ID> V<REVISAO> E AUTORIZO GERAR O SYSTEM PROMPT.`

Parar e aguardar nova mensagem.
