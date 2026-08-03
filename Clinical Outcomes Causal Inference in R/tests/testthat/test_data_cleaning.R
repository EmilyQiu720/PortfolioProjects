library(testthat)
library(dplyr)

source("../../R/01_generate_data.R")
source("../../R/02_clean_data.R")

test_that("clean_clinical_outcomes validates and derives expected fields", {
  raw_data <- generate_synthetic_clinical_data(n = 200, seed = 123)
  clean_data <- clean_clinical_outcomes(raw_data)

  expect_equal(nrow(clean_data), 200)
  expect_true(all(c("treatment_binary", "age_group", "severity_band") %in% names(clean_data)))
  expect_true(all(clean_data$age >= 18 & clean_data$age <= 100))
  expect_true(all(clean_data$baseline_severity >= 0 & clean_data$baseline_severity <= 100))
  expect_true(all(clean_data$readmitted_30d %in% c(0, 1)))
  expect_true(all(clean_data$event_observed %in% c(0, 1)))
})

test_that("clean_clinical_outcomes rejects duplicate patient ids", {
  raw_data <- generate_synthetic_clinical_data(n = 50, seed = 456)
  raw_data$patient_id[2] <- raw_data$patient_id[1]

  expect_error(
    clean_clinical_outcomes(raw_data),
    "patient_id must be unique"
  )
})
