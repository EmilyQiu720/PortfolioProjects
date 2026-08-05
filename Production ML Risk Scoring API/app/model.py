"""Lightweight model runtime for deterministic risk scoring."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from .features import FeatureVector


@dataclass(frozen=True)
class ModelArtifact:
    model_name: str
    model_version: str
    coefficients: dict[str, float]
    thresholds: dict[str, float]
    training_metrics: dict[str, float]

    @classmethod
    def from_path(cls, path: Path) -> "ModelArtifact":
        payload = json.loads(path.read_text(encoding="utf-8"))
        active_version = payload["active_version"]
        model_payload = payload["models"][active_version]
        return cls(
            model_name=model_payload["model_name"],
            model_version=active_version,
            coefficients={key: float(value) for key, value in model_payload["coefficients"].items()},
            thresholds={key: float(value) for key, value in model_payload["thresholds"].items()},
            training_metrics={key: float(value) for key, value in model_payload["training_metrics"].items()},
        )


def sigmoid(value: float) -> float:
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1 + exp_value)


def predict_probability(model: ModelArtifact, features: FeatureVector) -> float:
    raw_score = 0.0
    for name, coefficient in model.coefficients.items():
        raw_score += coefficient * features.values.get(name, 0.0)
    return round(sigmoid(raw_score), 6)


def explain_top_factors(model: ModelArtifact, features: FeatureVector, limit: int = 4) -> list[str]:
    impacts = []
    for label, candidate_value in features.top_factor_candidates.items():
        feature_name = {
            "high order amount": "log_order_amount",
            "long shipping distance": "log_shipping_distance",
            "new account": "new_account",
            "prior chargebacks": "chargeback_count",
            "failed payment attempts": "failed_payment_attempts",
            "new device": "low_device_age",
            "new email domain": "low_email_domain_age",
            "risky IP": "ip_risk_score",
            "transaction velocity": "velocity_score",
            "billing/shipping mismatch": "billing_shipping_mismatch",
        }[label]
        impact = abs(model.coefficients.get(feature_name, 0.0) * candidate_value)
        if impact > 0:
            impacts.append((impact, label))
    return [label for _, label in sorted(impacts, reverse=True)[:limit]]

