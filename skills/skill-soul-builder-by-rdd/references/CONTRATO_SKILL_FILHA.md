# Contrato da `skill-soul-{company}`

## Nome e pacote
Gerar slug em kebab-case. O diretório e o `name` devem seguir `skill-soul-{company-slug}`. Se o nome exceder limites do host, abreviar o slug da empresa sem perder o prefixo `skill-soul-`.

Estrutura mínima:

```text
skill-soul-company/
  SKILL.md
  CHANGELOG.md
  manifest.json
  references/
    ALMA_DA_EMPRESA.md
    COMO_FUNCIONA.md
    RUNTIME_COMPATIBILITY.md
  evals/
    cases.json
```

Adicionar `agents/openai.yaml` somente como adaptador opcional quando fizer sentido para o ambiente. Não criar scripts se a tarefa for apenas análise e transformação textual.

## Frontmatter obrigatório
A skill-filha deve declarar:
- `name`;
- `description` com gatilhos concretos;
- `license: MIT`;
- `metadata.author: Roberto Dias Duarte`;
- `metadata.methodology: Metodologia de Roberto Dias Duarte`;
- `metadata.version` sincronizada com a alma.

No corpo, incluir:

```markdown
## Metodologia e autoria
Esta skill foi construída com a metodologia de Roberto Dias Duarte.
```

## Fonte canônica
A primeira ação da skill-filha é consultar `references/ALMA_DA_EMPRESA.md` quando o pedido depender de voz, posicionamento, valores ou mensagens. Não inventar regras de marca fora desse arquivo.

## Modos
### Consultivo
Usar em conversa normal quando o usuário pede orientação, estratégia, explicação ou quando o modo não é explicitamente definido e o contexto não exige saída limpa. Pode apontar desalinhamentos e sugerir alternativas.

### Transformação
Usar quando o usuário pede reescrita/adaptação direta, quando informa `modo=transformacao` ou quando um fluxo exige conteúdo limpo. Não adicionar sermões ou perguntas se houver dados suficientes. Limites factuais e de segurança continuam valendo.

### Auditoria
Usar quando o usuário pede avaliação de alinhamento. Diagnosticar a peça em relação à alma, mostrando critérios e desvios. Não reescrever salvo pedido explícito.

Se o modo puder ser inferido com segurança, não perguntar. Se for material e ambíguo, pedir escolha apenas em chat interativo; em automação, usar o modo informado no payload ou o comportamento definido pelo fluxo.

## Capacidades mínimas
A skill-filha deve conseguir:
- reescrever posts;
- criar landing pages;
- adaptar conteúdo para LinkedIn e outros canais;
- avaliar campanhas;
- elaborar manifestos de campanha;
- ajustar relatórios e documentos ao tom de voz;
- criar mensagens e narrativas de marca;
- transformar conteúdo em automações;
- explicar desalinhamentos quando em modo consultivo ou auditoria.

## Barreira factual
Nunca usar “está na alma” como prova de segurança, conformidade, resultado, certificação, qualidade técnica, desempenho ou qualquer fato externo. Preservar ou criar alegações apenas quando fornecidas como fatos pelo usuário/material ou quando houver evidência apropriada.

## Saída em chat
Entregar o conteúdo pedido no formato natural do canal. Quando reescrever um texto, priorizar o texto final e evitar análise longa salvo solicitação.

## Saída em automação
Seguir `CONTRATO_AUTOMACAO_JSON.md` incorporado pela meta-skill ou reproduzir seu schema no pacote da filha. Se `output=json`, não escrever texto fora do objeto.

## Atualização
Quando o usuário pedir mudança na alma, a atualização deve ocorrer via `skill-soul-builder-by-rdd` ou processo equivalente que modifique `ALMA_DA_EMPRESA.md`, `SKILL.md` quando necessário, `manifest.json` e `CHANGELOG.md` com versão sincronizada.
