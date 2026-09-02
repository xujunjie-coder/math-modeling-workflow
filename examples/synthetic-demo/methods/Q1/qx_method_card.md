# Q1 Method Card

## Goal
Predict/explain per-period demand from `temperature` and `promotion`, compare one main method against one usable baseline under the same error definition, and test stability.

## main candidate — M1: OLS multiple linear regression
- Form: `demand = b0 + b1*temperature + b2*promotion`, solved from the normal equations (standard library Gaussian elimination).
- Why it fits: continuous target, two exogenous features, interpretable coefficient signs match the proposed mechanism.
- Risks to probe: small n=24; promotion support only 6 periods; residual structure; sign stability.
- Validation: leave-one-out RMSE/MAE; 200-trial fixed-seed demand perturbation.

## usable baseline — M0: global-mean predictor
- Predict every period with the training-sample mean.
- Why it is a usable baseline (not merely diagnostic): yields a point forecast for every period under the identical split and identical RMSE/MAE definitions, so the comparison is direct.

## Decision history
- Probe summary written to `methods/Q1/probes/risk_probe_summary.json`.
- Human method choice recorded in `methods/Q1/qx_decisions.jsonl` (`q1_method_choice`, G2.5).

## Notes
- No fallback was activated: the probe and first run showed no degeneracy or failed feasibility.
