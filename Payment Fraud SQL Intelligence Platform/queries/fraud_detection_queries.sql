SET search_path = fraud;

-- 1. Card velocity: more than three attempts on the same payment method in one hour.
WITH payment_method_attempts AS (
    SELECT
        transaction_id,
        payment_method_id,
        initiated_at,
        count(*) OVER (
            PARTITION BY payment_method_id
            ORDER BY initiated_at
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS attempts_last_hour,
        sum(amount) OVER (
            PARTITION BY payment_method_id
            ORDER BY initiated_at
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS amount_last_hour,
        avg(risk_score) OVER (
            PARTITION BY payment_method_id
            ORDER BY initiated_at
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS avg_risk_last_hour
    FROM transactions
)
SELECT *
FROM payment_method_attempts
WHERE attempts_last_hour > 3
ORDER BY attempts_last_hour DESC, initiated_at DESC;

-- 2. Device fan-out: one device hash linked to multiple customers.
WITH device_usage AS (
    SELECT
        df.device_hash,
        count(DISTINCT df.customer_id) AS customer_count,
        count(DISTINCT t.transaction_id) AS transaction_count,
        max(t.risk_score) AS max_risk_score,
        sum(t.amount) AS total_amount
    FROM device_fingerprints df
    LEFT JOIN transactions t ON t.device_id = df.device_id
    GROUP BY df.device_hash
)
SELECT *
FROM device_usage
WHERE customer_count >= 2
ORDER BY customer_count DESC, max_risk_score DESC;

-- 3. Composite risk score for analyst triage.
WITH chargeback_history AS (
    SELECT
        t.merchant_id,
        count(cb.chargeback_id)::numeric / NULLIF(count(t.transaction_id), 0) AS merchant_chargeback_rate
    FROM transactions t
    LEFT JOIN chargebacks cb ON cb.transaction_id = t.transaction_id
    GROUP BY t.merchant_id
),
scored AS (
    SELECT
        te.transaction_id,
        te.initiated_at,
        te.amount,
        te.merchant_name,
        te.customer_risk_tier,
        te.billing_country_mismatch,
        te.ip_country_mismatch,
        te.risk_score,
        coalesce(ch.merchant_chargeback_rate, 0) AS merchant_chargeback_rate,
        (
            te.risk_score
            + CASE WHEN te.amount >= 500 THEN 10 ELSE 0 END
            + CASE WHEN te.customer_risk_tier = 'high' THEN 12 ELSE 0 END
            + CASE WHEN te.billing_country_mismatch THEN 8 ELSE 0 END
            + CASE WHEN te.ip_country_mismatch THEN 8 ELSE 0 END
            + CASE WHEN coalesce(ch.merchant_chargeback_rate, 0) >= 0.08 THEN 15 ELSE 0 END
        ) AS composite_risk_score
    FROM v_transaction_enriched te
    LEFT JOIN chargeback_history ch ON ch.merchant_id = te.merchant_id
)
SELECT *
FROM scored
WHERE composite_risk_score >= 85
ORDER BY composite_risk_score DESC, amount DESC;

-- 4. Open review queue ranked by business risk and SLA age.
SELECT
    alert_id,
    transaction_id,
    priority,
    rule_code,
    amount,
    merchant_name,
    customer_risk_tier,
    alert_age_hours,
    dense_rank() OVER (
        ORDER BY
            CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END,
            amount DESC,
            alert_age_hours DESC
    ) AS queue_rank
FROM v_alert_review_queue
ORDER BY queue_rank;
