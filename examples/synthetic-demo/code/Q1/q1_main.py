"""Main method for Q1: ordinary least-squares demand model.

Model: demand = b0 + b1*temperature + b2*promotion. Solved from the normal
equations with a small Gaussian-elimination solver, so the example needs only
the Python standard library and stays bit-for-bit reproducible (no randomness
in fitting; the fixed-seed perturbation study lives in :func:`perturbation_study`).
"""

from __future__ import annotations

import csv
import random
from pathlib import Path


def load_rows(csv_path: Path) -> tuple[list[float], list[tuple[float, float]]]:
    demand: list[float] = []
    features: list[tuple[float, float]] = []
    with csv_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            demand.append(float(row["demand"]))
            features.append((float(row["temperature"]), float(row["promotion"])))
    return demand, features


def design_matrix(features: list[tuple[float, float]]) -> list[list[float]]:
    return [[1.0, temperature, promotion] for temperature, promotion in features]


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting for a small square system."""
    n = len(vector)
    aug = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular design matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for row in range(col + 1, n):
            factor = aug[row][col] / aug[col][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]
    solution = [0.0] * n
    for i in range(n - 1, -1, -1):
        solution[i] = (aug[i][n] - sum(aug[i][j] * solution[j] for j in range(i + 1, n))) / aug[i][i]
    return solution


def fit(features: list[tuple[float, float]], demand: list[float]) -> list[float]:
    x = design_matrix(features)
    xtx = [[sum(row[i] * row[j] for row in x) for j in range(3)] for i in range(3)]
    xty = [sum(row[i] * y for row, y in zip(x, demand)) for i in range(3)]
    return solve_linear(xtx, xty)


def predict(beta: list[float], temperature: float, promotion: float) -> float:
    return beta[0] + beta[1] * temperature + beta[2] * promotion


def error_metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    n = len(actual)
    mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / n
    rmse = (sum((a - p) ** 2 for a, p in zip(actual, predicted)) / n) ** 0.5
    return {"mae": mae, "rmse": rmse}


def full_fit(features, demand) -> tuple[list[float], list[float], dict[str, float]]:
    beta = fit(features, demand)
    fitted = [predict(beta, *feature) for feature in features]
    return beta, fitted, error_metrics(demand, fitted)


def loocv(features, demand) -> dict[str, float]:
    predicted: list[float] = []
    for index in range(len(demand)):
        train_features = features[:index] + features[index + 1 :]
        train_demand = demand[:index] + demand[index + 1 :]
        beta = fit(train_features, train_demand)
        predicted.append(predict(beta, *features[index]))
    return error_metrics(demand, predicted)


def perturbation_study(features, demand, trials: int = 200, seed: int = 2026) -> dict[str, float]:
    """Resample demand with small Gaussian noise; report sign and ranking stability."""
    rng = random.Random(seed)
    temp_positive = promo_positive = main_beats_baseline = 0
    for _ in range(trials):
        noisy = [value + rng.gauss(0.0, 1.5) for value in demand]
        beta = fit(features, noisy)
        if beta[1] > 0:
            temp_positive += 1
        if beta[2] > 0:
            promo_positive += 1
        loo_pred: list[float] = []
        for index in range(len(noisy)):
            tf = features[:index] + features[index + 1 :]
            td = noisy[:index] + noisy[index + 1 :]
            b = fit(tf, td)
            loo_pred.append(predict(b, *features[index]))
        main_rmse = error_metrics(noisy, loo_pred)["rmse"]
        base_pred = []
        for index in range(len(noisy)):
            rest = noisy[:index] + noisy[index + 1 :]
            base_pred.append(sum(rest) / len(rest))
        base_rmse = error_metrics(noisy, base_pred)["rmse"]
        if main_rmse < base_rmse:
            main_beats_baseline += 1
    return {
        "trials": trials,
        "temperature_coef_positive_rate": temp_positive / trials,
        "promotion_coef_positive_rate": promo_positive / trials,
        "main_beats_baseline_rate": main_beats_baseline / trials,
    }


if __name__ == "__main__":
    data = Path(__file__).resolve().parents[2] / "workspace" / "data_clean" / "observations_clean.csv"
    demand, features = load_rows(data)
    beta, _, metrics = full_fit(features, demand)
    print({"beta": beta, "full_fit": metrics, "loocv": loocv(features, demand)})
