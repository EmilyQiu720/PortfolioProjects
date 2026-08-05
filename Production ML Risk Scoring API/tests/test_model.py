from pathlib import Path

from app.features import build_feature_vector
from app.model import ModelArtifact, predict_probability
from app.scoring import score_record


ROOT = Path(__file__).resolve().parents[1]


def low_risk_record():
    return {
        "request_id": "REQ-LOW-0001",
        "customer_id": "CUST-LOW",
        "customer_segment": "enterprise",
        "channel": "partner_api",
        "account_age_days": 1200,
        "prior_transactions_30d": 4,
        "prior_chargebacks_180d": 0,
        "failed_payment_attempts_24h": 0,
        "order_amount": 120.0,
        "shipping_distance_km": 12.0,
        "device_age_days": 300,
        "email_domain_age_days": 1200,
        "ip_risk_score": 0.05,
        "billing_shipping_match": True,
        "velocity_score": 0.05,
    }


def high_risk_record():
    record = low_risk_record()
    record.update(
        {
            "request_id": "REQ-HIGH-0001",
            "account_age_days": 3,
            "prior_transactions_30d": 44,
            "prior_chargebacks_180d": 4,
            "failed_payment_attempts_24h": 7,
            "order_amount": 7200.0,
            "shipping_distance_km": 3500.0,
            "device_age_days": 1,
            "email_domain_age_days": 2,
            "ip_risk_score": 0.96,
            "billing_shipping_match": False,
            "velocity_score": 0.95,
        }
    )
    return record


def test_high_risk_scores_above_low_risk():
    model = ModelArtifact.from_path(ROOT / "artifacts" / "model_registry.json")
    low = predict_probability(model, build_feature_vector(low_risk_record()))
    high = predict_probability(model, build_feature_vector(high_risk_record()))
    assert high > low
    assert high > model.thresholds["manual_review"]


def test_scoring_returns_decision_and_explanations():
    model = ModelArtifact.from_path(ROOT / "artifacts" / "model_registry.json")
    prediction = score_record(high_risk_record(), model)
    assert prediction["risk_decision"] in {"manual_review", "decline"}
    assert prediction["top_factors"]

