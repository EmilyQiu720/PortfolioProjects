# Clinical Outcomes Causal Inference in R

## Goal

Build a reproducible R analytics project that estimates treatment effects from non-randomized clinical outcome data using propensity score methods, survival analysis, regression modeling, diagnostics, reporting, and an interactive Shiny dashboard.

## Business Problem

A new clinical care program appears to improve patient outcomes, but patients were not randomly assigned to treatment. Treated patients differ from control patients in age, baseline severity, comorbidities, prior utilization, and hospital site.

The central analytical question is:

> After adjusting for confounding, is the treatment associated with better outcomes?

This project answers that question with a statistically disciplined R workflow.

## Why This Project Is Portfolio-Grade

This project demonstrates senior R skills beyond basic EDA:

- Reproducible analysis pipeline with `targets`
- Isolated dependency management pattern with `renv`
- Synthetic clinical dataset with documented data-generating logic
- Data cleaning and validation functions
- Covariate balance diagnostics before and after adjustment
- Propensity score estimation
- Nearest-neighbor matching
- Inverse probability weighting
- Logistic outcome modeling
- Cox proportional hazards survival modeling
- Kaplan-Meier visualization
- Quarto report for written statistical communication
- Shiny dashboard for stakeholder exploration
- `testthat` tests for data cleaning, modeling, and output contracts

## Project Structure

```text
Clinical Outcomes Causal Inference in R/
  README.md
  renv.lock
  _targets.R
  data/
    synthetic_clinical_outcomes.csv
  R/
    01_generate_data.R
    02_clean_data.R
    03_balance_checks.R
    04_propensity_score.R
    05_survival_analysis.R
    06_outcome_models.R
    07_visualizations.R
  reports/
    clinical_outcomes_report.qmd
  app/
    app.R
  tests/
    testthat/
      test_data_cleaning.R
      test_model_outputs.R
  docs/
    methodology.md
    data_dictionary.md
  scripts/
    run_project_checks.R
```

## Analytical Workflow

1. Generate or load synthetic clinical outcomes data.
2. Clean data, validate ranges, encode factors, and derive clinical risk features.
3. Compare baseline covariate balance between treatment and control groups.
4. Estimate propensity scores using logistic regression.
5. Create matched and weighted analysis cohorts.
6. Evaluate post-adjustment balance with standardized mean differences.
7. Estimate treatment effect for binary outcome using adjusted logistic regression.
8. Estimate time-to-event treatment association using Cox proportional hazards.
9. Produce visualizations for balance, treatment effect, and survival curves.
10. Render a Quarto report and run the Shiny dashboard.

## Key Statistical Methods

### Propensity Score

The propensity score estimates:

```text
P(treatment = 1 | age, severity, comorbidity, prior utilization, hospital site)
```

It is used for matching and inverse probability weighting to reduce measured confounding.

### Standardized Mean Difference

Balance is assessed with standardized mean difference:

```text
SMD = (mean_treated - mean_control) / pooled_sd
```

Absolute SMD below 0.10 is commonly treated as acceptable balance.

### Treatment Effect

The project estimates treatment association through:

- Unadjusted logistic regression
- Adjusted logistic regression
- Propensity-score matched logistic regression
- IPTW weighted logistic regression
- Cox proportional hazards model for time-to-event outcome

## How To Run

Install R 4.3+ and the packages listed in `renv.lock`.

Run the full pipeline:

```r
targets::tar_make()
```

Run tests:

```r
testthat::test_dir("tests/testthat")
```

Render the report:

```r
quarto::quarto_render("reports/clinical_outcomes_report.qmd")
```

Run the dashboard:

```r
shiny::runApp("app")
```

Run static project checks:

```r
source("scripts/run_project_checks.R")
```

## Technology

R, tidyverse, targets, renv, MatchIt, cobalt-style balance diagnostics, survival, broom, ggplot2, Quarto, Shiny, testthat.

## Results Demonstrated

- Built a synthetic but realistic non-randomized clinical dataset with confounding.
- Implemented reproducible cleaning, diagnostics, causal adjustment, survival modeling, and reporting.
- Demonstrated how naive treatment comparisons can differ from adjusted estimates.
- Created reusable R functions and tests instead of one-off notebook logic.
- Packaged outputs for both technical review and stakeholder-facing exploration.
