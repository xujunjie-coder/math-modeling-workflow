# Mathematical Modeling Workflow Policy

This plugin coordinates an evidence-first mathematical-modeling workflow. The user's request and the current contest rules remain authoritative.

## Core invariants

- Keep raw data unchanged. Record every cleaning, filtering, aggregation, and unit conversion rule.
- Treat each subquestion as a gated unit with one canonical manifest under `planning/manifests/`.
- Do not infer human choices. Method selection, result acceptance, claim boundaries, and final freeze require an explicit human decision in the decision ledger.
- Do not invent data, results, citations, figures, robustness evidence, or interpretations.
- Every numerical paper claim must trace to a canonical result artifact from the approved run.
- Separate exploratory artifacts from frozen submission artifacts.
- A formal statistical figure must be generated deterministically from saved evidence. Generative image tools may be used only for non-evidentiary illustrations.
- Prefer a main method, a usable baseline, and at most one trigger-based fallback. Do not add models merely for breadth.
- Preserve upstream/downstream interfaces across subquestions: IDs, units, filters, labels, symbols, parameters, seeds, and versions.
- A semantic change to frozen evidence requires affected work to be rerun and re-frozen before paper claims are updated.

## Rigor profiles

- `lean`: optimize for rapid, reviewable modeling. Keep manifests, method cards, human decisions, risk probes, run summaries, and compact evidence.
- `submission`: additionally require final explanations, robustness, a signed solution package, frozen numbers, formal figure plans, paper sections, full-paper assembly, render verification, and three independent final audits.

## Final submission boundary

Do not mark the submission complete until every active subquestion passes G5, the master paper passes G5.5, the rendered DOCX/PDF passes G5.6, and consistency, completeness, and quality-assurance audits pass G6.

Never place project-specific progress items in this packaged policy. Current gaps belong in project manifests or a generated status report.
