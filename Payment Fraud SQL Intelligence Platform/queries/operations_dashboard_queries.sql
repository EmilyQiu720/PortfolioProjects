SET search_path = fraud;

-- Fraud operations queue overview.
SELECT
    alert_status,
    priority,
    count(*) AS alert_count,
    min(created_at) AS oldest_alert_at,
    max(created_at) AS newest_alert_at
FROM fraud_alerts
GROUP BY alert_status, priority
ORDER BY alert_status, priority;

-- Analyst throughput and open work.
SELECT
    analyst_id,
    count(*) AS review_count,
    count(*) FILTER (WHERE review_status = 'decided') AS decided_count,
    count(*) FILTER (WHERE review_status <> 'decided') AS open_count,
    avg(decided_at - created_at) FILTER (WHERE review_status = 'decided') AS average_decision_time
FROM manual_reviews
GROUP BY analyst_id
ORDER BY open_count DESC, average_decision_time DESC NULLS LAST;

-- SLA breach candidates for review managers.
SELECT
    mr.review_id,
    mr.analyst_id,
    mr.review_status,
    fa.priority,
    fa.alert_score,
    mr.created_at,
    now() - mr.created_at AS review_age
FROM manual_reviews mr
JOIN fraud_alerts fa ON fa.alert_id = mr.alert_id
WHERE mr.review_status <> 'decided'
  AND (
      (fa.priority = 'critical' AND now() - mr.created_at > INTERVAL '30 minutes')
      OR (fa.priority = 'high' AND now() - mr.created_at > INTERVAL '2 hours')
      OR (fa.priority IN ('medium', 'low') AND now() - mr.created_at > INTERVAL '24 hours')
  )
ORDER BY fa.alert_score DESC, review_age DESC;

-- Dashboard-ready payment volume.
SELECT
    date_trunc('day', initiated_at)::date AS payment_date,
    currency,
    count(*) AS transaction_count,
    sum(amount) AS gross_payment_volume,
    avg(risk_score) AS average_risk_score,
    count(*) FILTER (WHERE authorization_status = 'approved') AS approved_count,
    count(*) FILTER (WHERE authorization_status = 'declined') AS declined_count,
    count(*) FILTER (WHERE authorization_status = 'requires_review') AS review_required_count
FROM transactions
GROUP BY date_trunc('day', initiated_at)::date, currency
ORDER BY payment_date DESC, currency;
