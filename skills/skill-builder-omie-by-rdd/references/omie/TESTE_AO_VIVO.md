# Teste ao vivo (antes de entregar)

A filha exercita a skill gerada **só em leitura**, na empresa do próprio usuário, pelo conector dele. Escrita
nunca é exercida pela meta-skill: não existe ambiente de teste na Omie.

## Sequência

1. `omie_listar_apps` respondeu? Sim ⇒ `mcp_disponivel: true`. Não ⇒ dizer, com estas palavras:
   "Não encontrei a conexão com o Omie neste ambiente. Posso gerar o perfil Operador, que você testa depois de
   conectar." — e gravar `mcp_disponivel: false`.
2. Para cada operação declarada: `omie_descrever_operacao` (contrato real) e conferir que os campos usados na skill
   existem com esse nome. Divergência ⇒ corrigir o texto da skill antes de entregar.
3. Para cada operação de **leitura**: uma chamada mínima (1 registro por página, período curto) com
   `omie_executar`. Erro de campo ⇒ corrigir e repetir uma vez.
4. Perfil Conferidor com Python e `.env` disponíveis: rodar `scripts/omie_num.py totalizar` da skill gerada uma vez
   e conferir que a saída traz `conferencia` com `lidos` igual a `informados`.
5. Gravar `evidencias/exercida.md` na skill gerada.

## O que vai em `evidencias/exercida.md`

Data, cliente usado (Claude, Claude Code), operações chamadas, quantidade de registros devolvida e o status da
conferência. **Nunca:** `app_hash`, CNPJ, CPF, razão social, nome de pessoa, valores em reais. Valores aparecem
como `R$ ***`; contagens podem aparecer.

## Sem teste ao vivo

Sem `evidencias/exercida.md`, `manifest.json › pending` contém `nao_exercida_contra_omie` e a entrega diz que a
skill não foi exercida contra o Omie.
