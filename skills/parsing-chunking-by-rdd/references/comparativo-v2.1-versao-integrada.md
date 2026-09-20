# Comparativo v2.1.0 x versão integrada

## Existia na v2.1.0 e havia desaparecido
- modo `semantic`;
- modo `full`;
- processador automatizado DOCX/PDF/TXT;
- catálogo de unidades normativas;
- mapa semântico/índice de remissões;
- validador de referências e relações bidirecionais;
- verificador de qualidade do Markdown.

## Existia na versão atual e foi preservado
- esquema rígido de relatório;
- revisão obrigatória e bloqueio de publicação incompleta;
- SHA-256;
- escrita sem sobrescrita;
- casos de aceitação;
- regras mais fortes de vigência e extração;
- proteção contra conteúdo-instrução.

## Decisões da integração
- `parse` continua sendo o padrão e mantém exatamente dois arquivos.
- `semantic` e `full` exigem pedido explícito.
- o processador v2.1 é auxiliar; a revisão da versão atual prevalece.
- o validador semântico ficou mais estrito para âncoras inexistentes.
