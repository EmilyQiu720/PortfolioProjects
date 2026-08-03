SET search_path = fraud;

CREATE INDEX idx_transactions_initiated_at
    ON transactions (initiated_at DESC);

CREATE INDEX idx_transactions_customer_time
    ON transactions (customer_id, initiated_at DESC);

CREATE INDEX idx_transactions_merchant_time
    ON transactions (merchant_id, initiated_at DESC);

CREATE INDEX idx_transactions_payment_method_time
    ON transactions (payment_method_id, initiated_at DESC);

CREATE INDEX idx_transactions_device_time
    ON transactions (device_id, initiated_at DESC);

CREATE INDEX idx_transactions_high_risk_open
    ON transactions (risk_score DESC, initiated_at DESC)
    WHERE risk_score >= 75 AND transaction_status IN ('authorized', 'captured');

CREATE INDEX idx_alerts_open_priority
    ON fraud_alerts (priority, created_at)
    WHERE alert_status IN ('open', 'in_review');

CREATE INDEX idx_chargebacks_transaction
    ON chargebacks (transaction_id);

CREATE INDEX idx_chargebacks_opened_at
    ON chargebacks (opened_at DESC);

CREATE INDEX idx_events_transaction_time
    ON transaction_events (transaction_id, event_at);

CREATE INDEX idx_devices_hash
    ON device_fingerprints (device_hash);
