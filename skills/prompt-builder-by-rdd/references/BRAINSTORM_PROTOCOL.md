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

1. processo/tarefa, resultado concreto e criterio de pronto;
2. publico, contexto e decisao habilitada pelo output;
3. dominio e fronteiras;
4. entradas, saida e dados de runtime;
5. modo `interativo` ou `autonomo` e regra de continuidade;
6. evidencia minima e prioridade entre fontes, quando pertinente;
7. estados fechados e tabela de decisao, quando pertinente;
8. jurisdicao e periodos, se alterarem o comportamento;
9. regras, excecoes, proibicoes e condicoes de parada;
10. materiais existentes;
11. calculos e mecanismo de validacao numerica, quando pertinente;
12. ferramentas/capacidades do agente final;
13. pesquisa externa;
14. criterios de aceite, revisao e estabilidade;
15. lacunas e riscos.

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
Formula, memoria de calculo, algoritmo, sequencia decisoria, ordem de operacoes, excecoes, arredondamento, estados e criterios de validacao.

### Base
POP, manual, guia, playbook, FAQ, corpus, politica interna ou material de referencia.

## Contrato, nao roteiro de raciocinio

Investigar o resultado pronto, limites e verificacao. Nao perguntar "como o modelo deve pensar em N passos". Se o usuario trouxer um roteiro de raciocinio, extrair dele apenas etapas observaveis, regras, dependencias, evidencias e criterios de conclusao.

## Evidencia e prioridade

Quando a tarefa tiver julgamento factual, classificacao ou decisao material, perguntar progressivamente:

- qual evidencia minima permite concluir;
- quais evidencias existem na sessao ou materiais;
- qual fonte/regra prevalece em caso de conflito;
- o que deve acontecer quando a evidencia nao basta.

Nao inventar hierarquia universal. A ordem pode variar por dominio, entidade, contrato ou jurisdicao.

## Autonomia na cobertura; cerca no julgamento

Perguntar obrigatoriamente se o prompt final operara de modo `interativo` ou `autonomo`.

**Interativo:** falta essencial -> perguntar somente o minimo necessario.

**Autonomo:** falta essencial -> registrar insuficiencia, nao inventar e encaminhar ponto material para revisao humana quando necessario.

Em ambos, identificar o que deve continuar sendo processado mesmo com itens pendentes. O agente nao deve abandonar o lote no primeiro caso incerto nem completar julgamento por plausibilidade para "terminar bonito".

## Nao dourar o ouro

Perguntar ou inferir das exclusoes o que o agente nao pode adicionar por iniciativa propria. Se descobrir oportunidade, erro lateral ou melhoria fora do pedido, registrar como observacao ou pendencia sem executar a expansao.

## Estados fechados

Quando houver classificacao, fila, risco, aprovacao ou conclusao, pedir a lista fechada de estados. Definir tambem quais estados impedem a conclusao final.

Se o usuario nao souber os estados, propor poucos estados funcionais e marca-los como `proposto` ate confirmacao.

## Numeros e validacao

Quando houver calculo material, perguntar:

- formula e constantes;
- unidade e arredondamento;
- quem calcula;
- quem valida;
- qual ferramenta deterministica existe;
- o que acontece se o validador nao estiver disponivel ou divergir.

Nao usar aumento de "profundidade" do modelo como substituto de regra ou validacao numerica.

## Separacao entre instrucao e dado

Identificar quais conteudos serao inseridos como dados de runtime. Planejar delimitadores especificos, por exemplo `<documentos>`, `<dados_do_caso>`, `<briefing>` ou `<extrato>`. O prompt deve dizer que esses blocos sao dados e nao instrucoes.

## Exemplos e contraexemplos

Se nao houver caso real, registrar `nao_disponivel`. Nao bloquear a geracao apenas por isso.

Pode propor casos sinteticos para testar estrutura e comportamento, mas rotula-los como sinteticos e nunca usa-los como prova normativa ou profissional.

Preferir poucos exemplos curtos de fronteira quando eles ajudarem: um caso claro, um ambiguo e um que deve permanecer pendente.

Contraexemplos tipicos:

- prompt vago ou ambiguo;
- objetivo sem criterio de conclusao;
- saida indefinida;
- regra misturada com dado ou exemplo;
- fonte inventada;
- dados faltantes preenchidos por suposicao;
- estado livre que muda entre execucoes;
- numero "fechado" em prosa sem validador;
- configuracao dependente de fornecedor dentro do prompt portatil;
- excesso de texto sem contrato operacional;
- ausencia de condicao de parada;
- prompt que expande o escopo silenciosamente.

## Sensibilidade e confidencialidade

Se a conversa indicar dados pessoais ou confidenciais, emitir o alerta definido em `SOURCE_AND_SECURITY.md` antes de incentivar o envio de novos documentos sensiveis.

## Fechamento do brainstorm

Consolidar um escopo versionado com ID e revisao. O resumo deve conter, conforme aplicavel:

- objetivo e criterio de pronto;
- publico e contexto;
- dominio e interfaces;
- jurisdicao;
- periodo consultivo;
- periodo de calculo;
- cobertura e exclusoes;
- entradas, saida e dados de runtime;
- modo de operacao e regra de continuidade;
- evidencia minima e prioridade;
- estados fechados;
- materiais utilizados e ausentes;
- regras e premissas;
- calculos e mecanismo de validacao;
- ferramentas;
- pesquisa;
- seguranca;
- revisao humana;
- testes e estabilidade;
- limitacoes.

Em seguida pedir a frase:

`CONFIRMO O ESCOPO <ID> V<REVISAO> E AUTORIZO GERAR O SYSTEM PROMPT.`

Parar e aguardar nova mensagem.
