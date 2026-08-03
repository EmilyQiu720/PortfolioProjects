library(testthat)
library(dplyr)
library(broom)
library(survival)
library(MatchIt)

source("../../R/01_generate_data.R")
source("../../R/02_clean_data.R")
source("../../R/03_balance_checks.R")
source("../../R/04_propensity_score.R")
source("../../R/05_survival_analysis.R")
source("../../R/06_outcome_models.R")

test_that("propensity score workflow returns bounded scores and weights", {
  data <- generate_synthetic_clinical_data(n = 300, seed = 720) |>
    clean_clinical_outcomes()

  model <- fit_propensity_model(data)
  scored <- add_propensity_scores(data, model)

  expect_true(all(scored$propensity_score >= 0.01))
  expect_true(all(scored$propensity_score <= 0.99))
  expect_true(all(is.finite(scored$iptw)))
  expect_true(all(scored$iptw > 0))
})

test_that("balance table returns one row per numeric covariate", {
  data <- generate_synthetic_clinical_data(n = 200, seed = 721) |>
    clean_clinical_outcomes()

  balance <- calculate_balance_table(data, "treatment")

  expect_equal(nrow(balance), length(balance_covariates))
  expect_true(all(c("covariate", "smd", "abs_smd", "balanced") %in% names(balance)))
})

test_that("outcome and survival model summaries include treatment effect", {
  data <- generate_synthetic_clinical_data(n = 350, seed = 722) |>
    clean_clinical_outcomes()
  ps_model <- fit_propensity_model(data)
  scored <- add_propensity_scores(data, ps_model)
  matched <- create_matched_cohort(scored)
  weighted <- create_iptw_cohort(scored)

  outcome_results <- fit_outcome_models(data, matched, weighted) |>
    tidy_outcome_results()
  survival_results <- fit_survival_models(data, matched, weighted) |>
    tidy_survival_results()

  expect_true(nrow(outcome_results) >= 3)
  expect_true(nrow(survival_results) >= 3)
  expect_true(all(outcome_results$estimate > 0))
  expect_true(all(survival_results$estimate > 0))
})
