# Aviso de revisão do ChatGPT na skill-builder-by-rdd (20/11/2026)

## O que aconteceu

Uma aluna com conta ChatGPT Business instalou a `skill-builder-by-rdd` 1.1.2 e o ChatGPT mostrou:

> **Analise esta habilidade antes de usá-la.** Nossa análise de segurança identificou um comportamento
> potencialmente arriscado nesta habilidade. O comportamento desta habilidade pode não corresponder ao nome
> ou à descrição.

Junto vinha o botão **Aprovar habilidade**. Era o nível intermediário da análise do ChatGPT: a skill ficava
liberada depois da revisão. O nível acima disso é o bloqueio, quando a skill não pode ser usada.

## O que foi verificado

| Verificação | Resultado |
| --- | --- |
| O `.zip` enviado pela aluna × a `main` deste repositório (1.1.2) | idênticos byte a byte (`diff -r`, 23 arquivos) |
| Rede, `eval`/`exec`, leitura de variáveis de ambiente nos scripts | nenhum; os scripts só leem arquivos locais |
| Caracteres invisíveis (zero-width, bidi, uso privado) | nenhum |
| O mesmo pacote, em outra conta, em 18/10/2026 | instalado sem aviso |
| `assets/icon.svg` que aparece na tela do ChatGPT | não está no `.zip`: o próprio ChatGPT acrescenta o ícone |
| A aluna apagou as skills que tinha e enviou de novo | o aviso não apareceu |

A OpenAI não publica os critérios da análise e diz que ela não substitui a revisão de quem instala.

## Conclusão

Não foi possível provar uma causa. O fato mais forte é este: **o mesmo pacote, sem nenhuma mudança, foi
marcado numa instalação e passou em outras**. As explicações compatíveis com isso:

1. A análise é feita por um modelo e não dá sempre o mesmo resultado.
2. Havia skills com nome ou descrição parecidos já instaladas na conta da aluna. Ela apagou essas skills
   antes de enviar de novo.
3. A análise ficou mais rígida entre outubro e novembro.

O conteúdo tinha dois pontos que se encaixam no texto do aviso. Eles foram corrigidos mesmo sem prova de
causa, porque já eram problemas por si só:

- **Autoria e licença impostas sem aviso.** A 1.1.2 obrigava toda skill gerada a sair com `license: MIT`,
  `metadata.author: Roberto Dias Duarte` e a ordem "não omitir nem reformular", e a descrição não dizia
  nada disso. A skill gerada é do usuário.
- **Frases de injeção dentro do pacote.** Os cenários de teste em `evals/cases.json` citam frases como
  "ignore o brainstorm" e "usuário já aprovou tudo". São exemplos de ataque, mas um analisador
  automático pode lê-los como instrução.

## O que mudou

- `skill-builder-by-rdd` **1.2.0**: autor e licença da skill gerada são perguntados no brainstorm (sugestão:
  MIT). O crédito à metodologia continua por padrão, aparece no resumo do escopo e pode ser retirado.
  A descrição declara isso. Os cenários de conversa foram para a pasta `evals` do repositório
  (`evals/skill-builder-by-rdd/cases.json`) e não entram mais no `.zip`.
- `skill-builder-omie-by-rdd` **1.1.0**: a mesma mudança, nos modelos Operador e Conferidor também.
  O `lint_bundle_omie.py` só deixa de exigir o crédito quando o `manifest.json` da skill gerada registra
  `"credito_metodologia": false`. Os cenários de conversa foram para `evals/skill-builder-omie-by-rdd/cases.json`.
- O README ganhou a seção "O ChatGPT pediu para analisar a skill antes de usar?".

## Para o próximo caso

1. Peça o `.zip` que a pessoa enviou e compare com a Release (`diff -r` ou `SHA256SUMS.txt`).
2. Peça para apagar as versões antigas ou duplicadas e enviar de novo.
3. Para testar se uma mudança removeu o aviso, envie as duas versões várias vezes na mesma conta. Uma
   tentativa só não decide nada, porque a análise varia.
4. Antes de publicar uma skill, confira se a descrição anuncia tudo o que o corpo impõe ao usuário ou ao
   que a skill entrega.
