# API Contract

## Authentication

Protected routes require:

```text
x-api-key: dev-local-key
```

For local development, the key is configured in `.env.example`.

## `POST /v1/score`

### Request

```json
{
  "request_id": "REQ-DEMO-0001",
  "customer_id": "CUST-12345",
  "customer_segment": "consumer",
  "channel": "mobile",
  "account_age_days": 12,
  "prior_transactions_30d": 27,
  "prior_chargebacks_180d": 2,
  "failed_payment_attempts_24h": 4,
  "order_amount": 2800.5,
  "shipping_distance_km": 1200,
  "device_age_days": 3,
  "email_domain_age_days": 15,
  "ip_risk_score": 0.82,
  "billing_shipping_match": false,
  "velocity_score": 0.91
}
```

### Response

```json
{
  "request_id": "REQ-DEMO-0001",
  "model_name": "transaction_risk_logistic_baseline",
  "model_version": "risk-logit-2026-08-05",
  "risk_score": 0.912441,
  "risk_decision": "decline",
  "decision_thresholds": {
    "manual_review": 0.42,
    "decline": 0.78
  },
  "top_factors": [
    "risky IP",
    "transaction velocity",
    "failed payment attempts",
    "prior chargebacks"
  ],
  "scored_at": "2026-08-05T00:00:00Z"
}
```

## Decision Policy

| Risk Score | Decision |
|---|---|
| `< 0.42` | `approve` |
| `>= 0.42` and `< 0.78` | `manual_review` |
| `>= 0.78` | `decline` |

## Error Cases

The API returns validation errors when:

- Required features are missing.
- Numeric features exceed allowed ranges.
- Categorical values are not supported.
- API key is missing or invalid.

