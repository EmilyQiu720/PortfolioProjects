SET search_path = fraud;

CREATE OR REPLACE VIEW v_masked_customers AS
SELECT
    customer_id,
    concat(left(email, 2), '***@', split_part(email, '@', 2)) AS masked_email,
    concat(left(full_name, 1), '***') AS masked_name,
    kyc_status,
    risk_tier,
    country_code,
    created_at
FROM customers;

CREATE OR REPLACE VIEW v_transaction_enriched AS
SELECT
    t.transaction_id,
    t.initiated_at,
    t.amount,
    t.currency,
    t.transaction_status,
    t.authorization_status,
    t.risk_score,
    c.customer_id,
    c.risk_tier AS customer_risk_tier,
    c.country_code AS customer_country,
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.country_code AS merchant_country,
    pm.payment_method_id,
    pm.method_type,
    pm.billing_country,
    df.device_id,
    df.device_hash,
    df.ip_country,
    (c.country_code <> pm.billing_country) AS billing_country_mismatch,
    (c.country_code <> df.ip_country) AS ip_country_mismatch
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
JOIN merchants m ON m.merchant_id = t.merchant_id
JOIN payment_methods pm ON pm.payment_method_id = t.payment_method_id
JOIN device_fingerprints df ON df.device_id = t.device_id;

CREATE OR REPLACE VIEW v_alert_review_queue AS
SELECT
    fa.alert_id,
    fa.created_at,
    fa.priority,
    fa.alert_score,
    fa.alert_status,
    rr.rule_code,
    rr.rule_name,
    rr.severity,
    te.transaction_id,
    te.amount,
    te.currency,
    te.merchant_name,
    te.customer_risk_tier,
    te.billing_country_mismatch,
    te.ip_country_mismatch,
    EXTRACT(EPOCH FROM (now() - fa.created_at)) / 3600.0 AS alert_age_hours
FROM fraud_alerts fa
JOIN risk_rules rr ON rr.rule_id = fa.rule_id
JOIN v_transaction_enriched te ON te.transaction_id = fa.transaction_id
WHERE fa.alert_status IN ('open', 'in_review');

CREATE OR REPLACE VIEW v_customer_payment_profile AS
SELECT
    c.customer_id,
    c.risk_tier,
    c.country_code,
    count(t.transaction_id) AS transaction_count,
    count(*) FILTER (WHERE t.authorization_status = 'approved') AS approved_count,
    count(*) FILTER (WHERE t.authorization_status = 'declined') AS declined_count,
    count(*) FILTER (WHERE t.transaction_status = 'chargeback') AS chargeback_count,
    coalesce(sum(t.amount), 0) AS gross_payment_volume,
    max(t.initiated_at) AS last_transaction_at
FROM customers c
LEFT JOIN transactions t ON t.customer_id = c.customer_id
GROUP BY c.customer_id, c.risk_tier, c.country_code;

CREATE OR REPLACE VIEW v_merchant_daily_summary AS
SELECT
    m.merchant_id,
    m.merchant_name,
    date_trunc('day', t.initiated_at)::date AS transaction_date,
    count(t.transaction_id) AS transaction_count,
    count(*) FILTER (WHERE t.authorization_status = 'approved') AS approved_count,
    count(*) FILTER (WHERE t.authorization_status = 'declined') AS declined_count,
    count(*) FILTER (WHERE t.transaction_status = 'chargeback') AS chargeback_count,
    sum(t.amount) AS gross_payment_volume,
    avg(t.risk_score) AS avg_risk_score
FROM merchants m
JOIN transactions t ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_id, m.merchant_name, date_trunc('day', t.initiated_at)::date;
