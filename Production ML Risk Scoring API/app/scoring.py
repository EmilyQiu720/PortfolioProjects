"""Scoring service that combines feature engineering, model inference, and policy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .features import build_feature_vector
from .model import ModelArtifact, explain_top_factors, predict_probability


def score_record(record: dict[str, Any], model: ModelArtifact) -> dict[str, Any]:
    features = build_feature_vector(record)
    risk_score = predict_probability(model, features)
    thresholds = model.thresholds
    if risk_score >= thresholds["decline"]:
        decision = "decline"
    elif risk_score >= thresholds["manual_review"]:
        decision = "manual_review"
    else:
        decision = "approve"
    return {
        "request_id": str(record["request_id"]),
        "model_name": model.model_name,
        "model_version": model.model_version,
        "risk_score": risk_score,
        "risk_decision": decision,
        "decision_thresholds": thresholds,
        "top_factors": explain_top_factors(model, features),
        "scored_at": datetime.now(timezone.utc),
    }

