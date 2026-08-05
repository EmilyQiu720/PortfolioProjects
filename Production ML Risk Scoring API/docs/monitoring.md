# Monitoring

## Prediction Logging

Every online prediction writes:

- `request_id`
- masked customer hash
- model name
- model version
- risk score
- risk decision
- top factors
- scored timestamp

This supports auditing, model monitoring, delayed-label joins, and incident investigation.

## Operational Metrics

Recommended metrics:

- p50/p95/p99 latency
- request volume
- validation error rate
- auth failure rate
- approve/review/decline distribution
- batch scoring duration
- prediction log write failures

## Model Metrics

Recommended delayed-label monitoring:

- AUC
- average precision
- calibration curve
- approval precision
- manual-review hit rate
- decline false-positive rate
- score distribution by segment

## Drift Metrics

This project includes Population Stability Index in `app/drift.py`.

Common PSI interpretation:

| PSI | Interpretation |
|---|---|
| `< 0.10` | Stable |
| `0.10 - 0.25` | Moderate drift |
| `> 0.25` | Significant drift |

High drift does not automatically mean model failure, but it should trigger investigation.

## Alert Examples

- p95 latency above 250 ms for 10 minutes
- validation error rate above 2%
- manual-review rate changes by more than 8 percentage points day over day
- PSI above 0.25 for `velocity_score`, `order_amount`, or `ip_risk_score`
- score distribution shift without a matching business event

