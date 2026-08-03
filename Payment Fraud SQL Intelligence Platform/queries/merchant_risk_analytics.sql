SET search_path = fraud;

-- Merchant-level risk scorecard.
WITH merchant_base AS (
    SELECT
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        m.onboarding_risk_score,
        count(t.transaction_id) AS transaction_count,
        sum(t.amount) AS gross_payment_volume,
        avg(t.amount) AS average_order_value,
        avg(t.risk_score) AS average_transaction_risk,
        count(*) FILTER (WHERE t.authorization_status = 'declined') AS declined_count,
        count(cb.chargeback_id) AS chargeback_count
    FROM merchants m
    LEFT JOIN transactions t ON t.merchant_id = m.merchant_id
    LEFT JOIN chargebacks cb ON cb.transaction_id = t.transaction_id
    GROUP BY m.merchant_id, m.merchant_name, m.merchant_category, m.onboarding_risk_score
)
SELECT
    *,
    declined_count::numeric / NULLIF(transaction_count, 0) AS decline_rate,
    chargeback_count::numeric / NULLIF(transaction_count, 0) AS chargeback_rate,
    ntile(4) OVER (ORDER BY coalesce(average_transaction_risk, 0)) AS risk_quartile
FROM merchant_base
ORDER BY chargeback_rate DESC NULLS LAST, average_transaction_risk DESC NULLS LAST;

-- Daily merchant trend for dashboard monitoring.
SELECT
    merchant_id,
    merchant_name,
    transaction_date,
    transaction_count,
    gross_payment_volume,
    avg_risk_score,
    chargeback_rate,
    decline_rate,
    avg(avg_risk_score) OVER (
        PARTITION BY merchant_id
        ORDER BY transaction_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_day_avg_risk
FROM mv_merchant_risk_daily
ORDER BY transaction_date DESC, avg_risk_score DESC;

-- Merchants requiring risk policy review.
SELECT
    merchant_id,
    merchant_name,
    transaction_date,
    transaction_count,
    chargeback_rate,
    decline_rate,
    avg_risk_score
FROM mv_merchant_risk_daily
WHERE chargeback_rate >= 0.08
   OR decline_rate >= 0.25
   OR avg_risk_score >= 75
ORDER BY avg_risk_score DESC, chargeback_rate DESC;
