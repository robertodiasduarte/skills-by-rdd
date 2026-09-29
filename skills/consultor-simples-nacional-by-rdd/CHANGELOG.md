# Changelog

## 4.1.1 — 2026-09-29

### Alterado
- nome da skill passa a ser `consultor-simples-nacional-by-rdd`, no padrão do catálogo público `skills-by-rdd`;
- `SKILL.md` ganha o aviso de uso para aprendizado e o link para `COMECE_AQUI.md`.

### Adicionado
- `COMECE_AQUI.md`: mapa das peças da skill, na ordem da página de estudo da plataforma RDD.

### Corrigido
- `tests/test_security.py` monta em tempo de execução as sequências repetidas usadas como não-PII, para o pacote passar no filtro de conteúdo do repositório público; o teste confere exatamente o mesmo.

### IMPACTO
- nenhum cálculo, tabela, fonte, gabarito ou regra mudou; resultados da 4.1.0 permanecem idênticos;
- o conteúdo continua datado de setembro de 2026 e não recebe atualização.

## 4.1.0 — 2026-09-13

### Adicionado
- suporte auditado ao `modo=exportacao_anexo_i` para revenda de mercadorias com mercado interno e exportação, sem efeito de sublimite;
- golden oficial `PGDAS-EX6-ANEXO-I-EXPORTACAO`, extraído do Manual do PGDAS-D e DEFIS, Seção 12, Exemplo 6;
- regressão que exige R$ 9.935,02 no mercado interno, R$ 2.154,76 no mercado externo e R$ 12.089,78 no total do Exemplo 6;
- gate explícito contra uso de exportação no `modo=ordinario`.

### Alterado
- `apurar_verificado.py` deixa de usar qualquer status genérico `PASS`;
- entrada arbitrária sem golden específico passa a ser rotulada `CALCULO_DETERMINISTICO_SEM_GABARITO_ESPECIFICO`;
- `verify.py` cobre também o modo de exportação por implementação separada com `Decimal`;
- schema exige `modo` explícito e campos separados de mercado interno/externo no modo de exportação;
- documentação diferencia concordância de implementação de validação normativa específica.

### Corrigido
- o Exemplo 6 não pode mais receber aprovação com um cálculo ordinário que misture mercado interno e exportação;
- gabaritos ativos exigem fonte, localizador, procedência e `conferido_por`;
- valores produzidos pela própria Skill não podem ser promovidos a golden;
- todos os comandos continuam independentes do diretório atual por meio de `$SKILL_ROOT`;
- a presença de `allowed-tools: Read, Bash` é descrita apenas como allowlist de ferramentas; isolamento de rede em Claude Code continua responsabilidade do host;
- perguntas conceituais de 2027 continuam separadas dos motores numéricos 2018–2026.

### IMPACTO
- apurações de revenda no Anexo I com mercado interno + exportação que tenham sido tratadas como receita ordinária por versões antigas devem ser reconferidas;
- o Exemplo 6 oficial agora é reproduzido exatamente e funciona como golden externo de regressão;
- exportação com efeito de sublimite, outros anexos com exportação, ST, monofásico e início de atividade continuam bloqueados quando não houver rotina auditada específica;
- nenhum cálculo de 2027 é liberado; consultas conceituais sobre 2027 permanecem possíveis quando a base local sustentar a resposta.

## 4.0.0 — 2026-09-13

### Adicionado
- perfil A normativo-numérico formal;
- `references/graph.yaml` com communities, nodes, edges e queries;
- `references/router.md` e dez páginas conceituais de roteamento;
- `scripts/verify.py` restaurado com decomposição matemática diferente, `Decimal` e proibição de importar `engine.py`/`simples_core.py`;
- `scripts/safe_facts.py` e `scripts/ingest_guard.py` para barreira documental e ingestão fail-closed;
- `scripts/lint_bundle.py` com gates estruturais;
- testes de sabotagem do hard-stop, grafo, segurança e independência do verify;
- política explícita de cut-off conservador por corpus e versões por documento.

### Alterado
- `apurar_verificado.py` volta a exigir concordância engine/verify, mas declara que a independência é de implementação, não de fonte normativa;
- `validate_goldens.py` confronta engine e verify contra exemplos externos e exige `conferido_por` + `fonte_do_gabarito`;
- `SOURCE_CATALOG.md`, `RULE_MAP.md`, `GLOSSARIO.md`, `FORMULAS.md` e `COMO_FUNCIONA.md` foram ampliados;
- todos os documentos longos em `references/` ganharam sumário de navegação no topo;
- `search_kb.py` passa registros recuperados por barreira estrutural;
- fronteira negativa e recusa canônica foram alinhadas ao período consultivo 2018–2027 e período numérico 2018–2026;
- frontmatter volta a declarar `allowed-tools: Read, Bash`, sem alegar que isso sozinho prova isolamento de rede no Claude Code.

