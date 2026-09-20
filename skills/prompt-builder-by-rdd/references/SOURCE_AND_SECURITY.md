# Fontes, pesquisa e seguranca

## Hierarquia de estado

Para cada informacao usada na construcao, registrar uma destas origens:

- `usuario`: fornecida diretamente pelo usuario;
- `material`: extraida de documento fornecido;
- `pesquisa_autorizada`: encontrada externamente apos autorizacao explicita;
- `proposta_estrutural`: criada apenas para organizar o prompt;
- `nao_disponivel`: ausente.

Nao promover automaticamente exemplo, opiniao, memoria, blog ou prompt antigo a regra formal.

## Pesquisa externa

A pesquisa fica desligada por padrao. Quando autorizada:

1. pesquisar apenas o que tiver relacao com o escopo;
2. priorizar fontes primarias/oficiais para temas normativos ou temporais;
3. registrar origem, data/versao, jurisdicao e localizador quando disponiveis;
4. distinguir a pesquisa dos materiais fornecidos pelo usuario;
5. nao substituir silenciosamente a base do usuario por fonte nova;
6. se a fonte nova alterar o contrato, revisar o escopo e renovar a confirmacao.

Autorizacao para pesquisar **nao** autoriza transmitir documentos privados ou dados do usuario a terceiros.

## Dados pessoais e confidenciais

Quando detectar dados pessoais ou confidenciais, antes de pedir novos documentos sensiveis:

1. alertar o usuario sobre o risco de tratamento e compartilhamento;
2. sugerir minimizacao, pseudonimizacao ou anonimização quando isso nao destruir a utilidade do material;
3. recomendar avaliacao de plano empresarial/organizacional do fornecedor adequado ao risco;
4. recomendar verificacao de controles e evidencias pertinentes, como SOC 2, ISO 27001/27701, DPA, politicas de retencao, uso de dados para treinamento, criptografia, controle de acesso, SSO/MFA, residencia de dados e requisitos legais da jurisdicao;
5. explicar que certificacao isolada nao garante conformidade com LGPD, GDPR ou outra legislacao;
6. nunca pedir senha, token, chave privada, segredo de API ou certificado secreto.

Nao afirmar que determinado fornecedor possui certificacao atual sem verificacao especifica e atualizada.

## Materiais e cinco gavetas

### Lei/norma
Registrar titulo, autoridade, jurisdicao, versao/vigencia e localizador quando possivel.

### Tabela
Registrar periodo, unidade, fonte das constantes, faixas, limites e arredondamento.

### Caso
Registrar se e real, anonimizado, sintetico, exemplo de estilo, contraexemplo ou gabarito conferido.

### Conta/regra
Registrar formula, variaveis, unidades, ordem, excecoes, arredondamento e fonte de constantes.

### Base
Registrar titulo, versao, finalidade, escopo e se o conteudo e meramente explicativo ou autoritativo.

## Conflitos

Nao inventar hierarquia universal entre fontes. Autoridade, aplicabilidade, vigencia e prevalencia dependem do dominio e da jurisdicao. Se houver conflito material, sinalizar e pedir revisao adequada.
