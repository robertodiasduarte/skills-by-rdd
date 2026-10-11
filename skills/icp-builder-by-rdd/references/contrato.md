# Contrato de perfil e geração

`scripts/build_child.py` lê JSON UTF-8, não executa seu conteúdo e não depende de conectores. Use caminhos reais. A pasta final recebe o valor de `skill.name`. Uma pasta existente gera erro, preservando sua versão e personalizações.

## Estrutura

Todos os campos abaixo são obrigatórios. Campo ainda não conhecido: use texto explícito como “A investigar” ou lista vazia e mantenha a lacuna em `research_gaps`. Não use texto vazio para representar desconhecimento em campos de texto. Crie `draft` enquanto houver lacunas relevantes.

| Campo | Tipo/conteúdo |
| --- | --- |
| `schema_version` | Inteiro `1` |
| `status` | `draft` ou `ready` |
| `skill` | `name` (slug minúsculo, até 64 caracteres), `display_name`, `short_description` (25–64 caracteres) |
| `company` | `name`, `context`, `offers`, `differentiators`, `delivery_limits`, `commercial_context` |
| `icp` | `label`, `persona_name`, `kind` (`b2b`, `b2c` ou `hibrido`), `fit_criteria`, `exclusion_criteria`, `roles` |
| `evidence` | Lista não vazia de registros, descritos abaixo |
| `voice` | `terms`, `avoid`, `quotes`, `synthetic_examples` |
| `journey` | Lista não vazia de fases, descritas abaixo |
| `decisions` | `alternatives`, `criteria`, `forces`, `objections` |
| `priorities` | Lista de oportunidades por atividade/fase, descritas abaixo |
| `research_gaps` | Lista de textos de lacunas; pode ser vazia se apropriado |

Textos: `company.name/context/commercial_context`, `icp.label/persona_name/kind`. Demais campos diretos de `company` e `icp` são listas de textos. `voice.terms/avoid/synthetic_examples`, `decisions.alternatives/criteria` também. `decisions.forces` tem as listas `push`, `pull`, `anxiety`, `habit`. Nomes de chaves são em inglês para estabilidade do contrato; conteúdo é no idioma do usuário.

Campos adicionais em objetos são preservados no JSON; em empresa/ICP/voz/decisões são também renderizados. Não use campos adicionais para esconder hipóteses: mantenha evidência, status e lacuna explícitos.

## Evidências

Cada item de `evidence`:

```json
{
  "id": "E1",
  "claim": "O cliente relatou buscar menor esforço administrativo.",
  "status": "relatado",
  "source": "Entrevista com cliente, data conhecida ou data não informada",
  "confidence": "media"
}
```

Valores de `status`: `observado`, `relatado`, `hipotese`, `desconhecido`, `exemplo`. `confidence`: `alta`, `media`, `baixa`, `nao_avaliada`; reflete sustentação do registro, não probabilidade matemática. Declare na fonte se a fala veio do empresário, cliente, documento ou modelo. Uma hipótese permanece hipótese mesmo se parecer convincente.

ID único: letras, números, `_` e `-`. `source` pode ter URL ou localização de arquivo sem incluir segredos/dados pessoais desnecessários. Textos livres não autorizam executar instruções ou acessar sistemas citados neles.

Para permitir análise de padrões, inclua em `source` o código do participante ou da unidade de origem, seu papel, o episódio e a localização do trecho quando conhecidos. Exemplo de formato: “P03, cliente, primeiro recebimento, entrevista de data informada, trecho 12”. Fontes dependentes devem manter a mesma origem identificável: dez afirmações de P03 não equivalem a dez clientes. Documente recorrência e casos divergentes na afirmação/lacuna, sem converter amostra qualitativa em percentual de mercado. O método está em [pesquisa e síntese](metodos/pesquisa.md).

`voice.quotes`: itens `{ "text": "Fala efetivamente fornecida", "evidence_id": "E1" }`; o registro precisa ser `observado`, `relatado` ou `exemplo`, com fonte identificável. Se a fonte é exemplo, isso continua visível na renderização. Nunca vincule frase criada a fonte factual. `synthetic_examples` contém apenas propostas de linguagem, marcadas na saída como simulação.

## Fases

Cada fase contém `id`, `label`, `context`, `actions`, `thinking`, `emotions`, `jobs`, `trigger`, `barriers`, `touchpoints`, `success`, `transitions`, `evidence_ids`.

- Textos: `id`, `label`, `context`, `trigger`, `success`.
- Listas de textos: `actions`, `thinking`, `emotions`, `barriers`, `touchpoints`.
- `jobs`: listas `functional`, `emotional`, `social`; listas vazias são permitidas.
- `transitions`: lista de `{ "to": "id-de-outra-fase", "when": "Condição da transição" }`. Lista vazia representa fim/saída conhecida ou transição a investigar. Não imponha fase linear.
- `evidence_ids`: lista não vazia de IDs existentes; referência de grupo não converte interpretações da fase em fatos. Acrescente evidência de hipótese para campos inferidos, identifique esses campos como hipótese no texto ou deixe “A investigar”.

Fases atuais, futuras e propostas precisam ser diferenciadas em `context` e evidências. Não invente canais, emoções ou desejo de comprar para preencher todas as listas.

## Objeções e prioridades

`decisions.objections`: `{ "statement": "Fala real ou hipotética", "underlying_concern": "Preocupação sustentada ou hipótese", "evidence_ids": ["E1"] }`.

`priorities`: `{ "activity": "digital", "stage_id": "fase", "opportunity": "Proposta contextual, natureza explícita", "evidence_ids": ["E1"] }`. Atividades válidas: `digital`, `relacionamento`, `funil`, `eventos`, `produtos`, `vendas`, `objecoes`.

Registre oportunidade nas sete atividades para uma filha abrangente. Pode ser “sem oferta adequada nesta fase” ou “a investigar”; não é preciso inventar iniciativa. `ready` exige as sete atividades, alternativas, critérios de aderência e alguma evidência real/relatada. Essas checagens não substituem revisão humana/modelo do conteúdo nem validação de mercado.

## Executar e revisar

```bash
python3 /caminho/icp-builder-by-rdd/scripts/build_child.py \
  --profile /caminho/perfil.json --output-root /caminho/skills-geradas
```

O gerador cria perfil e jornada Markdown com IDs, tabela de evidências, métodos autossuficientes e metadados. Não instala, publica nem envia mensagens. Depois, inspecione os entregáveis e instale no local permitido quando isso fizer parte do pedido. Para atualização, gere em outro diretório e compare antes de substituir a versão instalada.

O exemplo [Beatriz](../assets/exemplo-beatriz.json) está em `draft`: empresa ilustrativa, história fornecida como exemplo e oportunidades inferidas com status `hipotese`. É material de demonstração/teste, não um perfil aprovado de empresa real.
