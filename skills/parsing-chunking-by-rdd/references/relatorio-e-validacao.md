# Relatório e validação da entrega

## Conteúdo
1. Responsabilidade do agente e do publicador
2. Nomes e datas
3. JSON interno obrigatório
4. Regras de preenchimento
5. Formato fixo do TXT
6. Revisão final e entrega

## 1. Responsabilidade do agente e do publicador

Concluir a extração, as decisões conservadoras e a revisão ANTES da publicação.
O script `scripts/finalizar_entrega.py` não lê o conteúdo semântico de DOCX/PDF,
não identifica tachado e não cria chunks. Ele recebe Markdown já revisado e um
relatório interno estruturado, valida o esquema e grava os dois arquivos finais.

Usar Python 3.9+ e a biblioteca padrão. Não instalar bibliotecas ou acessar a
rede para usar o publicador. Se a base de fusos do ambiente não estiver disponível,
informar a data correta com `--data` em vez de assumir UTC silenciosamente.

Não usar campos de revisão com `true` como substitutos de uma revisão real.
Somente declarar cada verificação após realizá-la.

## 2. Nomes e datas

Aplicar obrigatoriamente:

    UF-{SIGLA}_{NOME_BASE}_Texto-Ajustado_ate-AAAA-MM-DD.md
    UF-{SIGLA}_{NOME_BASE}_README_ate-AAAA-MM-DD.txt

Usar `XX` se a UF não tiver sido fornecida. Aceitar a sigla ou `UF-SIGLA` no
parâmetro `--uf`. Não inferir UF pela jurisdição aparente do conteúdo.
Usar o nome original sem extensão; remover acentos e caracteres especiais,
substituir espaços por hífens e preservar letras ASCII, números, hífens e
underscores. Não inventar uma base quando o nome não for normalizável; usar
um nome legível fornecido ou confirmado pelo usuário.

Quando o sistema alterar o nome físico do upload, passar o nome original
visível no chat em `--nome-original`. Não usar esse parâmetro para fingir que
um arquivo de outro tipo é DOCX/PDF/TXT.

Usar a data fornecida, ou a data corrente no fuso do usuário. O padrão do
utilitário é America/Sao_Paulo; adaptar com `--fuso` quando necessário.
Não empregar automaticamente datas de legislação encontradas dentro do texto.

O nome `readme.txt` na especificação designa a função do relatório; o nome
efetivo deve obedecer ao padrão com `README`. Não criar ambos os nomes:
isso produziria um terceiro arquivo.

## 3. JSON interno obrigatório

Criar o JSON abaixo apenas na pasta de trabalho. Adaptar TODOS os conteúdos
ao documento analisado; os valores a seguir descrevem um exemplo fictício
de TXT simples, não são resultados de uma análise real.

```json
{
  "tipo": "TXT",
  "metodo_extracao": "Leitura integral em UTF-8, com localização por linha.",
  "diagnosticos": {
    "extraibilidade": "Texto integralmente legível; nenhuma lacuna identificada.",
    "colunas_ordem": "Texto linear; ordem original preservada.",
    "cabecalhos_rodapes": "Nenhum elemento repetitivo de margem identificado.",
    "hifenizacao_quebras": "Nenhuma hifenização de quebra a corrigir.",
    "unicode_espacos": "Unicode legível; nenhum caractere corrompido identificado.",
    "imagens": "Arquivo TXT; nenhum conteúdo de imagem disponível.",
    "tabelas_diagramas": "Nenhuma tabela ou diagrama identificado.",
    "titulos_listas_chunking": "Título da primeira linha convertido em H1; demais parágrafos preservados.",
    "referencias_internas": "Nenhuma referência indireta identificada.",
    "vigencia": "Nenhum marcador textual inequívoco de não vigência identificado."
  },
  "correcoes": [
    {
      "local": "Linha 1",
      "problema": "Título sem marcação Markdown.",
      "solucao": "Aplicada marcação H1, preservando o texto do título.",
      "evidencia": "Primeira linha isolada, com função inequívoca de título documental."
    }
  ],
  "vigencia": {
    "metodo": "TXT: busca de marcadores textuais explícitos, com verificação do alcance.",
    "blocos_removidos": 0,
    "linhas_removidas": 0,
    "trechos_removidos": 0,
    "contagem_aproximada": false,
    "ocorrencias": [],
    "ambiguidades": []
  },
  "pendencias": [],
  "verificacoes": {
    "conteudo_conferido": true,
    "ordem_conferida": true,
    "exclusoes_conferidas": true,
    "ambiguidades_registradas": true,
    "numeros_referencias_conferidos": true,
    "sem_ocr": true,
    "sem_reescrita": true,
    "sem_texto_essencial_ausente": true
  }
}
```

