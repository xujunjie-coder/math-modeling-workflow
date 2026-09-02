# Q1 Code Plan (round1)

- Target language: Python (standard library only).
- Approved decision: `q1_method_choice` (main M1 = OLS; usable baseline M0 = global mean).
- Inputs: `workspace/data_clean/observations_clean.csv` (24 rows; columns period, demand, temperature, promotion).
- Fixed seed: 2026 (only the perturbation study is stochastic; OLS fitting is deterministic).

## Scope (exactly main + usable baseline)
- `q1_baseline.py` — M0 global-mean predictor, full-fit and leave-one-out RMSE/MAE.
- `q1_main.py` — M1 OLS via normal equations + Gaussian elimination; full-fit, LOOCV, and fixed-seed perturbation stability.
- `run_all.py` — runs both under the identical split and writes metrics, the Type 2 comparison SVG, and `run_summary.json`.

## Comparable output contract
- Both methods report `{mae, rmse}` on full fit and leave-one-out, on the same 24 points.
- `comparison.json` reports leave-one-out RMSE for both and the relative reduction.

## Monitored probe risks
- small n=24 → use LOOCV (no single random split);
- promotion support=6 → record coefficient and its sign-stability rate;
- fallback trigger → activate only if the design matrix is singular or M1 fails to beat M0.

## Expected outputs
```text
results/Q1/experiments/round1/
├── metrics/{main_metrics,baseline_metrics,comparison,perturbation_stability}.json
├── figures/main_vs_baseline.svg
└── run_summary.json
```

## Named review checks expected downstream
syntax, input_contract, method_alignment, reproducibility, output_contract.
