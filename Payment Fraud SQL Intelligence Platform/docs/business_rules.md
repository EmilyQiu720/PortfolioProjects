# Business Rules

## Fraud Rules

### CARD_VELOCITY_1H

Flag a payment method when more than three transaction attempts occur within one hour.

Purpose:

- Detect card testing
- Catch automated retry behavior
- Prioritize payment methods with high risk scores and concentrated attempts

### DEVICE_FANOUT

Flag a device hash when it is linked to two or more customers.

Purpose:

- Detect account farming
- Identify synthetic identity clusters
- Escalate cases where device sharing overlaps with high-risk transactions

### COUNTRY_MISMATCH

Flag transactions where customer country differs from billing country or device IP country.

Purpose:

- Identify unusual geography signals
- Support analyst triage rather than automatic decline

### HIGH_AMOUNT_HIGH_RISK

Flag high-value transactions with elevated transaction risk.

Purpose:

- Reduce loss exposure
- Route expensive payments to manual review before capture

### MERCHANT_CHARGEBACK_RATE

Flag merchants whose chargeback rate exceeds tolerance.

Purpose:

- Detect merchant fraud
- Identify weak merchant onboarding
- Trigger reserves, monitoring, or suspension review

## Manual Review Rules

- Critical alerts should be reviewed within 30 minutes.
- High-priority alerts should be reviewed within 2 hours.
- Medium and low alerts should be reviewed within 24 hours.
- A review with status `decided` must include a decision.

## Governance Rules

- Analysts should use masked customer views by default.
- Investigators may access raw tables only for case investigation.
- Sensitive table changes are written to `audit_log`.
- Data quality tests should run before dashboard refresh and before portfolio demo execution.
