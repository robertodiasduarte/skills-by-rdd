# Formatos rígidos do Mapa Semântico

## Nome dos arquivos

### Sem UF fornecida

Usar literalmente `UF-MAPA-XX` como prefixo:

- `UF-MAPA-XX_{NOME_BASE}_Mapa-Semantico_Indice-Remissoes_ate-AAAA-MM-DD.md`
- `UF-MAPA-XX_{NOME_BASE}_README_Mapa-Semantico_ate-AAAA-MM-DD.txt`

### Com UF fornecida

Usar `UF-{SIGLA}`:

- `UF-SP_{NOME_BASE}_Mapa-Semantico_Indice-Remissoes_ate-AAAA-MM-DD.md`
- `UF-SP_{NOME_BASE}_README_Mapa-Semantico_ate-AAAA-MM-DD.txt`

Derivar `NOME_BASE` do nome do Markdown de origem sem extensão:
- remover acentos;
- trocar espaços por hífen;
- remover caracteres especiais;
- manter letras, números, hífen e underscore.

Usar a data fornecida pelo usuário quando existir; caso contrário, usar a data corrente.

## Template obrigatório do mapa

Usar esta estrutura e estes títulos:

```markdown
# Mapa Semântico (Índice de Remissões por Tema)

## Metadados
- Fonte: {nome_do_md_origem}
- Data: {AAAA-MM-DD}
- Total de temas: {N}
- Observações: {curto}

## Taxonomia de Temas
1. {TEMA_1}
2. {TEMA_2}

## Entradas por Tema

### Tema: {NOME_DO_TEMA}
**Perguntas típicas**
1. ...
2. ...

**Onde está na norma**
- Art. ...
- § ...
- Anexo ...

**Regras principais**
- ...
- ...

**Exceções e condições**
- ...

**Relacionados**
- [[Tema: ...]]
- [[Tema: ...]]

**Vigência/versão**
- ...

## Índice de Anexos e Tabelas

### {Anexo/Tabela}: {IDENTIFICADOR}
- O que é: ...
- Aplicável quando: ...
- Como usar: ...
- Referências no corpo: Art. ...; Seção ...;
```

Repetir o bloco `### Tema:` uma vez por tema.

Se não houver anexos ou tabelas, manter `## Índice de Anexos e Tabelas` e escrever:
`- Nenhum anexo ou tabela identificável na fonte.`

## Template obrigatório do README semântico

O arquivo deve ser texto puro, sem Markdown estrutural, HTML ou XML:

```text
============================================================
RELATORIO - MAPA SEMANTICO / INDICE DE REMISSOES
============================================================

ARQUIVO DE ORIGEM:
- Nome: {nome_origem}
- Data de processamento: {AAAA-MM-DD}

ESCOPO:
- Objetivo RAG: aumentar recall e reduzir perda em temas distribuidos.
- Itens gerados: Mapa Semantico (MD) + Relatorio (TXT).

ESTATISTICAS:
- Temas criados: {N}
- Entradas com remissao bidirecional: {K}
- Unidades normativas identificadas: {contagem_artigos} artigos; {contagem_anexos} anexos; {contagem_tabelas} tabelas

CRITERIOS E REGRAS:
- Temas em linguagem funcional.
- Referencias somente ao que existe no arquivo origem.
- Anexos/tabelas indexados por "como usar" sem colagem integral.

LIMITACOES / PENDENCIAS:
1) ...
2) ...

ARQUIVOS GERADOS:
- Mapa (MD): {NOME_MAPA_MD}
- Relatorio (TXT): {NOME_README_TXT}

============================================================
FIM
============================================================
```

Preferir ASCII simples no README quando isso não reduzir clareza. Manter linhas em aproximadamente 120 caracteres quando possível.

## Contrato da resposta no modo semantic

A resposta final no chat deve conter apenas:
- linha 1: link de download do mapa `.md`;
- linha 2: link de download do relatório `.txt`.

Não incluir nomes de arquivo, títulos, bullets, explicações ou conteúdo inline.

## Contrato da resposta no modo full

Entregar quatro links, um por linha:
1. Markdown ajustado;
2. README de parsing;
3. Mapa Semântico;
4. README do mapa.

Não imprimir os conteúdos inline.
