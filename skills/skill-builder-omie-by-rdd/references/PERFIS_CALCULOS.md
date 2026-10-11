# Perfis e cálculo verificado

## Perfil pedido versus perfil efetivo

Preservar os perfis da documentação RDD (§§2.2–2.3):
A calcula e audita; B consulta a base; AB combina; C opera sem base normativa utilizável.

Para A, exigir processo normativo e material em norma, tabela ou regra.
Para B, exigir ao menos um Markdown de base efetivamente disponível.
Caso isolado não substitui norma, tabela, regra ou base.

| Pedido | Base e material normativo utilizáveis | Perfil |
|---|---|---|
| operacional | qualquer situação | C |
| consulta | base | B |
| consulta | sem base | C |
| calcula | processo normativo + norma/tabela/regra | A |
| calcula | falta o gatilho duplo | C |
| ambas | ambos | AB |
| ambas | só base | B |
| ambas | só gatilho normativo | A |
| ambas | nenhum | C |

O script scope_gate.py deriva essa matriz para os materiais do contrato.
Ele não decide se uma norma é juridicamente suficiente nem se a classificação feita
pelo responsável está correta. Valida presença, tipos, arquivos e consistência.

## Três níveis que não se confundem

1. **Perfil elegível:** há materiais do tipo necessário.
2. **Caminho implementado:** um código declara e executa aquela hipótese.
3. **Caminho liberado:** fontes, tabelas, implementação, verificação, gabaritos e testes
   foram efetivamente conferidos.

Não promover nível 1 diretamente a nível 3.
A falta de prova pode permitir entregar uma skill consultora ou operacional, com
autorização renovada, mas não um executor numericamente “quase validado”.

## Preservação dos princípios numéricos RDD

P1: número profissional final nasce de código, nunca de prosa estimada.
P2: motor e verificador calculam por caminhos independentes; divergência bloqueia.
P3: constante vigente vem de tabela local versionada e fonte, nunca da memória.
P4: gabarito normativo tem procedência e conferência humana; não é inventado pelo LLM.
P5: COMO_FUNCIONA explica o cálculo a quem não lê código.
P11: declarar o que não foi provado.
P12: valor condicionado a enquadramento jurídico usa campo `*_sugerido`, com premissa.

A concordância entre motor e verificador prova aspectos da implementação, não uma
segunda fonte normativa. Ambos podem compartilhar uma tabela incorreta.
Casos oficiais conferidos podem fornecer validação externa; ainda assim não provam
todos os cenários não testados.

## Separação de passes e independência

Preparar primeiro um contrato comum: entradas, unidades, fontes, tabelas, período,
hipóteses, caminhos, arredondamentos e tratamento de erro.

Gerar engine.py em um contexto. Gerar verify.py em **outro contexto isolado**,
recebendo somente o contrato comum e as fontes, nunca motor, derivados explicativos
de sua implementação ou resultados produzidos por ele.

Uma mensagem “ignore o motor” no mesmo histórico não prova cegueira.
Um único chat que gerou os dois não deve afirmar independência de geração.
Sem recurso de isolamento, registrar `independencia_de_geracao_nao_comprovada`.
Não declarar o caminho liberado. Entregar contrato e pendências, ou migrar para
consulta/operação com confirmação.

Preservar a convenção técnica da fonte: engine com float, verify com Decimal.
Documentar arredondamento e testes de fronteira; não inferir tolerância monetária.
Usar formulação alternativa publicada quando existir; senão, decomposição diferente.
Não chamar decomposição diferente de segunda fórmula publicada.
Se for proposta outra arquitetura numérica, identificá-la como alteração a aprovar.

## Contrato de execução

Scripts de cálculo: Python 3, biblioteca padrão, offline, entradas explícitas,
saída JSON determinística, sem ações externas. Usar caminhos independentes do cwd.
Todo número constante tem fonte documentada. Schemas fechados recusam campos extras.

verify.py não importa engine.py nem suas funções. Compartilhar um carregador de
tabelas não equivale a compartilhar a lógica de cálculo.

Ambos declaram CAMINHOS_IMPLEMENTADOS em nível de módulo, fora de docstrings.
Confrontar declaração, âncoras, escopo e testes executados. A âncora isolada não prova
implementação. Cada caminho precisa de execução positiva e negativa pertinente.

O carregador de tabelas recusa período ausente, esquema incompatível e fonte ausente.
Não reaproveitar “a tabela mais próxima” ou o último ano sem autorização normativa.

## Gabaritos e hard-stop

Cada gabarito deve conter fonte_do_gabarito, conferido_por, entrada, saída esperada,
período e localizador. Um nome escrito pelo LLM não prova conferência humana.
Se o material não fornecer evidência, registrar a pendência.

A ordem da rotina verificada é baseline oficial, engine, verify, comparação e entrega.
Preservar os nomes/códigos do contrato RDD quando essa camada for implementada:
BASELINE_OFICIAL_FALHOU (5); MOTOR_OU_VERIFY_RECUSOU (4);
DIVERGENCIA_ENGINE_VERIFY (6); GABARITO_OFICIAL_DIVERGIU (7); sucesso (0).

Em falha, `entrega_bloqueada=true` e nenhum número de resultado.
Não mostrar “os dois valores para o usuário escolher”.
Aplicar teste de sabotagem e confirmar que a saída não vaza o resultado.

## Zero caminho liberado

Remover engine.py, verify.py e apurar_verificado.py da entrega operacional da filha.
Manter documentação e pendências sem oferecer um caminho alternativo para obter números.
Não incluir executável rebatizado como “rascunho” que permita contornar o bloqueio.
Renovar confirmação se a capacidade final for menor que a aprovada.

Essas regras orientam a geração futura. Esta meta-skill não inclui motor tributário,
tabelas de tributos, cálculos trabalhistas ou gabaritos jurídicos prontos.
