clean_clinical_outcomes <- function(data) {
  required_columns <- c(
    "patient_id",
    "hospital_site",
    "age",
    "female",
    "baseline_severity",
    "comorbidity_index",
    "prior_admissions",
    "treatment",
    "readmitted_30d",
    "follow_up_days",
    "event_observed"
  )

  missing_columns <- setdiff(required_columns, names(data))
  if (length(missing_columns) > 0) {
    stop("Missing required columns: ", paste(missing_columns, collapse = ", "), call. = FALSE)
  }

  data |>
    dplyr::mutate(
      patient_id = as.character(patient_id),
      hospital_site = factor(hospital_site),
      age = as.numeric(age),
      female = factor(female, levels = c(0, 1), labels = c("Male", "Female")),
      baseline_severity = as.numeric(baseline_severity),
      comorbidity_index = as.numeric(comorbidity_index),
      prior_admissions = as.numeric(prior_admissions),
      treatment = factor(treatment, levels = c(0, 1), labels = c("Control", "Treated")),
      treatment_binary = as.integer(treatment == "Treated"),
      readmitted_30d = as.integer(readmitted_30d),
      follow_up_days = as.numeric(follow_up_days),
      event_observed = as.integer(event_observed),
      age_group = dplyr::case_when(
        age < 50 ~ "<50",
        age < 65 ~ "50-64",
        age < 80 ~ "65-79",
        TRUE ~ "80+"
      ),
      severity_band = dplyr::case_when(
        baseline_severity < 35 ~ "Low",
        baseline_severity < 70 ~ "Medium",
        TRUE ~ "High"
      )
    ) |>
    validate_clean_clinical_data()
}

validate_clean_clinical_data <- function(data) {
  if (anyDuplicated(data$patient_id) > 0) {
    stop("patient_id must be unique.", call. = FALSE)
  }
  if (any(is.na(data$age)) || any(data$age < 18 | data$age > 100)) {
    stop("age must be non-missing and between 18 and 100.", call. = FALSE)
  }
  if (any(is.na(data$baseline_severity)) || any(data$baseline_severity < 0 | data$baseline_severity > 100)) {
    stop("baseline_severity must be non-missing and between 0 and 100.", call. = FALSE)
  }
  if (any(is.na(data$follow_up_days)) || any(data$follow_up_days <= 0)) {
    stop("follow_up_days must be positive.", call. = FALSE)
  }
  if (!all(data$readmitted_30d %in% c(0, 1))) {
    stop("readmitted_30d must be binary.", call. = FALSE)
  }
  if (!all(data$event_observed %in% c(0, 1))) {
    stop("event_observed must be binary.", call. = FALSE)
  }

  data
}
