# Escopo confirmado — CA001 V2

Confirmado em 11/10/2026 com a frase `CONFIRMO O ESCOPO CA001 V2 E AUTORIZO GERAR A SKILL.`
(registro em `references/CONFIRMACAO.md`). Perfil pedido: operacional. Perfil efetivo: **C**.
A V1 foi confirmada antes, no mesmo dia; a V2 acrescentou a confirmação do usuário antes de qualquer chamada.

**Objetivo.** Verificar se a conexão MCP com a Conta Azul de uma empresa funciona, só com leitura, e explicar
ao contador o que fazer em cada falha.

**Público.** Contador que atende empresas na Conta Azul Pro e usa Claude Desktop ou ChatGPT Desktop.
**Jurisdição.** Brasil; empresas com conta ativa na Conta Azul Pro (API v2).

## Cobre
1. Conferir pré-requisitos: Pro × Mais, app de computador, autenticador e autorização da empresa
2. Descobrir as ferramentas MCP da Conta Azul na sessão e o fornecedor provável
3. Classificar cada ferramenta em leitura, escrita ou indeterminada e alertar quando houver escrita
4. Mostrar as ferramentas de leitura e chamar só após o ok do usuário: empresa e 1 registro por módulo
5. Emitir relatório verde, amarelo ou vermelho por item, com causa provável e próximo passo
6. Traduzir os erros do catálogo: código expirado, invalid_grant, 401, 429, conta Mais, API antiga
7. Sem MCP visível, orientar a instalação pelo passo a passo da página /conta-azul/
8. Explicar como revogar a autorização dada à Conta Azul

## Não cobre
1. Chamar a API da Conta Azul diretamente ou pedir client_id, client_secret, token ou senha
2. Executar ferramenta de escrita ou indeterminada, nem como teste
3. Editar arquivo de configuração do app ou instalar MCP (só mostra o passo a passo)
4. Analisar dados contábeis ou financeiros retornados: mostra só contagens e o nome da empresa
5. Consolidar ou comparar empresas
6. Auditar a segurança do código de um MCP de terceiro (é a skill auditar-harness)
7. Funcionar no navegador sem MCP (claude.ai e chatgpt.com web)
8. Guardar ou exportar os dados retornados

> Nota editorial (11/10/2026, depois da confirmação): a skill de auditoria citada na exclusão 6 se chama, no
> catálogo público, **`rdd-audita-harness`**; `auditar-harness` é o nome interno dela. A exclusão é a mesma — só o nome
> foi corrigido nos demais arquivos para o aluno conseguir achá-la. O texto acima é o literal confirmado.

## Períodos
- **Consulta:** dados ao vivo no momento do teste; catálogo de erros e padrões de fornecedor com corte em 10/10/2026.
- **Cálculo:** não aplicável.

## Entradas e saída
- Entradas: o pedido do usuário; as ferramentas MCP visíveis (nome e descrição); as respostas aos pré-requisitos.
- Saída: relatório Markdown com fornecedor provável, empresa conectada, ferramentas por classe, resultado por item,
  alertas e próximos passos.

## Materiais
- M1 (base): descobertas técnicas sobre a API v2 e a central de ajuda, conferidas em 10/10/2026.
- M2 (regra): plano da frente, §4.2 a §4.7 (escopo, heurística, bateria, catálogo, casos).

## Lacunas declaradas
- Nenhuma saída real de MCP da Conta Azul como amostra; exemplos são ilustrativos.
- Nomes de ferramentas de um MCP da própria Conta Azul: sem fonte pública em 10/10/2026.
- Contador autorizar pelo login de parceiro da Mais: não confirmado.
- Execução de script no ChatGPT Desktop: a provar nos casos E1–E7.

## Revisão humana
O contador aprova a lista de ferramentas antes de qualquer chamada e decide se usa o MCP; a skill só informa.
Os 8 casos de avaliação são rodados por Roberto nos 2 apps antes da publicação.
