# DAX Measures

Create a blank table named `Measures`, then add these measures.

## Revenue Measures

```DAX
Gross Charges =
SUM ( fact_claims[gross_charge] )
```

```DAX
Allowed Amount =
SUM ( fact_claims[allowed_amount] )
```

```DAX
Payer Payments =
SUM ( fact_payments[payer_payment] )
```

```DAX
Patient Payments =
SUM ( fact_payments[patient_payment] )
```

```DAX
Total Payments =
[Payer Payments] + [Patient Payments]
```

```DAX
Contractual Adjustments =
SUM ( fact_payments[contractual_adjustment] )
```

```DAX
Write-Off Amount =
SUM ( fact_payments[writeoff_amount] )
```

```DAX
Net Revenue =
[Total Payments] - [Write-Off Amount]
```

```DAX
Collection Rate =
DIVIDE ( [Total Payments], [Allowed Amount] )
```

```DAX
Write-Off Rate =
DIVIDE ( [Write-Off Amount], [Allowed Amount] )
```

## Claim and Denial Measures

```DAX
Claim Count =
DISTINCTCOUNT ( fact_claims[claim_id] )
```

```DAX
Paid Claim Count =
CALCULATE (
    [Claim Count],
    fact_claims[claim_status] = "Paid"
)
```

```DAX
Denied Claim Count =
DISTINCTCOUNT ( fact_denials[claim_id] )
```

```DAX
Denial Rate =
DIVIDE ( [Denied Claim Count], [Claim Count] )
```

```DAX
Denied Amount =
SUM ( fact_denials[denial_amount] )
```

```DAX
Preventable Denied Amount =
CALCULATE (
    [Denied Amount],
    fact_denials[preventable_flag] = 1
)
```

```DAX
Preventable Denial Rate =
DIVIDE ( [Preventable Denied Amount], [Denied Amount] )
```

```DAX
Recovered Denial Amount =
SUM ( fact_denials[recovered_amount] )
```

```DAX
Denial Recovery Rate =
DIVIDE ( [Recovered Denial Amount], [Denied Amount] )
```

```DAX
Clean Claim Rate =
DIVIDE (
    CALCULATE ( [Claim Count], fact_claims[clean_claim_flag] = 1 ),
    [Claim Count]
)
```

```DAX
First Pass Resolution Rate =
1 - [Denial Rate]
```

## AR Aging Measures

```DAX
AR Balance =
SUM ( fact_ar_snapshot[ar_balance] )
```

```DAX
AR Over 90 Days =
CALCULATE (
    [AR Balance],
    fact_ar_snapshot[aging_bucket] IN { "91-120", "120+" }
)
```

```DAX
AR Over 90 Days % =
DIVIDE ( [AR Over 90 Days], [AR Balance] )
```

```DAX
Days in AR =
DIVIDE ( [AR Balance], DIVIDE ( [Net Revenue], 365 ) )
```

```DAX
Average Claim Age =
AVERAGE ( fact_ar_snapshot[age_days] )
```

## Payment Lag Measures

```DAX
Average Reimbursement Lag =
AVERAGE ( fact_payments[payment_lag_days] )
```

```DAX
Claims Paid Within 30 Days =
CALCULATE (
    DISTINCTCOUNT ( fact_payments[claim_id] ),
    fact_payments[payment_lag_days] <= 30
)
```

```DAX
Paid Within 30 Days % =
DIVIDE (
    [Claims Paid Within 30 Days],
    DISTINCTCOUNT ( fact_payments[claim_id] )
)
```

## Payer and Mix Measures

```DAX
Payer Mix % =
DIVIDE (
    [Net Revenue],
    CALCULATE ( [Net Revenue], ALL ( dim_payer[payer_name] ) )
)
```

```DAX
Top Payer Concentration =
VAR TopPayers =
    TOPN ( 3, VALUES ( dim_payer[payer_name] ), [Net Revenue], DESC )
RETURN
    DIVIDE (
        CALCULATE ( [Net Revenue], TopPayers ),
        CALCULATE ( [Net Revenue], ALL ( dim_payer[payer_name] ) )
    )
```

## Time Intelligence

```DAX
Net Revenue Prior Year =
CALCULATE (
    [Net Revenue],
    SAMEPERIODLASTYEAR ( dim_date[date] )
)
```

```DAX
Net Revenue YoY Change =
[Net Revenue] - [Net Revenue Prior Year]
```

```DAX
Net Revenue YoY % =
DIVIDE ( [Net Revenue YoY Change], [Net Revenue Prior Year] )
```

```DAX
Rolling 3M Denial Rate =
CALCULATE (
    [Denial Rate],
    DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -3, MONTH )
)
```

```DAX
Rolling 3M Net Revenue =
CALCULATE (
    [Net Revenue],
    DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -3, MONTH )
)
```

## Dynamic Metric Selector

Create a disconnected table:

```DAX
Metric Selector =
DATATABLE (
    "Metric", STRING,
    {
        { "Net Revenue" },
        { "Collection Rate" },
        { "Denial Rate" },
        { "Days in AR" },
        { "AR Over 90 Days %" }
    }
)
```

Then create:

```DAX
Selected Metric Value =
SWITCH (
    SELECTEDVALUE ( 'Metric Selector'[Metric], "Net Revenue" ),
    "Net Revenue", [Net Revenue],
    "Collection Rate", [Collection Rate],
    "Denial Rate", [Denial Rate],
    "Days in AR", [Days in AR],
    "AR Over 90 Days %", [AR Over 90 Days %]
)
```

## Risk Labels

```DAX
Denial Risk Band =
SWITCH (
    TRUE (),
    [Denial Rate] >= 0.16, "High",
    [Denial Rate] >= 0.11, "Watch",
    "Healthy"
)
```

```DAX
AR Risk Band =
SWITCH (
    TRUE (),
    [AR Over 90 Days %] >= 0.35, "High",
    [AR Over 90 Days %] >= 0.22, "Watch",
    "Healthy"
)
```

## Formatting

Use these formats:

| Measure | Format |
|---|---|
| Money measures | `$#,0;($#,0)` |
| Rates | `0.0%` |
| Days / lag | `0.0` |
| Counts | `#,0` |
