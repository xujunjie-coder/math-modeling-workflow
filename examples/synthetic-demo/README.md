# Synthetic Demo — end-to-end lean golden example

This example is intentionally small and **fully synthetic** (no real contest statement or data). It walks one question `Q1` through the complete **lean** trail **G0 → G4** with a canonical artifact at every gate, so you can see what "evidence on disk" looks like and verify the deterministic enforcers against a known-good workspace.

## The task

Using 24 synthetic periods (`data_raw/observations.csv`: period, demand, temperature, promotion), model demand and compare:

- **main M1** — OLS multiple regression `demand = b0 + b1·temperature + b2·promotion` (`code/Q1/q1_main.py`, standard-library Gaussian elimination);
- **usable baseline M0** — global-mean predictor (`code/Q1/q1_baseline.py`).

Validation uses leave-one-out RMSE/MAE and a 200-trial, seed-2026 perturbation study. **Every reported number is produced by code**; the JSON/Markdown artifacts only transcribe those outputs.

## Reproduce

```powershell
# 1) rerun the experiment (writes metrics, comparison SVG, and run_summary.json)
python code/Q1/run_all.py
# 2) inspect the gate state that the on-disk evidence actually supports
python ../../plugins/math-modeling-workflow/scripts/gate_check.py . status
# 3) action guards
python ../../plugins/math-modeling-workflow/scripts/gate_check.py . guard --action code_generation --question Q1
```

Expected: highest gate **G4**, no integrity violation, guard PASS.

## Artifact trail by gate

| Gate | Artifact(s) |
|---|---|
| G0 | `planning/session_config.json`, `planning/manifests/Q1.json` |
| G1 | `planning/parse/problem_parse.json`, `planning/classification/problem_classification.json`, `workspace/data/data_profile.json`, `workspace/data_clean/observations_clean.csv` |
| G2 | `methods/Q1/qx_method_card.md`, `methods/Q1/probes/risk_probe_summary.json` |
| G2.5 | `methods/Q1/qx_decisions.jsonl` — human `method_choice` |
| G3 | `code/Q1/qx_code_plan.md`, `code/Q1/{q1_main,q1_baseline,run_all}.py`, `results/Q1/experiments/round1/run_summary.json` + `metrics/` + `figures/`, `code/Q1/reviews/qx_python_review.json` |
| G4 | `robustness/Q1/qx_robustness_summary.json`, human `result_verdict` in the decision ledger |

Lean ends at G4: there is deliberately **no** freeze, paper section, or G5/G6 artifact. To continue toward a submission, switch `rigor_profile` to `submission` and follow `docs/lean-to-submission-checklist.zh-CN.md`.

## Result snapshot (deterministic)

- Estimated coefficients ≈ intercept 29.93, temperature 1.78, promotion 12.56 (data was generated from 30 / 1.8 / 12).
- Leave-one-out RMSE: M1 2.92 vs M0 9.71 → 69.9% reduction.
- 200 perturbations: both coefficient signs positive in 100% of trials, M1 beats M0 in 100% of trials → robustness `PASS`, no stability verdict required.

## Naming note

Directories substitute the question id (`Qx` → `Q1`), while the shared evidence-file prefix is the literal `qx_` (`methods/Q1/qx_method_card.md`). Per-question executable code uses the lowercased id (`code/Q1/q1_main.py`). See `docs/directory-mapping.zh-CN.md`.
