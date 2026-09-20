# Skills by RDD

Skills profissionais para contabilidade, tributos, trabalhista e jurídico — prontas para instalar no seu ChatGPT, Claude, Claude Code ou Codex.

Cada skill aqui resolve um trabalho que se repete. Você instala uma vez e aciona pelo nome, dentro do app de IA que já usa.

## As skills

### `parsing-chunking-by-rdd`

**Prepara DOCX, PDF e TXT para virar base de conhecimento de IA.**

Extrai o texto, corrige o ruído de layout, organiza em Markdown por seção e retira o que está tachado ou explicitamente revogado — sempre com evidência no próprio documento. Devolve o Markdown ajustado e um relatório do que saiu. Quando você pede, também monta o mapa semântico e o índice de remissões do material.

Não faz OCR, não reescreve e não decide vigência por conta própria.

Três modos: `parse` (o padrão), `semantic` (mapa semântico sobre Markdown já ajustado) e `full` (os dois em sequência).

[Baixar o .zip](../../releases/latest/download/parsing-chunking-by-rdd.zip)

### `prompt-builder-by-rdd`

**Transforma um processo seu em um system prompt profissional.**

Conduz um brainstorm progressivo sobre o trabalho, reúne os materiais que sustentam as regras, consolida o escopo e só produz o prompt depois da sua confirmação explícita. Quando o assunto depende de data, delimita o período de consulta e o de cálculo, em vez de deixar implícito.

Funciona em qualquer domínio e jurisdição. Não executa o processo profissional no seu lugar, não monta arquitetura de vários agentes e não busca fontes externas sem você autorizar.

[Baixar o .zip](../../releases/latest/download/prompt-builder-by-rdd.zip)

### `skill-builder-by-rdd`

**Transforma um processo seu em uma skill profissional.**

Ela entrevista você sobre o trabalho, pede os materiais que sustentam as regras, fecha o escopo por escrito e só então gera a skill — depois da sua confirmação. Entrega outra skill, não a resposta do caso contábil que você usou como exemplo.

A skill que ela cria não vem com motor de cálculo verificado: para conta conferida por dois caminhos independentes, use a esteira "Skill avançada" da plataforma RDD.

[Baixar o .zip](../../releases/latest/download/skill-builder-by-rdd.zip)

## Instalação

Baixe o `.zip` da [última Release](../../releases/latest).

- **Claude (claude.ai):** Configurações → Capacidades → Skills → upload do `.zip` **sem descompactar**.
- **ChatGPT:** Configurações → Habilidades (`chatgpt.com/admin/skills`) → **+** → arraste o `.zip`. Sem acesso à administração? Crie um Projeto, envie os arquivos e instrua: *"Siga o SKILL.md que está nos arquivos deste projeto."*
- **Claude Code, Codex, Cursor e outros agentes de terminal:** peça, dentro do seu projeto:

  > Instale a skill `parsing-chunking-by-rdd` do repositório `robertodiasduarte/skills-by-rdd`.

  O agente descobre o repositório e roda o instalador sozinho. Ele pede sua autorização antes de executar — aprove e pronto. A skill cai em `.claude/skills/` (Claude Code) ou `.agents/skills/` (Codex); peça a instalação global para tê-la em todos os projetos.

Troque o nome da skill pela que quiser: `parsing-chunking-by-rdd`, `prompt-builder-by-rdd` ou `skill-builder-by-rdd`.

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
