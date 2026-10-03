# Compatibilidade por capacidades

## Núcleo portátil
A metodologia depende de leitura, diálogo e geração de texto. Não depende de um fornecedor específico.

## Modos de ambiente
**Conversacional:** conduz entrevista, sintetiza alma e entrega conteúdo dos arquivos em blocos.

**Com arquivos:** cria diretório da skill-filha e seus recursos.

**Com empacotamento:** entrega ZIP com raiz única, se o ambiente permitir.

**Com pesquisa:** consulta fontes públicas somente após autorização do usuário.

**Com agentes/orquestradores:** a `skill-soul-{company}` pode ser usada como instrução de transformação e responder em JSON. Make e n8n são exemplos de orquestradores, não dependências.

## ChatGPT e Claude
O pacote pode ser usado em ambientes que aceitem skills ou instruções equivalentes, desde que o host ofereça as capacidades necessárias. Não afirmar suporte nativo, instalação ou comportamento idêntico sem teste naquele produto e plano.

## Automação
Em fluxos sem interação humana, definir `modo`, tarefa e formato de saída no payload. Não fazer perguntas conversacionais dentro do pipeline; retornar status estruturado quando faltar contexto.

## Limites
A existência de uma skill não prova persistência, isolamento, controle de acesso, DLP, suporte a ZIP ou conectores. Essas capacidades pertencem ao host.
