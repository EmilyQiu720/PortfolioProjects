balance_covariates <- c(
  "age",
  "baseline_severity",
  "comorbidity_index",
  "prior_admissions"
)

standardized_mean_difference <- function(x, treatment, weights = NULL) {
  treated <- treatment == "Treated"
  control <- treatment == "Control"

  if (is.null(weights)) {
    mean_treated <- mean(x[treated], na.rm = TRUE)
    mean_control <- mean(x[control], na.rm = TRUE)
    sd_treated <- stats::sd(x[treated], na.rm = TRUE)
    sd_control <- stats::sd(x[control], na.rm = TRUE)
  } else {
    mean_treated <- stats::weighted.mean(x[treated], weights[treated], na.rm = TRUE)
    mean_control <- stats::weighted.mean(x[control], weights[control], na.rm = TRUE)
    sd_treated <- weighted_sd(x[treated], weights[treated])
    sd_control <- weighted_sd(x[control], weights[control])
  }

  pooled_sd <- sqrt((sd_treated^2 + sd_control^2) / 2)
  if (is.na(pooled_sd) || pooled_sd == 0) {
    return(0)
  }

  (mean_treated - mean_control) / pooled_sd
}

weighted_sd <- function(x, w) {
  valid <- !is.na(x) & !is.na(w)
  x <- x[valid]
  w <- w[valid]
  weighted_mean <- stats::weighted.mean(x, w)
  sqrt(sum(w * (x - weighted_mean)^2) / sum(w))
}

calculate_balance_table <- function(data, treatment_col = "treatment") {
  treatment <- data[[treatment_col]]

  dplyr::bind_rows(lapply(balance_covariates, function(covariate) {
    x <- data[[covariate]]
    tibble::tibble(
      covariate = covariate,
      mean_treated = mean(x[treatment == "Treated"], na.rm = TRUE),
      mean_control = mean(x[treatment == "Control"], na.rm = TRUE),
      smd = standardized_mean_difference(x, treatment),
      abs_smd = abs(smd),
      balanced = abs_smd < 0.10
    )
  }))
}

calculate_weighted_balance_table <- function(data, treatment_col = "treatment", weight_col = "iptw") {
  treatment <- data[[treatment_col]]
  weights <- data[[weight_col]]

  dplyr::bind_rows(lapply(balance_covariates, function(covariate) {
    x <- data[[covariate]]
    tibble::tibble(
      covariate = covariate,
      mean_treated = stats::weighted.mean(x[treatment == "Treated"], weights[treatment == "Treated"], na.rm = TRUE),
      mean_control = stats::weighted.mean(x[treatment == "Control"], weights[treatment == "Control"], na.rm = TRUE),
      smd = standardized_mean_difference(x, treatment, weights),
      abs_smd = abs(smd),
      balanced = abs_smd < 0.10
    )
  }))
}
