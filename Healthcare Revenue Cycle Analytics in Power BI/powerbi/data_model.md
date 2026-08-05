# Power BI Data Model

## Modeling Approach

Use a star schema. Keep the fact tables narrow and numeric, keep descriptive labels in dimensions, and create all report logic as DAX measures in a dedicated `Measures` table.

## Tables

### Fact Tables

- `fact_claims`: one row per claim
- `fact_payments`: one row per payment event
- `fact_denials`: one row per denial event
- `fact_ar_snapshot`: one row per claim balance in the month-end AR snapshot

### Dimension Tables

- `dim_date`
- `dim_patient_masked`
- `dim_provider`
- `dim_department`
- `dim_payer`
- `dim_procedure`
- `dim_denial_reason`

## Relationships

Create these relationships in Model view:

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter |
|---|---|---|---|---|---|
| `dim_date` | `date` | `fact_claims` | `service_date` | One-to-many | Single |
| `dim_patient_masked` | `patient_id` | `fact_claims` | `patient_id` | One-to-many | Single |
| `dim_provider` | `provider_id` | `fact_claims` | `provider_id` | One-to-many | Single |
| `dim_department` | `department_id` | `fact_claims` | `department_id` | One-to-many | Single |
| `dim_payer` | `payer_id` | `fact_claims` | `payer_id` | One-to-many | Single |
| `dim_procedure` | `procedure_id` | `fact_claims` | `procedure_id` | One-to-many | Single |
| `fact_claims` | `claim_id` | `fact_payments` | `claim_id` | One-to-many | Single |
| `fact_claims` | `claim_id` | `fact_denials` | `claim_id` | One-to-many | Single |
| `dim_denial_reason` | `denial_reason_id` | `fact_denials` | `denial_reason_id` | One-to-many | Single |
| `fact_claims` | `claim_id` | `fact_ar_snapshot` | `claim_id` | One-to-many | Single |
| `dim_payer` | `payer_id` | `fact_ar_snapshot` | `payer_id` | One-to-many | Single |
| `dim_department` | `department_id` | `fact_ar_snapshot` | `department_id` | One-to-many | Single |

## Date Handling

Mark `dim_date` as the date table:

```text
Table tools -> Mark as date table -> date
```

The active relationship should connect `dim_date[date]` to `fact_claims[service_date]`.

For payment-date analysis, create an inactive relationship from `dim_date[date]` to `fact_payments[payment_date]` and activate it inside measures with `USERELATIONSHIP()` only when needed.

## Semantic Model Conventions

- Hide raw key columns from report view after relationships are built.
- Hide technical columns that are not useful to end users.
- Create a display folder named `Revenue Cycle KPIs` for core measures.
- Create separate display folders for `Time Intelligence`, `Denials`, `AR Aging`, and `Drillthrough`.
- Use explicit measures only; avoid implicit aggregation in visuals.
- Format money as `$#,0;($#,0)`.
- Format rates as `0.0%`.
- Format lag/day measures as `0.0`.

## Recommended Model Diagram

```text
                 dim_date
                    |
dim_patient -> fact_claims <- dim_provider <- dim_department
                    |
                 dim_payer
                    |
              dim_procedure
                    |
    +---------------+---------------+
    |               |               |
fact_payments  fact_denials   fact_ar_snapshot
                    |               |
          dim_denial_reason     dim_payer
                                    |
                              dim_department
```
