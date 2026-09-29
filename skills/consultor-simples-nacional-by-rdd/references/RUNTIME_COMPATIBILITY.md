# Compatibilidade de runtime — V4.1

## Sumário de navegação
- Python
- Diretório de trabalho
- Rede
- Claude Code
- API
- Evals de corpus fechado

## Python

Os comandos documentados usam `python3`. Os scripts dependem apenas da biblioteca padrão.

## Diretório de trabalho

Nunca dependa do diretório atual. Defina `SKILL_ROOT` como o caminho do diretório que contém `SKILL.md` e execute:

`python3 "$SKILL_ROOT/scripts/<script>.py" ...`

Os scripts localizam dados internos por `Path(__file__)`, não pelo `cwd`.

## Rede

O frontmatter declara `allowed-tools: Read, Bash`, omitindo WebSearch/WebFetch. Isso é uma **allowlist de ferramentas da Skill, não um firewall**. No Claude Code, `Bash` pode alcançar a rede se o host permitir egress.

Em especial, se o ambiente permitir egress por Bash, a ausência de WebSearch/WebFetch não impede um comando de rede por si só.

## Claude Code

Para execução comprovadamente fechada:
1. bloquear egress no sandbox/host;
2. restringir comandos conforme política organizacional;
3. registrar tool log;
4. executar eval com `forbid_network=true`;
5. não considerar o detector de log como substituto de firewall/sandbox.

## API

O desenho é offline e stdlib-only. Nenhum script da Skill precisa de rede ou instalação de pacote.

## Evals de corpus fechado

Ablação e avaliação devem ocorrer com rede efetivamente desabilitada. Caso contrário, a execução pode compensar falhas de recuperação consultando fontes externas e produzir falso-verde.
