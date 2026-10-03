# Governança e versionamento

O controle de acesso pertence ao host empresarial. Esta skill governa conteúdo e versão, não identidade ou permissão de usuários.

## Versão sincronizada
Usar a mesma versão em:
- frontmatter de `SKILL.md`;
- cabeçalho de `references/ALMA_DA_EMPRESA.md`;
- `manifest.json`;
- `CHANGELOG.md`.

## Regra sugerida
Adotar `MAJOR.MINOR.PATCH`:

- **MAJOR:** mudança que redefine propósito, valores centrais, identidade central ou posicionamento de modo incompatível com a versão anterior.
- **MINOR:** mudança de tom, mensagens, públicos, diferenciais, identidade estendida ou capacidade operacional sem romper a essência central.
- **PATCH:** correção editorial, exemplo, clareza, typo ou ajuste que não muda a decisão de marca.

Se houver dúvida entre duas classes, escolher a maior somente quando a mudança realmente alterar como a skill decide ou escreve.

## Changelog
Cada entrada deve conter:
- versão;
- data;
- motivo;
- elementos alterados;
- impacto esperado na comunicação;
- materiais usados na alteração, quando relevante.

Não registrar dados pessoais desnecessários nem tentar identificar o solicitante se o host não fornecer isso de forma apropriada.

## Atualização da alma
Nunca alterar apenas o prompt da skill quando a mudança é conceitual. Atualizar primeiro a fonte canônica `ALMA_DA_EMPRESA.md` e depois ajustar o comportamento da skill somente se necessário.

## Histórico
O `CHANGELOG.md` é obrigatório. Snapshots completos de versões anteriores da alma são opcionais e só devem ser mantidos quando o usuário pedir ou o ambiente de governança exigir. Não criar arquivos históricos que aumentem exposição de dados pessoais sem necessidade.
