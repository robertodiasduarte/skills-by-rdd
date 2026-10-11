# Como funciona

Esta é uma fábrica de skills para o Omie, filha da `skill-builder-by-rdd`. Ela não consulta nem grava nada no
Omie em seu nome: ela entrevista você e entrega **outra skill** que faz isso, testada antes da entrega.

A conversa segue o mesmo método da skill-mãe: o trabalho que se repete, um caso real, o resultado esperado, uma
situação em que a skill deve parar, e só então o escopo por escrito. A geração começa depois de uma nova mensagem
sua confirmando aquele escopo com a frase pedida.

O que muda por ser Omie:

- **O conector do Omie precisa estar ligado** no aplicativo onde a entrevista acontece. É por ele que a filha lê o
  contrato real de cada operação (`omie_descrever_operacao`) e faz uma leitura de teste na sua empresa antes de
  entregar. Nenhum dado da empresa passa pela RDD.
- **Duas perguntas decidem o perfil da skill.** Se ela só mostra e opera, é Operador: roda no Claude comum e nunca
  soma valores. Se ela precisa somar ou comparar valores de vários registros e você roda Python (Claude Code), é
  Conferidor: todo total sai de um script que confere se leu tudo o que a Omie informou.
- **Gravar no Omie tem freio por escrito.** Toda skill que inclui pedido, OS, tarefa ou cadastro traz o mesmo
  protocolo de seis passos e pede uma frase literal antes de cada gravação. Recomendamos também marcar "pedir
  aprovação" para `omie_executar` no conector — é o único freio que não depende do modelo.
- **Faturar e inutilizar ficam de fora** desta versão: o servidor da Omie não pede confirmação para essas duas
  ações e não existe ambiente de teste.

A filha não verifica a sua identidade nem garante que todo modelo seguirá todas as instruções. O que ela prova por
código está em `VALIDACAO.md`; o que ainda não prova está em `manifest.json › pending`.
