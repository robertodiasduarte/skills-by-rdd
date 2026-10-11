# Compatibilidade por capacidades

Diferença em relação à `skill-builder-by-rdd`: aqui **a integração é requisito**. Sem o conector MCP do Omie a
filha ainda conduz a entrevista, mas só gera o perfil Operador e marca a skill como não exercida.

## Modos

| Modo | Capacidades | O que dá para fazer |
|---|---|---|
| Conversacional | texto e diálogo | entrevista, escopo e confirmação; arquivos entregues em blocos de texto; sem teste ao vivo |
| Integrado | conector MCP Omie autorizado (`https://api.omie.com.br/mcp`) | contrato real das operações, leitura de teste na sua empresa, perfil Operador exercido |
| Integrado + executável | conector + Python 3.10+ com rede para `app.omie.com.br` + `.env` com `OMIE_APP_KEY` e `OMIE_APP_SECRET` | perfil Conferidor exercido (`omie_num.py`), gate de escopo e lints locais |

Os scripts usam só a biblioteca padrão. O `.env` fica na pasta do projeto do usuário, nunca no chat.

## Onde instalar

- **Claude (web e desktop):** Configurações → Conectores → Omie (rótulo "Comunidade") → Conectar; depois instalar o
  zip em Skills. Marcar `omie_executar` e `omie_executar_em_varias` como "pedir aprovação".
- **Claude Code:** `claude mcp add --transport http omie https://api.omie.com.br/mcp`, depois `/mcp` → omie →
  autorizar no navegador. Instalar a skill na pasta de skills do projeto ou do usuário.
- **ChatGPT:** o conector existe (Apps e integrações), mas esta filha **não foi testada** lá. Colar o `SKILL.md` e
  as referências funciona como texto, sem os controles por script.

Suporte real de cada aplicativo é característica dele, não garantia derivada do nome. O caminho de menu acima foi
conferido em 10/10/2026.

## Sem persistência

Salvar o resumo do escopo, o `perfil_omie.json` e o registro de confirmação fora da conversa. Contexto perdido ⇒
não presumir que uma versão antiga continua autorizada.
