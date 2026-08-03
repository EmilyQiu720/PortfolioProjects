# Data Dictionary

## synthetic_clinical_outcomes.csv

| Column | Type | Description |
|---|---|---|
| `patient_id` | character | Unique patient identifier. |
| `hospital_site` | categorical | Hospital site where the patient was treated. |
| `age` | numeric | Patient age in years. |
| `female` | binary | 1 if patient is female, 0 otherwise. |
| `baseline_severity` | numeric | Baseline clinical severity score from 0 to 100. |
| `comorbidity_index` | numeric | Count-like comorbidity burden indicator. |
| `prior_admissions` | numeric | Number of prior admissions before treatment index date. |
| `treatment` | binary | 1 if patient received treatment, 0 if control. |
| `treatment_probability_true` | numeric | Synthetic true treatment probability used during data generation. Not used in modeling. |
| `readmitted_30d` | binary | 1 if patient was readmitted within 30 days. |
| `follow_up_days` | numeric | Follow-up duration for time-to-event analysis. |
| `event_observed` | binary | 1 if event occurred during follow-up, 0 if censored. |

## Derived Fields

| Column | Description |
|---|---|
| `treatment_binary` | Numeric treatment indicator created after cleaning. |
| `age_group` | Age category: `<50`, `50-64`, `65-79`, `80+`. |
| `severity_band` | Baseline severity category: `Low`, `Medium`, `High`. |
| `propensity_score` | Estimated probability of treatment given baseline covariates. |
| `iptw` | Inverse probability of treatment weight. |
| `stabilized_iptw` | Stabilized inverse probability weight. |

## Privacy Note

The dataset is fully synthetic. It is generated for portfolio demonstration and does not contain protected health information.
