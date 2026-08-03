library(targets)
library(tarchetypes)

source("R/01_generate_data.R")
source("R/02_clean_data.R")
source("R/03_balance_checks.R")
source("R/04_propensity_score.R")
source("R/05_survival_analysis.R")
source("R/06_outcome_models.R")
source("R/07_visualizations.R")

tar_option_set(
  packages = c(
    "dplyr",
    "readr",
    "ggplot2",
    "broom",
    "survival",
    "MatchIt"
  )
)

list(
  tar_target(raw_clinical_data, load_or_generate_clinical_data("data/synthetic_clinical_outcomes.csv")),
  tar_target(clean_clinical_data, clean_clinical_outcomes(raw_clinical_data)),
  tar_target(unadjusted_balance, calculate_balance_table(clean_clinical_data, "treatment")),
  tar_target(propensity_model, fit_propensity_model(clean_clinical_data)),
  tar_target(scored_data, add_propensity_scores(clean_clinical_data, propensity_model)),
  tar_target(matched_data, create_matched_cohort(scored_data)),
  tar_target(weighted_data, create_iptw_cohort(scored_data)),
  tar_target(matched_balance, calculate_balance_table(matched_data, "treatment")),
  tar_target(weighted_balance, calculate_weighted_balance_table(weighted_data, "treatment", "iptw")),
  tar_target(logistic_models, fit_outcome_models(clean_clinical_data, matched_data, weighted_data)),
  tar_target(survival_models, fit_survival_models(clean_clinical_data, matched_data, weighted_data)),
  tar_target(balance_plot, plot_balance_comparison(unadjusted_balance, matched_balance, weighted_balance)),
  tar_target(survival_plot, plot_kaplan_meier(clean_clinical_data)),
  tar_render(report, "reports/clinical_outcomes_report.qmd")
)
