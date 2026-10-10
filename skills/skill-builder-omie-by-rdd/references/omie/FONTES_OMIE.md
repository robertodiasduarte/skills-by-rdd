# Fontes Omie

| Fonte | Uso | Coleta |
|---|---|---|
| Central de ajuda Omie — "Conectando o Omie a um assistente de IA (MCP)", "… ao Claude", "… ao ChatGPT" | servidor, OAuth, conexão, confirmação | 10/10/2026 |
| Documentação técnica do MCP — https://api.omie.com.br/docs | 5 ferramentas, endereçamento `<serviço>:<Método>` | 10/10/2026 |
| Guia de habilidades — https://api.omie.com.br/guia (pacote `omie-habilidades.md`) | operações, campos e pegadinhas de [OPERACOES.md](OPERACOES.md) | 10/10/2026 (16 habilidades; `omie-cadastrar` indisponível) |
| `consulta-omie-somente-leitura` 1.0.0 (Metodologia RDD) | catálogo de leitura e transporte do `omie_num.py` | catálogo coletado em 04/10/2026 |

Mudou alguma dessas fontes ⇒ nova versão da filha, com data de corte nova.

<a id="omie_num"></a>
## `assets/omie/omie_num.py` — o que mudou em relação ao `omie_consulta.py`

Origem: `consulta-omie-somente-leitura@1.0.0:scripts/omie_consulta.py`. O `assets/omie/catalogo_leitura.json` é
cópia exata do `references/catalogo_leitura.json` da mesma versão. Vigia: `HERANCA.json` (modo `derivado`).

Mantido igual: barreira dupla de leitura (catálogo **e** regra de nome, as duas exigidas), teto de 5 páginas e
100 registros por página, retentativa só em erro transitório, parada em HTTP 425, credenciais do ambiente ou do
`.env`, higienização de credencial nas mensagens, `OMIE_BASE_URL` só https (http só para localhost em teste).

Mudou:
- um subcomando só, `totalizar`; saíram `metodos` e `baixar` (o MCP faz a descoberta; download não é deste perfil);
- o catálogo é lido ao lado do script, não de `references/`;
- total só sai quando a API informou a contagem, os registros lidos batem com ela, nada foi truncado, todo valor do
  campo somado é numérico e a soma direta bate com a soma por grupo (ou por página). Qualquer falha ⇒
  `status: divergente`, exit 2, sem nenhum valor agregado na saída;
- valor não numérico, ausente, infinito ou NaN não é mais "ignorado e contado": reprova o total.
