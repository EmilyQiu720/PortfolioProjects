"""Validate the generated Power BI revenue cycle star schema."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    path = DATA_DIR / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def assert_unique(rows: list[dict[str, str]], key: str, table: str) -> None:
    counts = Counter(row[key] for row in rows)
    duplicates = [value for value, count in counts.items() if count > 1]
    if duplicates:
        raise AssertionError(f"{table}.{key} has duplicates: {duplicates[:5]}")


def assert_fk(child_rows: list[dict[str, str]], child_key: str, parent_rows: list[dict[str, str]], parent_key: str, relationship: str) -> None:
    parent_values = {row[parent_key] for row in parent_rows}
    missing = sorted({row[child_key] for row in child_rows if row[child_key] not in parent_values})
    if missing:
        raise AssertionError(f"{relationship} has missing keys: {missing[:10]}")


def assert_nonnegative_money(rows: list[dict[str, str]], columns: list[str], table: str) -> None:
    for row in rows:
        for column in columns:
            if float(row[column]) < 0:
                raise AssertionError(f"{table}.{column} has negative value in row {row}")


def main() -> None:
    claims = read_csv("fact_claims.csv")
    payments = read_csv("fact_payments.csv")
    denials = read_csv("fact_denials.csv")
    ar_snapshot = read_csv("fact_ar_snapshot.csv")
    departments = read_csv("dim_department.csv")
    providers = read_csv("dim_provider.csv")
    payers = read_csv("dim_payer.csv")
    procedures = read_csv("dim_procedure.csv")
    denial_reasons = read_csv("dim_denial_reason.csv")
    patients = read_csv("dim_patient_masked.csv")
    dates = read_csv("dim_date.csv")

    for table, rows, key in [
        ("fact_claims", claims, "claim_id"),
        ("fact_payments", payments, "payment_id"),
        ("fact_denials", denials, "denial_id"),
        ("dim_department", departments, "department_id"),
        ("dim_provider", providers, "provider_id"),
        ("dim_payer", payers, "payer_id"),
        ("dim_procedure", procedures, "procedure_id"),
        ("dim_denial_reason", denial_reasons, "denial_reason_id"),
        ("dim_patient_masked", patients, "patient_id"),
        ("dim_date", dates, "date"),
    ]:
        assert_unique(rows, key, table)

    assert_fk(claims, "department_id", departments, "department_id", "claims -> departments")
    assert_fk(claims, "provider_id", providers, "provider_id", "claims -> providers")
    assert_fk(claims, "payer_id", payers, "payer_id", "claims -> payers")
    assert_fk(claims, "procedure_id", procedures, "procedure_id", "claims -> procedures")
    assert_fk(claims, "patient_id", patients, "patient_id", "claims -> patients")
    assert_fk(claims, "service_date", dates, "date", "claims service date -> date")
    assert_fk(payments, "claim_id", claims, "claim_id", "payments -> claims")
    assert_fk(denials, "claim_id", claims, "claim_id", "denials -> claims")
    assert_fk(denials, "denial_reason_id", denial_reasons, "denial_reason_id", "denials -> denial reasons")
    assert_fk(ar_snapshot, "claim_id", claims, "claim_id", "ar snapshot -> claims")
    assert_fk(ar_snapshot, "payer_id", payers, "payer_id", "ar snapshot -> payers")
    assert_fk(ar_snapshot, "department_id", departments, "department_id", "ar snapshot -> departments")

    assert_nonnegative_money(claims, ["gross_charge", "allowed_amount", "expected_patient_responsibility"], "fact_claims")
    assert_nonnegative_money(payments, ["payer_payment", "patient_payment", "contractual_adjustment", "writeoff_amount"], "fact_payments")
    assert_nonnegative_money(denials, ["denial_amount", "recovered_amount"], "fact_denials")
    assert_nonnegative_money(ar_snapshot, ["ar_balance"], "fact_ar_snapshot")

    denial_rate = len(denials) / len(claims)
    paid_claims = {row["claim_id"] for row in payments}
    if not 0.08 <= denial_rate <= 0.20:
        raise AssertionError(f"Unexpected denial rate: {denial_rate:.2%}")
    if len(paid_claims) < len(claims) * 0.60:
        raise AssertionError("Too few claims have payment activity.")

    print("Validation passed.")
    print(f"Claims: {len(claims):,}")
    print(f"Payments: {len(payments):,}")
    print(f"Denials: {len(denials):,} ({denial_rate:.1%})")
    print(f"AR snapshot rows: {len(ar_snapshot):,}")


if __name__ == "__main__":
    main()
