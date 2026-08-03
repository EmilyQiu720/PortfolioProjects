SET search_path = fraud;

ALTER TABLE customers
    ADD CONSTRAINT customers_kyc_status_chk
        CHECK (kyc_status IN ('pending', 'verified', 'rejected')),
    ADD CONSTRAINT customers_risk_tier_chk
        CHECK (risk_tier IN ('low', 'medium', 'high')),
    ADD CONSTRAINT customers_country_code_chk
        CHECK (country_code ~ '^[A-Z]{2}$');

ALTER TABLE accounts
    ADD CONSTRAINT accounts_type_chk
        CHECK (account_type IN ('consumer_wallet', 'business_wallet')),
    ADD CONSTRAINT accounts_status_chk
        CHECK (account_status IN ('open', 'frozen', 'closed')),
    ADD CONSTRAINT accounts_closed_after_opened_chk
        CHECK (closed_at IS NULL OR closed_at >= opened_at);

ALTER TABLE merchants
    ADD CONSTRAINT merchants_status_chk
        CHECK (merchant_status IN ('active', 'suspended', 'offboarded')),
    ADD CONSTRAINT merchants_risk_score_chk
        CHECK (onboarding_risk_score BETWEEN 0 AND 100),
    ADD CONSTRAINT merchants_country_code_chk
        CHECK (country_code ~ '^[A-Z]{2}$');

ALTER TABLE payment_methods
    ADD CONSTRAINT payment_methods_type_chk
        CHECK (method_type IN ('card', 'bank_account', 'wallet_token')),
    ADD CONSTRAINT payment_methods_status_chk
        CHECK (method_status IN ('active', 'expired', 'blocked')),
    ADD CONSTRAINT payment_methods_last4_chk
        CHECK (card_last4 IS NULL OR card_last4 ~ '^[0-9]{4}$'),
    ADD CONSTRAINT payment_methods_bin_chk
        CHECK (card_bin IS NULL OR card_bin ~ '^[0-9]{6}$');

ALTER TABLE device_fingerprints
    ADD CONSTRAINT device_seen_order_chk
        CHECK (last_seen_at >= first_seen_at),
    ADD CONSTRAINT device_hash_not_blank_chk
        CHECK (length(trim(device_hash)) >= 8);

ALTER TABLE transactions
    ADD CONSTRAINT transactions_amount_chk
        CHECK (amount > 0),
    ADD CONSTRAINT transactions_currency_chk
        CHECK (currency ~ '^[A-Z]{3}$'),
    ADD CONSTRAINT transactions_status_chk
        CHECK (transaction_status IN ('authorized', 'captured', 'declined', 'refunded', 'chargeback')),
    ADD CONSTRAINT transactions_auth_status_chk
        CHECK (authorization_status IN ('approved', 'declined', 'requires_review')),
    ADD CONSTRAINT transactions_risk_score_chk
        CHECK (risk_score BETWEEN 0 AND 100),
    ADD CONSTRAINT transactions_settlement_order_chk
        CHECK (settled_at IS NULL OR settled_at >= initiated_at);

ALTER TABLE transaction_events
    ADD CONSTRAINT transaction_events_type_chk
        CHECK (event_type IN ('authorization_requested', 'authorization_approved', 'authorization_declined', 'captured', 'refunded', 'chargeback_opened', 'chargeback_closed'));

ALTER TABLE risk_rules
    ADD CONSTRAINT risk_rules_severity_chk
        CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    ADD CONSTRAINT risk_rules_threshold_chk
        CHECK (threshold_value >= 0);

ALTER TABLE fraud_alerts
    ADD CONSTRAINT fraud_alerts_status_chk
        CHECK (alert_status IN ('open', 'in_review', 'closed', 'suppressed')),
    ADD CONSTRAINT fraud_alerts_priority_chk
        CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    ADD CONSTRAINT fraud_alerts_score_chk
        CHECK (alert_score BETWEEN 0 AND 100),
    ADD CONSTRAINT fraud_alerts_resolved_after_created_chk
        CHECK (resolved_at IS NULL OR resolved_at >= created_at);

ALTER TABLE manual_reviews
    ADD CONSTRAINT manual_reviews_status_chk
        CHECK (review_status IN ('queued', 'assigned', 'decided')),
    ADD CONSTRAINT manual_reviews_decision_chk
        CHECK (decision IS NULL OR decision IN ('approve', 'decline', 'escalate', 'request_more_info')),
    ADD CONSTRAINT manual_reviews_decided_after_created_chk
        CHECK (decided_at IS NULL OR decided_at >= created_at),
    ADD CONSTRAINT manual_reviews_decision_required_chk
        CHECK ((review_status <> 'decided') OR decision IS NOT NULL);

ALTER TABLE chargebacks
    ADD CONSTRAINT chargebacks_amount_chk
        CHECK (dispute_amount > 0),
    ADD CONSTRAINT chargebacks_status_chk
        CHECK (chargeback_status IN ('open', 'representment', 'won', 'lost')),
    ADD CONSTRAINT chargebacks_closed_after_opened_chk
        CHECK (closed_at IS NULL OR closed_at >= opened_at);
