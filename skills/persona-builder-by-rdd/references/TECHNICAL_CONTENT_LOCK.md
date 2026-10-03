# Technical content lock

## Purpose
Persona adaptation changes communication, not the professional result contained in the source.

## Protected elements
Unless the user supplies an authoritative correction, preserve:
- numbers and signs;
- percentages and rates;
- dates and periods;
- account, tax, payroll, legal, medical, regulatory, and technical labels;
- named regimes or classifications;
- factual claims attributed to the technical source;
- uncertainty or qualification language;
- conclusions and recommendations from the professional source;
- references and citations supplied with the source.

## Allowed transformation
The persona skill may change:
- order and hierarchy;
- headings and summaries;
- explanations around protected content;
- vocabulary when meaning remains unchanged;
- examples and analogies that do not introduce new facts;
- emphasis based on avatar relevance;
- call to action around the professional result;
- length and formatting.

## Suspected source issue
If an inconsistency appears, do not silently repair it. Preserve the original and add a signal such as:
`possible_source_issue: [brief description]`.

If the user wants correction, request the corrected result or invoke a separate appropriate professional workflow when available.

## Example
Source: "RBT12: R$ 1.200.000; aliquota efetiva informada: 10,25%."

Allowed: explain what RBT12 means for the avatar and why the effective rate matters, while retaining both values exactly.

Not allowed: recompute the effective rate, change 10,25% to a remembered rate, or infer a tax annex not stated by the source.

## News and regulation
A persona skill may adapt a provided regulatory news item to the avatar. It must not convert the persona corpus into legal or tax authority. If current verification is requested, research and cite current sources separately from persona evidence.
