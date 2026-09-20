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

### `skill-builder-by-rdd`

**Transforma um processo seu em uma skill profissional.**

Ela entrevista você sobre o trabalho, pede os materiais que sustentam as regras, fecha o escopo por escrito e só então gera a skill — depois da sua confirmação. Entrega outra skill, não a resposta do caso contábil que você usou como exemplo.

A skill que ela cria não vem com motor de cálculo verificado: para conta conferida por dois caminhos independentes, use a esteira "Skill avançada" da plataforma RDD.

[Baixar o .zip](../../releases/latest/download/skill-builder-by-rdd.zip)

## Instalação

Baixe o `.zip` da [última Release](../../releases/latest).

- **Claude (claude.ai):** Configurações → Capacidades → Skills → upload do `.zip` **sem descompactar**.
- **ChatGPT:** Configurações → Habilidades (`chatgpt.com/admin/skills`) → **+** → arraste o `.zip`. Sem acesso à administração? Crie um Projeto, envie os arquivos e instrua: *"Siga o SKILL.md que está nos arquivos deste projeto."*
- **Claude Code:** `npx skills add robertodiasduarte/skills-by-rdd -s parsing-chunking-by-rdd -a claude-code -y` (instala em `.claude/skills/` do projeto; com `-g`, em `~/.claude/skills/`).
- **Codex:** `npx skills add robertodiasduarte/skills-by-rdd -s parsing-chunking-by-rdd -a codex -y` (instala em `.agents/skills/` do projeto; com `-g`, em `~/.agents/skills/`).
- **Cursor, Kimi e outros:** mesmo comando com o nome do agente em `-a`. Sem Node.js, descompacte o `.zip` e copie a pasta para o diretório de skills do seu agente.

Troque `-s <nome>` pela skill que quiser, ou use `-s '*'` para instalar todas.

Depois acione pelo nome: *"Use a skill parsing-chunking-by-rdd. Prepare este documento para a minha base."*

## Verificar o download

Cada release publica `SHA256SUMS.txt`. Para conferir:

```bash
shasum -a 256 -c SHA256SUMS.txt
```

## Autoria e licença

Skills construídas com a metodologia de Roberto Dias Duarte.

MIT — veja [LICENSE](LICENSE).
