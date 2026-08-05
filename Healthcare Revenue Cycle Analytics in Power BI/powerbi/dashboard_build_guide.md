# Power BI Dashboard Build Guide

This guide assumes Power BI Desktop is installed.

## Step 1: Load Data

1. Open Power BI Desktop.
2. Choose `Get Data -> Text/CSV`.
3. Load each file in `data/`.
4. In Power Query, apply the type cleanup in `power_query_steps.md`.
5. Close and apply.

## Step 2: Build Relationships

Open Model view and create the relationships in `data_model.md`.

Check that:

- Dimension tables filter fact tables.
- Cross-filter direction is Single.
- `dim_date` is marked as the date table.
- Raw ID fields are hidden from report view after relationships are created.

## Step 3: Create Measures

1. Home -> Enter Data.
2. Create one row with a column named `Measure Placeholder`.
3. Name the table `Measures`.
4. Hide `Measure Placeholder`.
5. Copy DAX from `dax_measures.md`.
6. Set measure formats.

## Step 4: Executive Overview Layout

Set page size:

```text
Canvas settings -> Type: 16:9
```

Recommended layout:

```text
Header
KPI KPI KPI KPI KPI
Denial by Payer | Revenue Trend | AR Aging by Payer
Denial Root Cause | Department Performance
```

Use a restrained business palette:

```text
Dark header: #12212F
Good: #0F766E
Warning: #F97316
Risk: #BE123C
Blue accent: #2563EB
Text: #334155
Background: #F7FAFC
Border: #D8E1EA
```

## Step 5: KPI Cards

Create cards for:

- `Net Revenue`
- `Collection Rate`
- `Denial Rate`
- `Days in AR`
- `AR Over 90 Days %`

Formatting:

- White card background
- Light gray border
- Title 11-13 px
- Value 28-36 px
- Consistent card spacing

## Step 6: Denial by Payer

Visual: Clustered bar chart

- Y-axis: `dim_payer[payer_name]`
- X-axis: `Denial Rate`
- Sort descending by `Denial Rate`
- Data labels on
- Conditional color:
  - High: red
  - Watch: orange
  - Healthy: teal

## Step 7: Revenue and Denials Trend

Visual: Line chart

- X-axis: `dim_date[year_month]`
- Y-axis: `Net Revenue`
- Secondary or additional line: `Denied Amount`
- Use `dim_date[month_number]` to sort `year_month`

## Step 8: AR Aging by Payer

Visual: Matrix or bar chart

- Rows: `dim_payer[payer_name]`
- Values: `AR Over 90 Days`, `AR Over 90 Days %`, `AR Risk Band`
- Sort descending by `AR Over 90 Days`

## Step 9: Denial Root Cause Mix

Visual: Horizontal bar chart

- Y-axis: `dim_denial_reason[denial_category]`
- X-axis: `Denied Amount`
- Color by `preventable_flag` or `denial_category`

## Step 10: Department Performance

Visual: Matrix

- Rows: `dim_department[department_name]`
- Values:
  - `Net Revenue`
  - `Denial Rate`
  - `Clean Claim Rate`
  - `Average Reimbursement Lag`

Use conditional formatting on `Denial Rate` and `Average Reimbursement Lag`.

## Step 11: Drillthrough

Create a page named `Claim Detail`.

Add drillthrough fields:

- `dim_payer[payer_name]`
- `dim_department[department_name]`
- `dim_provider[provider_name]`
- `dim_denial_reason[denial_category]`

Add a claim-level table using fields from `dashboard_spec.md`.

## Step 12: Publish

1. Save the file as `healthcare_revenue_cycle_analytics.pbix`.
2. Publish to Power BI Service if available.
3. If no public report link is available, export a screenshot for the portfolio.
4. Paste the published URL into `powerbi/powerbi_service_link.txt`.
