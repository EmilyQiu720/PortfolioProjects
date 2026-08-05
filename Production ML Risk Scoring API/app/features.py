"""Feature transformation and validation logic for risk scoring."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any


NUMERIC_FEATURES = [
    "account_age_days",
    "prior_transactions_30d",
    "prior_chargebacks_180d",
    "failed_payment_attempts_24h",
    "order_amount",
    "shipping_distance_km",
    "device_age_days",
    "email_domain_age_days",
    "ip_risk_score",
    "velocity_score",
]

CATEGORICAL_FEATURES = {
    "customer_segment": ["consumer", "small_business", "enterprise"],
    "channel": ["web", "mobile", "partner_api", "call_center"],
}


@dataclass(frozen=True)
class FeatureVector:
    values: dict[str, float]
    top_factor_candidates: dict[str, float]


class FeatureValidationError(ValueError):
    """Raised when a scoring record violates the model feature contract."""


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _as_float(record: dict[str, Any], field: str) -> float:
    if field not in record:
        raise FeatureValidationError(f"Missing required feature: {field}")
    try:
        value = float(record[field])
    except (TypeError, ValueError) as exc:
        raise FeatureValidationError(f"Feature {field} must be numeric") from exc
    if not math.isfinite(value):
        raise FeatureValidationError(f"Feature {field} must be finite")
    return value


def build_feature_vector(record: dict[str, Any]) -> FeatureVector:
    """Convert a request dictionary into model-ready numeric features.

    This logic is deliberately centralized so API scoring, batch scoring, tests,
    and future retraining pipelines use the same feature contract.
    """

    numeric = {name: _as_float(record, name) for name in NUMERIC_FEATURES}
    segment = str(record.get("customer_segment", "")).strip()
    channel = str(record.get("channel", "")).strip()
    if segment not in CATEGORICAL_FEATURES["customer_segment"]:
        raise FeatureValidationError(f"Unsupported customer_segment: {segment}")
    if channel not in CATEGORICAL_FEATURES["channel"]:
        raise FeatureValidationError(f"Unsupported channel: {channel}")

    billing_shipping_match = record.get("billing_shipping_match")
    if isinstance(billing_shipping_match, str):
        billing_shipping_match = billing_shipping_match.lower() in {"true", "1", "yes"}
    if not isinstance(billing_shipping_match, bool):
        raise FeatureValidationError("billing_shipping_match must be boolean")

    values = {
        "bias": 1.0,
        "log_order_amount": math.log1p(numeric["order_amount"]),
        "log_shipping_distance": math.log1p(numeric["shipping_distance_km"]),
        "new_account": 1.0 if numeric["account_age_days"] < 30 else 0.0,
        "mature_account": 1.0 if numeric["account_age_days"] >= 365 else 0.0,
        "chargeback_count": numeric["prior_chargebacks_180d"],
        "failed_payment_attempts": numeric["failed_payment_attempts_24h"],
        "low_device_age": 1.0 if numeric["device_age_days"] < 7 else 0.0,
        "low_email_domain_age": 1.0 if numeric["email_domain_age_days"] < 30 else 0.0,
        "ip_risk_score": numeric["ip_risk_score"],
        "velocity_score": numeric["velocity_score"],
        "billing_shipping_mismatch": 0.0 if billing_shipping_match else 1.0,
        "high_transaction_velocity": 1.0 if numeric["prior_transactions_30d"] >= 20 else 0.0,
        "segment_small_business": 1.0 if segment == "small_business" else 0.0,
        "segment_enterprise": 1.0 if segment == "enterprise" else 0.0,
        "channel_mobile": 1.0 if channel == "mobile" else 0.0,
        "channel_partner_api": 1.0 if channel == "partner_api" else 0.0,
        "channel_call_center": 1.0 if channel == "call_center" else 0.0,
    }
    top_factor_candidates = {
        "high order amount": values["log_order_amount"],
        "long shipping distance": values["log_shipping_distance"],
        "new account": values["new_account"],
        "prior chargebacks": values["chargeback_count"],
        "failed payment attempts": values["failed_payment_attempts"],
        "new device": values["low_device_age"],
        "new email domain": values["low_email_domain_age"],
        "risky IP": values["ip_risk_score"],
        "transaction velocity": values["velocity_score"],
        "billing/shipping mismatch": values["billing_shipping_mismatch"],
    }
    return FeatureVector(values=values, top_factor_candidates=top_factor_candidates)

