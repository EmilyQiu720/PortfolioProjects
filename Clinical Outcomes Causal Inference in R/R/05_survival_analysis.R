fit_survival_models <- function(clean_data, matched_data, weighted_data) {
  list(
    unadjusted = survival::coxph(
      survival::Surv(follow_up_days, event_observed) ~ treatment,
      data = clean_data
    ),
    adjusted = survival::coxph(
      survival::Surv(follow_up_days, event_observed) ~
        treatment +
        age +
        baseline_severity +
        comorbidity_index +
        prior_admissions +
        female +
        hospital_site,
      data = clean_data
    ),
    matched = survival::coxph(
      survival::Surv(follow_up_days, event_observed) ~ treatment,
      data = matched_data,
      weights = matched_weight
    ),
    weighted = survival::coxph(
      survival::Surv(follow_up_days, event_observed) ~ treatment,
      data = weighted_data,
      weights = stabilized_iptw,
      robust = TRUE
    )
  )
}

tidy_survival_results <- function(models) {
  dplyr::bind_rows(lapply(names(models), function(model_name) {
    broom::tidy(models[[model_name]], exponentiate = TRUE, conf.int = TRUE) |>
      dplyr::mutate(model = model_name)
  })) |>
    dplyr::filter(grepl("treatment", term)) |>
    dplyr::select(model, term, estimate, conf.low, conf.high, p.value)
}

check_proportional_hazards <- function(model) {
  survival::cox.zph(model)
}
