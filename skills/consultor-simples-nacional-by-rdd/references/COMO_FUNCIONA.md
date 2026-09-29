# Como funciona — auditabilidade humana V4.1

## Sumário de navegação
- scripts/apurar_verificado.py
- scripts/avaliar_limite_receita.py
- scripts/avaliar_sublimite.py
- scripts/calcular_anexo_i_st.py
- scripts/calcular_anexo_ii.py
- scripts/calcular_anexo_iii.py
- scripts/calcular_anexo_iv.py
- scripts/calcular_anexo_v.py
- scripts/calcular_fator_r.py
- scripts/calcular_rbt12p.py
- scripts/engine.py
- scripts/ingest_guard.py
- scripts/lint_bundle.py
- scripts/lookup_cnae.py
- scripts/safe_facts.py
- scripts/search_kb.py
- scripts/simples_core.py
- scripts/tables_loader.py
- scripts/validate_goldens.py
- scripts/verify.py

Este arquivo explica os scripts em linguagem de negócio. A verificação redundante usa **implementação separada, decomposição algébrica própria e tipo numérico distinto**; engine e verify compartilham a **mesma tabela normativa local**. Portanto ela detecta divergências de implementação/precisão, mas não transforma a mesma tabela em segunda fonte normativa. Erros de regra ou tabela exigem golden externo ou outra evidência independente.

## scripts/apurar_verificado.py
1. Recebe a apuração já classificada, inclusive o `modo`, e valida primeiro a baseline de exemplos oficiais.
2. Executa o cálculo principal e o caminho de conferência independente sobre a mesma entrada; o Exemplo 6 oficial é tratado no modo de exportação do Anexo I.
3. Compara campos materiais; se houver divergência, bloqueia a entrega. Sem golden específico, rotula o resultado apenas como cálculo determinístico, nunca como aprovação normativa.

## scripts/avaliar_limite_receita.py
1. Recebe a receita acumulada usada para avaliar o limite anual.
2. Compara o valor com os marcos previstos pela rotina e identifica a faixa de excesso.
3. Devolve uma triagem para orientar a leitura da regra documental; a conclusão jurídica continua dependente da fonte recuperada.

## scripts/avaliar_sublimite.py
1. Recebe receita acumulada e sublimite informado para o caso.
2. Compara abaixo, no limite ou acima, preservando a distinção entre limite do regime e sublimite de ICMS/ISS.
3. Devolve uma triagem que deve ser combinada com período, UF e evidência documental antes de concluir.

## scripts/calcular_anexo_i_st.py
1. Separa receita ordinária, receita com ICMS-ST e receita monofásica informada.
2. Aplica a tabela vigente do Anexo I e retira apenas as parcelas tributárias que a segregação permite.
3. Devolve o DAS calculado com avisos de escopo; cenários fora da rotina exigem outra análise.

## scripts/calcular_anexo_ii.py
1. Recebe RBT12, receita do período e ano já classificados como Anexo II.
2. Aplica a faixa e a tabela vigente do período.
3. Devolve cálculo do Anexo II; não decide se a atividade é industrial nem se existe qualificação especial.

## scripts/calcular_anexo_iii.py
1. Recebe RBT12, receita do período e eventual receita que sofreu retenção de ISS.
2. Aplica a tabela vigente do Anexo III e reduz a parcela de ISS somente sobre a receita retida.
3. Devolve o cálculo sem decidir, por si, se a atividade pertence ao Anexo III.

## scripts/calcular_anexo_iv.py
1. Recebe RBT12, receita do período e eventual receita com ISS retido.
2. Aplica a tabela do Anexo IV e preserva a regra de que a CPP patronal não integra o DAS desta rotina.
3. Devolve o cálculo com os avisos necessários para não confundir DAS com a contribuição patronal externa.

## scripts/calcular_anexo_v.py
1. Recebe RBT12, receita do período, FS12 e eventual receita com ISS retido.
2. Calcula o fator R como apoio e usa a regra documentada para sugerir III ou V somente se a premissa jurídica já tiver sido confirmada.
3. Devolve o cálculo e mantém explícita a premissa de sujeição ao fator R.

