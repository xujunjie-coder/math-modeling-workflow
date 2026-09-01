---
name: quality-assurance-auditor
description: Perform the final submission-level audit of mathematical-modeling workflow integrity, evidence quality, anti-fabrication, paper coherence, figures, references, and contest readiness after consistency and completeness audits pass.
---

# Preconditions

- `rigor_profile` is `submission`.
- All Qx reached G5, global G5.5 assembly passed, and G5.6 formatted/rendered artifacts passed visual verification.
- Final consistency and completeness audits exist.

# Audit Dimensions

1. **Workflow integrity**
   - G1–G5 passed per Qx.
   - Human judgments trace to the decision ledger.
   - Main/baseline/fallback execution respected approved scope.

2. **Evidence integrity**
   - No fabricated data, references, experiments, metrics, or figures.
   - Main claims trace to frozen numbers and robustness evidence.
   - Limitations and uncertainty are visible.

3. **Method quality**
   - Baseline is usable.
   - Assumptions, units, objectives, constraints, and solution steps are coherent.
   - Output concentration/degeneracy and failure triggers were addressed.

4. **Paper quality**
   - Problem, method, results, and conclusions align.
   - Claims are proportional to tested comparisons.
   - Human-owned physical meaning and contribution are present.
   - One global outline covers every active Qx once; no standalone question paper restarts inside the master.
   - Shared preprocessing, assumptions, symbols, references, and appendices are not duplicated.
   - Cross-question transitions name the upstream object and preserve its scope, units, labels, thresholds, and version.

5. **Presentation**
   - Required figures/tables exist and passed render checks.
   - Figure types are used correctly.
   - References are real, complete, and consistently cited.
   - AI-use disclosure follows the current contest profile and verified rules.
   - No orphan caption, missing image, split table header, unexplained blank page, or broken cross-reference remains in the rendered final paper.

# Workflow

1. Read the two earlier audits and unresolved blockers.
2. Read the assembly manifest and sample canonical sources directly; do not trust summaries alone.
3. Inspect the rendered final paper, including all pages with dense formulas, wide tables, figures, chapter transitions, references, and appendices.
4. Record blocking and nonblocking findings with artifact paths and repair owners.
5. Save `paper/qa_report.md`.
6. Set verdict:
   - `PASSED`
   - `FAILED`
   - `NOT_RUN`

# Rules

- Do not approve on partial audits.
- Do not use artifact count or bullet count as a proxy for quality.
- Do not repair issues inside QA.
- Do not hide uncertainty or downgrade a blocker silently.
- Do not claim compliance with time-varying contest rules without verification.

# Verification

- All five audit dimensions were evaluated.
- Blocking findings are explicit and actionable.
- QA verdict agrees with consistency/completeness verdicts and sampled evidence.
- Submission is recommended only when assembly, render verification, and all three audits pass.
