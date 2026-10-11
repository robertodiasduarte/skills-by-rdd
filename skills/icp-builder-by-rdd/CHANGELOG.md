# Changelog

## 1.0.0 - 2026-10-11
- Primeira versão pública.
- Entrevista o usuário, uma pergunta central por vez, e reconstrói a jornada de vida ou trabalho e a de compra e uso do cliente ideal.
- Classifica cada evidência como observada, relatada, hipótese, desconhecida ou exemplo, com fonte e confiança.
- Consolida o contexto em `perfil.json` (`draft` com lacunas explícitas ou `ready`) e gera a skill-filha com `scripts/build_child.py`, sem dependências além da biblioteca padrão do Python.
- A skill-filha personifica o cliente (sempre como simulação), orienta, revisa e simula conversas nas sete atividades: campanha, relacionamento, funil, eventos, produtos, vendas e objeções.
- Acompanha o exemplo `icp-contabilidade-beatriz-exemplo`, gerado a partir de uma história ilustrativa.
