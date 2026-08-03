load_or_generate_clinical_data <- function(path = "data/synthetic_clinical_outcomes.csv") {
  if (file.exists(path)) {
    return(readr::read_csv(path, show_col_types = FALSE))
  }

  generate_synthetic_clinical_data(n = 1200, seed = 720)
}

generate_synthetic_clinical_data <- function(n = 1200, seed = 720) {
  set.seed(seed)

  hospital_site <- sample(c("North", "Central", "South", "West"), n, replace = TRUE, prob = c(0.30, 0.25, 0.25, 0.20))
  age <- round(pmin(pmax(rnorm(n, mean = 62, sd = 13), 21), 92))
  baseline_severity <- pmin(pmax(round(rnorm(n, mean = 54, sd = 18)), 5), 100)
  comorbidity_index <- pmin(rpois(n, lambda = 2.1), 9)
  prior_admissions <- pmin(rpois(n, lambda = 1.4 + baseline_severity / 80), 8)
  female <- rbinom(n, 1, 0.52)

  site_effect <- dplyr::case_when(
    hospital_site == "North" ~ 0.45,
    hospital_site == "Central" ~ 0.20,
    hospital_site == "South" ~ -0.20,
    TRUE ~ -0.05
  )

  treatment_logit <- -2.1 +
    0.020 * age +
    0.026 * baseline_severity +
    0.20 * comorbidity_index +
    0.12 * prior_admissions +
    site_effect

  treatment_probability <- stats::plogis(treatment_logit)
  treatment <- rbinom(n, 1, treatment_probability)

  outcome_logit <- -0.5 -
    0.55 * treatment +
    0.018 * age +
    0.030 * baseline_severity +
    0.24 * comorbidity_index +
    0.18 * prior_admissions +
    ifelse(hospital_site == "South", 0.18, 0)

  readmitted_30d <- rbinom(n, 1, stats::plogis(outcome_logit))

  event_rate <- exp(-3.15 +
    0.012 * age +
    0.020 * baseline_severity +
    0.18 * comorbidity_index -
    0.38 * treatment)
  time_to_event <- ceiling(stats::rexp(n, rate = pmax(event_rate, 0.01)) * 30)
  follow_up_days <- pmin(time_to_event, 180)
  event_observed <- as.integer(time_to_event <= 180)

  tibble::tibble(
    patient_id = sprintf("P%05d", seq_len(n)),
    hospital_site = hospital_site,
    age = age,
    female = female,
    baseline_severity = baseline_severity,
    comorbidity_index = comorbidity_index,
    prior_admissions = prior_admissions,
    treatment = treatment,
    treatment_probability_true = round(treatment_probability, 4),
    readmitted_30d = readmitted_30d,
    follow_up_days = follow_up_days,
    event_observed = event_observed
  )
}
