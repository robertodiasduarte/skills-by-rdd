# Operações do Omie — base de conhecimento

Corte: **10/10/2026**. Fontes em [FONTES_OMIE.md](FONTES_OMIE.md). As habilidades oficiais da Omie entram aqui
**só** como fonte de operação, campo e pegadinha medida — nunca como modelo de skill.

Endereço de operação: `<serviço>:<Método>` (ex.: `financas/pesquisartitulos:PesquisarLancamentos`).
A skill gerada escreve toda operação nesse formato e declara cada uma em `manifest.json › operacoes`.

## Como uma operação é classificada

A mesma regra vale no lint (`scripts/lint_bundle_omie.py`) e no script de totalização (`assets/omie/omie_num.py`):

| Classe | Regra | Efeito na skill gerada |
|---|---|---|
| leitura | o método consta como leitura do serviço em `assets/omie/catalogo_leitura.json` **e** passa na regra de nome (`Listar`, `Consultar`, `Pesquisar`, `Obter`, `Status`…; nunca `ObterProximoLote`, `GerarBoleto`…) | sem gate de escrita |
| escrita | qualquer outro método de um serviço do catálogo — inclusive prefixo desconhecido | gate de escrita literal + `"confirmado": true` + pré-requisito "pedir aprovação" |
| recusada | método marcado `deprecated` no catálogo, ou serviço ausente do catálogo | a filha não gera a skill com essa operação |
| fora do s1 | nome com `Faturar` ou `Inutilizar` | sempre recusada; nomeada em "Quando não usar" |

O catálogo de leitura foi coletado em 04/10/2026 da documentação pública da API (138 serviços, 222 métodos de
leitura). Serviços que o MCP passou a expor depois — **`geral/auditoria`** (quem alterou, o que foi excluído) — não
estão nele e por isso são recusados até a filha ser atualizada.

## Antes de qualquer operação

- `omie_listar_apps` lista as empresas acessíveis. Toda chamada leva `app_hash`; não existe "empresa selecionada".
  Mais de uma empresa e a pessoa não disse qual ⇒ perguntar.
- `omie_buscar_operacao` acha a operação por intenção; `somente_leitura` só **filtra a busca**, não bloqueia nada.
- `omie_descrever_operacao` devolve campos, obrigatoriedade, exemplo e pré-requisitos. É o contrato vivo: a filha
  chama antes de gerar e grava o resumo no `ESCOPO_CONFIRMADO.md` da skill.
- `omie_executar_em_varias` roda a mesma operação em até 40 empresas (caso BPO).

## Financeiro

| Operação | Classe | Campos que importam | Pegadinha medida pela Omie |
|---|---|---|---|
| `financas/resumo:ObterResumoFinancas` | leitura | `dDia` (dd/mm/aaaa), `lApenasResumo`; saída `fluxoCaixa` (`vReceber`, `vPagar`, `vSaldo`) | o total de atraso do resumo **não** reflete todos os títulos atrasados — não usar para atraso |
| `financas/pesquisartitulos:PesquisarLancamentos` | leitura | `cStatus` (`ATRASADO`, `VENCEHOJE`), `cNatureza` (`R`/`P`), `dDtVencDe`/`dDtVencAte`, `nPagina`, `nRegPorPagina`; saída `nTotRegistros`, `nTotPaginas`, valor em aberto `nValAberto` | a contagem está em `nTotRegistros` (1 por página basta para contar); somar valor exige percorrer páginas |

## Vendas

| Operação | Classe | Campos que importam | Pegadinha |
|---|---|---|---|
| `geral/clientes:ListarClientes` | leitura | `clientesFiltro` (`cnpj_cpf`, `razao_social`, `nome_fantasia`) | mais de um resultado ⇒ perguntar; nenhum ⇒ parar, não cadastrar sem pedido |
| `estoque/resumo:ObterEstoqueProduto` | leitura | `xCodigo` (código, EAN ou descrição), `dDia`; saída `nPrecoUnitario`, `listaEstoque`, `nIdProduto` | mais de um produto ⇒ perguntar |
| `geral/parcelas:ListarParcelas` | leitura | código da condição de pagamento | pergunte a condição se a pessoa não disse |
| `produtos/pedido:IncluirPedido` | **escrita** | etapa `"10"` (pedido) | incluir não emite nota, mas o pedido passa a existir |
| `produtos/pedido:ConsultarPedido` | leitura | `numero_pedido` (o da tela) → `codigo_pedido` | — |
| `produtos/pedido:ListarPedidos` | leitura | `etapa` `"50"` = a faturar; `total_de_registros`; `total_pedido.valor_total_pedido`; `infoCadastro.dInc` | — |
| `produtos/pedido:StatusPedido` | leitura | `ListaNfe` | — |
| `produtos/pedidovendafat:FaturarPedidoVenda` | **fora do s1** | — | o servidor **não** exige `confirmado` para faturar |

## Serviços

| Operação | Classe | Campos que importam | Pegadinha |
|---|---|---|---|
| `servicos/os:ListarOS` | leitura | `filtrar_por_status` `"N"` (não faturada), `dDtPrevisao`, `nValorTotal` | — |
| `servicos/os:ConsultarOS` | leitura | `cNumOS` (o da tela) → `nCodOS` | — |
| `servicos/os:StatusOS` | leitura | `nCodOS`, `lMsg` `"S"` | — |
| `servicos/osp:FaturarOS` | **fora do s1** | — | o servidor **não** exige `confirmado` |

## Estoque e CRM

| Operação | Classe | Campos que importam | Pegadinha |
|---|---|---|---|
| `estoque/consulta:ListarPosEstoque` | leitura | `dDataPosicao`, `cExibeTodos` `"S"`, `lista_local_estoque` `"TODOS"`; `nSaldo`, `estoque_minimo`, `reservado`, `fisico` | — |
| `estoque/consulta:ListarMovimentoEstoque` | leitura | `idProd`, `dDtInicial`, `dDtFinal`; `tipo`, `qtde`, `desOrigem`, `dtMov` | sem movimento **não é erro** |
| `crm/fases:ListarFases` | leitura | `nCodigo`; a última fase é a conclusão | — |
| `crm/oportunidades:ListarOportunidades` | leitura | `fase`; `ticket.nTicket`; `previsaoTemp`; `outrasInf.dAlteracao`; `total_de_registros` | — |
| `geral/tarefas:ListarTarefas` | leitura | `cIntervalo`, `cSituacao`, `cAtribuidasAMim`, `dDataInicial`/`dDataFinal`; `cUrgente`, `cImportante`; `nTotRegistros` | — |

## Conduta que vale copiar das oficiais

- Todo destaque declara o critério ("abaixo do mínimo: `estoque_minimo` > 0 e `nSaldo` < `estoque_minimo`").
- Não recomenda, não sugere compra, desconto ou ordem de cobrança; não reorganiza a agenda.
- Escrita: um documento por vez, conferir o status depois e não tentar de novo sozinho.

O que **não** copiar: soma de valores pelo modelo (vira `omie_num.py` no perfil Conferidor ou recusa no Operador) e
confirmação só em prosa (vira o gate literal de [PADRAO_ESCRITA.md](PADRAO_ESCRITA.md)).
