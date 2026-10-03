# Escopo confirmado - E002 V1

Confirmation received from the user after the scope summary:
`CONFIRMO O ESCOPO E002 V1 E AUTORIZO GERAR A SKILL.`

## Approved objective
Create `persona-builder-by-rdd`, a meta-skill that researches and builds one evidence-based market avatar per child package, generating `persona-{avatar}` for personification, transformation, and audit of communication.

## Approved coverage
- evidence from niche research, studies, communities, interviews, reviews, user materials, and web research;
- possible detection of multiple market segments, with user choice of one avatar per child;
- canonical `PERSONA.md` and detailed references;
- three child modes: personification, transformation, audit;
- market geography and language required;
- versioned child and persona with CHANGELOG;
- optional JSON for agents and automation;
- new web research in child only when user asks;
- contradictory new evidence does not auto-update the current persona;
- public-source summaries of Value Proposition, Jobs to Be Done, launch methods, persuasion, behavioral communication, and clear writing.

## Approved exclusions and protections
- one avatar only per child skill;
- the child does not recalculate, correct, or replace technical source conclusions;
- misleading or unsupported claims are signaled without persuasive amplification;
- no pseudoscientific claim of neurological effects from classic NLP/PNL;
- no copying of paid or proprietary course materials;
- Formula de Lancamento public content is a practitioner reference; commercial claims remain provider claims unless independently verified.

## Operational profile
RDD profile: C - operational.
Calculation period: not applicable.
Research: mandatory for initial build; later research only on user request.

## Deterministic scope-gate limitation
The `scope_gate.py` bundled with Skill Builder by RDD accepts only the area values `contabil`, `tributario`, `trabalhista`, or `juridico`. This approved scope is marketing/communication and cannot be represented truthfully by that enum. Therefore no false area was inserted merely to make the script pass. Approval linkage for this release is conversational and documented here; structural lint and packaging are executed separately.
