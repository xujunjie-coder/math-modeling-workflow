"""Usable baseline for Q1: global-mean demand predictor.

Deliberately simple and reproducible. It serves as the comparison point for the
OLS main method; a diagnostic mean is a legitimate usable baseline here because
it produces a point forecast for every period under the exact same error
definitions (RMSE/MAE, leave-one-out) as the main method.

Standard library only.
"""

from __future__ import annotations

import csv
from pathlib import Path


def load_demand(csv_path: Path) -> list[float]:
    with csv_path.open(encoding="utf-8") as handle:
        return [float(row["demand"]) for row in csv.DictReader(handle)]


def fit_mean(values: list[float]) -> float:
    return sum(values) / len(values)


def errors(actual: list[float], predicted: list[float]) -> dict[str, float]:
    n = len(actual)
    mae = sum(abs(a - p) for a, p in zip(actual, predicted)) / n
    rmse = (sum((a - p) ** 2 for a, p in zip(actual, predicted)) / n) ** 0.5
    return {"mae": mae, "rmse": rmse}


def full_fit(demand: list[float]) -> dict[str, float]:
    mean = fit_mean(demand)
    return errors(demand, [mean] * len(demand))


def loocv(demand: list[float]) -> dict[str, float]:
    predicted: list[float] = []
    for index in range(len(demand)):
        rest = demand[:index] + demand[index + 1 :]
        predicted.append(fit_mean(rest))
    return errors(demand, predicted)


if __name__ == "__main__":
    data = Path(__file__).resolve().parents[2] / "workspace" / "data_clean" / "observations_clean.csv"
    demand = load_demand(data)
    print({"full_fit": full_fit(demand), "loocv": loocv(demand)})
