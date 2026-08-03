# Data Dictionary

## assumptions.csv

| Column | Description |
|---|---|
| `Scenario` | Base, Upside, or Downside case. |
| `Starting_Cash` | Cash balance at forecast start. |
| `Starting_Customers` | Customer count at forecast start. |
| `Starting_ARPA` | Starting average revenue per account. |
| `Monthly_New_Customers` | New customers acquired each month. |
| `Monthly_Churn` | Monthly logo churn rate. |
| `Monthly_Expansion` | Monthly expansion rate used for NRR. |
| `ARPA_Growth` | Monthly ARPA growth assumption. |
| `Gross_Margin` | Gross margin percentage. |
| `CAC_Per_Customer` | Customer acquisition cost per new customer. |
| `Base_Payroll_Per_FTE` | Average monthly fully loaded payroll cost per FTE. |
| `NonPayroll_Opex` | Monthly non-payroll operating expense. |
| `Sales_Marketing_Budget` | Monthly sales and marketing spend. |

## historical_actuals.csv

Historical operating actuals used to set context for the forecast.

## hiring_plan.csv

Monthly headcount plan by function. The workbook uses this table to calculate payroll and total headcount.
