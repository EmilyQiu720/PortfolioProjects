SET search_path = fraud;

-- Each query returns failing rows. Empty result sets mean the check passed.

SELECT
    'duplicate_customer_email' AS test_name,
    email AS failing_key,
    count(*)::text AS details
FROM customers
GROUP BY email
HAVING count(*) > 1;

SELECT
    'transaction_account_customer_mismatch' AS test_name,
    t.transaction_id::text AS failing_key,
    concat('transaction customer ', t.customer_id, ' differs from account customer ', a.customer_id) AS details
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id
WHERE t.customer_id <> a.customer_id;

SELECT
    'transaction_payment_method_customer_mismatch' AS test_name,
    t.transaction_id::text AS failing_key,
    concat('transaction customer ', t.customer_id, ' differs from payment method customer ', pm.customer_id) AS details
FROM transactions t
JOIN payment_methods pm ON pm.payment_method_id = t.payment_method_id
WHERE t.customer_id <> pm.customer_id;

SELECT
    'negative_or_zero_transaction_amount' AS test_name,
    transaction_id::text AS failing_key,
    amount::text AS details
FROM transactions
WHERE amount <= 0;

SELECT
    'chargeback_amount_exceeds_transaction_amount' AS test_name,
    cb.chargeback_id::text AS failing_key,
    concat('dispute=', cb.dispute_amount, ', transaction=', t.amount) AS details
FROM chargebacks cb
JOIN transactions t ON t.transaction_id = cb.transaction_id
WHERE cb.dispute_amount > t.amount;

SELECT
    'event_before_transaction' AS test_name,
    te.event_id::text AS failing_key,
    concat('event_at=', te.event_at, ', initiated_at=', t.initiated_at) AS details
FROM transaction_events te
JOIN transactions t ON t.transaction_id = te.transaction_id
WHERE te.event_at < t.initiated_at;

SELECT
    'open_alert_without_review_record' AS test_name,
    fa.alert_id::text AS failing_key,
    fa.alert_status AS details
FROM fraud_alerts fa
LEFT JOIN manual_reviews mr ON mr.alert_id = fa.alert_id
WHERE fa.alert_status IN ('open', 'in_review')
  AND mr.review_id IS NULL;
