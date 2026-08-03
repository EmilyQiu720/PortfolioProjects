SET search_path = fraud;

CREATE MATERIALIZED VIEW mv_merchant_risk_daily AS
SELECT
    merchant_id,
    merchant_name,
    transaction_date,
    transaction_count,
    approved_count,
    declined_count,
    chargeback_count,
    gross_payment_volume,
    avg_risk_score,
    chargeback_count::numeric / NULLIF(transaction_count, 0) AS chargeback_rate,
    declined_count::numeric / NULLIF(transaction_count, 0) AS decline_rate
FROM v_merchant_daily_summary
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_merchant_risk_daily
    ON mv_merchant_risk_daily (merchant_id, transaction_date);

CREATE MATERIALIZED VIEW mv_payment_method_velocity_hourly AS
SELECT
    payment_method_id,
    date_trunc('hour', initiated_at) AS transaction_hour,
    count(*) AS transaction_count,
    sum(amount) AS total_amount,
    avg(risk_score) AS avg_risk_score,
    count(*) FILTER (WHERE authorization_status = 'declined') AS declined_count
FROM transactions
GROUP BY payment_method_id, date_trunc('hour', initiated_at)
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_payment_method_velocity_hourly
    ON mv_payment_method_velocity_hourly (payment_method_id, transaction_hour);
