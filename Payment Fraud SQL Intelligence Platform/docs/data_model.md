# Data Model

## Design Summary

The schema separates payment operations, fraud investigation, and analytics.

Operational tables capture customer, account, merchant, device, payment method, transaction, event, alert, manual review, and chargeback records. Analytical views and materialized views sit on top of these tables so dashboard logic does not duplicate complex joins.

## Core Entities

### Customers and Accounts

`customers` stores identity, KYC status, country, and risk tier. `accounts` represents payment wallets owned by customers. Transactions reference both customer and account, and data quality tests check that the two agree.

### Merchants

`merchants` stores merchant category, country, status, and onboarding risk score. Merchant analytics combine onboarding risk with observed transaction risk, decline rate, and chargeback rate.

### Payment Methods and Devices

`payment_methods` stores card or token metadata without full card numbers. `device_fingerprints` stores a reusable device hash and IP country signal. Shared device hashes across customers are used as a fraud signal.

### Transactions and Events

`transactions` is the core fact table for payment attempts, authorization outcome, final status, amount, and risk score. `transaction_events` stores lifecycle events such as authorization, capture, refund, and chargeback transitions.

### Fraud Alerts and Reviews

`risk_rules` defines configurable fraud rules. `fraud_alerts` records rule hits. `manual_reviews` captures human-in-the-loop decisions and analyst queue state.

### Chargebacks

`chargebacks` captures dispute reason, amount, status, close time, and whether the platform won the dispute.

### Audit Log

`audit_log` records inserts, updates, and deletes on sensitive operational tables. The trigger uses the `app.actor` setting when available, which allows application code to identify the user or service responsible for a change.

## Modeling Choices

- UUID primary keys make records portable across services.
- Foreign keys enforce relationship integrity.
- Text statuses are constrained through `CHECK` constraints for readability.
- Raw PII access is separated from masked analyst views.
- Materialized views support dashboard and risk-monitoring workloads.
- Audit logging is implemented in SQL so sensitive changes are captured below the application layer.
