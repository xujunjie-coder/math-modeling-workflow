---
name: consistency-auditor
description: Run scoped or final cross-media consistency checks for mathematical-modeling artifacts, comparing canonical numbers, symbols, parameters, decisions, files, and paper claims without performing full-workspace audits for low-risk changes.
---

# Modes

- `scoped`: run only for a `CANONICAL` or `FROZEN` change and only for affected Qx/identifiers.
- `final`: run across all submission artifacts after global assembly and final render, before submission approval.

# Sources of Truth

Prefer:

- `frozen_numbers.json` for paper numbers;
- `qx_decisions.jsonl` for human judgments;
- `planning/symbol_table.md` for symbols/units;
- approved code plan and run summary for parameters and executed methods;
- solution package for writer-facing structure.

Use legacy decision logs or Markdown reviews only during migration.

# Checks

1. Numerical claims match frozen values and units.
2. Formula, parameter, constraint, and method roles match approved code and plan.
3. Symbols and units match the global symbol table.
4. Referenced tables, figures, code, and data files exist.
5. Why-this-method, result verdict, stability, confidence, and claim scope resolve to human decision IDs.
6. Freeze and decisions are not stale relative to materially changed cited evidence.
7. The assembled master covers every active Qx exactly once and preserves registered upstream/downstream interfaces.
8. Global problem restatement, analysis, preprocessing, assumptions, symbols, references, and appendices do not restart inside question sections.
9. Abstract, body, conclusion, final DOCX/PDF, assembly manifest, claim map, and renumber map agree.
10. Figure/table/equation/reference numbers and artifact paths are continuous and valid; no caption is orphaned.

# Scoped Workflow

1. Receive changed files/identifiers and their impact class.
2. Resolve affected Qx and downstream consumers.
3. Check only those relationships.
4. Return a compact digest or save `results/Qx/reports/scoped_consistency.json` when durable evidence is needed.
5. Do not rewrite other artifacts.

# Final Workflow

1. Check all submission Qx and `paper/master/full_paper.md` against the assembly manifest.
2. Check rendered final DOCX/PDF against the master paper and renumber map.
3. Save `paper/audits/cross_media_consistency_audit.md`.
4. Report `PASSED`, `FAILED`, or `NOT_RUN`.
5. List concrete divergences and repair owners. Do not pad a pass list.

# Rules

- Do not run a full audit for formatting, comments, scratch work, or ordinary pre-freeze exploration.
- Do not infer canonical numbers from the paper.
- Do not repair divergences inside the audit.
- Do not repair or approve final assembly directly.

# Verification

- Scope matches the semantic impact.
- Every divergence identifies source, consumer, and expected repair.
- Final audit covers all ten check classes, including global assembly and rendered artifacts.
- Verdict follows actual evidence rather than an item count.
