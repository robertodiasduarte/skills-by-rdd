# Fornecedor provável do MCP

A skill não pressupõe nomes de ferramentas: ela olha o que está na sessão e descreve o **tipo** de MCP.
Isto não é recomendação de fornecedor. Corte: 10/10/2026.

| Tipo | Como reconhecer | O que dizer no relatório |
|---|---|---|
| MCP da própria Conta Azul | Sem fonte pública em 10/10/2026: não há padrão de nome conhecido | Não afirmar que um MCP é da Conta Azul só pelo nome. Dizer "fornecedor não identificado" e sugerir conferir na documentação do próprio MCP |
| MCP local de terceiro | Ferramentas aparecem como servidor local do aplicativo (extensão ou arquivo de configuração) | "MCP local: roda no seu computador. Onde ele guarda a autorização e para onde envia os dados depende do MCP — confira na documentação dele" |
| Conector remoto de terceiro | Ferramentas vêm de um conector com endereço na internet | "Conector remoto: a autorização e as consultas passam pelo servidor de quem mantém o conector" |
| Desconhecido | Nenhum dos sinais acima | "Fornecedor não identificado" |

Em qualquer tipo: se houver ferramenta de **escrita**, o alerta de segurança vale. Para avaliar o código de
um MCP antes de instalar, a indicação é a skill `rdd-audita-harness` — esta skill não audita código.

Atualização: quando houver fonte pública sobre um MCP da Conta Azul, esta tabela ganha os padrões dele
numa nova versão (v1.1), sem mudar o procedimento.
