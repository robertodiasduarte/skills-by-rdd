# Como funciona — em uma página, para o contador

**Para que serve.** Você instalou um MCP da Conta Azul no Claude Desktop ou no ChatGPT Desktop e quer saber
se ele funciona com a empresa do seu cliente, sem correr o risco de lançar, alterar ou dar baixa em nada.

**O que você pede.** "Teste minha conexão com a Conta Azul."

**O que a skill faz.**
1. Pergunta, numa mensagem só, os 5 pré-requisitos (Conta Azul Pro, quem autoriza, aplicativo de computador,
   autenticador, ciência de que a autorização lê e escreve).
2. Olha as ferramentas que o MCP oferece e separa cada uma em **leitura**, **escrita** ou **indeterminada**.
   Na dúvida, indeterminada. "Baixa" é sempre indeterminada: na Conta Azul, dar baixa é quitar.
3. Mostra a lista das ferramentas de leitura que vai chamar e **espera o seu ok**. Se alguma parecer escrever no
   ERP, tire da lista: ela não é chamada. A separação é feita por uma lista de palavras e não pega todo verbo:
   **leia a descrição** de cada ferramenta antes de dar o ok.
4. Chama **só** as de leitura aprovadas: a empresa conectada e 1 registro de pessoas, financeiro e vendas.
5. Entrega um relatório verde, amarelo ou vermelho por item, com a causa provável e o próximo passo.

**O que ela não faz.** Não pede nem aceita senha, token ou `client_secret`. Não chama ferramenta de escrita,
nem para testar. Não instala nem configura o MCP. Não analisa os seus dados: mostra só o nome da empresa e
quantos registros leu. Não audita o código do MCP — para isso, use a skill `rdd-audita-harness`.

**Como ler o resultado.** Verde quer dizer: o MCP está instalado, a empresa responde e as consultas de leitura
funcionam. Vermelho em "Segurança" quer dizer que o MCP tem ferramentas que escrevem no ERP: elas não foram
chamadas, mas a IA poderia chamá-las numa conversa comum. Prefira um MCP só leitura.

**Quem decide.** Você. A skill só informa.
