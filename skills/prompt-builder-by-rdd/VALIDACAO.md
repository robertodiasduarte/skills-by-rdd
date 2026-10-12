# Validação da entrega

Versão: 5.0.0
Data: 2026-10-12
Base: prompt-builder do SDD Open by RDD, v2.0.0 (11/09/2026)

## O que foi verificado

| Verificação | Status | Evidência resumida |
|---|---|---|
| Corpo do `SKILL.md` idêntico à cópia pública do SDD Open | `executado_aprovado` | `cmp` byte a byte de tudo o que vem depois do frontmatter |
| As 3 references idênticas à cópia pública | `executado_aprovado` | `cmp` de `prompt-building-rules.md`, `output-template.md` e `sdd-integration.md` |
| Frontmatter | `executado_aprovado` | `name`, `description` (igual à da cópia pública), `license`, `metadata.author` e `metadata.version` |
| Conteúdo proibido em repositório público | `executado_aprovado` | `scripts/publish-check.sh` do catálogo, mais uma varredura de vocabulário privado |
| Empacotamento | `executado_aprovado` | `scripts/package.sh`; o zip tem 10 arquivos sob `prompt-builder-by-rdd/` e declara 5.0.0 |
| Herança entre skills do catálogo | `executado_aprovado` | `scripts/heranca-check.py` |

## O que esta validação não prova

- Que a skill se comporta da mesma forma em todos os produtos de IA. A validação é estrutural: confere arquivos e texto, não executa a skill num modelo.
- Que um prompt gerado está correto para o seu processo. A skill organiza o contrato do prompt; as regras do domínio continuam sendo responsabilidade de quem as fornece.

Esta versão não traz cenários de avaliação próprios. Os da 4.0.0 testavam um fluxo (brainstorm com gate de confirmação) que a 5.0.0 não tem, e por isso saíram junto com ela.
