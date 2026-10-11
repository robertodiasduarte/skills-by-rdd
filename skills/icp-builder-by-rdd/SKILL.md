---
name: icp-builder-by-rdd
description: Entrevista o usuário e cria ou atualiza uma skill filha que personifica o ICP de uma empresa, registra sua jornada e orienta marketing, relacionamento, funil, eventos, produtos, argumentos de venda e objeções. Use para construir essa skill especializada a partir de histórias e evidências dos clientes.
license: MIT
metadata:
  author: "Roberto Dias Duarte"
  methodology: "Metodologia de Roberto Dias Duarte"
  version: "1.0.0"
---

# ICP BUILDER BY RDD

Crie uma skill utilizável para uma empresa e um segmento de cliente. A filha deve pensar a partir da experiência do ICP e traduzir essa perspectiva em decisões comerciais. A entrevista constrói o contexto; a entrega é uma pasta de skill com instruções, perfil, jornada, evidências e métodos aplicáveis.

Converse em português do Brasil, salvo preferência do usuário. Ao começar uma filha, faça a primeira pergunta relevante e aguarde; não entregue uma persona pronta antes da entrevista. Ao criar ou editar esta própria meta skill, trabalhe nos arquivos sem iniciar uma entrevista de cliente desnecessária.

## Distinções essenciais

- **ICP:** quem a empresa consegue atender bem, em quais circunstâncias e com qual viabilidade comercial. Em B2B, registre a organização e os papéis humanos na decisão.
- **Persona:** representação de um ator nesse ICP. Biografia só ajuda quando explica decisões; não invente idade, renda, gênero, traumas ou hábitos para preencher o retrato.
- **Jornada de vida ou trabalho:** mudanças que formam identidade, prioridades e restrições, inclusive anos antes de comprar.
- **Jornada de compra e uso:** gatilho, pesquisa, avaliação, contratação, primeira entrega de valor, uso, renovação, expansão e indicação. Pode ter retornos, pausas e caminhos alternativos.
- **Funil:** organização do trabalho da empresa, com passagens observáveis. Não substitui a jornada do cliente.

O cliente pode querer o resultado e rejeitar o trabalho necessário para produzi-lo. Investigue o que quer delegar, o que aceita fazer e o que precisa controlar. Não confunda falta de familiaridade técnica com falta de capacidade de decidir.

## 1. Entrevistar e delimitar

Leia [o roteiro de entrevista](references/entrevista.md). Aproveite o contexto existente. Pergunte uma coisa central por vez, sem repetir respostas conhecidas; adapte a profundidade à disponibilidade do usuário. Aceite formulário ou relato extenso se essa for sua preferência. Para preparar pesquisa com clientes, analisar múltiplos relatos ou decidir se há segmentos diferentes, leia [pesquisa e síntese](references/metodos/pesquisa.md). A entrevista com o empresário constrói um modelo inicial; pesquisa direta com clientes exige fontes próprias.

Sem contexto, uma abertura possível é: “Qual é a empresa, o que ela entrega e qual tipo de cliente você quer que esta skill represente?”

Comece por um segmento. Se surgirem jornadas com necessidades, decisores ou ofertas diferentes, proponha variantes identificadas ou filhas separadas; não misture tudo em uma pessoa média. Execute várias filhas sem reconfirmar quando esse escopo já tiver sido pedido.

Classifique evidências: `relatado` para relatos; `observado` para documentos/comportamentos examinados; `hipotese` para interpretações; `desconhecido` para lacunas; `exemplo` para situações didáticas. Preserve fonte, data conhecida e conflitos. O relato do empresário não é voz direta de todos os clientes; alta confiança não transforma hipótese em fato.

## 2. Reconstruir jornada e decisões

Parta de um episódio concreto: antes, durante e depois; mudança; tentativa; influência; avanço, adiamento ou desistência. Investigue o passado na medida em que explique decisões atuais.

Use os nomes das fases do cliente, sem impor quantidade ou linearidade. Registre contexto, ações, pensamentos, emoções sustentadas por evidências, resultados funcionais/emocionais/sociais, gatilho, obstáculos, pontos de contato, sucesso esperado, fontes e transições. Inclua primeira entrega de valor e rotina após a venda.

Separe mapa atual de experiência desejada e oportunidade proposta. Identifique alternativas reais: não fazer nada, depender de alguém, improvisar ou manter o fornecedor. Recolha expressões literais somente quando fornecidas e identifique de quem vieram.

