# Versioning and governance

## Synchronized governance
The child skill version and `PERSONA.md` version move together. Record every released change in `CHANGELOG.md`.

Use semantic versioning as a practical convention:
- PATCH: editorial correction, broken link repair, formatting, or non-substantive clarification without changing the modeled persona;
- MINOR: new evidence, refined wording, added language pattern, expanded use case, or moderate persona refinement without replacing the core avatar;
- MAJOR: material change to jobs, pains, gains, role, market, language, decision criteria, or other core persona assumptions.

## Research cut-off
Record the research cut-off date in `PERSONA.md` and `manifest.json`.

## No silent drift
Normal child use never edits the persona implicitly. New research on user request may be used for the current answer, but changing the bundled persona requires an explicit update request.

## Contradiction protocol
Present:
1. current persona statement;
2. new evidence;
3. why they conflict;
4. source-quality and population comparison;
5. possible impact on communication;
6. update recommendation as a proposal, not an automatic change.

## Changelog entry
Each version entry should include:
- version;
- date;
- reason;
- files affected;
- persona dimensions changed;
- sources added or retired;
- compatibility or behavior impact.
