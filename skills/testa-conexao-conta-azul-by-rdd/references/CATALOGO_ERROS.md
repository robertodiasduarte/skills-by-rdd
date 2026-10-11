# Catálogo de erros da conexão com a Conta Azul

Cada linha diz o que aparece, a causa provável e o próximo passo, no vocabulário de quem opera a Conta Azul.
As chaves da 1ª coluna são as mesmas da tabela "Problemas comuns" da página `/conta-azul/` da plataforma RDD.
Conferido em 10/10/2026 na documentação da API v2 (developers.contaazul.com) e na central de ajuda da Conta Azul.

| Chave | O que aparece | Causa provável | Próximo passo | Fonte |
|---|---|---|---|---|
| `mais_sem_permissao` | acesso negado ao autorizar | O login usado é da Conta Azul Mais (a plataforma do contador), ou a empresa não tem Conta Azul Pro ativa | Autorizar com um usuário da Conta Azul Pro da empresa | Central de ajuda, artigo “API disponível só para a Conta Azul Pro” |
| `invalid_grant` | `invalid_grant` | O código de autorização passou dos 3 minutos, já foi usado, ou o endereço de retorno do MCP difere do cadastrado | Refazer a autorização do início, sem pausa | Portal do Desenvolvedor, erros comuns e FAQ |
| `http_401` | `401 Unauthorized` | A autorização venceu e a renovação falhou, ou a empresa revogou o acesso | Conectar de novo pelo MCP | Portal do Desenvolvedor, erros comuns e revogação de acesso |
| `invalid_token_api_legada` | `invalid_token` com autorização válida | O MCP chama a API antiga (`api.contaazul.com/v1`), que foi desligada | Trocar de MCP: ele não foi atualizado | Central de ajuda, artigo sobre a desativação da API antiga |
| `http_429` | `429 Too Many Requests` | Mais de 10 consultas por segundo ou 600 por minuto na mesma empresa conectada | Esperar um minuto e repetir | Portal do Desenvolvedor, erros comuns |
| `codigo_2fa` | pede código de autenticação | A Conta Azul exige o segundo fator na autorização | Abrir o autenticador de quem autoriza e usar o código atual | Central de ajuda, artigo sobre o código do autenticador |
| `sem_ferramentas_visiveis` | nenhuma ferramenta da Conta Azul aparece | O MCP não está instalado ou ligado, ou a conversa está no navegador | Seguir o passo a passo da página `/conta-azul/` para o seu aplicativo | — |
| `bloqueio_ip` | acesso bloqueado | Filtro de segurança da Conta Azul, por suspeita ou por acesso de fora do Brasil | Falar com o chat do Portal do Desenvolvedor da Conta Azul | Portal do Desenvolvedor, FAQ item 17 |

## Como usar

- Procure a mensagem de erro que a ferramenta devolveu na coluna "O que aparece". Ela pode vir em inglês ou em português.
- Se a mensagem não estiver aqui, diga isso ao usuário, mostre o texto do erro sem valores nem identificadores
  e não invente causa.
- Nunca peça ao usuário o token, o `client_secret` ou a senha para "investigar" o erro.
