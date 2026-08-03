# Query Performance Notes

## Tuning Goals

The project is tuned for fraud operations workloads:

- Fast review queue reads
- Time-window scans over transactions
- Merchant risk dashboard refreshes
- Payment method velocity detection
- Chargeback investigation by transaction and merchant

## Slow Query Pattern 1: Repeated Dashboard Aggregation

The raw dashboard query in `slow_queries.sql` scans `transactions`, joins `chargebacks`, and performs a correlated subquery for each merchant-day group.

Expected issue:

- Repeated aggregation work
- Poor scalability as transaction history grows
- High latency for dashboard refreshes

Optimization:

- Move reusable daily metrics into `mv_merchant_risk_daily`
- Create a unique index on `(merchant_id, transaction_date)`
- Refresh the materialized view on a schedule or after batch ingestion

## Slow Query Pattern 2: Function-Wrapped Date Filter

The slow query filters with:

```sql
date_trunc('day', initiated_at)::date = DATE '2026-05-03'
```

That pattern can prevent efficient use of an index on `initiated_at`.

Optimization:

```sql
initiated_at >= TIMESTAMPTZ '2026-05-03 00:00:00+00'
AND initiated_at < TIMESTAMPTZ '2026-05-04 00:00:00+00'
```

This preserves an index-friendly range scan.

## Index Strategy

The project includes indexes for:

- `transactions(initiated_at DESC)` for recent activity
- `transactions(customer_id, initiated_at DESC)` for customer investigations
- `transactions(merchant_id, initiated_at DESC)` for merchant dashboards
- `transactions(payment_method_id, initiated_at DESC)` for card velocity checks
- `transactions(device_id, initiated_at DESC)` for device investigations
- Partial high-risk index for active high-risk payments
- Partial open-alert index for fraud operations queues

## How To Validate

Run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
```

against the before and after queries. In a large dataset, the optimized versions should show fewer rows scanned, better index usage, and lower execution time.
