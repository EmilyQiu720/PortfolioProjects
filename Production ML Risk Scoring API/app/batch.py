"""Batch scoring utilities shared by API endpoint and CLI script."""

from __future__ import annotations

import csv
from pathlib import Path

from .model import ModelArtifact
from .scoring import score_record


def score_csv(input_path: Path, output_path: Path, model: ModelArtifact) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open(newline="", encoding="utf-8") as source, output_path.open("w", newline="", encoding="utf-8") as target:
        reader = csv.DictReader(source)
        fieldnames = list(reader.fieldnames or []) + ["risk_score", "risk_decision", "top_factors", "model_version"]
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        count = 0
        for row in reader:
            row["billing_shipping_match"] = str(row["billing_shipping_match"]).lower() in {"true", "1", "yes"}
            prediction = score_record(row, model)
            row.update(
                {
                    "risk_score": prediction["risk_score"],
                    "risk_decision": prediction["risk_decision"],
                    "top_factors": "|".join(prediction["top_factors"]),
                    "model_version": prediction["model_version"],
                }
            )
            writer.writerow(row)
            count += 1
    return count