### Corrigido
- eliminada a falsa equivalência “concordância = segunda fonte normativa”;
- restaurado hard-stop redundante sem desfazer a política de goldens externos;
- corrigida a lacuna de navegação em corpus grande com router + grafo;
- corrigida a ausência de gate determinístico para conteúdo documental não confiável;
- redigidos identificadores válidos detectados em exemplo do Manual PGDAS-D antes do empacotamento; valores não foram registrados no log;
- corrigida a possibilidade de arquivo órfão, aresta órfã e link silenciosamente quebrado por lint bloqueante.

### IMPACTO
- resultados numéricos da V3.1 continuam utilizáveis somente dentro das regras já validadas, mas a V4 exige também concordância de implementação entre engine e verify para o motor ordinário;
- nenhum cálculo de 2027 é liberado: os motores continuam limitados a 01/2018–12/2026;
- consultas conceituais sobre 2027 permanecem possíveis somente quando sustentadas por evidência local incorporada;
- o novo verify não corrige uma tabela normativa errada por si só; por isso os goldens oficiais/humanos continuam gate independente de release;
- qualquer automação externa que dependia da ausência de `verify.py` deve ser ajustada para o novo hard-stop.

## 3.1.0 — 2026-09-13

### Corrigido
- removido `verify.py`: duas implementações da mesma fórmula/tabela não são validação normativa independente;
- `apurar_verificado.py` não retorna mais `PASS` para entrada arbitrária;
- baseline agora usa gabaritos oficiais externos ao código;
- removidos como gabaritos dois resultados monetários que vinham do próprio motor e não possuíam fonte externa conferida;
- motor genérico agora exige flags de cenário e bloqueia exportação, sublimite, ST, monofásico e início de atividade;
- removida a afirmação de que `allowed-tools` bloqueia internet no Claude Code;
- todos os comandos documentados usam `$SKILL_ROOT`, sem depender do cwd;
- corte 2018–2026 passou a limitar os motores de cálculo, não perguntas conceituais;
- adicionado eval positivo para consulta conceitual de 2027.

### Adicionado
- `references/goldens/official_examples.json` com exemplos oficiais do Manual do PGDAS-D;
- `scripts/validate_goldens.py`;
- `references/RUNTIME_COMPATIBILITY.md`;
- gate específico contra simplificação indevida de cenários como o Exemplo 6 do Manual do PGDAS-D.

### Impacto
- resultados da V3.0 rotulados `PASS` por concordância `engine/verify` não devem ser interpretados como validação independente;
- qualquer release anterior que tenha promovido resultado do próprio motor a gabarito deve ser reavaliado;
- cálculos complexos antes aceitos pelo motor genérico podem agora ser recusados, deliberadamente, até existir rotina específica validada;
- perguntas conceituais sobre 2027 deixam de ser recusadas só por causa do ano.


## 3.0.0 — 2026-09-13

### Adicionado
- gates operacionais de escopo, recuperação e período;
- recusa canônica literal;
- política de não uso de internet sem autorização (na V3.0, incorretamente descrita como bloqueio mecânico por frontmatter);
- `SOURCE_CATALOG.md`, `RULE_MAP.md`, `GLOSSARIO.md`, `FORMULAS.md` e `COMO_FUNCIONA.md`;
- tabelas versionadas por ano, 2018–2026, com carregamento fail-closed;
- `engine.py`, `verify.py` e `apurar_verificado.py` com hard-stop em divergência (arquitetura posteriormente substituída na V3.1 por não constituir verificação normativa independente);
- `evals/` com os três casos negativos obrigatórios;
- `tests/test_calculos.py` e `tests/test_evals.py`;
- schema de entrada e política de goldens;
- segregação de receita com ISS retido nos Anexos III, IV e V;
- busca CNAE por radical e sinônimos.

### Alterado
- todos os comandos passaram a usar `python3`;
- `calcular_rbt12p.py` agora aceita pontuação brasileira e listas com separador `;`;
- o fator R retorna `anexo_sugerido` e declara a premissa jurídica não verificada;
- a resposta só pode citar localizador efetivamente recuperado;
- CNAE permanece triagem, agora com recuperação semântica leve.

### Corrigido
- ambiguidade de vírgula decimal em listas de receitas da RBT12p;
- ausência de segregação de ISS retido no cálculo dos Anexos III, IV e V;
- busca por “programação” que não priorizava “desenvolvimento de programas de computador”;
- ausência de regressão unitária formal para as regras fiscais implementadas.

### Impacto
- cálculos de períodos 2018–2026 continuam usando as mesmas tabelas fiscais validadas na V2;
- casos com **receita que sofreu retenção de ISS** podem produzir DAS menor que na V2, pois a V3 retira a parcela de ISS apenas dessa receita;
- entradas de RBT12p com formato brasileiro deixam de ser interpretadas incorretamente como múltiplos itens;
- classificação jurídica não foi automatizada: CNAE, fator R e scripts continuam dependentes de confirmação documental;
- 2027 permanece bloqueado até que uma tabela específica e validada seja incorporada;
- qualquer mudança futura de regra/tabela exige novo release e regressão.
