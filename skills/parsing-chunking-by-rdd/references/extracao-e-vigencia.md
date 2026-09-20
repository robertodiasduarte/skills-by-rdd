# Extração conservadora e tratamento de vigência

## Conteúdo
1. Princípios e registro de evidências
2. DOCX
3. PDF
4. TXT
5. Correções e chunking
6. Conclusão ou interrupção

## 1. Princípios e registro de evidências

Aplicar a especificação integral em `references/parsing.md`. Usar este roteiro
como detalhamento de execução, não como licença para ampliar as exclusões.
Não fazer pesquisa jurídica; “vigência” aqui é o estado evidenciado no arquivo.

Guardar texto original, texto mantido, localizador, método e motivo das
transformações em área interna de trabalho. Registrar exclusões também quando
não restar texto do bloco. Não incluir no Markdown limpo o conteúdo removido
como apêndice, comentário HTML ou versão alternativa.

Não quantificar como “linhas originais” quebras de linha geradas artificialmente
pelo extrator. No DOCX, contar trechos/runs e blocos afetados; informar que linhas
visuais não foram mensuradas quando não houver renderização confiável.
Contar cada bloco afetado uma vez, mesmo que possua vários runs tachados.
Não classificar o mesmo evento simultaneamente como cabeçalho e tachado.

## 2. DOCX

Usar uma ferramenta que permita acessar o documento e seus metadados, por
exemplo `python-docx` e, quando necessário, o XML do pacote. Não se limitar a
`paragraph.text` ou a uma exportação TXT para decidir o que está tachado.

Percorrer parágrafos e tabelas na ordem real do corpo. Incluir hiperlinks,
notas e outros componentes textuais acessíveis; registrar os componentes
que a biblioteca não expuser. Preservar posições de tabelas e texto em células.
Não duplicar conteúdo por iterar repetidamente células mescladas.

Para cada trecho textual:
1. Ler tachado simples e duplo na formatação direta.
2. Resolver propriedades herdadas do estilo de caractere, estilo de parágrafo,
   estilos-base e padrões, respeitando sobreposições e desativação explícita.
3. Não interpretar um valor ausente/indeterminado como falso sem verificar
   herança. Não considerar a mera presença de uma tag com valor falso como tachado.
4. Resolver corretamente a semântica de propriedades de alternância do OOXML.
   Se o leitor não resolver a cascata de modo confiável, manter o caso duvidoso
   e registrar a limitação, em vez de fazer OR de todos os estilos encontrados.
5. Remover somente o trecho com formatação efetiva objetivamente tachada.
   Preservar trechos não tachados e ajustar somente espaços e pontuação
   deixados pela remoção, sem mudar o sentido.

Distinguir tachado de controle de alterações, texto oculto, comentários e
cor de fonte. Não eliminar automaticamente esses outros conteúdos como se
fossem tachado. Quando uma exclusão controlada coexistir com uma inserção,
não aceitar/rejeitar revisões sem regra explícita e evidência suficiente.

Exemplo objetivo:
    Original: “Prazo: [run tachado: 10] [run normal: 15] dias.”
    Resultado: “Prazo: 15 dias.”
    Registro: um bloco afetado; um trecho removido; detecção por formatação.

Recuperar níveis de títulos, numeração de listas e seus identificadores;
não presumir que o texto visível do parágrafo contenha a numeração automática.
Não transformar todos os parágrafos em negrito em headings.

Examinar cabeçalhos e rodapés antes de removê-los. Preservar notas substantivas,
autoria relevante ou referências que não sejam mero ruído repetitivo.
Sinalizar desenhos, caixas de texto, equações e imagens não extraídos; não
transcrever conteúdo rasterizado nem usar OCR.

## 3. PDF

Usar extração por página/bloco/palavra com coordenadas, por exemplo com
PyMuPDF ou pdfplumber disponíveis no ambiente. Preservar localizadores.
Não assumir que a ordem textual padrão do extrator corresponda à leitura.

Diagnosticar páginas individualmente: quantidade de texto útil, imagens,
sobreposição de blocos e áreas sem texto extraível. Um PDF pode misturar páginas
selecionáveis e scans. Não registrar “sem imagens” apenas porque a extração textual
não as mostrou. Não fazer OCR, nem usar visão para transcrever as imagens.

Quando houver renderização/screenshot disponível ou exigido pela ferramenta,
usar apenas para verificar layout, colunas, tabelas e correspondência visual do
texto já extraído. Não ler texto contido somente em imagem. Não usar inspeção
visual de linhas sobre letras como fundamento suficiente para remoção de tachado.

Distinguir colunas de tabela e blocos laterais. Recuperar colunas só quando as
fronteiras, títulos de largura total e ordem forem claros. Não aplicar uma
simples ordenação global por coordenada vertical; ela pode intercalar colunas.
Se não for possível recuperar a ordem, pedir uma versão linear.

