# Power Query Steps

Use these steps after loading the CSV files.

## General Cleanup

For every table:

1. Promote headers.
2. Trim text columns.
3. Set correct data types.
4. Disable automatic date hierarchy if you prefer the explicit `dim_date` table.
5. Rename columns only if needed for display. Keep source column names stable for DAX examples.

## Data Types

### Dates

Set these columns to Date:

- `dim_date[date]`
- `dim_date[week_start_date]`
- `fact_claims[service_date]`
- `fact_claims[claim_submit_date]`
- `fact_payments[payment_date]`
- `fact_denials[denial_date]`
- `fact_ar_snapshot[snapshot_date]`

### Currency / Decimal

Set these columns to Decimal Number or Fixed Decimal Number:

- `fact_claims[gross_charge]`
- `fact_claims[allowed_amount]`
- `fact_claims[expected_patient_responsibility]`
- `fact_payments[payer_payment]`
- `fact_payments[patient_payment]`
- `fact_payments[contractual_adjustment]`
- `fact_payments[writeoff_amount]`
- `fact_denials[denial_amount]`
- `fact_denials[recovered_amount]`
- `fact_ar_snapshot[ar_balance]`

### Whole Numbers

Set these columns to Whole Number:

- `fact_claims[clean_claim_flag]`
- `fact_claims[length_of_stay]`
- `fact_payments[payment_lag_days]`
- `fact_denials[preventable_flag]`
- `fact_ar_snapshot[age_days]`
- `dim_date[year]`
- `dim_date[month_number]`
- `dim_date[is_weekend]`

## Recommended Display Columns

In Power Query or Model view, rename for readability:

| Source Column | Display Name |
|---|---|
| `payer_name` | Payer |
| `department_name` | Department |
| `provider_name` | Provider |
| `denial_reason` | Denial Reason |
| `denial_category` | Denial Category |
| `procedure_group` | Procedure Group |
| `year_month` | Year Month |

## Optional Power Query Validation Columns

You may add these columns for QA, then hide them from report view:

### Claim Submitted After Service

```powerquery
if [claim_submit_date] >= [service_date] then "Valid" else "Invalid"
```

### Payment Lag Bucket

```powerquery
if [payment_lag_days] <= 30 then "0-30"
else if [payment_lag_days] <= 60 then "31-60"
else if [payment_lag_days] <= 90 then "61-90"
else "90+"
```

## Load Settings

Load all tables to the model. Do not merge facts into one flat table; the point of this project is to show a governed semantic model.
