# Validação da entrega

Data: 20/09/2026. Versão: 1.1.1.
Ambiente de teste: Python 3.13.5, execução local.
Os testes são de software e de protocolo; não contêm gabaritos normativos.

## Testes executados

Comando equivalente, independente do diretório corrente:

```bash
python3 -B -m unittest discover -s "$SKILL_ROOT/tests" -p "test_*.py" -v
```

Resultado observado: **43 testes executados; 43 aprovados; 0 falhas; 0 pulados.**
Inclui 16 combinações de perfil verificadas como subtestes dentro de um dos 43 testes.
Subtestes não foram somados à contagem de testes.

Foram exercitados: aprovação válida; aprovação anterior ao resumo; “ok” ambíguo;
origem documental; falta de evidência da mensagem; escopo ou revisão alterados;
material alterado; matriz de perfis; caminho inseguro; symlink; JSON inválido,
duplicado ou não finito; estrutura de skill; ordem de seções; script órfão;
referência ausente; numeral romano; credencial sintética e colisão de caminhos.

O fluxo CLI foi executado com resultado positivo e com entradas negativas.
Os scripts foram compilados sintaticamente sem gerar arquivos de cache.


## Validação estrutural local

Executado `python3 "$SKILL_ROOT/scripts/lint_bundle.py" --root "$SKILL_ROOT"`.
Resultado observado: `pass: true`, lista de erros vazia, 24 arquivos.

O empacotador de skills do ambiente também valida o frontmatter antes de criar o ZIP.
O pacote deve conter uma única raiz e uma única entrada principal SKILL.md.

## Fonte preservada

SHA-256 da documentação original incluída:

```text
34907dee229d6ce5c783e60a10127c12654ba3b90caa4b60703da279af8d35d9
```

A cópia incluída corresponde byte a byte ao arquivo fornecido.
Não houve acesso ao repositório citado na documentação.

## O que esta skill ainda NÃO prova

Os 14 cenários comportamentais em evals/cases.json foram escritos, mas não
executados em Claude, ChatGPT, Grok, Kimi ou outro produto.
Os 43 testes locais não demonstram obediência universal de modelos ao protocolo.

Não foram executados os templates nem o validador original da plataforma RDD.
Não houve validação normativa, conferência profissional ou teste de motores de domínio.
O gate verifica consistência de dados: autenticação, captura de consentimento,
isolamento de contexto e restrição de rede dependem do host.

O lint básico não é auditoria jurídica, scanner completo de PII ou implementação
integral de YAML. A portabilidade é de instruções e recursos, não uma promessa
de instalação nativa ou comportamento idêntico em todos os fornecedores.