Marcar como candidatos a cabeçalho/rodapé textos recorrentes na mesma faixa
de margem de várias páginas. Confirmar função e conteúdo antes de remover;
uma frase repetida no corpo não é necessariamente ruído.

Aplicar a decisão de não vigência nesta ordem:
1. Localizar marcador explícito e estabelecer o trecho exato que ele qualifica.
2. Verificar se o marcador é anotação de estado, e não descrição/citação.
3. Para redações coexistentes, exigir identidade do dispositivo e evidência
   inequívoca de substituição/efeitos; preservar notas e exceções relevantes.
4. Se houver incerteza temporal, sobre o alcance ou sobre qual versão se aplica,
   manter ambas e registrar a pendência.

Não usar isoladamente “Redação dada”, “Incluído”, “Produção de efeitos”,
uma data maior ou a posição posterior como prova suficiente. Não deduzir tachado
a partir de traços vetoriais sobrepostos. Explicitar no relatório que PDF pode
perder a formatação e que a análise se limita às evidências disponíveis.

## 4. TXT

Tentar decodificação sem perda a partir de BOM e evidências de codificação.
Não usar `errors="ignore"` nem `errors="replace"` para esconder falhas.
Se UTF-8 falhar, identificar e testar outra codificação justificável; não
“corrigir” mojibake sem verificar o texto obtido. Registrar a codificação usada.

Preservar linhas/parágrafos e tabulações que possam representar tabelas.
Não afirmar que TXT conserva tachado visual.

Remover apenas trechos com marcadores explícitos de não vigência e alcance
inequívoco, como `[REVOGADO]`, `(Revogado)`, `(VETADO)` ou `(sem eficácia)`.
Não presumir que `~~texto~~`, um asterisco ou uma palavra isolada sejam marcação
de revogação se a convenção do documento não estiver estabelecida.

Exemplos de decisão:
- “Art. 3º. [REVOGADO] Texto antigo.”, com marcador inequivocamente aplicado
  ao dispositivo: retirar apenas o conteúdo abrangido, mantendo o restante.
- “A expressão ‘revogado’ indica...” : manter; trata-se de texto explicativo.
- “Art. 4º. (Revogado)” sem redação substantiva: não inventar texto removido;
  registrar eventual retirada do identificador/marcador sem excluir o artigo seguinte.
- “[REVOGADO]” isolado entre dois parágrafos: não presumir alcance; manter e
  registrar se não houver delimitadores ou estrutura que desfaçam a ambiguidade.

## 5. Correções e chunking

Aplicar alterações localizadas e reversíveis a partir do registro:
- Reflow: unir somente linhas do mesmo parágrafo, sem cruzar títulos, listas,
  artigos, células, notas ou fronteiras de colunas.
- Hífen: distinguir hífen ortográfico e quebra editorial; usar recorrências
  inequívocas no próprio documento quando existirem. Em dúvida, preservar.
- Unicode: preferir NFC; não aplicar NFKC indiscriminadamente a símbolos,
  sobrescritos, unidades e expressões matemáticas.
- Caracteres: preservar acentos, símbolos, cifras e sinais substantivos;
  sinalizar o caractere substituto U+FFFD e outras corrupções não resolvidas.
- Tabelas: preservar cabeçalhos, células vazias, unidades, notas e associações.
  Escapar pipes ao converter para Markdown; não transformar uma tabela sem
  cabeçalho em dados com cabeçalho inventado.
- Referências: substituir somente o alvo textual que seja determinístico,
  mantendo sentido e identificadores originais.

Usar um único Markdown. Títulos e separadores devem representar fronteiras
existentes, não categorias temáticas inventadas. Na ausência de títulos
inequívocos, preservar o texto e registrar a limitação estrutural.
Não adicionar título com tese/resumo nem notas editoriais ao conteúdo limpo.

Não cortar por tamanho fixo, duplicar passagens para overlap ou reorganizar
assuntos entre seções. Se um bloco indivisível permanecer longo, mantê-lo e
registrar por que a divisão seria arriscada.

## 6. Conclusão ou interrupção

Prosseguir com pendências quando ambiguidades puderem permanecer no conteúdo
sem falsificá-lo. Interromper se a ausência de texto essencial ou a quebra de
relações impedir uma entrega fiel.

Exemplo de interrupção:
“Não foi possível extrair o conteúdo essencial deste PDF sem OCR, que está
vedado neste fluxo. Envie uma versão com texto selecionável ou um DOCX/TXT
equivalente.”

Não gerar arquivos vazios para encobrir falha. Distinguir esse caso de uma
extração válida integralmente excluída por evidências objetivas, que exige
o tratamento excepcional documentado no esquema do relatório.
