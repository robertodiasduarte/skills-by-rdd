# Contrato de automação JSON

A skill-filha deve aceitar pedidos automatizados sem depender de Make, n8n ou outro orquestrador específico.

## Entrada sugerida
Campos opcionais, conforme o fluxo:

```json
{
  "modo": "transformacao",
  "tarefa": "reescrever_post",
  "canal": "linkedin",
  "texto_origem": "...",
  "instrucoes": "...",
  "output": "json"
}
```

A skill deve tolerar nomes de campos diferentes quando o sentido estiver claro. Não exigir este envelope em conversa normal.

## Saída padrão
Quando `output=json`:

```json
{
  "status": "ok",
  "modo": "transformacao",
  "versao_alma": "1.0.0",
  "texto_final": "...",
  "alinhamento_com_a_alma": {
    "nivel": "alto",
    "elementos_aplicados": ["..."],
    "desvios_relevantes": []
  },
  "alteracoes_realizadas": ["..."],
  "alertas": []
}
```

## Status
- `ok`: tarefa concluída.
- `ok_com_alertas`: conteúdo produzido, mas há ressalvas relevantes.
- `dados_insuficientes`: não é possível executar com segurança sem contexto essencial.
- `bloqueado`: pedido depende de alegação ou ação que a alma não pode validar.

## Regras
- Não escrever markdown, comentários ou preâmbulo fora do JSON quando `output=json`.
- `nivel` pode ser `alto`, `medio`, `baixo` ou `nao_avaliado`; é diagnóstico editorial, não pontuação científica.
- Alertas devem ser objetivos e consumíveis por máquina.
- Não iniciar uma entrevista dentro de um fluxo automático. Se faltar dado, retornar `dados_insuficientes` com a lista do que falta.
- Não incluir dados pessoais dos fundadores na saída.
- Em `transformacao`, `texto_final` é o principal produto. Em `auditoria`, pode ser `null` quando o usuário não pediu reescrita.
