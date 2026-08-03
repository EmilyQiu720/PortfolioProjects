plot_balance_comparison <- function(unadjusted, matched, weighted) {
  plot_data <- dplyr::bind_rows(
    dplyr::mutate(unadjusted, adjustment = "Unadjusted"),
    dplyr::mutate(matched, adjustment = "Matched"),
    dplyr::mutate(weighted, adjustment = "IPTW")
  )

  ggplot2::ggplot(plot_data, ggplot2::aes(x = abs_smd, y = covariate, fill = adjustment)) +
    ggplot2::geom_col(position = "dodge") +
    ggplot2::geom_vline(xintercept = 0.10, linetype = "dashed", color = "red") +
    ggplot2::labs(
      title = "Covariate Balance Before and After Adjustment",
      x = "Absolute standardized mean difference",
      y = NULL,
      fill = "Adjustment"
    ) +
    ggplot2::theme_minimal()
}

plot_kaplan_meier <- function(data) {
  fit <- survival::survfit(
    survival::Surv(follow_up_days, event_observed) ~ treatment,
    data = data
  )

  survival_summary <- summary(fit)
  plot_data <- tibble::tibble(
    time = survival_summary$time,
    survival = survival_summary$surv,
    strata = sub("treatment=", "", survival_summary$strata)
  )

  ggplot2::ggplot(plot_data, ggplot2::aes(x = time, y = survival, color = strata)) +
    ggplot2::geom_step(linewidth = 1) +
    ggplot2::labs(
      title = "Kaplan-Meier Event-Free Survival",
      x = "Follow-up days",
      y = "Event-free survival probability",
      color = "Group"
    ) +
    ggplot2::theme_minimal()
}

plot_propensity_overlap <- function(data) {
  ggplot2::ggplot(data, ggplot2::aes(x = propensity_score, fill = treatment)) +
    ggplot2::geom_density(alpha = 0.45) +
    ggplot2::labs(
      title = "Propensity Score Overlap",
      x = "Estimated propensity score",
      y = "Density",
      fill = "Group"
    ) +
    ggplot2::theme_minimal()
}
