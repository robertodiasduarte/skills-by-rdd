# Contract for generated persona child skills

## Naming
Generate one child named `persona-{avatar}` in lowercase kebab-case. One package equals one avatar.

## Required frontmatter
The generated child must include:
- name;
- description;
- license: MIT;
- metadata.author: Roberto Dias Duarte;
- metadata.methodology: Metodologia de Roberto Dias Duarte;
- metadata.version.

The body must include:
`## Metodologia e autoria`
with the literal sentence:
`Esta skill foi construída com a metodologia de Roberto Dias Duarte.`

## Required package
```text
persona-{avatar}/
  SKILL.md
  CHANGELOG.md
  manifest.json
  references/
    PERSONA.md
    SOURCE_CATALOG.md
    EVIDENCE_MAP.md
    LANGUAGE_PATTERNS.md
    COMMUNICATION_METHODS.md
    VALUE_PROPOSITION.md
    COPY_AND_CAMPAIGNS.md
    RESEARCH_LOG.md
    TECHNICAL_CONTENT_LOCK.md
    RUNTIME_COMPATIBILITY.md
  evals/
    cases.json
  agents/
    openai.yaml
```

Do not add files merely to look complete.

## PERSONA.md minimum content
- avatar name and role;
- market geography;
- language;
- version and research cut-off date;
- intended use cases;
- role context and responsibilities;
- functional, social, and emotional jobs;
- pains and obstacles;
- gains and desired outcomes;
- objections;
- decision criteria and trust signals;
- technical repertoire;
- vocabulary and formality;
- attention priorities;
- journey situations;
- communication preferences;
- ethical persuasion opportunities and limits;
- unresolved hypotheses;
- evidence ID links for consequential statements.

## Three modes
### personificacao
Respond from the researched perspective of the composite avatar. Use phrases such as "para este avatar" or "a pesquisa sugere" when uncertainty matters. Do not claim to be a real person or universal representative of the niche.

### transformacao
Adapt supplied content to the persona. Preserve protected source facts and conclusions. Improve hierarchy, context, vocabulary, examples, salience, explanation, persuasion, and call to action where justified.

### auditoria
Evaluate fit against jobs, pains, gains, objections, repertoire, language, trust criteria, and channel. Separate observations from recommendations.

## Default web policy
Normal use is corpus-first. Research the web only when the user explicitly requests new research or an update. New research does not automatically modify the bundled persona.

## JSON output contract
When the user requests machine-readable output, return a single JSON object with at least:
```json
{
  "texto_final": "...",
  "persona": "persona-{avatar}",
  "modo": "personificacao|transformacao|auditoria",
  "ajustes_realizados": [],
  "riscos_sinalizados": [],
  "versao_persona": "1.0.0",
  "fontes_utilizadas": []
}
```

Additional fields are allowed only when documented. Keep `texto_final` as the actual usable content, not an explanation about it.

## Technical source preservation
Copy the generated child version of `TECHNICAL_CONTENT_LOCK.md` and enforce it for reports, financial statements, tax summaries, payroll, regulatory news, or any other professional content.

## Updating
When new research contradicts the current persona, show the divergence. Update only after explicit user request. Version the child and PERSONA together and write the change to CHANGELOG.

## Validation cases
Every child must include at least:
- one personification case;
- one transformation case with protected technical facts;
- one audit case;
- one misleading-claim negative case;
- one recalculation negative case;
- one web-research-on-request case;
- one contradiction-without-auto-update case;
- one JSON-output case.
