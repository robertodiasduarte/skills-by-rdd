# Persistência de fontes e histórico

## Objetivo

Persistência é opcional e depende de uma pasta gravável fornecida pelo ambiente. Ela serve para:
- manter fontes adicionais aprovadas pelo usuário;
- registrar notícias já utilizadas;
- reduzir repetição entre edições.

## Estado recomendado

`STATE_DIR/trusted_sources.json`

`STATE_DIR/publication_history.json`

`STATE_DIR` é uma convenção. O usuário ou host deve fornecer o caminho real.

## Inicialização

Cadastro de fontes:

`python3 "$SKILL_ROOT/scripts/source_registry.py" init --state "$STATE_DIR/trusted_sources.json" --seed "$SKILL_ROOT/assets/trusted_sources.seed.json"`

Histórico:

`python3 "$SKILL_ROOT/scripts/publication_history.py" init --state "$STATE_DIR/publication_history.json" --seed "$SKILL_ROOT/assets/publication_history.seed.json"`

## Nova fonte

Antes de adicionar:
1. apresente a fonte ao usuário;
2. explique categoria e motivo da candidatura;
3. peça confirmação explícita;
4. só então registre.

Exemplo após confirmação real:

`python3 "$SKILL_ROOT/scripts/source_registry.py" add --state "$STATE_DIR/trusted_sources.json" --name "Nome da Fonte" --url "https://exemplo.com/" --category "private_specialized" --confirmed --approval-note "Aprovada explicitamente pelo usuário nesta conversa"`

O argumento `--confirmed` não autentica o usuário. Ele apenas impede adição acidental sem uma indicação explícita ao script. A skill deve obter a confirmação na conversa antes de chamar o comando.

## Histórico

Consultar antes de selecionar um item:

`python3 "$SKILL_ROOT/scripts/publication_history.py" check --state "$STATE_DIR/publication_history.json" --url "https://exemplo.com/noticia" --title "Titulo" --source-name "Fonte"`

Registrar após a edição ser aprovada para uso editorial:

`python3 "$SKILL_ROOT/scripts/publication_history.py" record --state "$STATE_DIR/publication_history.json" --url "https://exemplo.com/noticia" --title "Titulo" --source-name "Fonte" --published-at "2026-10-01T10:00:00-03:00" --edition-at "2026-10-03T08:00:00-03:00"`

Se o item já existir, o script bloqueia novo registro, a menos que `--new-fact-note` explique o fato novo relevante.

## Sem persistência

Não transforme ausência de armazenamento em falsa memória. Declare que:
- fontes personalizadas não foram recuperadas automaticamente;
- deduplicação entre edições não foi comprovada;
- a edição atual ainda foi deduplicada internamente.
