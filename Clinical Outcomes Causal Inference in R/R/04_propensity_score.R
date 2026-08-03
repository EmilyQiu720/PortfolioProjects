propensity_formula <- treatment_binary ~
  age +
  baseline_severity +
  comorbidity_index +
  prior_admissions +
  female +
  hospital_site

fit_propensity_model <- function(data) {
  stats::glm(
    propensity_formula,
    data = data,
    family = stats::binomial()
  )
}

add_propensity_scores <- function(data, model) {
  scores <- stats::predict(model, newdata = data, type = "response")

  data |>
    dplyr::mutate(
      propensity_score = pmin(pmax(scores, 0.01), 0.99),
      iptw = dplyr::if_else(
        treatment == "Treated",
        1 / propensity_score,
        1 / (1 - propensity_score)
      ),
      stabilized_iptw = dplyr::if_else(
        treatment == "Treated",
        mean(treatment == "Treated") / propensity_score,
        mean(treatment == "Control") / (1 - propensity_score)
      )
    )
}

create_matched_cohort <- function(data) {
  matchit_object <- MatchIt::matchit(
    treatment_binary ~
      age +
      baseline_severity +
      comorbidity_index +
      prior_admissions +
      female +
      hospital_site,
    data = data,
    method = "nearest",
    distance = data$propensity_score,
    ratio = 1,
    caliper = 0.20
  )

  MatchIt::match.data(matchit_object) |>
    dplyr::mutate(
      treatment = factor(treatment, levels = c("Control", "Treated")),
      matched_weight = weights
    )
}

create_iptw_cohort <- function(data) {
  data |>
    dplyr::filter(is.finite(iptw), iptw <= stats::quantile(iptw, 0.99, na.rm = TRUE))
}
