# Compatibilidade por capacidade

A skill é descrita pelo que o ambiente precisa **conseguir fazer**, não por fornecedor.

| Capacidade | Necessária? | Para quê | Sem ela |
|---|---|---|---|
| Ver as ferramentas MCP da sessão (nome e descrição) | Sim | Descobrir e classificar | Relatório vermelho em "MCP visível"; orientar a instalação |
| Chamar uma ferramenta MCP | Sim | Bateria de leitura | Só a classificação; itens da bateria "não testado" |
| Executar Python 3 local | Não | Rodar `scripts/classificar_ferramentas.py` | Aplicar a tabela de `references/CLASSIFICACAO_FERRAMENTAS.md` à mão, na mesma ordem |
| Ler arquivos da skill | Sim | Consultar as referências | — |
| Pesquisa na internet | Não usa | — | — |

## Onde roda

| Ambiente | Situação em 10/10/2026 |
|---|---|
| Claude Desktop (Mac/Windows) | Roda: aceita skills e MCP local ou remoto |
| ChatGPT Desktop (Mac/Windows) | Roda: aceita skills e conectores MCP no modo desenvolvedor. A execução do script ainda não foi provada nos casos de avaliação |
| claude.ai e chatgpt.com no navegador | Não roda o teste: MCP local não aparece no navegador |

Comando do script: `python3 "$SKILL_ROOT/scripts/classificar_ferramentas.py"`, com `SKILL_ROOT` igual ao
diretório que contém o `SKILL.md`. O host não define essa variável sozinho.