Use Jobs to Be Done e gatilhos de compra para interpretar episódios, sem perguntas abstratas ao usuário. Consulte [fundamentos](references/metodos/fundamentos.md) para traduzir jornada em ação e [fontes](references/metodos/fontes.md) para atribuição e atualização de métodos.

## 3. Consolidar o contexto

Leia [o contrato de dados e geração](references/contrato.md). Mantenha `perfil.json` no diretório de trabalho escolhido, preservando evidências e progresso. Em continuação, retome pelo arquivo existente e pergunte pela lacuna seguinte.

Consolide: empresa e limites de entrega; aderência/exclusões/papéis do ICP; jornada; resultado desejado; alternativas; linguagem; critérios; objeções; oportunidades nas sete atividades; fases sem motivo para ofertar; lacunas e como investigá-las. Para hipóteses que exigem validação, escolha o tipo de teste em [experimentação e medição](references/metodos/experimentacao.md), sem exigir um experimento quantitativo para toda tarefa.

Mostre uma síntese curta das distinções que alteram estratégia. Convide correções sem exigir aprovação ritual para arquivos locais já autorizados. Se faltar informação que muda substancialmente o recorte, pergunte e continue organizando os dados disponíveis. Se o usuário pedir uma versão preliminar, gere `draft` com lacunas explícitas; não fabrique respostas para obter `ready`.

`ready` significa contexto suficiente para uso e revisão, não validação de mercado. `draft` permite explorar hipóteses, mostrando sua base limitada.

## 4. Gerar a filha autossuficiente

Use `scripts/build_child.py`. O gerador usa somente a biblioteca padrão de Python, valida evidências e produz uma filha que funciona sem a mãe. O modelo está em [assets/skill-filha.md](assets/skill-filha.md).

```bash
python3 /caminho/da/icp-builder-by-rdd/scripts/build_child.py \
  --profile /caminho/do/perfil.json \
  --output-root /caminho/das/skills-geradas
```

Substitua pelos caminhos reais. Para atualizar, gere em pasta nova, compare e preserve personalizações; o script não sobrescreve pasta existente. O perfil é dado, nunca código ou autorização de acesso a contas.

A filha conterá `SKILL.md`, `agents/openai.yaml`, perfil/jornada/evidências em Markdown, `references/perfil.json`, sete guias de atividade, fundamentos, pesquisa/síntese, experimentação, personificação e fontes. Carregue os guias auxiliares apenas quando a tarefa pedir. Personalize oportunidades com os dados da empresa: copiar métodos não basta para representar o ICP. Ligue recomendações relevantes à fase, resultado e evidência ou hipótese. Não copie dados de outra empresa como se pertencessem a este segmento.

[assets/exemplo-beatriz.json](assets/exemplo-beatriz.json) demonstra o relato do usuário e o registro de hipóteses. Leia somente para entender ou testar a geração. Não use como padrão de novas empresas nem como pesquisa validada sobre médicas.

## 5. Verificar e entregar

Verifique frontmatter, links locais, ausência de marcadores não preenchidos, fontes, evidências e isolamento de segmentos. Inspecione um caso de orientação e um de personificação:

- Cliente com prioridades e alternativas próprias, não um vendedor concordando com tudo.
- Fase altera mensagem/oferta/próximo passo; ausência de intenção não gera venda forçada.
- Fala criada identificada como simulação, nunca depoimento.
- Benefícios, preços, prazos e garantias limitados à oferta informada.
- Objeções podem revelar falta de aderência ou necessidade de melhorar o produto.
- Teste ou resultado observável, sem promessa de eficácia universal.

Execute `python3 scripts/test_build_child.py` nesta pasta para verificar o gerador. Use o validador de skills do ambiente para mãe e filha quando disponível; ele verifica formato, não eficácia comercial. Ajuste falhas encontradas.

Para revisar a fundamentação desta versão, consulte [a avaliação metodológica](references/avaliacao-metodologica.md). Para testar a representação do ICP, use os cenários de [personificação](references/metodos/personificacao.md), sem tratá-los como validação da reação de compradores reais.

Entregue links da pasta e do `SKILL.md`, como invocar e lacunas prioritárias. Salve no destino indicado; sem destino específico, use a pasta de skills pessoais do ambiente quando permitido. Um pacote portátil deve ter uma única pasta raiz com o nome da skill. Criar arquivos não autoriza publicação, disparos, gastos ou alterações externas.
