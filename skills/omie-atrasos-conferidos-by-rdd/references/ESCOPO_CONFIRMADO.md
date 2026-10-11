# Escopo confirmado

Escopo **OMIE-ATR V2** · sha256 do escopo `5b6deec5-dd9e24fa-e7d14a08-9a0c3ed6-89bb92f4-070ff851-9785fcd2-75e054f4` · confirmado em 10/10/2026 com a frase
`CONFIRMO O ESCOPO OMIE-ATR V2 E AUTORIZO GERAR A SKILL.`. Gerada pela `skill-builder-omie-by-rdd` 1.0.0.

**Perfil Omie:** Conferidor — a skill precisa somar valores de vários títulos, e o ambiente declarado roda Python com rede e tem o conector do Omie.

**Objetivo:** mostrar quantos títulos estão atrasados e quanto somam, a receber e a pagar, por faixa de atraso, com o total conferido por script.

**Público:** contador ou BPO que acompanha títulos de uma empresa no Omie. **Revisão humana:** o contador confere os totais no painel do Omie antes de usar.

**Cobre:**
- títulos atrasados a receber e a pagar
- faixas: até 30, de 31 a 90 e mais de 90 dias
- quantidade por faixa pela contagem da Omie
- valor em aberto por faixa somado pelo omie_num.py com conferência

**Não cobre:**
- faturar ou inutilizar
- dar baixa, alterar ou excluir título
- dizer quem cobrar ou em que ordem
- análise financeira, de liquidez ou de inadimplência
- carteira de várias empresas
- total do resumo financeiro como total de atraso

**Entradas:**
- empresa (app_hash)
- natureza: a receber, a pagar ou as duas

**Saídas:**
- tabela natureza × faixa com quantidade e valor
- linha de conferência por total
- memória da consulta

**Período de consulta:** dados ao vivo no momento da execução; faixas contadas a partir da data da consulta. **Período de cálculo:** nao aplicavel.

**Critérios de aceite:**
- nenhum total sem status ok do omie_num.py
- linha de conferência junto de cada total
- faixa sem título aparece com zero títulos, não omitida

**Lacunas declaradas:**
- nomes de campo de PesquisarLancamentos confirmados só no teste ao vivo
- faixa com mais de 5 páginas sai sem total, só com a quantidade
