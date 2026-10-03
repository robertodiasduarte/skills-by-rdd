# Validação da entrega

Data: 03/10/2026.  
Versão: 1.0.0.  
Escopo: E001 V1.

## Gate de escopo

O gate local de consistência retornou `ESCOPO_CONFIRMADO`, com geração autorizada e hash `a709b27c245eed19abdd3c98065a945caf643fb82f9033087de5fb3352c6397e`.

O ambiente não expôs um identificador autenticado da mensagem de confirmação. O registro de build usou um rótulo local de turno; portanto, o gate comprova consistência de texto, versão e hash, não identidade ou autenticação.

## Testes locais executados

Comando equivalente:

```bash
python3 -B -m unittest discover -s tests -p "test_*.py" -v
```

Resultado observado: **7 testes executados; 7 aprovados; 0 falhas**.

Cobertura dos testes:
- janela diária D-1;
- janela semanal D-7;
- bloqueio de nova fonte sem confirmação;
- inclusão de fonte com confirmação registrada;
- normalização de URL e remoção de parâmetros de rastreamento;
- bloqueio de duplicidade sem fato novo;
- permissão de repetição quando o fato novo é explicitado.

Os três scripts foram compilados sintaticamente após os testes. Arquivos `__pycache__` gerados pela compilação foram removidos antes do lint e do empacotamento.

## Smoke tests de CLI

Executados com estado temporário fora do pacote:
- cálculo de janela semanal em `America/Sao_Paulo`, de 26/09/2026 08:05 a 03/10/2026 08:05;
- inicialização e listagem do cadastro de fontes com 19 entradas persistíveis;
- inicialização do histórico, registro de item e detecção posterior como duplicado;
- validação sintática dos arquivos JSON do bundle.

## Lint estrutural local

Executado o lint básico do Skill Builder by RDD sobre a raiz da skill.

Resultado observado: `pass: true`, **20 arquivos**, lista de erros vazia.

Esse lint verifica estrutura, frontmatter, seções, referências locais, scripts citados, extensões, limites e alguns padrões simples de credenciais. Não substitui validador oficial de plataforma, auditoria tributária, revisão editorial nem avaliação comportamental.

## Cenários comportamentais

Foram escritos 14 cenários em `evals/cases.json`, incluindo casos positivos, ausência de novidades, corte temporal, opinião, material promocional, fonte nova, duplicidade, ausência de persistência, ausência de web, cálculo fora de escopo e publicação automática.

Esses cenários **não foram executados como bateria comportamental independente** em um host/modelo-alvo. Portanto, o comportamento de pesquisa, curadoria e redação permanece `escrito_nao_executado` como avaliação comportamental, embora a lógica local dos utilitários esteja `executado_aprovado`.

## O que esta skill ainda NÃO prova

- não prova que a pesquisa encontrará toda publicação existente na internet;
- não prova vigência ou aplicabilidade tributária de uma conclusão sem revisão profissional;
- não prova comportamento idêntico em todos os modelos e hosts;
- não prova disponibilidade permanente dos sites cadastrados;
- não prova persistência quando o host não oferecer armazenamento gravável;
- não prova agendamento recorrente quando o host não oferecer scheduler;
- não autentica a confirmação do usuário por meio do arquivo JSON do gate;
- não prova publicação correta em CMS, pois publicação automática está fora do escopo.
