# Política de goldens — V4.1

## Sumário de navegação
- Regra
- Fontes aceitáveis
- Campos obrigatórios
- O que não é golden
- Lacunas

## Regra

Golden só nasce de:
1. exemplo oficial publicado; ou
2. caso real conferido por profissional identificado fora da Skill.

Resultado produzido pela própria Skill, por LLM ou por script não vira gabarito.

## Fontes aceitáveis

Ordem de preferência:
1. exemplo numérico publicado em manual/norma oficial;
2. apuração real conferida/assinada por profissional;
3. cálculo manual a partir da norma, conferido por profissional.

## Campos obrigatórios

Cada caso em `official_examples.json` deve registrar:
- `id`;
- entrada;
- resultado esperado;
- `conferido_por`;
- `fonte_do_gabarito`;
- documento, localizador e evidência curta.

## O que não é golden

- invariante matemático;
- concordância engine/verify;
- resultado obtido em execução anterior;
- saída de LLM;
- valor “plausível” sem procedência.

## Lacunas

A ausência de golden não autoriza inventar um. O resultado pode ter verificação redundante de implementação e continuar explicitamente **sem golden específico**.

A V4.1 acrescenta o Exemplo 6 oficial do Manual PGDAS-D para mercado interno + exportação no Anexo I. Nenhum valor produzido pela própria Skill é aceito como golden.
