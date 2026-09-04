---
name: python-code-reviewer
description: Review, run, debug, and verify approved Python modeling code against its code plan, data contract, method decision, risk conditions, and experiment outputs, saving one compact JSON review.
---

# Preconditions

- Python code and `code/Qx/qx_code_plan.md` exist.
- Approved method decision, method card, data profile, and relevant run summary are available.
- Required inputs are accessible.

# Workflow

1. Resolve the approved main and usable baseline. Flag scripts for unapproved candidates unless a fallback activation exists.
2. Inspect and run the code in the intended order.
3. Evaluate required checks:
   - `syntax`: imports, execution, exceptions, obvious runtime faults, and variable naming compliance (flags standard variable naming conventions; enforces chemical formulas for elements/substances like `Pb`, CET-4 English for common terms, and Pinyin for domain/out-of-scope terms; exempts library kwargs and standard math abbreviations like `opt`, `loss`, `res`, `grad`, `iter`).
   - `input_contract`: paths, fields, units, shapes, missing-data handling, and raw-data protection.
   - `method_alignment`: formulas, objectives, constraints, assumptions, main/baseline roles, and fallback scope match the approved plan.
   - `reproducibility`: seed, deterministic setup, dependency/runtime record, and rerun consistency.
   - `output_contract`: saved tables/metrics/figures, valid run summary, comparable main/baseline metrics, degeneracy evidence, and fallback-trigger state.
4. Add risk-specific checks only when relevant, such as leakage, constraint feasibility, numerical stability, or scale.
5. If asked to fix findings, make minimal changes, rerun affected checks, and record the repair. Otherwise report findings without changing code.
6. Save `code/Qx/reviews/qx_python_review.json`.

# Review Schema

```json
{
  "schema_version": 1,
  "question_id": "Q1",
  "language": "python",
  "reviewed_files": [],
  "decision_id": "q1_method_choice",
  "checks": {
    "syntax": {"status": "PASS", "evidence": []},
    "input_contract": {"status": "PASS", "evidence": []},
    "method_alignment": {"status": "PASS", "evidence": []},
    "reproducibility": {"status": "PASS", "evidence": []},
    "output_contract": {"status": "PASS", "evidence": []}
  },
  "findings": [],
  "verdict": "PASSED",
  "reviewed_at": "ISO-8601"
}
```

Statuses are `PASS`, `FAIL`, or `NOT_APPLICABLE` with a reason. Any required `FAIL` blocks G3.

# Rules

- Do not pad evidence to reach a count.
- Do not fabricate execution or outputs.
- Do not approve a toy diagnostic reference as the official baseline.
- Do not silently change mathematical meaning.
- Do not create success logs beyond the review JSON.
- Treat code newer than its review as requiring the affected checks to rerun, not necessarily the entire pipeline.
- Flag variables violating the chemical-formula + CET-4 English + Pinyin convention as review findings.

# Verification

- Every required named check has concrete evidence.
- Variable naming compliance against non-standard rules is verified.
- Main and baseline are approved and comparable.
- Run summary and on-disk outputs agree.
- Review verdict follows check statuses.