## 4. Regras de preenchimento

Preencher `tipo` com `DOCX`, `PDF` ou `TXT`; ele deve corresponder à extensão
do nome original. Descrever o método efetivamente executado, não o planejado.

Preencher todos os dez diagnósticos, inclusive com “Não aplicável” acompanhado
do motivo quando pertinente. Não preencher “não encontrado” se a inspeção não
foi realizada; descrever a limitação e registrá-la também em `pendencias`.

Em `correcoes`, registrar as mudanças reais de parsing e estrutura com
local/problema/solução/evidência. Usar lista vazia quando não houver mudanças.
Agrupar ocorrências equivalentes somente preservando locais e quantificação
suficientes para rastrear a transformação.

Em `vigencia.ocorrencias`, registrar apenas exclusões realizadas. Usar:
```json
{
  "local": "Parágrafo 12, runs 3 a 4",
  "evidencia": "Formatação efetiva de tachado identificada no DOCX.",
  "acao": "Removida somente a redação tachada; mantida a redação adjacente."
}
```

Registrar contagens como inteiros não negativos ou `null` quando não mensuradas.
Usar `contagem_aproximada: true` para estimativas. Não usar strings como `"cerca
de 5"` nos campos numéricos. Explicar a unidade e o critério no método.
Uma contagem positiva exige ocorrência com evidência, e uma ocorrência de
exclusão exige pelo menos uma contagem positiva.

Não inventar linhas visuais no DOCX. Usar `linhas_removidas: null` quando
necessário, com contagem de runs/trechos e de blocos afetados.
Um bloco parcialmente afetado conta como um bloco com conteúdo excluído,
não como um bloco inteiro desaparecido.

Em `vigencia.ambiguidades`, informar local, dúvida e decisão de manter.
Em `pendencias`, informar local, limitação e ação recomendada.
O status será “CONCLUIDO COM PENDENCIAS” se qualquer dessas listas tiver itens.
Não ocultar limitações apenas nos diagnósticos para obter status sem pendências.

Declarar todas as verificações como verdadeiras somente após a revisão.
Uma dúvida preservada e registrada não impede confirmar que a ambiguidade
foi tratada; uma lacuna ESSENCIAL impede concluir e publicar.

Caso excepcional: se a extração tiver conteúdo, mas TODO o texto for
objetivamente abrangido por exclusões, não inventar texto vigente.
Usar Markdown vazio, contagens/evidências e o campo adicional
`"conteudo_integralmente_excluido": true`. O relatório declarará que nenhum
texto foi mantido. Nunca usar esse campo para contornar PDF scan, falha de
extração, senha, codificação ou conteúdo essencial ausente.

## 5. Formato fixo do TXT

Publicar texto puro UTF-8, sem BOM, XML, Markdown, tabelas renderizadas ou
blocos de código. Usar seções fixas e campos `Rótulo: valor`.
Quebrar linhas preferencialmente em 88 colunas, sem dividir tokens indivisíveis,
nomes de arquivos ou hashes. Manter esta ordem:

    01 IDENTIFICACAO
    02 EXTRACAO E DIAGNOSTICOS
    03 CORRECOES APLICADAS
    04 TACHADO E NAO VIGENCIA DOCUMENTAL
    05 ESTRUTURA PARA CHUNKING
    06 PENDENCIAS
    07 VERIFICACOES
    08 LIMITACOES E RECOMENDACOES

O publicador calcula os nomes, hashes SHA-256 e contagens básicas do Markdown.
A contagem de blocos separados por linhas em branco é aproximada; não
apresentá-la como quantidade exata de parágrafos semânticos ou tokens.

O publicador normaliza quebras de linha para LF e garante a quebra final de
um Markdown não vazio. Não faz NFC, reflow, remoção de tachado ou revisão do
texto nessa etapa: concluir essas decisões antes.

## 6. Revisão final e entrega

Usar pasta de destino nova e exclusiva. O script não sobrescreve pastas
existentes e remove sua saída parcial se ocorrer erro de gravação.
Em caso de erro, corrigir a causa; não ocultar a falha nem publicar um arquivo só.

Reabrir os dois arquivos e verificar nomes, UTF-8, estrutura do relatório,
contagens, marcação de pendências e fidelidade do Markdown.
Verificar que existam exatamente dois arquivos na pasta final.
Entregar apenas os dois links com os nomes completos; manter JSON e logs internos.

A verificação automática cobre estrutura e persistência. Ela não prova que
uma exclusão foi juridicamente correta, que a ordem de um PDF foi recuperada
nem que o extrator preservou toda a formatação.
