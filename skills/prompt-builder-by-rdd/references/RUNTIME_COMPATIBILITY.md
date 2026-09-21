# Compatibilidade por capacidades

## Principio

A skill e escrita para ser agnostica de fornecedor. O comportamento central depende de conversa, leitura de materiais e geracao de texto; nao depende de nomes de modelos ou parametros proprietarios.

## Capacidades minimas

- manter contexto da conversa durante o brainstorm;
- ler texto fornecido pelo usuario;
- gerar um system prompt estruturado em Markdown/texto;
- usar delimitadores de dados quando necessario;
- respeitar o gate de confirmacao.

## Capacidades opcionais

### Leitura de arquivos
Se o ambiente puder ler arquivos, a skill pode catalogar e extrair regras dos materiais fornecidos. Se nao puder, pedir trechos ou resumos necessarios sem alegar leitura inexistente.

### Pesquisa web
Usar somente com autorizacao explicita do usuario e quando o ambiente realmente disponibilizar pesquisa. Priorizar fontes primarias quando houver dependencia normativa ou temporal.

### Execucao de codigo ou planilha
Nao e requisito para todo prompt. Quando houver calculos, totais, saldos, reconciliacoes ou outras operacoes numericas materiais, pode ser requisito de confiabilidade. Nesses casos, definir quem calcula e quem valida e nao afirmar validacao deterministica sem execucao real.

### Conectores
Nao presumir conectores. Se o prompt final depender de CRM, banco de dados, documentos, planilhas ou outro sistema, descrever a capacidade e somente nomear o fornecedor quando isso fizer parte do escopo confirmado.

### Contexto limpo para verificacao
Quando o ambiente permitir nova sessao, chamada separada ou contexto limpo, a skill pode recomendar um segundo passe de verificacao para tarefas materiais. Essa recomendacao nao cria arquitetura multiagente obrigatoria.

## Portabilidade

Nao colocar parametros proprietarios de effort, nomes de modos ou configuracoes de UI dentro do system prompt portatil. Traduzir intencoes em regras operacionais.

Se o ambiente-alvo for conhecido e uma configuracao especifica for util, registra-la no relatorio externo de geracao como recomendacao de deployment.

## Limites

A existencia desta skill nao prova que qualquer fornecedor executara o prompt de forma identica. Avaliacao comportamental deve ser feita no ambiente-alvo quando houver requisito de alta confiabilidade.
