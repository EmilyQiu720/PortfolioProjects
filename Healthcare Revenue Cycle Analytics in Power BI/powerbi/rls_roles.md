# Row-Level Security Roles

This project includes RLS design documentation because enterprise Power BI projects often need governed access, not just visuals.

## Role: East Finance

Table: `dim_department`

```DAX
[region] = "East"
```

## Role: Central Finance

Table: `dim_department`

```DAX
[region] = "Central"
```

## Role: West Finance

Table: `dim_department`

```DAX
[region] = "West"
```

## Role: Department Manager Template

Use a security mapping table in production. For this portfolio dataset, a static example is:

Table: `dim_department`

```DAX
[department_name] IN { "Emergency Medicine", "Cardiology" }
```

## Production Pattern

For real deployment, create a table named `security_user_department`:

```text
user_principal_name
department_id
```

Then relate `security_user_department[department_id]` to `dim_department[department_id]` and use:

```DAX
[user_principal_name] = USERPRINCIPALNAME()
```

## RLS Testing Checklist

- View as East Finance and confirm only East departments appear.
- Confirm payer totals update under regional filters.
- Confirm hidden key columns do not leak patient identity.
- Confirm `dim_patient_masked` contains no direct PII.
- Confirm drillthrough pages respect RLS.
