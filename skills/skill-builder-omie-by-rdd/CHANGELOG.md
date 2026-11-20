# Histórico

## 1.1.0 — 20/11/2026

Acompanha a `skill-builder-by-rdd` 1.2.0. A skill gerada pertence ao usuário: autor e licença são perguntados no
brainstorm, em vez de fixados em Roberto Dias Duarte e MIT; os modelos Operador e Conferidor trazem marcadores no
lugar. O crédito à metodologia continua por padrão e pode ser removido a pedido: nesse caso o `manifest.json` da skill
gerada grava `"credito_metodologia": false` e o `lint_bundle_omie.py` deixa de exigir a seção. Os 12 cenários de
conversa saem do pacote e vão para a pasta evals do repositório. A descrição passa a declarar a escolha de licença.

## 1.0.0 — 10/10/2026

Meta-skill inicial, filha da `skill-builder-by-rdd` 1.1.2. Herda por cópia vigiada (`HERANCA.json`) o fluxo de
entrevista, o gate de escopo, o lint estrutural, os testes de controle e os modelos. Acrescenta: base de operações do
Omie (corte 10/10/2026), perfis Operador e Conferidor derivados por pergunta, `perfil_omie.json` amarrado ao escopo
por hash, padrão de escrita literal, teste ao vivo só de leitura, `omie_num.py` (totalização com conferência,
derivado da `consulta-omie-somente-leitura` 1.0.0) e `lint_bundle_omie.py`.
