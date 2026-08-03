SET search_path = fraud;

-- Chargeback loss analysis by merchant and reason code.
SELECT
    m.merchant_id,
    m.merchant_name,
    cb.reason_code,
    count(cb.chargeback_id) AS chargeback_count,
    sum(cb.dispute_amount) AS disputed_amount,
    sum(cb.dispute_amount) FILTER (WHERE cb.chargeback_status = 'lost') AS lost_amount,
    count(*) FILTER (WHERE cb.won_by_platform = true) AS won_count,
    count(*) FILTER (WHERE cb.won_by_platform = false) AS lost_count
FROM chargebacks cb
JOIN transactions t ON t.transaction_id = cb.transaction_id
JOIN merchants m ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_name, cb.reason_code
ORDER BY lost_amount DESC NULLS LAST;

-- Time from transaction to chargeback.
SELECT
    cb.chargeback_id,
    cb.transaction_id,
    t.initiated_at,
    cb.opened_at,
    cb.opened_at - t.initiated_at AS time_to_chargeback,
    cb.dispute_amount,
    cb.chargeback_status
FROM chargebacks cb
JOIN transactions t ON t.transaction_id = cb.transaction_id
ORDER BY time_to_chargeback DESC;

-- Chargeback rate by transaction risk bucket.
WITH risk_buckets AS (
    SELECT
        t.transaction_id,
        CASE
            WHEN t.risk_score < 30 THEN 'low'
            WHEN t.risk_score < 70 THEN 'medium'
            WHEN t.risk_score < 90 THEN 'high'
            ELSE 'critical'
        END AS risk_bucket,
        cb.chargeback_id
    FROM transactions t
    LEFT JOIN chargebacks cb ON cb.transaction_id = t.transaction_id
)
SELECT
    risk_bucket,
    count(*) AS transaction_count,
    count(chargeback_id) AS chargeback_count,
    count(chargeback_id)::numeric / NULLIF(count(*), 0) AS chargeback_rate
FROM risk_buckets
GROUP BY risk_bucket
ORDER BY chargeback_rate DESC;
