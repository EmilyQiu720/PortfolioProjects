SET search_path = fraud;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'fraud_readonly') THEN
        CREATE ROLE fraud_readonly;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'fraud_analyst') THEN
        CREATE ROLE fraud_analyst;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'fraud_investigator') THEN
        CREATE ROLE fraud_investigator;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA fraud TO fraud_readonly, fraud_analyst, fraud_investigator;

GRANT SELECT ON
    v_masked_customers,
    v_transaction_enriched,
    v_customer_payment_profile,
    v_merchant_daily_summary,
    mv_merchant_risk_daily,
    mv_payment_method_velocity_hourly
TO fraud_readonly;

GRANT SELECT ON
    v_masked_customers,
    v_transaction_enriched,
    v_alert_review_queue,
    v_customer_payment_profile,
    v_merchant_daily_summary,
    mv_merchant_risk_daily,
    mv_payment_method_velocity_hourly,
    fraud_alerts,
    risk_rules
TO fraud_analyst;

GRANT SELECT ON ALL TABLES IN SCHEMA fraud TO fraud_investigator;
GRANT INSERT, UPDATE ON manual_reviews TO fraud_investigator;
GRANT INSERT, UPDATE ON fraud_alerts TO fraud_investigator;

REVOKE ALL ON customers FROM fraud_readonly, fraud_analyst;
GRANT SELECT ON v_masked_customers TO fraud_readonly, fraud_analyst;
