# Changelog

## 3.0.0 - 2026-09-20

### Adicionado
- Modos `semantic` e `full` recuperados da v2.1.0.
- `semantic_catalog.py`, `validate_semantic_map.py` e `validar.py`.
- `process_document.py` como pré-processador determinístico auxiliar.
- Regras e templates de mapa semântico.
- LICENSE MIT.

### Preservado da versão atual
- Publicador com relatório estruturado e validação fail-closed.
- SHA-256, nomes padronizados, UTF-8/LF e proteção contra sobrescrita.
- Casos de aceitação e política conservadora de vigência.
- Proteção contra instruções embutidas em documentos.

### Aprimorado
- O processador automático não é tratado como certificação final: revisão rígida prevalece.
- `LOCALIZACAO APROXIMADA` não permite inventar artigo, anexo ou tabela.
- Frontmatter corrigido e consolidado com autoria/licença.
- Comandos documentados padronizados em `python3`.
