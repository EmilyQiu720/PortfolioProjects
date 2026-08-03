# Methodology

## Study Design

This project simulates an observational clinical study. Treatment is not randomly assigned. Higher-risk patients are more likely to receive treatment, which creates confounding by indication.

The analysis estimates the association between treatment and outcomes after adjusting for observed baseline covariates.

## Confounding Variables

The adjustment set includes:

- Age
- Sex
- Baseline severity
- Comorbidity index
- Prior admissions
- Hospital site

These variables affect treatment assignment and patient outcomes, so they must be balanced or adjusted.

## Propensity Score

The propensity model estimates the probability of treatment using baseline covariates.

```r
treatment_binary ~ age + baseline_severity + comorbidity_index +
  prior_admissions + female + hospital_site
```

The score is used in two ways:

- Nearest-neighbor matching
- Inverse probability of treatment weighting

## Balance Diagnostics

Covariate balance is assessed with standardized mean differences. The project flags covariates with absolute SMD below 0.10 as balanced.

## Outcome Models

The binary outcome is 30-day readmission. The project fits:

- Unadjusted logistic regression
- Covariate-adjusted logistic regression
- Matched logistic regression
- Weighted logistic regression

The time-to-event outcome uses:

- Unadjusted Cox proportional hazards model
- Covariate-adjusted Cox model
- Matched Cox model
- Weighted Cox model with robust standard errors

## Interpretation

Odds ratios or hazard ratios below 1.0 suggest lower risk in the treated group. Because the dataset is observational, estimates should be interpreted as adjusted associations unless all causal identification assumptions are accepted.

## Limitations

- Synthetic data cannot represent real clinical complexity.
- Unmeasured confounding is not removed by propensity score methods.
- Matching can reduce sample size.
- IPTW can be unstable when propensity scores approach 0 or 1.
- Clinical implementation would require domain review and sensitivity analyses.
