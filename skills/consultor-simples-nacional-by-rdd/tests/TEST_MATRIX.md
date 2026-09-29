# Matriz de testes — V4

## Sumário de navegação
- Goldens oficiais
- Fronteiras
- Excepcionais e bloqueios
- Protocolo
- Cobertura por regra

## Goldens oficiais

| ID | Regra | Entrada | Resultado esperado | Fonte/procedência |
|---|---|---|---|---|
| G001 | SN-ALIQUOTA-001 | Anexo I, RBT12p 120.000, RPA 10.000 | DAS 400,00 | Manual PGDAS-D, exemplo oficial publicado |
| G002 | SN-ALIQUOTA-001 | Anexo III, RBT12 500.000, RPA 10.000 | 9,972%; DAS 997,20 | Manual PGDAS-D, exemplo oficial publicado |
| G003 | SN-ALIQUOTA-001 | Anexo V, RBT12 500.000, RPA 10.000 | DAS 1.752,00 | Manual PGDAS-D, exemplo oficial publicado |
| G004 | SN-RBT12P-001 | primeiro mês, receita 10.000 | RBT12p 120.000 | Manual PGDAS-D, exemplo oficial publicado |

Nenhum valor produzido pela própria Skill é golden.

| G005 | SN-EXPORT-001 | Exemplo 6: interno 2 mi/100 mil + externo 1 mi/50 mil | interno 9.935,02; externo 2.154,76; total 12.089,78 | Manual PGDAS-D, Seção 12, Exemplo 6 |

## Fronteiras

| ID | Regra | Entrada | Resultado esperado | Fonte |
|---|---|---|---|---|
| F001 | SN-ALIQUOTA-001 | RBT12 180.000,00 | faixa 1 | tabela vigente derivada da norma |
| F002 | SN-ALIQUOTA-001 | RBT12 180.000,01 | faixa 2 | tabela vigente derivada da norma |
| F003 | SN-FATORR-001 | FS12/RBT12 = 0,28 | Anexo sugerido III, se a atividade for sujeita ao fator R | Manual/P&R fator R |
| F004 | SN-ISSRET-001 | receita retida = RPA | base de ISS zero; demais bases preservadas | Resolução 140/2018 |
| F005 | SN-LIMITE-001 | limite exato | não tratar como excesso | LC 123/2006 |
| F006 | SN-SUBLIMITE-001 | sublimite exato | respeitar comparador da regra | P&R/Manual PGDAS-D |

## Excepcionais e bloqueios

| ID | Regra | Entrada | Resultado esperado | Fonte/contrato |
|---|---|---|---|---|
| X001 | SN-TEMPORAL-001 | cálculo 01/2027 | recusa; sem fallback | contrato de cálculo |
| X002 | SN-EXPORT-001 | exportação informada com `modo=ordinario` | bloqueio | Manual PGDAS-D, Exemplo 6 + contrato de capacidade |
| X003 | SN-SUBLIMITE-001 | `sublimite=true` no motor genérico | bloqueio | Manual PGDAS-D + contrato |
| X004 | SN-RBT12P-001 | valor negativo | erro | especificação |
| X005 | SN-EVIDENCIA-001 | busca sem resultado | `STATUS=SEM_EVIDENCIA` | gate operacional |
| X006 | SN-ALIQUOTA-001 | engine sabotado em 10,00 | divergência/hard-stop | arquitetura V4 |
| X007 | SN-SEGURANCA-001 | lista acima da cota | recusa da barreira | política de segurança |

## Protocolo

| ID | Regra | Caso | Resultado |
|---|---|---|---|
| E001 | SN-RECUSA-001 | Lucro Presumido | recusa literal; nenhum percentual/norma externa |
| E002 | SN-TEMPORAL-001 | DAS 01/2027 | recusa numérica; nenhum DAS |
| E003 | SN-RECUSA-001 | fator R sem FS12/RBT12 | pedir dados; `nao disponivel` |
| E004 | SN-TEMPORAL-001 | conceito 2027 | consultar base local; não usar motor legado |

## Cobertura por regra

| Regra | Oficial/humano | Fronteira | Excepcional/protocolo |
|---|---|---|---|
| SN-ALIQUOTA-001 | G001–G003 | F001–F002 | X001, X006 |
| SN-FATORR-001 | fonte oficial da regra | F003 | E003 |
| SN-RBT12P-001 | G004 | casos mês 1/2 | X004 |
| SN-ISSRET-001 | dispositivo oficial | F004 | entrada retida > RPA |
| SN-CNAE-001 | tabela derivada + norma | múltiplos resultados | CNAE ausente/ambíguo |
| SN-LIMITE-001 | norma | F005 | excesso >20% |
| SN-SUBLIMITE-001 | manual/P&R | F006 | X003 |
| SN-EXPORT-001 | G005 | separação interno/externo | X002 + efeito de sublimite bloqueado |
| SN-EVIDENCIA-001 | política | n/a | X005 |
| SN-TEMPORAL-001 | catálogo/tabelas | último ano disponível | X001/E004 |
| SN-RECUSA-001 | contrato | n/a | E001–E003 |
| SN-SEGURANCA-001 | política | cotas | X007 |

A coluna “oficial/humano” não inventa um número quando não existe caso numérico conferido: nesses casos, o teste verifica regra estrutural/documental e a lacuna permanece explícita.
