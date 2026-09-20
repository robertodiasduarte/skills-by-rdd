# Regras do Mapa Semântico / Índice de Remissões

## Objetivo

Gerar um índice temático para RAG a partir de Markdown normativo já ajustado, aumentando recall sem substituir o texto-fonte. O mapa deve apontar para unidades normativas reais e resumir relações de forma curta e recuperável.

## Catálogo de unidades

Antes da síntese semântica:

1. Parsear headings `#` a `######`.
2. Identificar unidades normativas citáveis:
   - `Art. X`;
   - `§ Y` e `Parágrafo único`;
   - incisos;
   - alíneas;
   - capítulos/seções;
   - anexos;
   - tabelas.
3. Manter identificador canônico, linha aproximada, caminho de headings e contexto curto.
4. Registrar sinais explícitos de vigência, revogação ou disposições transitórias.
5. Não transformar mera menção a um artigo em nova unidade normativa.

Usar `scripts/semantic_catalog.py` para obter o catálogo estrutural inicial.

## Taxonomia temática

Criar de 20 a 80 temas quando o tamanho do documento comportar essa faixa.

Permitir menos de 20 quando o documento for curto ou tiver poucas unidades normativas. Registrar a justificativa no README.

Priorizar temas com alto valor de recuperação, por exemplo:
- competência;
- âmbito de aplicação;
- sujeitos abrangidos;
- definições;
- requisitos;
- documentos exigidos;
- procedimentos;
- prazos;
- condições;
- exceções;
- dispensas;
- isenções;
- obrigações;
- vedações;
- fiscalização;
- penalidades;
- recursos;
- vigência;
- transição;
- anexos operacionais.

Esses itens são exemplos de classes funcionais, não uma taxonomia obrigatória. Criar somente temas efetivamente suportados pelo texto.

Evitar:
- temas quase sinônimos;
- nomes vagos como `Regras gerais`;
- temas baseados apenas em frequência lexical;
- microtemas sem utilidade para pergunta;
- tema sem referência normativa.

## Mapeamento tema -> norma

Para cada tema:

1. Identificar artigos centrais.
2. Identificar exceções e condições aplicáveis.
3. Acrescentar parágrafos/incisos quando aumentarem precisão.
4. Ligar definições relevantes.
5. Ligar anexos/tabelas sem reproduzi-los integralmente.
6. Registrar atos correlatos somente se forem mencionados na fonte.
7. Se a localização exata não puder ser determinada, usar literalmente `LOCALIZACAO APROXIMADA` e explicar a incerteza no README.

Nunca inventar identificador para tornar o mapa “completo”.

## Perguntas típicas

Gerar de 2 a 5 perguntas naturais por tema.

As perguntas devem:
- parecer consultas reais de usuário;
- conter vocabulário alternativo quando isso melhorar recall;
- ser respondíveis pelas referências apontadas;
- evitar inserir fatos que não estejam na norma.

Variar intenção, por exemplo:
- quem está sujeito?;
- qual o prazo?;
- quando se aplica?;
- há exceção?;
- quais documentos são exigidos?;
- qual anexo deve ser consultado?

## Regras principais e exceções

Usar bullets curtos e autoexplicativos.

Não copiar artigos longos. Parafrasear de forma fiel e conservadora.

Separar:
- regra principal;
- exceção;
- condição;
- remissão.

Se a distinção não estiver clara no texto, não criá-la artificialmente.

## Relações entre temas

Criar relação quando houver dependência, exceção, sequência procedimental, definição compartilhada ou coocorrência normativa forte.

Formato obrigatório:
`[[Tema: NOME_DO_TEMA]]`

Impor simetria:
- se A relaciona B, B deve relacionar A.

Não criar relações apenas para aumentar densidade do grafo.

## Vigência e versão

Quando o texto contiver informação de vigência, revogação, produção de efeitos ou transição, registrar no tema correspondente.

Quando não houver informação específica para o tema, usar uma formulação neutra, por exemplo:
`- Sem observação específica de vigência nesta entrada.`

Não inferir data de vigência a partir da data de processamento.

## Anexos e tabelas

Para cada anexo/tabela identificável, registrar:
- o que é;
- quando se aplica;
- como usar;
- referências no corpo.

Não colar o conteúdo integral.

Quando o documento apenas menciona anexo/tabela externa sem fornecer conteúdo suficiente, dizer que a fonte apenas o menciona.

## Stop conditions

Encerrar a etapa semântica quando:
1. o Markdown não puder ser lido;
2. o conteúdo estiver vazio ou insuficiente;
3. não houver headings nem unidades normativas confiáveis;
4. o conteúdo for predominantemente tabela sem referências textuais que permitam mapeamento sem especulação.

## Verificação final

Executar `scripts/validate_semantic_map.py`.

Corrigir:
- relações unilaterais;
- tema sem bloco obrigatório;
- referência ausente da fonte;
- quantidade inválida de perguntas;
- inconsistência entre taxonomia e blocos;
- ausência de índice de anexos/tabelas quando aplicável.

Warnings de estilo podem ser mantidos quando justificados. Warnings de integridade factual ou referencial devem ser resolvidos.
