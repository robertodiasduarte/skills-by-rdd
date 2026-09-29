# Mapa de regras — V4.1

## Sumário de navegação
- SN-ALIQUOTA-001
- SN-FATORR-001
- SN-RBT12P-001
- SN-ISSRET-001
- SN-CNAE-001
- SN-LIMITE-001
- SN-SUBLIMITE-001
- SN-EXPORT-001
- SN-EVIDENCIA-001
- SN-TEMPORAL-001
- SN-RECUSA-001
- SN-SEGURANCA-001

IDs são estáveis. Não reaproveitar nem renumerar. Regra aposentada permanece com status explícito.

## SN-ALIQUOTA-001
**Assunto:** alíquota efetiva e DAS ordinário dos Anexos I a V.  
**Condição:** atividade/anexo previamente classificados; período com tabela validada; nenhuma qualificação complexa ativa.  
**Entradas:** competência, anexo, RBT12, RPA, receita com ISS retido quando aplicável.  
**Regra:** faixa pela RBT12; alíquota efetiva = `(RBT12 × Aliq − PD) / RBT12`; partilha pela tabela vigente.  
**Fonte principal:** Resolução CGSN nº 140/2018, art. 21 e Anexos.  
**Fonte complementar:** Manual do PGDAS-D e DEFIS, seção de cálculo.  
**Algoritmo:** `scripts/engine.py` + `scripts/verify.py` + `scripts/apurar_verificado.py`.  
**Testes:** goldens oficiais, fronteiras de faixa, período sem tabela, sabotagem de divergência.

## SN-FATORR-001
**Assunto:** fator R.  
**Condição:** atividade efetivamente sujeita ao fator R.  
**Entradas:** FS12, RBT12, competência.  
**Regra:** aplicar regra de precisão vigente e limiar documental de 0,28; retorno é sugerido enquanto a sujeição jurídica não estiver confirmada.  
**Fonte principal:** Perguntas e Respostas — Simples Nacional, item 5.11.  
**Fonte complementar:** Manual do PGDAS-D e DEFIS, item 8.2.1.  
**Algoritmo:** `scripts/calcular_fator_r.py`.  
**Testes:** fronteira 0,28, zero, período inválido.

## SN-RBT12P-001
**Assunto:** RBT12 proporcionalizada em início de atividade.  
**Condição:** empresa nos primeiros 12 meses de atividade.  
**Entradas:** receita atual, receitas anteriores, competência.  
**Regra:** primeiro mês = RPA × 12; meses 2 a 12 = média dos meses anteriores × 12.  
**Fonte principal:** Perguntas e Respostas, item 5.4; Manual PGDAS-D, item 8.3.  
**Algoritmo:** `scripts/calcular_rbt12p.py`.  
**Testes:** exemplo oficial, mês 2, mês 12, número negativo.

## SN-ISSRET-001
**Assunto:** receita com ISS retido.  
**Condição:** serviço sujeito a ISS dentro dos Anexos III, IV ou V e retenção válida.  
**Entradas:** RPA, receita sujeita à retenção, anexo/faixa.  
**Regra:** os demais tributos usam a receita integral; a parcela de ISS não incide sobre a receita que sofreu retenção.  
**Fonte principal:** Resolução CGSN nº 140/2018, art. 25, § 9º, II e art. 27, VII.  
**Algoritmo:** núcleo de cálculo e verificação redundante.  
**Testes:** invariante de base do ISS e validação de receita retida ≤ RPA.

## SN-CNAE-001
**Assunto:** triagem CNAE.  
**Condição:** usuário fornece CNAE ou descrição de atividade.  
**Entradas:** CNAE/texto e atividade efetivamente exercida.  
**Regra:** tabela derivada devolve todas as possibilidades; conclusão depende da atividade efetiva e da norma.  
**Fonte principal:** LC 123/2006 e Resolução 140/2018.  
**Fonte complementar:** tabela CNAE × Anexo, nível D.  
**Algoritmo:** `scripts/lookup_cnae.py`.  
**Testes:** CNAE com múltiplos enquadramentos; busca por radical/sinônimo.

