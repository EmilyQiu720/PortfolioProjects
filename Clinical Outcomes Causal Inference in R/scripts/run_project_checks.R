required_files <- c(
  "README.md",
  "renv.lock",
  "_targets.R",
  "data/synthetic_clinical_outcomes.csv",
  "R/01_generate_data.R",
  "R/02_clean_data.R",
  "R/03_balance_checks.R",
  "R/04_propensity_score.R",
  "R/05_survival_analysis.R",
  "R/06_outcome_models.R",
  "R/07_visualizations.R",
  "reports/clinical_outcomes_report.qmd",
  "app/app.R",
  "tests/testthat/test_data_cleaning.R",
  "tests/testthat/test_model_outputs.R",
  "docs/methodology.md",
  "docs/data_dictionary.md"
)

missing_files <- required_files[!file.exists(required_files)]
if (length(missing_files) > 0) {
  stop("Missing project files: ", paste(missing_files, collapse = ", "), call. = FALSE)
}

required_patterns <- list(
  "R/04_propensity_score.R" = c("glm", "matchit", "iptw"),
  "R/05_survival_analysis.R" = c("coxph", "Surv"),
  "R/06_outcome_models.R" = c("binomial", "readmitted_30d"),
  "reports/clinical_outcomes_report.qmd" = c("Propensity", "Survival", "Limitations"),
  "app/app.R" = c("shinyApp", "renderPlot", "renderTable")
)

for (file in names(required_patterns)) {
  text <- paste(readLines(file, warn = FALSE), collapse = "\n")
  missing_patterns <- required_patterns[[file]][!grepl(required_patterns[[file]], text, fixed = TRUE)]
  if (length(missing_patterns) > 0) {
    stop(file, " is missing expected content: ", paste(missing_patterns, collapse = ", "), call. = FALSE)
  }
}

message("Project structure checks passed.")
