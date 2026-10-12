# Skills by RDD

Skills profissionais para contabilidade, tributos, trabalhista, jurídico e marketing — prontas para instalar no seu ChatGPT, Claude, Claude Code ou Codex.

Cada skill aqui resolve um trabalho que se repete. Você instala uma vez e aciona pelo nome, dentro do app de IA que já usa.

## As skills

### `parsing-chunking-by-rdd`

**Prepara DOCX, PDF e TXT para virar base de conhecimento de IA.**

Extrai o texto, corrige o ruído de layout, organiza em Markdown por seção e retira o que está tachado ou explicitamente revogado — sempre com evidência no próprio documento. Devolve o Markdown ajustado e um relatório do que saiu. Quando você pede, também monta o mapa semântico e o índice de remissões do material.

Não faz OCR, não reescreve e não decide vigência por conta própria.

Três modos: `parse` (o padrão), `semantic` (mapa semântico sobre Markdown já ajustado) e `full` (os dois em sequência).

[Baixar o .zip](../../releases/latest/download/parsing-chunking-by-rdd.zip)

### `prompt-builder-by-rdd`

**Escreve o prompt de produção do seu app ou da sua automação.**

Gera um único prompt pronto para rodar dentro do sistema, com contrato de saída explícito: o que entra, o formato exato do que sai, as fórmulas de cada cálculo e o que fazer quando faltar informação. Corta o texto decorativo e devolve um único bloco para colar.

Não escreve e-mail, texto de tela nem documentação; é para o prompt que roda dentro do sistema. É a mesma skill que o SDD Open by RDD distribui como `sdd-prompt-builder`.

**Versão 5.0.0:** é outra skill com o mesmo nome da 4.x. Se você instalou a 4.x, remova-a antes de instalar a 5.0.0. A 4.0.0 continua na Release v1.2.0, como histórico.

[Baixar o .zip](../../releases/latest/download/prompt-builder-by-rdd.zip)

### `skill-builder-by-rdd`

**Transforma um processo seu em uma skill profissional.**

Ela entrevista você sobre o trabalho, pede os materiais que sustentam as regras, fecha o escopo por escrito e só então gera a skill — depois da sua confirmação. Entrega outra skill, não a resposta do caso contábil que você usou como exemplo.

A skill que ela cria não vem com motor de cálculo verificado: para conta conferida por dois caminhos independentes, use a esteira "Skill avançada" da plataforma RDD.

[Baixar o .zip](../../releases/latest/download/skill-builder-by-rdd.zip)

## Omie

### `skill-builder-omie-by-rdd`

**Cria skills que consultam e operam o ERP Omie pelo conector oficial, testadas na sua empresa antes da entrega.**

Filha da `skill-builder-by-rdd`: mesma entrevista e mesma confirmação do escopo antes de gerar. Duas perguntas decidem o perfil da skill gerada. **Operador** mostra e grava (pedido, OS, tarefa) com um protocolo de confirmação literal e nunca soma valores. **Conferidor** soma por script e só entrega o total quando leu exatamente o que a Omie informou. Exige o conector MCP do Omie; o perfil Conferidor exige também Claude Code. Não gera skill que fatura ou inutiliza.

