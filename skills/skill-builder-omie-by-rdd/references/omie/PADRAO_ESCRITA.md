# Padrão de escrita

O MCP da Omie **não tem ambiente de teste**: toda gravação é real e imediata. O servidor só recusa sem
`"confirmado": true` para excluir, cancelar, contratar serviço pago, negativar e protestar. **Faturar e inutilizar
não exigem confirmação** — por isso ficam fora desta versão.

Uma regra em prosa é preferência do modelo, não controle. Esta filha coloca três coisas verificáveis em toda skill
com escrita, e o `scripts/lint_bundle_omie.py` reprova o pacote que não as tiver:

## 1. O gate literal (copiar sem reescrever)

```markdown
### Gate de escrita

1. **Validar** antes: chame a operação de validação da Omie quando existir; sem ela, confira cliente, itens e condição com as operações de leitura. Status diferente de "0" ou dado faltando ⇒ pare e mostre o motivo.
2. **Mostrar** o documento completo que será gravado (cliente, itens, quantidades, valores e condição).
3. Pedir a **frase literal** `CONFIRMO GRAVAR <tipo> <identificador>`. Qualquer outra resposta não autoriza.
4. **Um por vez**: uma frase por documento; lote exige uma frase para cada um.
5. Executar com `"confirmado": true` e **conferir o status** com a operação de consulta.
6. **Não repetir**: erro ou dúvida no status ⇒ pare e informe; nunca tente de novo sozinho.
```

Os seis passos ficam numerados de 1 a 6, nesta ordem, sob o título `### Gate de escrita`.

## 2. `"confirmado": true` explícito

A chamada de escrita leva `"confirmado": true` mesmo quando a operação não exige — documenta que a pessoa confirmou
naquela mensagem. A skill nunca envia `"confirmado": true` antes da frase literal.

## 3. Pré-requisito no conector

No Claude, em Configurações → Conectores → Omie, marcar `omie_executar` e `omie_executar_em_varias` como
**pedir aprovação**. É o único freio mecânico do lado do cliente. A filha pergunta se isso foi feito e grava a
resposta em `perfil_omie.json › aprovacao_por_ferramenta` (declaração, não verificação).

## Fronteira desta versão

Toda skill gerada lista em "Quando não usar": **faturar** pedido ou OS (NF-e, NFS-e) e **inutilizar** numeração,
inclusive "só desta vez", inclusive com confirmação. Operação com `Faturar` ou `Inutilizar` no nome reprova o pacote.
