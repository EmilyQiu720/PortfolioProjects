fit_outcome_models <- function(clean_data, matched_data, weighted_data) {
  list(
    unadjusted = stats::glm(
      readmitted_30d ~ treatment,
      data = clean_data,
      family = stats::binomial()
    ),
    adjusted = stats::glm(
      readmitted_30d ~
        treatment +
        age +
        baseline_severity +
        comorbidity_index +
        prior_admissions +
        female +
        hospital_site,
      data = clean_data,
      family = stats::binomial()
    ),
    matched = stats::glm(
      readmitted_30d ~ treatment,
      data = matched_data,
      weights = matched_weight,
      family = stats::binomial()
    ),
    weighted = stats::glm(
      readmitted_30d ~ treatment,
      data = weighted_data,
      weights = stabilized_iptw,
      family = stats::binomial()
    )
  )
}

tidy_outcome_results <- function(models) {
  dplyr::bind_rows(lapply(names(models), function(model_name) {
    broom::tidy(models[[model_name]], exponentiate = TRUE, conf.int = TRUE) |>
      dplyr::mutate(model = model_name)
  })) |>
    dplyr::filter(grepl("treatment", term)) |>
    dplyr::select(model, term, estimate, conf.low, conf.high, p.value)
}

estimate_absolute_risk_difference <- function(data) {
  summary <- data |>
    dplyr::group_by(treatment) |>
    dplyr::summarise(
      risk = mean(readmitted_30d),
      n = dplyr::n(),
      .groups = "drop"
    )

  treated_risk <- summary$risk[summary$treatment == "Treated"]
  control_risk <- summary$risk[summary$treatment == "Control"]

  tibble::tibble(
    control_risk = control_risk,
    treated_risk = treated_risk,
    risk_difference = treated_risk - control_risk
  )
}
