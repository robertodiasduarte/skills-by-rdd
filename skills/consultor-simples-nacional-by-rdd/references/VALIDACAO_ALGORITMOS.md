# Validação didática dos algoritmos de cálculo — versão 4.1

## Sumário de navegação
- Critérios de validação
- Vereditos por algoritmo
- Ajustes incorporados
- Casos-limite
- Adendo V4.1 — Exemplo 6 e política de validação

Validação realizada na construção da V2 com confronto entre os algoritmos enviados, a base interna e fontes oficiais consultadas mediante autorização expressa. Os scripts corrigidos desta skill são didáticos e não substituem a apuração oficial do PGDAS-D.

## Resumo

| Algoritmo enviado | Resultado | Principais ajustes incorporados |
|---|---|---|
| Anexo I com ST | Corrigido | Partilhas por faixa; IRPJ/CSLL/CPP/ICMS corrigidos; “ST de PIS/Cofins” tratada como tributação monofásica; validação de segregações; alerta de sublimite na 6ª faixa. |
| Anexo III | Corrigido | Partilhas corrigidas em várias faixas; limite de RBT12; teto efetivo de ISS de 5% e redistribuição conforme tabela. |
| Anexo IV | Corrigido | 5ª faixa corrigida de 18% para 22%; partilhas corrigidas; CPP explicitamente fora do DAS; teto de ISS e redistribuição; remoção da premissa de “ISS municipal por fora” apenas por estar na 6ª faixa. |
| Anexo V | Corrigido | Partilhas completas; fator R validado antes do cálculo; remoção da premissa de que a 6ª faixa, por si só, determina ISS municipal fora do DAS. |
| Fator R / escolha III × V | Corrigido conceitualmente | O fator R determina o Anexo aplicável; não há livre escolha do anexo mais barato. Incluídos casos RBT12/FS12 zero e truncamento a duas casas sem arredondamento a partir de 04/2018. |

## Regras confirmadas

### Alíquota efetiva

Fórmula usada nos cálculos de 2018 a 2026:

`[(RBT12 × alíquota nominal) − parcela a deduzir] / RBT12`

Referência interna: **Manual do PGDAS-D e DEFIS, item 8.1 — Alíquota nominal e alíquota efetiva**.

### Fator R

Para atividades sujeitas ao fator R:
- fator R igual ou superior a 0,28: Anexo III;
- fator R inferior a 0,28: Anexo V;
- FS12 = 0 e RBT12 = 0: fator R = 0,01;
- FS12 = 0 e RBT12 > 0: fator R = 0,01;
- FS12 > 0 e RBT12 = 0: fator R = 0,28;
- a partir de 04/2018, considerar duas casas decimais **sem arredondamento**.

Referências internas: **Perguntas e Respostas — Simples Nacional, item 5.11**; **Manual do PGDAS-D e DEFIS, item 8.2.1**.

### Anexo IV e CPP

A CPP não integra o DAS para atividades tributadas pelo Anexo IV. O script informa essa exclusão, mas não calcula a contribuição previdenciária fora do DAS porque isso depende de dados e regras previdenciárias adicionais.

Referência interna: **Perguntas e Respostas — Simples Nacional, item 5.12**.

### ST de ICMS e tributação monofásica de PIS/Cofins

O algoritmo do Anexo I foi remodelado em bases segregadas:
- a parcela de ICMS do Simples é retirada da receita sujeita à substituição tributária de ICMS;
- as parcelas de PIS/Pasep e Cofins são retiradas da receita submetida à tributação monofásica, sem retirar essa receita da base dos demais tributos.

Referência interna: **Perguntas e Respostas — Simples Nacional, item 7.4 e notas correlatas**.

### Sublimite

RBT12 e faixa de tributação, isoladamente, não bastam para concluir a data em que ICMS/ISS passam a ser recolhidos fora do Simples. A análise exige RBA/RBAA, sublimite aplicável e, em início de atividade, proporcionalização.

