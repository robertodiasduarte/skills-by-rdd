# Compatibilidade por capacidades

## Núcleo portátil

O protocolo depende de leitura de texto e diálogo, não de nomes de ferramentas,
modelo ou fornecedor. A extensão Agent Skills usa SKILL.md com frontmatter YAML e
recursos opcionais; o suporte real é uma característica do aplicativo que hospeda
o modelo, não uma garantia derivada de seu nome.

Usar o mesmo protocolo em Claude, ChatGPT, Grok, Kimi ou outro ambiente quando ele
aceitar as instruções e disponibilizar o contexto necessário. Não declarar instalação
nativa ou equivalência de comportamento sem testar a superfície específica.

## Modos

| Modo | Capacidades | Entrega e limite |
|---|---|---|
| Conversacional | Texto e diálogo | Brainstorm, escopo, confirmação e conteúdo dos arquivos; controle apenas conversacional |
| Arquivos | Leitura e escrita | Pacote estruturado e referências; scripts ainda não executados |
| Executável | Arquivos e Python 3 | Gate de escopo, hashes, lint e testes locais |
| Isolado | Sessões/contextos realmente separados | Permite organizar motor e verificador sem expor um ao outro; exige evidências |
| Integrado | Conectores autorizados | Somente as ações aprovadas; integração não é requisito do núcleo |

Para os scripts fornecidos, usar Python 3.10 ou superior e biblioteca padrão.
Não presumir shell POSIX em todos os ambientes. Em um executor Python sem shell,
invocar o mesmo script com uma lista de argumentos e caminhos reais.
As variáveis mostradas nos comandos são convenções documentais, não recursos do modelo.

## Uso em um chat comum

Colar o conteúdo de `SKILL.md` e das referências do pacote que forem pertinentes ao caso.
Pedir que o assistente inicie o brainstorm.
Se o ambiente não conseguir ler algum recurso, fornecer o texto pertinente.

Sem persistência, salvar o resumo e o registro de aprovação externamente.
Se o contexto for perdido, não presumir que uma versão antiga continua autorizada.
Recuperar o contrato e o registro confiável; em caso de dúvida, reconfirmar.

A versão em texto não executa Python nem implementa uma barreira de segurança.
Não pode garantir que todos os modelos seguirão o protocolo com igual fidelidade.

## Uso com suporte nativo a skills

Importar o pacote ou colocar o diretório no local aceito pelo host, conforme sua
documentação atual. Não tratar um ZIP como instalável em qualquer produto.
Disponibilidade e instalação variam com conta, configuração e superfície.

O arquivo agents/openai.yaml deste pacote contém apenas rótulos de interface.
É um adaptador opcional, não dependência do fluxo. O padrão RDD descrito na fonte
deliberadamente o omite: removê-lo ao preparar uma exportação canônica RDD.
Os scripts não importam esse arquivo.

## Fontes externas consultadas para esta adaptação

Consulta em 20/09/2026, limitada ao formato e às condições de execução, sem pesquisa
de legislação nem complementação da base normativa do usuário.

- Agent Skills, “Specification”: diretório, frontmatter e recursos opcionais;
  allowed-tools é experimental. URL: `https://agentskills.io/specification`.
- OpenAI, “Skills in ChatGPT”: disponibilidade e instalação variam conforme produto
  e configurações. URL: `https://help.openai.com/en/articles/20001066-skills-in-chatgpt`.
- Anthropic, “Skills overview”: skills usam o padrão e dependem das capacidades do
  produto. URL: `https://claude.com/docs/skills/overview`.

Não foi feita validação nativa em Claude, ChatGPT, Grok ou Kimi.
Não foi verificado suporte nativo de Grok ou Kimi; o caminho proposto para eles é
a leitura das instruções em modo conversacional, condicionada ao ambiente.
