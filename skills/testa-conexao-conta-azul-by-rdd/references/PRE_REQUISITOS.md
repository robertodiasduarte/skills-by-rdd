# Pré-requisitos da conexão

Os mesmos 5 itens do checklist "Antes de começar" da página `/conta-azul/`. Conferidos em 10/10/2026.

| # | Pergunta ao usuário | Como saber | Se a resposta for não |
|---|---|---|---|
| 1 | A empresa está na **Conta Azul Pro**? | Pelo painel de parceiro: Clientes › Meus clientes › Acessar Conta Azul Pro. A Conta Azul Mais (plataforma do contador) não autoriza API | A conexão não sai. Cada empresa conectada precisa da própria Pro (central de ajuda: artigo “API disponível só para a Conta Azul Pro” e artigo sobre a Conta Azul Mais para parceiros) |
| 2 | Quem vai autorizar é um **usuário da Pro da empresa**, com o autenticador dele? | A autorização pede login e código de dois fatores. Se o login de parceiro do contador serve para isso ainda não está confirmado | Combinar com o dono da empresa quem autoriza |
| 3 | A conversa está no **Claude Desktop** ou no **ChatGPT Desktop**? | É o aplicativo instalado no computador, não a aba do navegador | No navegador o MCP local não aparece: abrir o aplicativo de computador |
| 4 | O **autenticador** de quem autoriza está à mão? | O código de autorização vale 3 minutos | Se passar disso, aparece `invalid_grant`: refazer sem pausa |
| 5 | O usuário sabe que a autorização **lê e escreve** tudo no ERP do cliente? | A Conta Azul não tem autorização só de leitura; quem limita a IA a consultar é o MCP | Recomendar um MCP que só lê, ou com trava de escrita |

Pergunte uma vez, em uma única mensagem curta. Respostas "não sei" não bloqueiam o teste: anote no relatório.
