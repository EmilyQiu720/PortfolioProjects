# PortfolioProjects

This repository contains selected portfolio projects across machine learning, optimization, databases, analytics, and agent engineering.

## Featured Project

### Retail Supply Chain Control Tower in Tableau

[`Retail Supply Chain Control Tower in Tableau`](./Retail%20Supply%20Chain%20Control%20Tower%20in%20Tableau) is a Tableau-ready BI project for monitoring fulfillment SLA, warehouse bottlenecks, inventory stockout risk, return rates, and SKU profitability.

The project includes:

- Tableau-ready CSV datasets for orders, shipments, inventory, returns, and warehouse targets
- Validated relationship model for order-to-shipment, order-to-return, warehouse target, and SKU inventory analysis
- Calculated fields for revenue, gross margin, on-time delivery rate, return rate, fill rate, inventory days remaining, stockout risk score, and SLA gap
- LOD-style Tableau calculations for warehouse-level and SKU-level performance
- Parameter-driven metric selector and SLA threshold
- Dashboard specification for Executive Overview, Fulfillment Performance, Inventory Risk, Returns & Profitability, and Drilldown pages
- Step-by-step Tableau Public build guide and dashboard mockup

This project demonstrates senior Tableau and BI skills: data modeling, KPI design, calculated fields, operational dashboard storytelling, drilldown workflows, and performance-aware dashboard planning.

### Healthcare Revenue Cycle Analytics in Power BI

[`Healthcare Revenue Cycle Analytics in Power BI`](./Healthcare%20Revenue%20Cycle%20Analytics%20in%20Power%20BI) is a Power BI-ready semantic modeling project for healthcare finance, denial management, accounts receivable aging, payer performance, and department-level revenue cycle operations.

The project includes:

- Synthetic star-schema datasets for claims, payments, denials, AR snapshots, and conformed dimensions
- Power BI relationship model with claims as the central operational grain
- DAX measure layer for net revenue, collection rate, denial rate, clean claim rate, days in AR, AR over 90 days, reimbursement lag, write-off rate, and payer mix
- Power Query cleanup guidance and data type mapping
- Row-level security design for regional finance and department manager access
- Dashboard specification for executive overview, denials root cause, AR aging, provider performance, and claim drillthrough pages
- Python validation checks for keys, relationships, money fields, denial rate, and payment activity

This project demonstrates senior Power BI skills: star schema design, semantic modeling, DAX, time intelligence, RLS, drillthrough design, healthcare revenue cycle analytics, and governed dashboard delivery.

### Production ML Risk Scoring API

[`Production ML Risk Scoring API`](./Production%20ML%20Risk%20Scoring%20API) is a production-style machine learning backend for real-time transaction risk scoring, batch scoring, prediction logging, model registry metadata, and drift monitoring.

The project includes:

- FastAPI service with `/health`, `/v1/score`, `/v1/batch-score`, and `/v1/prediction-summary` endpoints
- Pydantic request/response schemas for strict feature contract enforcement
- Deterministic model artifact loaded from a versioned model registry
- Shared feature transformation layer for online scoring, batch scoring, and tests
- Decision policy for approve, manual review, and decline routing
- SQLite prediction log with masked customer identifiers for auditability
- Batch scoring CLI and sample scoring input
- Drift monitoring utilities using Population Stability Index
- Docker, Docker Compose, environment configuration, docs, and unit tests

This project demonstrates senior MLE/backend skills: model serving, API design, schema validation, prediction logging, model versioning, batch inference, drift monitoring, auth, Docker packaging, and testable service architecture.

### FP&A Scenario Planning Model in Excel

[`FP&A Scenario Planning Model in Excel`](./FP%26A%20Scenario%20Planning%20Model%20in%20Excel) is an executive-ready SaaS financial planning workbook for revenue forecasting, scenario planning, cash runway, sensitivity analysis, and FP&A dashboard reporting.

The project includes:

- 24-month SaaS revenue forecast driven by customers, ARPA, churn, expansion, and new logos
- Base, Upside, and Downside scenario selector with active assumption lookup
- Hiring plan integration for headcount and payroll forecasting
- Expense forecast, cash flow roll-forward, burn rate, and runway calculation
- Sensitivity analysis for growth and churn assumptions
- Executive dashboard with KPI cards and native Excel charts
- Validation checks for scenario selection, assumption completeness, customer roll-forward, cash roll-forward, and negative cash flags
- Reproducible workbook generation from CSV inputs using a JavaScript builder

This project demonstrates senior Excel and FP&A skills: auditable model structure, formula-driven forecasting, scenario controls, financial dashboard design, validation checks, and reproducible spreadsheet automation.

### Clinical Outcomes Causal Inference in R

[`Clinical Outcomes Causal Inference in R`](./Clinical%20Outcomes%20Causal%20Inference%20in%20R) is a reproducible R analytics project for estimating treatment effects from non-randomized clinical outcome data.

The project includes:

- Synthetic clinical cohort generation with documented confounding structure
- Data cleaning, validation, factor encoding, and derived clinical risk features
- Baseline covariate balance diagnostics using standardized mean differences
- Propensity score modeling, nearest-neighbor matching, and inverse probability weighting
- Logistic regression outcome models for 30-day readmission
- Cox proportional hazards models and Kaplan-Meier survival analysis
- Quarto report for statistical communication
- Shiny dashboard for stakeholder exploration
- `targets` pipeline, `renv` dependency pattern, and `testthat` tests

This project demonstrates senior R skills in statistical modeling, causal inference, survival analysis, reproducible research workflows, and production-quality analytical project structure.

### Payment Fraud SQL Intelligence Platform

[`Payment Fraud SQL Intelligence Platform`](./Payment%20Fraud%20SQL%20Intelligence%20Platform) is a production-style PostgreSQL project for fraud monitoring, merchant risk analytics, chargeback investigation, data quality, governance, and query performance optimization.

The project includes:

- Normalized payment fraud schema covering customers, accounts, merchants, payment methods, devices, transactions, events, fraud alerts, manual reviews, chargebacks, and audit logs
- PostgreSQL constraints, indexes, materialized views, masked analyst views, audit triggers, and role-based access examples
- Fraud detection SQL for payment method velocity, device fan-out, country mismatch, high-risk transaction scoring, and review queue prioritization
- Merchant risk, customer behavior, chargeback, and operations dashboard queries using CTEs, window functions, filtered aggregates, and ranking
- Data quality tests for duplicate records, inconsistent relationships, invalid amounts, event ordering, and unresolved alerts
- Transaction integrity tests for review decisions and chargeback workflows
- Performance tuning examples with slow-query and optimized-query versions plus EXPLAIN guidance

This project demonstrates senior SQL skills beyond basic querying: production data modeling, operational analytics, governance, reliability checks, and performance-aware query design.

### Agent Engineering Systems

[`Agent Engineering Systems`](./Agent%20Engineering%20Systems) is a ten-project Python suite covering practical agent engineering from first principles through production and research workflows:

- Tool-calling agent loop with validation, retries, logging, and permission controls
- Stateful research agent with context engineering, memory, evidence, and checkpoint resume
- Workflow orchestration with router, planner-executor, supervisor-worker, handoff, and approval gates
- Industrial MCP-style server with tools, resources, prompts, schema validation, RBAC scopes, audit logs, and two-phase write approval
- Agent evaluation harness with golden datasets, trajectory metrics, system metrics, and regression gates
- Production observability runtime with gateway, queue, stores, tracing, retries, fallbacks, circuit breakers, bulkheads, and cost-per-success metrics
- Security guardrail layer for prompt injection, sandboxing, tenant isolation, SQL/shell/network allowlists, DLP, and kill switch behavior
- Advanced architecture lab for hierarchical planning, dependency graphs, critical path analysis, verifier-guided replanning, long-task checkpoints, and multi-agent coordination
- Training and reinforcement learning lab for trajectory collection, tool-call SFT data, negative examples, reward shaping, offline RL, and deterministic replay
- Research benchmark lab for ablations, confidence intervals, contamination checks, token budget control, and scaffold-vs-model gain analysis

Each module is self-contained, documented, and runnable through `--self-test`.
