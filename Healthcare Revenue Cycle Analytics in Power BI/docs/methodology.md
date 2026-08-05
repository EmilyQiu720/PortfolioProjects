# Methodology

## Synthetic Data Design

The dataset simulates a one-year healthcare revenue cycle operation. It is synthetic and contains no real patient information.

The generator creates:

- Claims across departments, providers, payers, procedures, and masked patients
- Payments with payer payments, patient payments, contractual adjustments, write-offs, and payment lag
- Denials with denial reason, preventability, appeal status, and recovered amount
- Month-end accounts receivable balances with aging buckets

## Business Logic

Denial probability is influenced by:

- Payer-specific denial tendency
- Department workflow pressure
- Procedure complexity

Payment lag is influenced by:

- Payer-specific lag profile
- Claim status
- Denial and write-off behavior

AR balances represent claims that are unpaid, partially paid, denied, or still aging at the December 31 snapshot.

## Portfolio Intent

The project is intentionally modeled for Power BI semantic modeling:

- Claims act as the central operational grain.
- Payments and denials are related child fact tables.
- AR snapshot supports aging analysis.
- Dimensions are conformed across pages.
- DAX measures define business logic rather than relying on implicit aggregation.

## Validation

Run:

```powershell
python "Healthcare Revenue Cycle Analytics in Power BI\scripts\validate_model.py"
```

The validation script checks:

- Primary key uniqueness
- Foreign key integrity
- Nonnegative money values
- Reasonable denial rate range
- Sufficient payment activity

## Limitations

This is a portfolio-grade synthetic dataset, not a regulatory or operational healthcare data product. It is designed to demonstrate BI modeling, DAX, dashboard design, governance thinking, and revenue cycle domain fluency.