## SN-LIMITE-001
**Assunto:** limite anual e excesso.  
**Condição:** análise de permanência/exclusão.  
**Entradas:** RBA, ano, início de atividade quando pertinente.  
**Regra:** usar limite e efeitos da ultrapassagem conforme fonte vigente; não usar RBT12 no lugar da RBA.  
**Fonte principal:** LC 123/2006 e Resolução 140/2018.  
**Algoritmo:** `scripts/avaliar_limite_receita.py` como apoio; conclusão exige evidência.  
**Testes:** limite exato, excesso até e acima de 20%.

## SN-SUBLIMITE-001
**Assunto:** sublimite de ICMS/ISS.  
**Condição:** RBA/RBAA e UF/ano relevantes.  
**Entradas:** RBA, RBAA quando cabível, sublimite, período.  
**Regra:** não simplificar pela RBT12; avaliar efeito temporal e recolhimento de ICMS/ISS.  
**Fonte principal:** P&R itens 4.1–4.6; Manual PGDAS-D 8.4.  
**Algoritmo:** `scripts/avaliar_sublimite.py` como apoio; motor genérico de DAS bloqueia esse cenário.  
**Testes:** sublimite exato, acima/abaixo, motor genérico bloqueado.

## SN-EXPORT-001
**Assunto:** exportação.  
**Condição:** receita de mercado externo.  
**Entradas:** RBT12/RPA/RBA internos e externos, período, anexo e sublimite.  
**Regra:** receitas interna e externa exigem tratamento separado; no escopo implementado, revenda de mercadorias do Anexo I sem efeito de sublimite usa `modo=exportacao_anexo_i`; exportação não pode ser tratada como receita ordinária.  
**Fonte principal:** Manual do PGDAS-D e DEFIS, Seção 12, Exemplo 6; LC 123/2006 e P&R, nota da pergunta 5.3.  
**Algoritmo:** `scripts/engine.py` + `scripts/verify.py` + `scripts/apurar_verificado.py`, somente para o escopo auditado acima.  
**Testes:** golden `PGDAS-EX6-ANEXO-I-EXPORTACAO`; exportação em `modo=ordinario` bloqueada; efeito de sublimite bloqueado.

## SN-EVIDENCIA-001
**Assunto:** gate de recuperação.  
**Condição:** qualquer afirmação material.  
**Entradas:** pergunta/termos.  
**Regra:** `search_kb.py` precisa retornar fato estruturado; sem evidência, parar.  
**Fonte:** política de auditabilidade V4.  
**Algoritmo:** `scripts/search_kb.py` + `scripts/safe_facts.py`.  
**Testes:** consulta sem resultado, limites de estrutura e hash.

## SN-TEMPORAL-001
**Assunto:** vigência.  
**Condição:** cálculo numérico.  
**Entradas:** competência.  
**Regra:** usar apenas tabela local do período; sem tabela, fail-closed; nunca fallback para ano vizinho.  
**Fonte:** contrato funcional + catálogo de fontes.  
**Algoritmo:** `scripts/tables_loader.py`.  
**Testes:** 2026 aceita; 2027 recusa cálculo; pergunta conceitual 2027 segue para evidência local.

## SN-RECUSA-001
**Assunto:** recusa operacional.  
**Condição:** fora de escopo, sem evidência, período numérico sem tabela ou dado essencial ausente.  
**Entradas:** classificação do pedido e resultado dos gates.  
**Regra:** usar texto canônico correspondente e não acrescentar dado de memória.  
**Fonte:** contrato funcional V4.  
**Algoritmo:** evals mecânicos.  
**Testes:** fora de escopo, corte temporal, dado faltante; falha simulada “recusa + dado proibido” deve reprovar.

## SN-SEGURANCA-001
**Assunto:** documento como entrada não confiável.  
**Condição:** ingestão ou consumo de material documental.  
**Entradas:** arquivo textual permitido ou trecho recuperado.  
**Regra:** extensão/tamanho → segredo → dado pessoal → cota → extração; fatos passam por barreira estrutural em ingestão e consumo.  
**Fonte:** política de segurança V4.  
**Algoritmo:** `scripts/ingest_guard.py`, `scripts/safe_facts.py`, `scripts/search_kb.py`.  
**Testes:** extensão recusada, cota, controle de estrutura, scanner de CPF/CNPJ por DV.
