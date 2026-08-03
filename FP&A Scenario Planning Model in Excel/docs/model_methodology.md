# Model Methodology

## Model Horizon

The workbook forecasts 24 monthly periods from January 2026 through December 2027.

## Revenue Logic

Monthly recurring revenue is driven by customer count and ARPA.

```text
Ending Customers = Beginning Customers + New Customers - Churned Customers
ARPA = Prior Month ARPA * (1 + ARPA Growth)
MRR = Ending Customers * ARPA
ARR = MRR * 12
NRR = 1 - Monthly Churn + Monthly Expansion
```

## Expense Logic

Payroll is based on headcount from the hiring plan and average payroll cost per FTE. Non-payroll opex and sales and marketing spend come from scenario assumptions.

```text
Total Headcount = Engineering + Sales + Customer Success + G&A
Payroll = Total Headcount * Base Payroll per FTE
Total Opex = Payroll + NonPayroll Opex + Sales & Marketing
```

## Cash Flow Logic

```text
Gross Profit = MRR * Gross Margin
Net Burn = Total Opex - Gross Profit
Ending Cash = Beginning Cash - Net Burn
Runway = Ending Cash / Net Burn
```

If burn is negative, runway is shown as blank because the company is cash-flow positive in that period.

## Sensitivity Analysis

The sensitivity table flexes monthly new customers and churn around the active scenario to estimate ending runway under different operating outcomes.

## Controls

The `Validation Checks` tab flags:

- invalid scenario selection
- missing assumptions
- customer roll-forward inconsistencies
- cash roll-forward inconsistencies
- negative ending cash

## Modeling Philosophy

The workbook separates inputs, calculations, outputs, and controls. Hardcoded assumptions live in source tabs, while forecast tabs are formula-driven and auditable.
