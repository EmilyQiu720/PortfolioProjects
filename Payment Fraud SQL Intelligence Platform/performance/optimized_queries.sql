SET search_path = fraud;

-- Optimized pattern 1:
-- Use the pre-aggregated materialized view for dashboard reads.
SELECT
    merchant_id,
    merchant_name,
    transaction_date,
    transaction_count,
    gross_payment_volume,
    avg_risk_score,
    chargeback_count,
    chargeback_rate,
    decline_rate
FROM mv_merchant_risk_daily
ORDER BY transaction_date DESC, avg_risk_score DESC;

-- Optimized pattern 2:
-- Preserve index-friendly range predicates instead of wrapping the column.
SELECT
    transaction_id,
    payment_method_id,
    amount,
    risk_score,
    initiated_at
FROM transactions
WHERE initiated_at >= TIMESTAMPTZ '2026-05-03 00:00:00+00'
  AND initiated_at <  TIMESTAMPTZ '2026-05-04 00:00:00+00'
  AND risk_score >= 75
ORDER BY initiated_at DESC;

-- Explain helper:
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT ...
