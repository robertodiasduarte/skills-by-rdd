# Registro da confirmação do escopo

| Campo | Valor |
|---|---|
| Escopo | CA001 |
| Revisão | 2 (vigente) |
| SHA-256 do escopo | `81a8452f46302b943dc2760a4cf8cf71da19714e3d5cac3e8dc4d1f3b899c3f1` |
| Frase recebida | `CONFIRMO O ESCOPO CA001 V2 E AUTORIZO GERAR A SKILL.` |
| Quem confirmou | Roberto Dias Duarte |
| Quando | 11/10/2026, depois da apresentação do resumo integral |
| Verificação | `scope_gate.py check` do skill-builder-by-rdd: `ESCOPO_CONFIRMADO`, `geracao_autorizada: true` |
| Limite | O registro prova consistência entre escopo e frase; a autoria da mensagem depende do host da conversa |

Histórico: a V1 (`90643ee2…`) foi confirmada antes, no mesmo dia, com a frase da V1. A V2 nasceu da revisão
pós-build: o usuário passa a aprovar a lista de ferramentas antes de qualquer chamada.

Na V1, uma primeira resposta ("Confirmo o escopo CA001 V1") foi recusada pelo gate por não trazer a frase completa,
que inclui a autorização de gerar; a geração só começou depois da frase exata.

Qualquer mudança de cobertura, exclusão, período, material, regra, saída, perfil ou ferramenta invalida esta
confirmação e exige uma nova versão do escopo.
