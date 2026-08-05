# Data Dictionary

## Relationship Keys

| Table | Primary Key |
|---|---|
| `fact_claims` | `claim_id` |
| `fact_payments` | `payment_id` |
| `fact_denials` | `denial_id` |
| `dim_date` | `date` |
| `dim_patient_masked` | `patient_id` |
| `dim_provider` | `provider_id` |
| `dim_department` | `department_id` |
| `dim_payer` | `payer_id` |
| `dim_procedure` | `procedure_id` |
| `dim_denial_reason` | `denial_reason_id` |

## `fact_claims.csv`

| Field | Description |
|---|---|
| `claim_id` | Unique claim identifier. |
| `patient_id` | Masked patient key. |
| `provider_id` | Rendering provider key. |
| `department_id` | Department key. |
| `payer_id` | Payer key. |
| `procedure_id` | Procedure key. |
| `service_date` | Date of service. |
| `claim_submit_date` | Date claim was submitted. |
| `claim_status` | Paid, Denied, In AR, or Written Off. |
| `claim_type` | Professional or Facility. |
| `gross_charge` | Full billed charge. |
| `allowed_amount` | Contracted allowed amount. |
| `expected_patient_responsibility` | Expected patient portion. |
| `clean_claim_flag` | 1 if submitted cleanly and not denied. |
| `length_of_stay` | Inpatient stay length where applicable. |

## `fact_payments.csv`

| Field | Description |
|---|---|
| `payment_id` | Unique payment event identifier. |
| `claim_id` | Claim key. |
| `payment_date` | Payment posting date. |
| `payer_payment` | Amount paid by payer. |
| `patient_payment` | Amount paid by patient. |
| `contractual_adjustment` | Difference between gross charge and allowed amount. |
| `writeoff_amount` | Balance written off. |
| `payment_lag_days` | Days from claim submission to payment. |

## `fact_denials.csv`

| Field | Description |
|---|---|
| `denial_id` | Unique denial event identifier. |
| `claim_id` | Claim key. |
| `denial_date` | Date denial was posted. |
| `denial_reason_id` | Denial reason key. |
| `denial_amount` | Amount denied. |
| `preventable_flag` | 1 if denial is operationally preventable. |
| `appeal_status` | Not Appealed, Appeal Pending, Appeal Won, or Appeal Lost. |
| `recovered_amount` | Amount recovered after appeal. |

## `fact_ar_snapshot.csv`

| Field | Description |
|---|---|
| `snapshot_date` | Month-end snapshot date. |
| `claim_id` | Claim key. |
| `payer_id` | Payer key for aging analysis. |
| `department_id` | Department key for ownership. |
| `ar_balance` | Open receivable balance. |
| `aging_bucket` | 0-30, 31-60, 61-90, 91-120, or 120+. |
| `age_days` | Days since date of service. |

## Dimensions

Dimension tables provide report labels and filtering attributes:

- `dim_date`: calendar attributes
- `dim_patient_masked`: patient segment, age band, risk band, and masked geography
- `dim_provider`: provider and specialty
- `dim_department`: department, service line, and region
- `dim_payer`: payer, payer type, denial tendency, and lag tendency
- `dim_procedure`: procedure code, group, description, base charge, and complexity
- `dim_denial_reason`: denial reason, category, and preventability