Referências internas: **Perguntas e Respostas — Simples Nacional, itens 4.1 a 4.6**; **Manual do PGDAS-D e DEFIS, itens 8.4 a 8.4.2**.

## Algoritmos adicionais incluídos

1. cálculo do Anexo II (indústria), ausente entre os arquivos enviados;
2. cálculo genérico dos Anexos I a V para 2018-2026;
3. RBT12 proporcionalizada nos 12 primeiros meses de atividade;
4. avaliação do limite anual de R$ 4,8 milhões e excesso de 20%;
5. avaliação de sublimite de ICMS/ISS;
6. consulta à tabela CNAE × Anexo, com retorno de todas as alternativas encontradas e alerta para confirmação normativa.

## Limitação temporal

Os cálculos dos Anexos I a V são intencionalmente válidos apenas para 2018-2026. A partir de 2027, CBS e IBS alteram tabelas e partilhas e existe a possibilidade de recolhimento regular desses tributos fora do DAS. Ver **Atualizações oficiais do Simples Nacional verificadas até 13/09/2026**.


## Adendo V3 — 13/09/2026

A V3 preserva as correções validadas na V2 e acrescenta quatro mudanças de implementação:

1. `calcular_rbt12p.py` aceita números brasileiros (`1.234,56`) e listas com `;`, sem confundir vírgula decimal com separador de meses;
2. Anexos III, IV e V aceitam `receita_iss_retido`, excluindo somente a parcela de ISS sobre essa receita, conforme Resolução CGSN nº 140/2018, art. 25, § 9º, II e art. 27, VII;
3. `lookup_cnae.py` possui busca por radical/sinônimos, incluindo a ponte controlada `programação → desenvolvimento de programas/software`, mantendo o retorno como triagem;
4. existe regressão unitária em `tests/test_calculos.py`;
5. exemplos oficiais independentes do código são validados por `scripts/validate_goldens.py`;
6. invariantes matemáticos são tratados como controles internos, não como gabaritos;
7. a V3.1 removeu a antiga dupla `engine.py`/`verify.py` porque ambos repetiam a mesma formulação/tabela e a concordância foi indevidamente tratada como prova normativa.

## Adendo V4 — 13/09/2026

A V4 restaura `verify.py` **com escopo de prova reduzido e explicitado**:

- `engine.py` usa o caminho principal e ponto flutuante;
- `verify.py` não importa `engine.py` nem `simples_core.py`, usa `Decimal` e uma decomposição matemática diferente;
- ambos leem a mesma tabela normativa pelo único `tables_loader.py`;
- portanto a concordância verifica independência de implementação/precisão, **não** independência da fonte normativa;
- a correção da tabela e da interpretação é confrontada separadamente por goldens externos, com procedência oficial/humana declarada;
- `apurar_verificado.py` aplica hard-stop em qualquer divergência de campos materiais;
- um teste de sabotagem altera propositalmente o total do motor principal e comprova que a divergência é detectada.

Essa combinação fecha o falso-verde da V3 sem voltar a alegar que duas contas sobre a mesma tabela constituem duas fontes jurídicas independentes.

A inclusão de suporte a ISS retido não autoriza o script a decidir local de incidência, retenção cabível ou enquadramento da atividade. Essas são premissas jurídicas anteriores ao cálculo.


## Adendo V4.1 — 13/09/2026

A revisão estrutural acrescentou um caso oficial que antes era apenas bloqueado: o **Exemplo 6 do Manual PGDAS-D**.

- mercado interno e externo são calculados separadamente;
- o segmento externo do Anexo I não recolhe Cofins, PIS/Pasep e ICMS no exemplo oficial;
- o total publicado de R$ 12.089,78 virou golden externo com fonte e conferência declaradas;
- `apurar_verificado.py` não emite `PASS` para entrada arbitrária;
- sem golden específico, a saída declara apenas consistência de implementação e baseline global;
- o mesmo modo bloqueia efeito de sublimite, ST, monofásico e início de atividade até existir rotina auditada para essas combinações.
