# Comece aqui — a skill do Simples Nacional, peça por peça

> Skill criada para aprendizado. O conteúdo — legislação, tabelas e regras — está datado de setembro de 2026 e não recebe atualização da RDD: mantê-la atualizada é por sua conta.

Esta pasta é uma skill padrão-ouro aberta para estudo. A maioria das peças existe porque uma versão anterior errou sem ela; as demais, pelo risco que evitam. A explicação completa — o que é, para que serve, por que importa e o que deu errado sem ela — está em **https://www.robertodiasduarte.com.br/anatomia-skill/**, na mesma ordem abaixo.

## Parte 1 — Uma pergunta atravessando a skill

1. **[O manual de instruções](https://www.robertodiasduarte.com.br/anatomia-skill/#manual-de-instrucoes)** — [SKILL.md](SKILL.md) e este arquivo: quando usar, quando não usar, os portões de cada consulta e o texto exato das recusas.
2. **[O mapa de consulta](https://www.robertodiasduarte.com.br/anatomia-skill/#mapa-de-consulta)** — `references/router.md`, `references/graph.yaml`, `references/concepts/` e `scripts/search_kb.py`: levam a IA ao trecho certo da lei, sem internet.
3. **[A biblioteca de leis](https://www.robertodiasduarte.com.br/anatomia-skill/#biblioteca-de-leis)** — os 9 textos oficiais `references/UF-XX_*.md` e as atualizações até 13/09/2026: a base de toda afirmação.
4. **[O fichário de fontes](https://www.robertodiasduarte.com.br/anatomia-skill/#fichario-de-fontes)** — `references/SOURCE_CATALOG.md` e `references/INDEX.md`: de onde veio cada documento e se ainda vale.
5. **[A especificação das regras](https://www.robertodiasduarte.com.br/anatomia-skill/#especificacao-das-regras)** — `references/RULE_MAP.md`, `FORMULAS.md`, `GLOSSARIO.md` e `schemas/`: classificar antes de calcular.
6. **[As tabelas por ano](https://www.robertodiasduarte.com.br/anatomia-skill/#tabelas-por-ano)** — `references/tabelas/2018` a `2026` e `CNAEANEXO.csv`: sem a tabela do período, o cálculo para.
7. **[O motor de cálculo](https://www.robertodiasduarte.com.br/anatomia-skill/#motor-de-calculo)** — `scripts/engine.py` e os `calcular_*`/`avaliar_*`: todo número vem de código.
8. **[O conferente independente](https://www.robertodiasduarte.com.br/anatomia-skill/#conferente-independente)** — `scripts/verify.py` e `scripts/apurar_verificado.py`: refaz a conta por outro caminho e trava a entrega se divergir.
9. **[O gabarito oficial](https://www.robertodiasduarte.com.br/anatomia-skill/#gabarito-oficial)** — `references/goldens/` e `scripts/validate_goldens.py`: exemplos do Manual do PGDAS-D conferidos por uma pessoa.

## Parte 2 — Como a skill prova que é confiável

10. **[Os testes](https://www.robertodiasduarte.com.br/anatomia-skill/#testes)** — `tests/`: fronteiras, exceções e sabotagens de propósito.
11. **[O simulado de comportamento](https://www.robertodiasduarte.com.br/anatomia-skill/#simulado-de-comportamento)** — `evals/`: perguntas que a skill NÃO deve responder.
12. **[A barreira de segurança](https://www.robertodiasduarte.com.br/anatomia-skill/#barreira-de-seguranca)** — `scripts/ingest_guard.py`, `safe_facts.py`, `lint_bundle.py`, `references/SECURITY.md` e `RUNTIME_COMPATIBILITY.md`: documento é dado, nunca ordem.
13. **[A tradução para humanos](https://www.robertodiasduarte.com.br/anatomia-skill/#traducao-para-humanos)** — `references/COMO_FUNCIONA.md` e `VALIDACAO_ALGORITMOS.md`: a lógica explicada sem código.
14. **[A carteira de identidade](https://www.robertodiasduarte.com.br/anatomia-skill/#carteira-de-identidade)** — `manifest.json`, `CHANGELOG.md` e `agents/`: o que esta versão cobre, o que ainda não provou e o que mudou em cada versão.
