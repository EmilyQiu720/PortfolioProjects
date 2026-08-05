# Model Card

## Model

`transaction_risk_logistic_baseline`

Active version:

```text
risk-logit-2026-08-05
```

## Intended Use

Estimate transaction risk for an online marketplace or payment platform. The score supports operational routing:

- approve
- manual review
- decline

## Features

The model uses behavioral, account, device, and transaction features:

- account age
- transaction velocity
- prior chargebacks
- failed payment attempts
- order amount
- shipping distance
- device age
- email domain age
- IP risk score
- billing/shipping match
- channel
- customer segment

## Training Metrics

Stored in `artifacts/model_registry.json`:

- ROC AUC: 0.913
- Average precision: 0.684
- Brier score: 0.071
- Precision at review threshold: 0.62
- Recall at review threshold: 0.81

## Decision Thresholds

| Threshold | Value |
|---|---|
| Manual review | 0.42 |
| Decline | 0.78 |

## Limitations

The model artifact is deterministic and synthetic for portfolio demonstration. It is built to show production serving architecture, not to make real financial decisions.

## Responsible AI Notes

- Customer IDs are hashed before logging.
- The service returns top risk factors for operational transparency.
- Thresholds are explicit and versioned.
- Drift monitoring is documented.
- Any real deployment should include fairness analysis, post-decision review, and appeal workflows.

