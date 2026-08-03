SET search_path = fraud;

-- Slow pattern 1:
-- This query scans raw transaction history repeatedly for a dashboard metric.
-- It is intentionally written as a before-optimization example.
SELECT
    m.merchant_id,
    m.merchant_name,
    date_trunc('day', t.initiated_at)::date AS transaction_date,
    count(*) AS transaction_count,
    sum(t.amount) AS gross_payment_volume,
    avg(t.risk_score) AS avg_risk_score,
    (
        SELECT count(*)
        FROM chargebacks cb
        JOIN transactions t2 ON t2.transaction_id = cb.transaction_id
        WHERE t2.merchant_id = m.merchant_id
          AND date_trunc('day', t2.initiated_at)::date = date_trunc('day', t.initiated_at)::date
    ) AS chargeback_count
FROM merchants m
JOIN transactions t ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_id, m.merchant_name, date_trunc('day', t.initiated_at)::date
ORDER BY transaction_date DESC, avg_risk_score DESC;

-- Slow pattern 2:
-- Applying functions to filtered columns can prevent efficient index usage.
SELECT
    transaction_id,
    payment_method_id,
    amount,
    risk_score,
    initiated_at
FROM transactions
WHERE date_trunc('day', initiated_at)::date = DATE '2026-05-03'
  AND risk_score >= 75
ORDER BY initiated_at DESC;
