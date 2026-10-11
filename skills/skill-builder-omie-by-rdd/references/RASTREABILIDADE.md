# Rastreabilidade e decisões de adaptação

## Base primária

“Geração de Agent Skills na Plataforma RDD — Documentação Técnica”,
versão 1.0, 20/09/2026, fornecida pelo usuário.
A cópia integral é interna da plataforma RDD e **não** acompanha este pacote público:
descreve migrations, políticas de acesso e detalhes de infraestrutura que não são
distribuíveis. As regras derivadas dela estão reproduzidas abaixo e bastam para usar a skill.

O documento relata leitura de código do commit e764e9f76. Este pacote não teve acesso
ao repositório citado: seus resultados, incidentes e caminhos são tratados como
afirmações da documentação, não como execução própria.

## Regras derivadas da fonte

| Decisão preservada | Localizador na documentação |
|---|---|
| Estrutura antes de domínio; prosa não substitui controle | §§1, 2.1, 8 |
| Perfis A/B/AB/C e degradação por material | §§2.2–2.3 |
| Cinco gavetas | §2.4 |
| Pacote, frontmatter, oito seções e referências | §§3, 3.1, 6 |
| Motor, verificação, gabaritos e hard-stop | §§2.1, 3.2, 4.3, 4.5 |
| Escopo confirmado, fronteira nomeada e dois períodos | §4.4 |
| Material tratado como dado; limites de allowed-tools | §9 |
| Divergências da plataforma frente à spec | §10 |
| Declarar o não provado e não confundir normas/implementação | §§2.1, 11.2 |

## Extensões propostas neste pacote

As seguintes decisões são adaptações de projeto, não transcrições do código RDD:

- Meta-skill focada em criar outras skills nas quatro áreas solicitadas.
- Entrevista de uma pergunta principal por vez, aproveitando respostas anteriores.
- Registro explícito de exemplos, contraexemplos e memórias nas gavetas existentes.
- Máquina de estados, confirmação após o resumo e invalidação por mudança de contrato.
- ID, revisão, SHA-256, evidência da mensagem e gate local de consistência.
- Modos conversacional, arquivos, executável e contexto isolado.
- Modelos de entrada e um lint local básico, sem alegar equivalência ao validador RDD.
- Adaptador opcional agents/openai.yaml, ausente no padrão canônico RDD.
- Versão consolidada em texto para hosts sem instalação nativa.

O gate estende o objeto de escopo RDD com entradas, saídas, materiais e critérios.
O limite de 4.000 bytes é aplicado à projeção dos sete campos RDD, não a todas
as informações adicionais coletadas nesta versão.

## Não transplantado

Não copiar roteamento de provedores, modelos hardcoded, custos, quotas, stages HTTP,
WordPress, Supabase, RLS, migrations ou mecanismos de publicação.
Esses detalhes pertencem à plataforma documentada, não ao objetivo da meta-skill.

Não alegar uso dos 18 templates originais: os arquivos não foram disponibilizados.
Não alegar correção do validador oficial, execução dos gates do repositório,
validação jurídica, auditoria humana ou teste em aplicativos terceiros.

## Tensões preservadas, sem reconciliação silenciosa

A fonte alterna “menos de 500 linhas” e “até 500”. Este pacote adota menos de 500,
a alternativa conservadora, e declara a escolha.

A fonte diferencia manter a geração disponível (P6) e bloquear números sem prova
(P1/P2/P4). Este pacote permite materialização de uma versão menor somente depois
da aprovação de sua capacidade reduzida; não interpreta P6 como liberação de cálculo.

A fonte descreve o problema com numerais romanos na regra de terceira pessoa.
O lint local não tenta inferir pessoa gramatical por um regex de pronomes.
A redação é revisada semanticamente; não se afirma que o defeito da plataforma foi corrigido.

A especificação aberta permite diretórios adicionais e não impõe as oito seções.
Este pacote preserva as oito seções como convenção RDD.
