# Dashboard Specification

## Page 1: Executive Overview

Purpose: Give finance and operations leaders a concise view of revenue cycle health.

Recommended visuals:

- KPI cards:
  - Net Revenue
  - Collection Rate
  - Denial Rate
  - Days in AR
  - AR Over 90 Days %
- Line chart:
  - Axis: `dim_date[year_month]`
  - Values: `Net Revenue`, `Denied Amount`
- Bar chart:
  - Axis: `dim_payer[payer_name]`
  - Values: `Denial Rate`
- Matrix:
  - Rows: `dim_department[department_name]`
  - Values: `Net Revenue`, `Denial Rate`, `Clean Claim Rate`, `Average Reimbursement Lag`
- Donut or stacked bar:
  - Legend: `dim_payer[payer_type]`
  - Values: `Net Revenue`

Filters:

- Date range
- Payer type
- Region
- Department

## Page 2: Denials Root Cause

Purpose: Identify preventable denial drivers.

Recommended visuals:

- Denied Amount by Denial Category
- Denial Rate by Payer
- Preventable Denied Amount by Department
- Appeal Status distribution
- Provider denial heatmap
- Claim table filtered to denied claims

Key measures:

- `Denied Amount`
- `Denial Rate`
- `Preventable Denied Amount`
- `Preventable Denial Rate`
- `Recovered Denial Amount`
- `Denial Recovery Rate`

## Page 3: AR Aging

Purpose: Explain where cash is delayed.

Recommended visuals:

- AR Balance by Aging Bucket
- AR Over 90 Days by Payer
- AR Balance by Department
- Average Claim Age by Payer
- High-balance claim table

Key measures:

- `AR Balance`
- `AR Over 90 Days`
- `AR Over 90 Days %`
- `Days in AR`
- `Average Claim Age`

## Page 4: Provider and Department Performance

Purpose: Compare operational performance by owner.

Recommended visuals:

- Net Revenue by Provider
- Denial Rate by Provider
- Clean Claim Rate by Department
- Average Reimbursement Lag by Department
- Scatter plot: Net Revenue vs Denial Rate

Recommended drillthrough:

- Right-click department -> Claim Detail Drillthrough
- Right-click provider -> Claim Detail Drillthrough

## Page 5: Claim Detail Drillthrough

Purpose: Support audit-style claim investigation.

Drillthrough filters:

- `dim_payer[payer_name]`
- `dim_department[department_name]`
- `dim_provider[provider_name]`
- `dim_denial_reason[denial_category]`

Detail table fields:

- Claim ID
- Service Date
- Claim Status
- Payer
- Department
- Provider
- Procedure Group
- Gross Charge
- Allowed Amount
- Total Payments
- Denial Reason
- AR Aging Bucket
- Age Days
