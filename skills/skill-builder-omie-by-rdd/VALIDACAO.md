# Validação da entrega

Data: 10/10/2026. Versão: 1.0.0. Ambiente: Python 3, execução local, sem acesso à Omie.

## Testes executados

```bash
python3 -B -m unittest discover -s "$SKILL_ROOT/tests" -p "test_*.py"
```

Resultado observado: **113 testes executados; 112 aprovados; 0 falhas; 1 pulado** (o mesmo teste de
symlink que o pai pula no macOS).

- 43 controles herdados da `skill-builder-by-rdd` (`tests/test_controls.py`, cópia vigiada).
- Controles Omie (`tests/test_omie.py`): derivação do perfil, amarração do perfil ao escopo por hash, mudança de
  perfil invalidando a confirmação herdada, gate de escrita (ausente, fora de ordem, sem `"confirmado": true`, sem
  pré-requisito), fronteira fiscal, faturar declarado, escrita fora da antiga lista de prefixos, operação
  `deprecated`, serviço fora do catálogo, operação não declarada (com endereço, pelo nome ou em JSON), perfil do escopo cruzado com o do pacote, Conferidor sem conferência de empresa, operação instruída fora do `SKILL.md`, faturar/inutilizar fora da parte "não usar" e varredura do catálogo inteiro (as 222 de leitura
  dão leitura; as bloqueadas dão escrita ou recusada; zero exceções).
- `omie_num.py` (`assets/omie/test_omie_num.py`, servidor HTTP local): total ok, teto exato de 5 páginas,
  6 páginas truncam, contagem divergente, valor não numérico ou ausente, sem contagem informada, consistência por
  injeção, valor infinito, lista vazia da Omie como zero, número em texto ambíguo, decimal sem passar por float, soma sem arredondamento silencioso, .env só da pasta do projeto, parâmetro inválido como erro de uso, limite de consumo que para sem retentar, empresa das chaves, agrupamento, escrita recusada, leitura fora dos exemplos aceita, barreira de nome independente,
  http fora de localhost recusado e credencial que não vaza em erro da API. Em toda saída divergente, nenhum
  valor agregado.

## Validação estrutural

`scripts/lint_bundle.py --root <esta pasta>` (herdado) e `scripts/heranca-check.py` do catálogo com exit 0.

## O que esta skill ainda NÃO prova

Os 12 cenários de `evals/cases.json` foram escritos e não executados em modelos; 3 deles exigem o
conector do Omie ligado. O lint de domínio prova que o protocolo de escrita está no texto da skill gerada, não que o
modelo do usuário o siga. "Pedir aprovação" no conector é declaração do usuário. Lista completa em
`manifest.json › pending`.
