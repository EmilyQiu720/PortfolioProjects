SET search_path = fraud;

-- Customer activation and repeat behavior.
WITH first_transaction AS (
    SELECT
        customer_id,
        min(initiated_at) AS first_transaction_at
    FROM transactions
    GROUP BY customer_id
),
customer_activity AS (
    SELECT
        c.customer_id,
        c.risk_tier,
        c.created_at,
        ft.first_transaction_at,
        count(t.transaction_id) AS transaction_count,
        count(*) FILTER (WHERE t.authorization_status = 'approved') AS approved_count,
        count(*) FILTER (WHERE t.transaction_status = 'chargeback') AS chargeback_count,
        sum(t.amount) AS total_spend
    FROM customers c
    LEFT JOIN first_transaction ft ON ft.customer_id = c.customer_id
    LEFT JOIN transactions t ON t.customer_id = c.customer_id
    GROUP BY c.customer_id, c.risk_tier, c.created_at, ft.first_transaction_at
)
SELECT
    *,
    first_transaction_at - created_at AS time_to_first_transaction,
    CASE WHEN approved_count >= 2 THEN true ELSE false END AS repeated_legitimate_activity,
    chargeback_count::numeric / NULLIF(transaction_count, 0) AS chargeback_rate
FROM customer_activity
ORDER BY total_spend DESC NULLS LAST;

-- Cohort-style monthly customer activity.
WITH monthly_activity AS (
    SELECT
        c.customer_id,
        date_trunc('month', c.created_at)::date AS signup_month,
        date_trunc('month', t.initiated_at)::date AS activity_month,
        count(t.transaction_id) AS monthly_transactions
    FROM customers c
    JOIN transactions t ON t.customer_id = c.customer_id
    GROUP BY c.customer_id, date_trunc('month', c.created_at)::date, date_trunc('month', t.initiated_at)::date
)
SELECT
    signup_month,
    activity_month,
    count(DISTINCT customer_id) AS active_customers,
    sum(monthly_transactions) AS transaction_count
FROM monthly_activity
GROUP BY signup_month, activity_month
ORDER BY signup_month, activity_month;

-- Payment method risk distribution by customer tier.
SELECT
    c.risk_tier,
    pm.method_type,
    count(DISTINCT pm.payment_method_id) AS payment_method_count,
    count(t.transaction_id) AS transaction_count,
    avg(t.risk_score) AS average_risk_score,
    count(*) FILTER (WHERE t.authorization_status = 'declined') AS declined_count
FROM customers c
JOIN payment_methods pm ON pm.customer_id = c.customer_id
LEFT JOIN transactions t ON t.payment_method_id = pm.payment_method_id
GROUP BY c.risk_tier, pm.method_type
ORDER BY c.risk_tier, average_risk_score DESC NULLS LAST;
