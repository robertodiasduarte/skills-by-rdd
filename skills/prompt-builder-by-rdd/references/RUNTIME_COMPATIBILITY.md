# Compatibilidade por capacidades

## Principio

A skill e escrita para ser agnostica de fornecedor. O comportamento central depende de conversa, leitura de materiais e geracao de texto; nao depende de nomes de modelos ou parametros proprietarios.

## Capacidades minimas

- manter contexto da conversa durante o brainstorm;
- ler texto fornecido pelo usuario;
- gerar um bloco de texto/XML;
- respeitar o gate de confirmacao.

## Capacidades opcionais

### Leitura de arquivos
Se o ambiente puder ler arquivos, a skill pode catalogar e extrair regras dos materiais fornecidos. Se nao puder, pedir trechos ou resumos necessarios sem alegar leitura inexistente.

### Pesquisa web
Usar somente com autorizacao explicita do usuario e quando o ambiente realmente disponibilizar pesquisa. Priorizar fontes primarias quando houver dependencia normativa ou temporal.

### Execucao de codigo
Nao e requisito para o funcionamento normal da skill. Pode ser util para validacoes deterministicas de formulas ou estruturas, se o ambiente permitir e o escopo exigir.

### Conectores
Nao presumir conectores. Se o prompt final depender de CRM, banco de dados, documentos, planilhas ou outro sistema, descrever a capacidade e somente nomear o fornecedor quando isso fizer parte do escopo confirmado.

## Portabilidade

Nao usar `Reasoning Effort`, `Agentic Eagerness`, nomes de modos proprietarios ou instrucoes que dependam de uma UI especifica. Traduzir intencoes em regras operacionais.

## Limites

A existencia desta skill nao prova que qualquer fornecedor executara o prompt de forma identica. Avaliacao comportamental deve ser feita no ambiente-alvo quando houver requisito de alta confiabilidade.
