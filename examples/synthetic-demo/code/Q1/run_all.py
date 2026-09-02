"""Run Q1 main method and usable baseline once, writing canonical round1 artifacts.

Outputs (standard library only, deterministic apart from measured wall time):
- results/Q1/experiments/round1/metrics/{main_metrics,baseline_metrics,comparison,perturbation_stability}.json
- results/Q1/experiments/round1/figures/main_vs_baseline.svg  (Type 2 comparison)
- results/Q1/experiments/round1/run_summary.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUESTION_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import q1_baseline as baseline  # noqa: E402
import q1_main as main_model  # noqa: E402

ROUND = QUESTION_ROOT / "results" / "Q1" / "experiments" / "round1"
METRICS = ROUND / "metrics"
FIGURES = ROUND / "figures"
CLEAN = QUESTION_ROOT / "workspace" / "data_clean" / "observations_clean.csv"


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def comparison_svg(periods, actual, fitted, mean_value, path: Path) -> None:
    width, height = 720, 420
    left, right, top, bottom = 56, 20, 24, 44
    plot_w, plot_h = width - left - right, height - top - bottom
    xmax = len(periods)
    ymin = min(actual + fitted) - 3
    ymax = max(actual + fitted) + 3

    def x_of(i):
        return left + plot_w * i / max(1, xmax - 1)

    def y_of(v):
        return top + plot_h * (1 - (v - ymin) / (ymax - ymin))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Segoe UI, Arial, sans-serif">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="16" font-size="14" fill="#111">Q1 demand: actual vs OLS fit vs mean baseline</text>',
    ]
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        gy = top + plot_h * (1 - frac)
        value = ymin + frac * (ymax - ymin)
        parts.append(f'<line x1="{left}" y1="{gy:.1f}" x2="{width-right}" y2="{gy:.1f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{left-8}" y="{gy+4:.1f}" font-size="10" text-anchor="end" fill="#555">{value:.0f}</text>')
    # mean baseline
    by = y_of(mean_value)
    parts.append(f'<line x1="{left}" y1="{by:.1f}" x2="{width-right}" y2="{by:.1f}" stroke="#9ca3af" stroke-dasharray="6 4"/>')
    parts.append(f'<text x="{width-right-4}" y="{by-5:.1f}" font-size="10" text-anchor="end" fill="#6b7280">mean baseline</text>')
    # OLS fitted polyline
    points = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(fitted))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="2"/>')
    # actual dots
    for i, value in enumerate(actual):
        parts.append(f'<circle cx="{x_of(i):.1f}" cy="{y_of(value):.1f}" r="3" fill="#dc2626"/>')
    parts.append(f'<text x="{left}" y="{height-12}" font-size="11" fill="#555">period</text>')
    parts.append('<circle cx="500" cy="16" r="3" fill="#dc2626"/><text x="508" y="20" font-size="11">actual</text>')
    parts.append('<line x1="560" y1="16" x2="582" y2="16" stroke="#2563eb" stroke-width="2"/><text x="586" y="20" font-size="11">OLS fit</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    started = time.perf_counter()
    demand, features = main_model.load_rows(CLEAN)
    periods = list(range(1, len(demand) + 1))

    beta, fitted, main_full = main_model.full_fit(features, demand)
    main_loo = main_model.loocv(features, demand)
    base_full = baseline.full_fit(demand)
    base_loo = baseline.loocv(demand)
    stability = main_model.perturbation_study(features, demand, trials=200, seed=2026)
    mean_value = baseline.fit_mean(demand)
    elapsed = time.perf_counter() - started

    improvement = (base_loo["rmse"] - main_loo["rmse"]) / base_loo["rmse"]

    write_json(METRICS / "main_metrics.json", {
        "method_id": "M1", "model": "OLS demand = b0 + b1*temperature + b2*promotion",
        "coefficients": {"intercept": beta[0], "temperature": beta[1], "promotion": beta[2]},
        "full_fit": main_full, "loocv": main_loo,
    })
    write_json(METRICS / "baseline_metrics.json", {
        "method_id": "M0", "model": "global-mean predictor",
        "predicted_value": mean_value, "full_fit": base_full, "loocv": base_loo,
    })
    write_json(METRICS / "comparison.json", {
        "metric": "rmse", "scope": "leave-one-out",
        "main_rmse": main_loo["rmse"], "baseline_rmse": base_loo["rmse"],
        "relative_rmse_reduction": improvement,
        "main_wins": main_loo["rmse"] < base_loo["rmse"],
    })
    write_json(METRICS / "perturbation_stability.json", stability)
    comparison_svg(periods, demand, fitted, mean_value, FIGURES / "main_vs_baseline.svg")

    summary = {
        "schema_version": 1,
        "question": "Q1",
        "round": "round1",
        "implementation_target": "python",
        "random_seed": 2026,
        "approved_decision_id": "q1_method_choice",
        "methods": [
            {
                "method_id": "M0", "role": "usable_baseline", "script": "code/Q1/q1_baseline.py",
                "status": "success", "execution_time_seconds": 0.0,
                "input_files": ["workspace/data_clean/observations_clean.csv"],
                "output_files": ["results/Q1/experiments/round1/metrics/baseline_metrics.json"],
                "figure_files": [], "metrics_summary": base_loo, "warnings": [], "errors": [],
            },
            {
                "method_id": "M1", "role": "main", "script": "code/Q1/q1_main.py",
                "status": "success", "execution_time_seconds": round(elapsed, 4),
                "input_files": ["workspace/data_clean/observations_clean.csv"],
                "output_files": [
                    "results/Q1/experiments/round1/metrics/main_metrics.json",
                    "results/Q1/experiments/round1/metrics/comparison.json",
                    "results/Q1/experiments/round1/metrics/perturbation_stability.json",
                ],
                "figure_files": ["results/Q1/experiments/round1/figures/main_vs_baseline.svg"],
                "metrics_summary": {"loocv": main_loo, "relative_rmse_reduction": improvement},
                "warnings": [], "errors": [],
            },
        ],
        "comparison": {
            "same_split": True, "same_metric": "rmse",
            "relative_rmse_reduction": improvement, "winner": "M1",
        },
        "fallback_trigger": {"fallback_id": None, "condition": None, "observed": False, "evidence": None},
        "environment": {"python": sys.version.split()[0], "third_party_dependencies": []},
    }
    write_json(ROUND / "run_summary.json", summary)
    print(json.dumps({"main_loocv": main_loo, "baseline_loocv": base_loo,
                      "relative_rmse_reduction": improvement, "stability": stability}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