## scripts/calcular_fator_r.py
1. Recebe FS12, RBT12 e competência.
2. Aplica as regras de zero e de precisão do período e compara o fator considerado com 0,28.
3. Devolve `anexo_sugerido` e uma premissa não verificada; não transforma cálculo em classificação jurídica.

## scripts/calcular_rbt12p.py
1. Recebe a receita atual e até onze receitas anteriores, aceitando pontuação brasileira.
2. Aplica receita do mês vezes doze no primeiro mês ou média dos meses anteriores vezes doze nos meses seguintes.
3. Devolve a RBT12 proporcionalizada e o critério usado; valores negativos ou quantidade excessiva de meses são recusados.

## scripts/engine.py
1. Recebe JSON com modo explícito: ordinário ou exportação de mercadorias no Anexo I.
2. No modo ordinário aplica a tabela anual; no modo de exportação calcula mercado interno e externo separadamente e zera Cofins, PIS/Pasep e ICMS no segmento externo.
3. Produz o número candidato; sozinho ele não autoriza entrega e o modo de exportação é bloqueado quando há efeito de sublimite.

## scripts/ingest_guard.py
1. Recebe um novo arquivo textual permitido e verifica extensão e tamanho antes de ler o conteúdo.
2. Recusa segredo ou dado pessoal com dígito verificador válido, normaliza o texto e extrai fatos sob cotas.
3. Passa a estrutura pela barreira duas vezes e só então entrega o material estruturado para consumo.

## scripts/lint_bundle.py
1. Inspeciona estrutura, links, frontmatter, grafo, scripts, goldens, evals e documentação antes do release.
2. Verifica independência do verificador, ausência de caminhos inválidos, dados pessoais válidos e arquivos órfãos.
3. Reprova o bundle se qualquer requisito bloqueante falhar.

## scripts/lookup_cnae.py
1. Recebe CNAE ou descrição textual e pesquisa a tabela derivada local.
2. Amplia a busca com radicais e sinônimos controlados para melhorar a triagem sem esconder ambiguidades.
3. Devolve todas as possibilidades relevantes, procedência e aviso de que a atividade efetiva e a norma precisam ser confirmadas.

## scripts/safe_facts.py
1. Recebe estruturas extraídas de documentos e aceita somente tipos escalares e coleções permitidas.
2. Reconstrói o conteúdo com limites de profundidade, quantidade e bytes UTF-8.
3. Serializa e reconstrói novamente para impedir que estruturas fora do contrato cheguem ao agente.

## scripts/search_kb.py
1. Recebe a pergunta ou termos e pesquisa somente o corpus local selecionado.
2. Localiza trechos, identifica título/seção/linhas e produz hash curto para rastreabilidade.
3. Entrega registros estruturados pela barreira; resultado vazio encerra o fluxo em vez de autorizar resposta de memória.

## scripts/simples_core.py
1. Centraliza parsing numérico brasileiro e operações matemáticas compartilhadas pelas rotinas auxiliares.
2. Obtém valores normativos somente pelo carregador de tabelas e aplica faixa, partilha e regras de ISS implementadas.
3. Não decide atividade, CNAE, enquadramento jurídico nem vigência fora das tabelas disponíveis.

## scripts/tables_loader.py
1. Recebe o ano do cálculo e procura somente a pasta daquele período.
2. Carrega o arquivo normativo local se ele existir e estiver válido.
3. Se o período não existir, lista os anos disponíveis e bloqueia o cálculo; nunca usa o ano mais próximo.

## scripts/validate_goldens.py
1. Percorre somente casos cujo resultado esperado veio de exemplo oficial publicado ou conferência humana declarada.
2. Executa engine e verify contra cada caso externo e compara o resultado esperado.
3. Reprova a baseline quando qualquer caminho deixa de reproduzir o caso conferido; o script nunca cria um golden.

## scripts/verify.py
1. Recebe exatamente a mesma apuração e a mesma tabela normativa local, inclusive no modo de exportação do Anexo I.
2. Recalcula com Decimal e implementação separada, sem importar `engine.py` nem `simples_core.py`.
3. A independência é de implementação e precisão, não de fonte normativa. O Exemplo 6 e demais casos publicados são conferidos por goldens externos; para entrada sem golden, a concordância não é chamada de validação normativa.
