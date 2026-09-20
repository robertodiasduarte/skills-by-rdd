# Fontes, materiais e ancoragem

## Cinco gavetas, preservadas

| Gaveta RDD | Slot | Conteúdo solicitado | Uso |
|---|---|---|---|
| Lei | norma | Texto normativo, ato, decisão ou instrumento pertinente | Fundamentação, aplicação e vigência |
| Tabela | tabela | Faixas, taxas, índices, limites, calendários com fonte | Dados versionados por período |
| Caso | caso | Entrada/saída, exemplo, contraexemplo, gabarito conferido | Avaliação positiva e negativa |
| Conta | regra | Fórmulas, memória de cálculo, ordem e arredondamentos | Especificação do procedimento ou motor |
| Base | base | POP, manual, guia, material explicativo e corpus de consulta | Recuperação e resposta ancorada |

Uma memória não vira fonte legal só porque contém uma fórmula.
Um contraexemplo é Caso com papel `negativo`, não gabarito de cálculo.
Um arquivo pode ter papéis relacionados, mas registrar a relação sem duplicar evidência.
As cotas de upload da plataforma descritas na fonte não são limites universais.

## Catálogo de material

Atribuir ID estável. Registrar:
título; nome do arquivo; slot; papel; origem; órgão/autor; jurisdição;
data/versão; vigência inicial/final; localizador; integridade (SHA-256 se executável);
situação de leitura; situação de uso; lacunas; autorização de compartilhamento.

Para norma: identificar dispositivo e hipótese de aplicação.
Para tabela: identificar período, unidade, fonte de cada constante, faixas e arredondamento.
Para caso: entrada, saída, fundamento, natureza sintética/real e conferência.
Para memória: fórmula, variáveis, unidade, ordem, exceções, arredondamento e fonte.
Para base: preservar conteúdo e headings; separar índice e anotações do original.

Os slots do escopo versionado registram apenas arquivos usados na geração.
Documentos pendentes podem constar como `nao disponivel`, sem capacidade derivada.
`utilizavel` significa lido e aceito para o papel declarado; não é certificação jurídica.

## Formatos e extração

Solicitar formato que o ambiente consiga ler fielmente. Preferir texto pesquisável.
Se o usuário enviar PDF, imagem ou planilha, extrair somente com recursos disponíveis.
Não afirmar que leu tabelas ou páginas inacessíveis. Preservar páginas/abas/células.
Registrar fonte original, derivado textual, método e limitações da extração.

O perfil B do contrato RDD exige base textual em Markdown. Para materiais em outro
formato, criar derivado verificável quando possível; não chamar um binário ilegível
de corpus disponível. Conferir o derivado contra a fonte, especialmente números.

No pacote RDD, conhecimento legível vai em references/; binários de saída vão em assets/.
Não mover um PDF para assets/ e afirmar que seu conteúdo virou base textual.
Não usar OCR quando houver extração textual confiável; declarar trechos ilegíveis.

## Protocolo de ancoragem da skill-filha

Para cada conclusão relevante, registrar fonte por título/ID e localizador:
artigo/parágrafo/inciso, seção/página, linha, aba/célula ou caso.
Usar “Segundo [título], [localizador]...” e distinguir inferência de texto da fonte.
Nunca fabricar número de artigo, ementa, precedente, página ou URL.

Separar ordem de busca de ordem de prevalência. Uma fonte encontrada primeiro não
vence por isso. Não inventar uma hierarquia universal entre fontes profissionais.
Aplicabilidade, autoridade, vigência e conflito dependem da jurisdição e do escopo.
Registrar conflitos e solicitar revisão competente.

Manter RULE_MAP com regra, fonte, hipótese, período, código e testes.
Manter SOURCES para constantes e SOURCE_CATALOG para o corpus quando o perfil exigir.
Não confundir CHANGELOG (mudanças na skill) com registro de atualização normativa.

## Pesquisa e atualização

O padrão é não pesquisar normas sem autorização expressa.
Quando autorizada e possível, priorizar fontes oficiais; registrar consulta, versão,
vigência e cópia/trecho utilizado. Não substituir silenciosamente a base do usuário.
A autorização de pesquisa não autoriza envio do acervo privado a serviços externos.

Se uma regra superior do host exigir pesquisa e o escopo exigir corpus fechado,
declarar o conflito de capacidades e não afirmar isolamento ou fonte exclusiva.
Fontes novas que alteram o contrato retornam à confirmação.

A data do upload e o ano do nome do arquivo não provam vigência.
Cobertura consultiva mais ampla não expande cobertura de cálculo.
Sem tabela local do período ou fonte aplicável, não preencher a partir da memória.

## Ausência de material

Usar literalmente `nao disponivel` para dado ausente.
Usar `nao aplicavel` apenas quando o responsável confirmou a inaplicabilidade.
Não substituir por zero. Registrar impacto: reduz cobertura, impede cálculo,
exige revisão ou permite somente operação guiada.

Material mínimo não é igual a competência profissional comprovada.
Não transformar a degradação transparente do RDD em liberação de números sem prova.
