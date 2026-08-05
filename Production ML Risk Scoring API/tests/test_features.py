from app.features import FeatureValidationError, build_feature_vector, stable_hash


def valid_record():
    return {
        "request_id": "REQ-TEST-0001",
        "customer_id": "CUST-123",
        "customer_segment": "consumer",
        "channel": "web",
        "account_age_days": 12,
        "prior_transactions_30d": 24,
        "prior_chargebacks_180d": 2,
        "failed_payment_attempts_24h": 4,
        "order_amount": 2500.0,
        "shipping_distance_km": 900.0,
        "device_age_days": 3,
        "email_domain_age_days": 20,
        "ip_risk_score": 0.8,
        "billing_shipping_match": False,
        "velocity_score": 0.9,
    }


def test_feature_vector_contains_expected_flags():
    vector = build_feature_vector(valid_record())
    assert vector.values["new_account"] == 1.0
    assert vector.values["billing_shipping_mismatch"] == 1.0
    assert vector.values["high_transaction_velocity"] == 1.0


def test_rejects_unknown_category():
    record = valid_record()
    record["channel"] = "unknown"
    try:
        build_feature_vector(record)
    except FeatureValidationError as exc:
        assert "Unsupported channel" in str(exc)
    else:
        raise AssertionError("expected FeatureValidationError")


def test_stable_hash_is_deterministic_and_masked():
    assert stable_hash("CUST-123") == stable_hash("CUST-123")
    assert stable_hash("CUST-123") != "CUST-123"

