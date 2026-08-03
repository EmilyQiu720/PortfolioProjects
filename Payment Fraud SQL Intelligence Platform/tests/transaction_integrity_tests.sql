SET search_path = fraud;

-- Test 1:
-- A manual review can be decided atomically and audited. The transaction is
-- rolled back because this is a repeatable integrity test, not production data.
BEGIN;
SET LOCAL app.actor = 'transaction_integrity_test';

UPDATE manual_reviews
SET
    review_status = 'decided',
    decision = 'decline',
    decision_reason = 'Integrity test decision for high-risk alert.',
    decided_at = now()
WHERE review_id = '80000000-0000-0000-0000-000000000003';

SELECT
    'manual_review_decision_audit' AS test_name,
    count(*) AS audit_rows_created_inside_transaction
FROM audit_log
WHERE table_name = 'manual_reviews'
  AND operation = 'UPDATE'
  AND row_pk = '80000000-0000-0000-0000-000000000003';

ROLLBACK;

-- Test 2:
-- Opening a chargeback and updating transaction status must happen together.
BEGIN;
SET LOCAL app.actor = 'transaction_integrity_test';

UPDATE transactions
SET transaction_status = 'chargeback'
WHERE transaction_id = '50000000-0000-0000-0000-000000000008';

INSERT INTO chargebacks (
    chargeback_id,
    transaction_id,
    reason_code,
    dispute_amount,
    chargeback_status,
    opened_at,
    closed_at,
    won_by_platform
)
VALUES (
    '90000000-0000-0000-0000-000000000099',
    '50000000-0000-0000-0000-000000000008',
    'product_not_received',
    725.00,
    'open',
    now(),
    NULL,
    NULL
);

SELECT
    'chargeback_transaction_pair' AS test_name,
    t.transaction_status,
    cb.chargeback_status,
    cb.dispute_amount
FROM transactions t
JOIN chargebacks cb ON cb.transaction_id = t.transaction_id
WHERE cb.chargeback_id = '90000000-0000-0000-0000-000000000099';

ROLLBACK;