A explicação passo a passo está em [robertodiasduarte.com.br/skills-omie](https://www.robertodiasduarte.com.br/skills-omie/).

[Baixar o .zip](../../releases/latest/download/skill-builder-omie-by-rdd.zip)

### `omie-atrasos-conferidos-by-rdd` (exemplo gerado pela filha)

Títulos atrasados a receber e a pagar em três faixas, com quantidade informada pela Omie e valor somado por script com conferência. Perfil Conferidor.

[Baixar o .zip](../../releases/latest/download/omie-atrasos-conferidos-by-rdd.zip)

### `omie-tirar-pedido-by-rdd` (exemplo gerado pela filha)

Monta o pedido de venda ditado, mostra na tela e só inclui com a frase literal de confirmação. Perfil Operador.

[Baixar o .zip](../../releases/latest/download/omie-tirar-pedido-by-rdd.zip)

## Marketing

### `skill-soul-builder-by-rdd`

**Transforma a história dos sócios na voz da sua empresa, numa skill que o time inteiro usa.**

Conduz uma entrevista em texto livre sobre a história dos fundadores e da fundação, separa o que você relatou do que ela inferiu e gera dois arquivos: o `ALMA_DA_EMPRESA.md` (essência, valores, personalidade, tom de voz, vocabulário e mensagens da marca) e uma segunda skill, `skill-soul-<sua-empresa>`, que escreve, reescreve e confere textos nessa voz. A skill da empresa tem três modos — orientar, reescrever e conferir — e responde em JSON limpo quando usada em automação (Make, n8n ou outro orquestrador).

Funciona para qualquer setor. Não inventa fatos, não valida alegações técnicas ou jurídicas, não leva detalhes íntimos para a skill da empresa e só pesquisa na internet se você autorizar. Os casos de teste que acompanham o pacote ainda não foram executados em cada aplicativo.

A explicação passo a passo, com exemplos, está em [robertodiasduarte.com.br/skills-marketing](https://www.robertodiasduarte.com.br/skills-marketing/).

[Baixar o .zip](../../releases/latest/download/skill-soul-builder-by-rdd.zip)

### `newsletter-reforma-tributaria-by-rdd`

**Pesquisa as novidades da Reforma Tributária do Consumo e monta a newsletter do seu escritório, com fonte, data e link de cada destaque.**

Você escolhe o público (empresários ou contadores) e a janela: diária (do dia anterior até agora) ou semanal (dos últimos sete dias). A skill pesquisa primeiro as fontes oficiais, depois as institucionais e os portais privados aprovados, abre cada página para conferir a data de publicação e confronta toda afirmação normativa com a fonte oficial correspondente — sem ela, a informação entra só como análise atribuída. Entrega de 5 a 10 destaques em Markdown, mais título SEO, meta description, slug, tags e uma chamada curta para LinkedIn ou WhatsApp, marcados como sujeitos à revisão do contador antes da publicação.

Exige pesquisa na internet no aplicativo. Não calcula tributos, não publica no site por você e não trata fonte nova como confiável sem a sua confirmação. Os 7 testes locais dos scripts foram executados e aprovados; os 14 casos de teste de comportamento ainda não foram executados em cada aplicativo.

A explicação passo a passo, com exemplos, está em [robertodiasduarte.com.br/skills-marketing](https://www.robertodiasduarte.com.br/skills-marketing/).

[Baixar o .zip](../../releases/latest/download/newsletter-reforma-tributaria-by-rdd.zip)

### `persona-builder-by-rdd`

**Pesquisa um público do seu mercado e cria uma skill que fala com ele, a `persona-<avatar>`.**

Você diz qual público quer representar (por exemplo, médicos donos de clínica), o país, o idioma e para quais textos vai usar. A skill pesquisa na internet, junta o que você trouxe — entrevistas, avaliações, materiais da empresa — e separa o que é evidência, o que é padrão recorrente, o que é inferência e o que é só hipótese. Se a pesquisa mostrar dois públicos diferentes no mesmo mercado, ela pede que você escolha um: cada skill-filha representa um público só. A `persona-<avatar>` tem três modos — falar do ponto de vista desse público, adaptar um texto para ele e avaliar se uma comunicação conversa com ele — e responde em JSON quando usada em automação.

Ao adaptar um relatório técnico, preserva números, datas, rótulos e conclusões: não recalcula nem substitui a conclusão profissional. Não imita uma pessoa real, não inventa dados para dar realismo e não reforça afirmação enganosa ou sem prova. Exige pesquisa na internet para criar a primeira versão da persona; depois, só pesquisa de novo se você pedir. Os 10 casos de teste de comportamento ainda não foram executados em cada aplicativo.

A explicação passo a passo, com exemplos, está em [robertodiasduarte.com.br/skills-marketing](https://www.robertodiasduarte.com.br/skills-marketing/).

[Baixar o .zip](../../releases/latest/download/persona-builder-by-rdd.zip)

### `icp-builder-by-rdd`

**Entrevista você sobre clientes reais e cria uma skill que pensa como o seu cliente ideal.**

ICP é o cliente que a sua empresa atende bem, em que circunstância e com que viabilidade comercial. A skill conduz uma entrevista — uma pergunta por vez, sem pesquisar na internet —, reconstrói a jornada desse cliente, da vida antes da necessidade à compra e ao uso, e marca cada afirmação como relatada, observada, hipótese, desconhecida ou exemplo. O resultado vai para um `perfil.json` (`draft`, com as lacunas listadas, ou `ready`, quando há contexto suficiente para usar — não é validação de mercado) e vira uma skill-filha gerada por script. A skill-filha personifica o cliente (sempre como simulação, nunca como depoimento), orienta, revisa e simula conversas em sete atividades: campanha, relacionamento, funil, eventos, produtos, vendas e objeções.

Exige um aplicativo que execute Python 3 e crie arquivos; sem isso, você recebe a síntese e o perfil em texto, não o pacote da skill-filha. Não inventa idade, renda, emoção ou depoimento, não promete resultado de venda e não publica nada por você. Os 9 testes do gerador foram executados e aprovados; os cenários de personificação ainda não foram executados em cada aplicativo.

A explicação passo a passo, com o exemplo abaixo, está em [robertodiasduarte.com.br/skills-marketing/icp](https://www.robertodiasduarte.com.br/skills-marketing/icp/).

[Baixar o .zip](../../releases/latest/download/icp-builder-by-rdd.zip)

### `icp-contabilidade-beatriz-exemplo` (exemplo gerado pela `icp-builder-by-rdd`)

A skill-filha que a ICP Builder gerou a partir de uma história ilustrativa: uma médica recém-formada que começa a receber plantões como pessoa jurídica, atendida por uma empresa de contabilidade fictícia. Mostra o que você recebe — jornada em sete fases, tabela de evidências e oportunidades por atividade —, com tudo marcado como exemplo ou hipótese. Não é pesquisa sobre médicas nem resultado de uma empresa real.

[Baixar o .zip](../../releases/latest/download/icp-contabilidade-beatriz-exemplo.zip)

## Modelo para estudo

### `consultor-simples-nacional-by-rdd`

**Uma skill padrão-ouro de Simples Nacional, aberta para você ver por dentro.**

Manual com fronteira nomeada e recusa literal, legislação e tabelas por ano dentro da pasta, motor de cálculo, conferente independente que trava a entrega se divergir, gabarito oficial do Manual do PGDAS-D, testes e casos negativos. A maioria das peças existe porque uma versão anterior errou sem ela — a explicação peça por peça está em [robertodiasduarte.com.br/anatomia-skill](https://www.robertodiasduarte.com.br/anatomia-skill/), e o `COMECE_AQUI.md` do pacote segue a mesma ordem.

> Skill criada para aprendizado. O conteúdo — legislação, tabelas e regras — está datado de setembro de 2026 e não recebe atualização da RDD: mantê-la atualizada é por sua conta.

[Baixar o .zip](../../releases/latest/download/consultor-simples-nacional-by-rdd.zip)

## Instalação

Baixe o `.zip` da [última Release](../../releases/latest).

- **Claude (claude.ai):** Configurações → Capacidades → Skills → upload do `.zip` **sem descompactar**.
- **ChatGPT:** Configurações → Habilidades (`chatgpt.com/admin/skills`) → **+** → arraste o `.zip`. Sem acesso à administração? Crie um Projeto, envie os arquivos e instrua: *"Siga o SKILL.md que está nos arquivos deste projeto."*
- **Claude Code, Codex, Cursor e outros agentes de terminal:** peça, dentro do seu projeto:

  > Instale a skill `parsing-chunking-by-rdd` do repositório `robertodiasduarte/skills-by-rdd`.

  O agente descobre o repositório e roda o instalador sozinho. Ele pede sua autorização antes de executar — aprove e pronto. A skill cai em `.claude/skills/` (Claude Code) ou `.agents/skills/` (Codex); peça a instalação global para tê-la em todos os projetos.

Troque o nome da skill pela que quiser: `parsing-chunking-by-rdd`, `prompt-builder-by-rdd`, `skill-builder-by-rdd`, `skill-soul-builder-by-rdd`, `newsletter-reforma-tributaria-by-rdd`, `persona-builder-by-rdd`, `icp-builder-by-rdd`, `icp-contabilidade-beatriz-exemplo` ou `consultor-simples-nacional-by-rdd`.

<details>
<summary>Prefere o comando direto?</summary>

```bash
npx skills add robertodiasduarte/skills-by-rdd -s <nome-da-skill> -a claude-code -y
```

Troque `-a claude-code` por `-a codex` ou pelo nome do seu agente, e use `-s '*'` para instalar todas. Sem Node.js, descompacte o `.zip` e copie a pasta para o diretório de skills do seu agente.

</details>

Depois acione pelo nome: *"Use a skill parsing-chunking-by-rdd. Prepare este documento para a minha base."*

## Verificar o download

Cada release publica `SHA256SUMS.txt`. Para conferir:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

## Autoria e licença

Skills construídas com a metodologia de Roberto Dias Duarte.

MIT — veja [LICENSE](LICENSE).
