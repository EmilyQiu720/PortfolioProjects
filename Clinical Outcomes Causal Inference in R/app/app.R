library(shiny)
library(dplyr)
library(ggplot2)
library(broom)
library(survival)
library(MatchIt)

source("../R/01_generate_data.R")
source("../R/02_clean_data.R")
source("../R/03_balance_checks.R")
source("../R/04_propensity_score.R")
source("../R/05_survival_analysis.R")
source("../R/06_outcome_models.R")
source("../R/07_visualizations.R")

raw_data <- load_or_generate_clinical_data("../data/synthetic_clinical_outcomes.csv")
clinical_data <- clean_clinical_outcomes(raw_data)
propensity_model <- fit_propensity_model(clinical_data)
scored_data <- add_propensity_scores(clinical_data, propensity_model)
matched_data <- create_matched_cohort(scored_data)
weighted_data <- create_iptw_cohort(scored_data)

ui <- fluidPage(
  titlePanel("Clinical Outcomes Causal Inference"),
  sidebarLayout(
    sidebarPanel(
      selectInput("site", "Hospital site", choices = c("All", levels(clinical_data$hospital_site))),
      selectInput("severity", "Severity band", choices = c("All", unique(clinical_data$severity_band))),
      checkboxInput("treated_only", "Show treated patients only", value = FALSE)
    ),
    mainPanel(
      tabsetPanel(
        tabPanel("Cohort", tableOutput("cohort_summary")),
        tabPanel("Balance", plotOutput("balance_plot", height = "460px")),
        tabPanel("Propensity", plotOutput("propensity_plot", height = "420px")),
        tabPanel("Survival", plotOutput("survival_plot", height = "420px")),
        tabPanel("Model Results", tableOutput("model_results"))
      )
    )
  )
)

server <- function(input, output, session) {
  filtered_data <- reactive({
    data <- scored_data

    if (input$site != "All") {
      data <- dplyr::filter(data, hospital_site == input$site)
    }
    if (input$severity != "All") {
      data <- dplyr::filter(data, severity_band == input$severity)
    }
    if (input$treated_only) {
      data <- dplyr::filter(data, treatment == "Treated")
    }

    data
  })

  output$cohort_summary <- renderTable({
    filtered_data() |>
      group_by(treatment) |>
      summarise(
        patients = n(),
        mean_age = round(mean(age), 1),
        mean_severity = round(mean(baseline_severity), 1),
        readmission_rate = round(mean(readmitted_30d), 3),
        event_rate = round(mean(event_observed), 3),
        .groups = "drop"
      )
  })

  output$balance_plot <- renderPlot({
    plot_balance_comparison(
      calculate_balance_table(scored_data, "treatment"),
      calculate_balance_table(matched_data, "treatment"),
      calculate_weighted_balance_table(weighted_data, "treatment", "iptw")
    )
  })

  output$propensity_plot <- renderPlot({
    plot_propensity_overlap(scored_data)
  })

  output$survival_plot <- renderPlot({
    plot_kaplan_meier(clinical_data)
  })

  output$model_results <- renderTable({
    models <- fit_outcome_models(clinical_data, matched_data, weighted_data)
    tidy_outcome_results(models) |>
      mutate(
        estimate = round(estimate, 3),
        conf.low = round(conf.low, 3),
        conf.high = round(conf.high, 3),
        p.value = round(p.value, 4)
      )
  })
}

shinyApp(ui, server)
