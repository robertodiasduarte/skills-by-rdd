# Contrato de geração da skill-filha

## Antes da geração

Gerar apenas após a mensagem real de aprovação do resumo versionado.
Congelar entradas, saídas, jurisdição, períodos, materiais, hipóteses, exclusões,
perfil efetivo, ferramentas e critérios de aceite. Guardar a confirmação e o escopo
anonimizados, sem incorporar histórico privado desnecessário ao pacote público.

O brainstorm e seus modelos podem existir antes da aprovação. A skill-filha,
seu texto operacional final e seus executores não.

## Passes

**Núcleo:** produzir SKILL.md, escopo, inventário e manifesto compatíveis com a versão
confirmada. Não expandir fronteiras para parecer mais completo.

**Domínio:** catalogar fontes e regras realmente disponíveis, apontar lacunas e
montar a navegação do corpus. Não escrever páginas conceituais para substituir
silenciosamente os documentos do responsável.

**Cálculo, quando elegível:** seguir PERFIS_CALCULOS.md. Motor e verificador em
contextos separados, com contrato comum e provas registradas. Sem isso, declarar a
limitação e não liberar cálculo.

**Auditoria:** gerar casos positivos e negativos, testar o que o ambiente permitir,
reparar apenas os defeitos encontrados e registrar o não provado.

**Entrega:** conferir novamente escopo, aprovação, materiais, referências e inventário.
Não publicar nem instalar automaticamente.

## Estrutura mínima

```text
nome-em-kebab-case/
  SKILL.md
  CHANGELOG.md
  manifest.json
  references/
    ESCOPO_CONFIRMADO.md
    COMO_FUNCIONA.md
    RUNTIME_COMPATIBILITY.md
  evals/
    cases.json
```

Acrescentar somente os recursos que o perfil e o processo exigirem.
Para B: corpus Markdown, INDEX, SOURCE_CATALOG, ancoragem, busca e barreira documental
quando tecnicamente implementadas; router/graph para base extensa, conforme a fonte.
Para A: SOURCES, RULE_MAP, FORMULAS, GLOSSARIO, schemas fechados, tabelas por período,
goldens com procedência, testes e scripts verificados. Não gerar todos os anos por rito.
Para AB: combinar sem duplicar fontes.
Para C: não inventar base ou camada de cálculo.

O inventário canônico completo consta no §3 da documentação RDD.
Os templates originais citados no §5 não foram anexados como código executável.
Quando a fidelidade aos templates da plataforma for requisito, solicitá-los.
Código novo deve ser identificado como implementação nova, testada separadamente;
não usar “boilerplate oficial RDD” para algo reconstruído da descrição.

## SKILL.md

Frontmatter: name e description obrigatórios. Em toda skill-filha gerada, incluir
obrigatoriamente `license: MIT`, `metadata.author: Roberto Dias Duarte` e
`metadata.methodology: Metodologia de Roberto Dias Duarte`. Compatibility e allowed-tools
continuam opcionais conforme o ambiente. Versão, se usada, fica dentro de metadata.
Não depender de ferramentas nomeadas de um fornecedor.

No corpo de toda skill-filha, incluir `## Metodologia e autoria` com a frase literal:
`Esta skill foi construída com a metodologia de Roberto Dias Duarte.`

Name: kebab-case, até 64 caracteres, sem hífens consecutivos ou nas pontas,
igual ao diretório. Preservar as palavras reservadas da validação RDD.
Description: terceira pessoa, até 1.024 caracteres, ação e gatilhos concretos,
períodos consultivo e de cálculo, vizinhos excluídos. Não usar filtro que confunda
numerais romanos com primeira pessoa.

Corpo: menos de 500 linhas, sem emojis, com estas oito seções nesta ordem:
```markdown
# Nome
## Quick start
## Quando usar / Quando não usar
## Dados necessários
## Procedimento passo a passo
## Validações e checklist de qualidade
## Tratamento de exceções
## Examples
```

Acrescentar as seções de perfil sem alterar a ordem:
Texto canônico de recusa; Base documental; Navegação; Protocolo de ancoragem;
Scripts determinísticos; Política de internet; Segurança documental;
Inventário do bundle, conforme aplicável.

O padrão de oito seções é uma decisão RDD, não uma exigência universal da spec aberta.
Citar todos os scripts no SKILL.md. Não deixar referências a arquivos prometidos na
entrega final. Mover detalhes para references/, mantendo a entrada enxuta.

Comandos de scripts:
`python3 "$SKILL_ROOT/scripts/arquivo.py"`.
Definir SKILL_ROOT pelo diretório real. Não depender do diretório corrente.
Não afirmar que o host reconhece a variável automaticamente.

## Manifesto e transparência

Separar:
perfil pedido; perfil efetivo; cobertura consultiva; cobertura de cálculo;
caminhos implementados; caminhos liberados; fontes e versões; ferramentas necessárias;
testes escritos; testes executados; testes aprovados; pendências.

Incluir o bloco “O que esta skill ainda NÃO prova”.
Não usar um booleano genérico `validado=true` para substituir essas distinções.
Não incluir valores de confirmação, nomes de clientes ou dados reais em exemplos públicos.

Se um contrato dependia de cálculo e os testes não o liberaram, apresentar a redução
ao usuário e renovar aprovação; não entregar silenciosamente uma consultora diferente.

## Recusas e respostas

Definir recusas específicas de fora de escopo, corte temporal e dado faltante.
Um caso válido deve demonstrar atendimento: o teste positivo evita aprovar uma skill
que só recusa tudo. Não devolver uma recusa seguida da resposta proibida.

Uma conclusão profissional condicionada a premissa deve ser marcada como sugerida,
com a premissa e o responsável pela revisão. Não confundir cálculo com enquadramento.

## Empacotamento

ZIP com uma raiz única igual ao name e SKILL.md na raiz dessa pasta.
Na exportação destinada ao RDD, aplicar teto de 120 arquivos e 25 MB conforme a
documentação enviada; não generalizar esses tetos a todos os fornecedores.

Recusar caminhos absolutos, travessia, links simbólicos, colisões de nomes e lixo de
arquivador. Não incluir ZIP dentro do ZIP. Recursos precisam ter função documentada.
Não entregar fontes tipográficas do ambiente.

A criação do pacote não prova aceitação na plataforma RDD: o código-fonte de seu
validador não foi executado aqui. Validar também no destino quando estiver disponível.
