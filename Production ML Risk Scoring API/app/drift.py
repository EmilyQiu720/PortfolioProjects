"""Data drift metrics used by monitoring jobs and API diagnostics."""

from __future__ import annotations

import csv
import math
from pathlib import Path


def bucket_counts(values: list[float], lower: float, upper: float, buckets: int = 10) -> list[float]:
    if not values:
        return [0.0] * buckets
    if math.isclose(lower, upper):
        counts = [0.0] * buckets
        counts[0] = float(len(values))
        return counts
    width = (upper - lower) / buckets
    counts = [0.0] * buckets
    for value in values:
        index = min(int((value - lower) / width), buckets - 1)
        counts[index] += 1
    return counts


def population_stability_index(reference: list[float], current: list[float], buckets: int = 10) -> float:
    values = reference + current
    if not values:
        return 0.0
    lower, upper = min(values), max(values)
    ref_counts = bucket_counts(reference, lower, upper, buckets)
    cur_counts = bucket_counts(current, lower, upper, buckets)
    ref_total = sum(ref_counts) or 1.0
    cur_total = sum(cur_counts) or 1.0
    psi = 0.0
    for ref_count, cur_count in zip(ref_counts, cur_counts):
        ref_pct = max(ref_count / ref_total, 0.0001)
        cur_pct = max(cur_count / cur_total, 0.0001)
        psi += (cur_pct - ref_pct) * math.log(cur_pct / ref_pct)
    return round(psi, 6)


def load_numeric_column(path: Path, column: str) -> list[float]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [float(row[column]) for row in csv.DictReader(handle) if row.get(column) not in {None, ""}]


def drift_report(reference_path: Path, current_path: Path, columns: list[str]) -> dict[str, float]:
    report = {}
    for column in columns:
        reference = load_numeric_column(reference_path, column)
        current = load_numeric_column(current_path, column)
        report[column] = population_stability_index(reference, current)
    return report
