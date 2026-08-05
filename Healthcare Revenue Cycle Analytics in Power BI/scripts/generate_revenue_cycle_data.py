"""Generate a synthetic healthcare revenue cycle dataset for Power BI.

The dataset is intentionally modeled as a star schema rather than a single flat
file. Power BI reviewers can inspect relationships, DAX measures, drillthrough
pages, and row-level security patterns against a realistic revenue cycle model.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
RNG = random.Random(720)


@dataclass(frozen=True)
class Payer:
    payer_id: str
    payer_name: str
    payer_type: str
    base_denial_rate: float
    lag_mean: int


@dataclass(frozen=True)
class Department:
    department_id: str
    department_name: str
    service_line: str
    region: str


@dataclass(frozen=True)
class Provider:
    provider_id: str
    provider_name: str
    department_id: str
    specialty: str


@dataclass(frozen=True)
class Procedure:
    procedure_id: str
    procedure_code: str
    procedure_group: str
    description: str
    base_charge: int
    complexity: str


@dataclass(frozen=True)
class DenialReason:
    denial_reason_id: str
    denial_reason: str
    denial_category: str
    preventable_default: int


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def money(value: float) -> str:
    return f"{value:.2f}"


def weighted_choice(items: list[tuple[object, float]]) -> object:
    total = sum(weight for _, weight in items)
    point = RNG.random() * total
    cumulative = 0.0
    for item, weight in items:
        cumulative += weight
        if point <= cumulative:
            return item
    return items[-1][0]


def build_dimensions() -> dict[str, list[object]]:
    departments = [
        Department("D001", "Emergency Medicine", "Acute Care", "East"),
        Department("D002", "Cardiology", "Specialty Care", "East"),
        Department("D003", "Orthopedics", "Surgical Care", "Central"),
        Department("D004", "Primary Care", "Ambulatory Care", "Central"),
        Department("D005", "Oncology", "Specialty Care", "West"),
        Department("D006", "Radiology", "Diagnostics", "West"),
        Department("D007", "Gastroenterology", "Procedural Care", "Central"),
        Department("D008", "Pediatrics", "Ambulatory Care", "East"),
    ]
    providers = []
    specialties = {
        "D001": "Emergency Physician",
        "D002": "Cardiologist",
        "D003": "Orthopedic Surgeon",
        "D004": "Primary Care Physician",
        "D005": "Oncologist",
        "D006": "Radiologist",
        "D007": "Gastroenterologist",
        "D008": "Pediatrician",
    }
    for index, department in enumerate(departments, start=1):
        for suffix in range(1, 4):
            providers.append(
                Provider(
                    f"P{index:02d}{suffix}",
                    f"{department.department_name.split()[0]} Provider {suffix}",
                    department.department_id,
                    specialties[department.department_id],
                )
            )

    payers = [
        Payer("PY001", "Blue Horizon Health", "Commercial", 0.075, 24),
        Payer("PY002", "United Regional Plan", "Commercial", 0.092, 31),
        Payer("PY003", "Medicare Advantage Plus", "Medicare Advantage", 0.118, 38),
        Payer("PY004", "State Medicaid", "Medicaid", 0.162, 47),
        Payer("PY005", "Aetna Choice", "Commercial", 0.086, 28),
        Payer("PY006", "Self Pay", "Self Pay", 0.210, 62),
    ]
    procedures = [
        Procedure("PR001", "99213", "Evaluation", "Established patient visit", 185, "Low"),
        Procedure("PR002", "99285", "Emergency", "Emergency department high severity", 1450, "High"),
        Procedure("PR003", "93000", "Cardiology", "Electrocardiogram", 240, "Low"),
        Procedure("PR004", "93306", "Cardiology", "Transthoracic echocardiography", 1450, "Medium"),
        Procedure("PR005", "27447", "Orthopedics", "Total knee arthroplasty", 23800, "High"),
        Procedure("PR006", "73721", "Radiology", "MRI lower extremity", 2600, "Medium"),
        Procedure("PR007", "45378", "Gastroenterology", "Diagnostic colonoscopy", 3900, "Medium"),
        Procedure("PR008", "96413", "Oncology", "Chemotherapy infusion", 6800, "High"),
        Procedure("PR009", "71046", "Radiology", "Chest x-ray", 310, "Low"),
        Procedure("PR010", "99392", "Pediatrics", "Preventive medicine visit", 210, "Low"),
    ]
    denial_reasons = [
        DenialReason("DR001", "Missing prior authorization", "Authorization", 1),
        DenialReason("DR002", "Eligibility inactive", "Eligibility", 1),
        DenialReason("DR003", "Medical necessity not supported", "Clinical Documentation", 1),
        DenialReason("DR004", "Coding mismatch", "Coding", 1),
        DenialReason("DR005", "Duplicate claim", "Billing Process", 1),
        DenialReason("DR006", "Coordination of benefits", "Payer Policy", 0),
        DenialReason("DR007", "Timely filing exceeded", "Billing Process", 1),
        DenialReason("DR008", "Bundled service", "Payer Policy", 0),
    ]
    return {
        "departments": departments,
        "providers": providers,
        "payers": payers,
        "procedures": procedures,
        "denial_reasons": denial_reasons,
    }


def build_date_dimension(start: date, end: date) -> list[dict[str, object]]:
    rows = []
    current = start
    while current <= end:
        quarter = (current.month - 1) // 3 + 1
        rows.append(
            {
                "date": current.isoformat(),
                "year": current.year,
                "month_number": current.month,
                "month_name": current.strftime("%b"),
                "year_month": current.strftime("%Y-%m"),
                "quarter": f"Q{quarter}",
                "week_start_date": (current - timedelta(days=current.weekday())).isoformat(),
                "day_of_week": current.strftime("%A"),
                "is_weekend": int(current.weekday() >= 5),
            }
        )
        current += timedelta(days=1)
    return rows


def build_patients(count: int = 2400) -> list[dict[str, object]]:
    rows = []
    age_bands = [("0-17", 0.12), ("18-34", 0.18), ("35-49", 0.22), ("50-64", 0.25), ("65+", 0.23)]
    risk_bands = [("Low", 0.42), ("Medium", 0.38), ("High", 0.20)]
    for index in range(1, count + 1):
        rows.append(
            {
                "patient_id": f"PT{index:06d}",
                "patient_segment": weighted_choice([("Commercial", 0.48), ("Medicare", 0.24), ("Medicaid", 0.18), ("Self Pay", 0.10)]),
                "age_band": weighted_choice(age_bands),
                "risk_band": weighted_choice(risk_bands),
                "zip3": f"{RNG.choice([100, 112, 191, 303, 606, 770, 802, 900, 981])}",
            }
        )
    return rows


def generate_facts(dimensions: dict[str, list[object]], patients: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    departments: list[Department] = dimensions["departments"]  # type: ignore[assignment]
    providers: list[Provider] = dimensions["providers"]  # type: ignore[assignment]
    payers: list[Payer] = dimensions["payers"]  # type: ignore[assignment]
    procedures: list[Procedure] = dimensions["procedures"]  # type: ignore[assignment]
    denial_reasons: list[DenialReason] = dimensions["denial_reasons"]  # type: ignore[assignment]

    providers_by_department = {}
    for provider in providers:
        providers_by_department.setdefault(provider.department_id, []).append(provider)

    claims = []
    payments = []
    denials = []
    start = date(2025, 1, 1)
    for index in range(1, 9001):
        claim_id = f"CLM{index:07d}"
        service_date = start + timedelta(days=RNG.randrange(0, 365))
        department = weighted_choice([(dept, 1.0) for dept in departments])
        assert isinstance(department, Department)
        provider = RNG.choice(providers_by_department[department.department_id])
        payer = weighted_choice([(p, 1.0) for p in payers])
        assert isinstance(payer, Payer)
        procedure = weighted_choice(
            [
                (procedures[0], 1.8),
                (procedures[1], 0.9),
                (procedures[2], 0.8),
                (procedures[3], 0.7),
                (procedures[4], 0.25),
                (procedures[5], 0.8),
                (procedures[6], 0.55),
                (procedures[7], 0.35),
                (procedures[8], 1.2),
                (procedures[9], 0.8),
            ]
        )
        assert isinstance(procedure, Procedure)
        patient = RNG.choice(patients)
        submit_delay = RNG.randint(1, 10)
        claim_submit_date = service_date + timedelta(days=submit_delay)
        complexity_multiplier = {"Low": 0.18, "Medium": 0.35, "High": 0.62}[procedure.complexity]
        gross_charge = procedure.base_charge * RNG.uniform(0.82, 1.28)
        payer_factor = {
            "Commercial": 0.58,
            "Medicare Advantage": 0.45,
            "Medicaid": 0.38,
            "Self Pay": 0.24,
        }[payer.payer_type]
        allowed_amount = gross_charge * RNG.uniform(payer_factor - 0.05, payer_factor + 0.07)
        patient_responsibility = allowed_amount * RNG.uniform(0.05, 0.22)
        preventable_pressure = 0.025 if department.department_name in {"Emergency Medicine", "Gastroenterology"} else 0.0
        high_complexity_pressure = complexity_multiplier * 0.05
        denial_probability = min(0.42, payer.base_denial_rate + preventable_pressure + high_complexity_pressure)
        denied = RNG.random() < denial_probability
        in_ar = (not denied) and RNG.random() < (0.08 + payer.lag_mean / 700)
        written_off = denied and RNG.random() < 0.16
        paid = not denied and not in_ar
        status = "Paid" if paid else "Denied" if denied and not written_off else "Written Off" if written_off else "In AR"
        clean_claim = int(not denied and submit_delay <= 5)

        claims.append(
            {
                "claim_id": claim_id,
                "patient_id": patient["patient_id"],
                "provider_id": provider.provider_id,
                "department_id": department.department_id,
                "payer_id": payer.payer_id,
                "procedure_id": procedure.procedure_id,
                "service_date": service_date.isoformat(),
                "claim_submit_date": claim_submit_date.isoformat(),
                "claim_status": status,
                "claim_type": weighted_choice([("Professional", 0.68), ("Facility", 0.32)]),
                "gross_charge": money(gross_charge),
                "allowed_amount": money(allowed_amount),
                "expected_patient_responsibility": money(patient_responsibility),
                "clean_claim_flag": clean_claim,
                "length_of_stay": RNG.choice([0, 0, 0, 1, 1, 2, 3, 5]) if procedure.complexity != "Low" else 0,
            }
        )

        if paid or written_off or (denied and RNG.random() < 0.45):
            lag_days = max(4, int(RNG.gauss(payer.lag_mean, 11)))
            payment_date = claim_submit_date + timedelta(days=lag_days)
            collection_factor = 0.0 if written_off else RNG.uniform(0.74, 1.02) if not denied else RNG.uniform(0.08, 0.45)
            payer_payment = max(0, allowed_amount * collection_factor - patient_responsibility * RNG.uniform(0.35, 0.65))
            patient_payment = max(0, patient_responsibility * RNG.uniform(0.35, 0.92))
            writeoff = allowed_amount * RNG.uniform(0.55, 0.95) if written_off else allowed_amount * RNG.uniform(0.0, 0.04)
            payments.append(
                {
                    "payment_id": f"PAY{len(payments) + 1:07d}",
                    "claim_id": claim_id,
                    "payment_date": payment_date.isoformat(),
                    "payer_payment": money(payer_payment),
                    "patient_payment": money(patient_payment),
                    "contractual_adjustment": money(max(0, gross_charge - allowed_amount)),
                    "writeoff_amount": money(writeoff),
                    "payment_lag_days": (payment_date - claim_submit_date).days,
                }
            )

        if denied:
            reason = weighted_choice([(r, 1.0 if r.preventable_default else 0.55) for r in denial_reasons])
            assert isinstance(reason, DenialReason)
            denial_date = claim_submit_date + timedelta(days=RNG.randint(8, 42))
            appealed = RNG.random() < 0.55
            recovered_amount = allowed_amount * RNG.uniform(0.15, 0.75) if appealed and RNG.random() < 0.44 else 0
            denials.append(
                {
                    "denial_id": f"DEN{len(denials) + 1:07d}",
                    "claim_id": claim_id,
                    "denial_date": denial_date.isoformat(),
                    "denial_reason_id": reason.denial_reason_id,
                    "denial_amount": money(allowed_amount),
                    "preventable_flag": reason.preventable_default,
                    "appeal_status": weighted_choice([("Not Appealed", 0.35), ("Appeal Pending", 0.24), ("Appeal Won", 0.21), ("Appeal Lost", 0.20)]),
                    "recovered_amount": money(recovered_amount),
                }
            )

    paid_claim_ids = {row["claim_id"] for row in payments}
    ar_rows = []
    snapshot_date = date(2025, 12, 31)
    for claim in claims:
        if claim["claim_id"] in paid_claim_ids and RNG.random() > 0.05:
            continue
        service_dt = date.fromisoformat(str(claim["service_date"]))
        age_days = (snapshot_date - service_dt).days
        allowed = float(claim["allowed_amount"])
        balance_factor = RNG.uniform(0.35, 1.0) if claim["claim_status"] != "Written Off" else RNG.uniform(0.05, 0.20)
        if age_days <= 30:
            bucket = "0-30"
        elif age_days <= 60:
            bucket = "31-60"
        elif age_days <= 90:
            bucket = "61-90"
        elif age_days <= 120:
            bucket = "91-120"
        else:
            bucket = "120+"
        ar_rows.append(
            {
                "snapshot_date": snapshot_date.isoformat(),
                "claim_id": claim["claim_id"],
                "payer_id": claim["payer_id"],
                "department_id": claim["department_id"],
                "ar_balance": money(allowed * balance_factor),
                "aging_bucket": bucket,
                "age_days": age_days,
            }
        )

    return {"claims": claims, "payments": payments, "denials": denials, "ar_snapshot": ar_rows}


def build_mockup() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="#f7fafc"/>
  <rect width="1600" height="74" fill="#12212f"/>
  <text x="36" y="48" font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="700" fill="#ffffff">Healthcare Revenue Cycle Analytics</text>
  <text x="1192" y="48" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#cbd5e1">Power BI Semantic Model | Executive View</text>
  <g font-family="Segoe UI, Arial, sans-serif">
    <rect x="34" y="106" width="280" height="118" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="56" y="138" font-size="15" fill="#64748b">Net Revenue</text><text x="56" y="187" font-size="36" font-weight="700" fill="#0f766e">$11.8M</text><text x="56" y="209" font-size="13" fill="#16a34a">+8.4% YoY</text>
    <rect x="344" y="106" width="280" height="118" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="366" y="138" font-size="15" fill="#64748b">Collection Rate</text><text x="366" y="187" font-size="36" font-weight="700" fill="#0f766e">86.2%</text><text x="366" y="209" font-size="13" fill="#b45309">2.1 pts below target</text>
    <rect x="654" y="106" width="280" height="118" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="676" y="138" font-size="15" fill="#64748b">Denial Rate</text><text x="676" y="187" font-size="36" font-weight="700" fill="#be123c">12.9%</text><text x="676" y="209" font-size="13" fill="#be123c">$1.7M denied charges</text>
    <rect x="964" y="106" width="280" height="118" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="986" y="138" font-size="15" fill="#64748b">Days in AR</text><text x="986" y="187" font-size="36" font-weight="700" fill="#b45309">43.6</text><text x="986" y="209" font-size="13" fill="#b45309">Commercial lag rising</text>
    <rect x="1274" y="106" width="292" height="118" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="1296" y="138" font-size="15" fill="#64748b">AR Over 90 Days</text><text x="1296" y="187" font-size="36" font-weight="700" fill="#be123c">28.4%</text><text x="1296" y="209" font-size="13" fill="#be123c">Self Pay and Medicaid risk</text>
    <rect x="34" y="258" width="492" height="286" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="58" y="292" font-size="20" font-weight="700" fill="#0f172a">Denial Rate by Payer</text>
    <rect x="78" y="337" width="352" height="30" fill="#be123c"/><text x="444" y="358" font-size="14" fill="#334155">Self Pay 21.8%</text>
    <rect x="78" y="384" width="286" height="30" fill="#f97316"/><text x="378" y="405" font-size="14" fill="#334155">State Medicaid 16.4%</text>
    <rect x="78" y="431" width="222" height="30" fill="#f59e0b"/><text x="314" y="452" font-size="14" fill="#334155">Medicare Adv. 12.2%</text>
    <rect x="78" y="478" width="168" height="30" fill="#14b8a6"/><text x="260" y="499" font-size="14" fill="#334155">Commercial 8.7%</text>
    <rect x="558" y="258" width="486" height="286" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="582" y="292" font-size="20" font-weight="700" fill="#0f172a">Net Revenue and Denials Trend</text>
    <polyline points="600,470 660,438 720,420 780,386 840,374 900,344 960,326 1020,308" fill="none" stroke="#0f766e" stroke-width="4"/>
    <polyline points="600,390 660,407 720,394 780,418 840,388 900,398 960,370 1020,360" fill="none" stroke="#be123c" stroke-width="4"/>
    <line x1="600" y1="498" x2="1020" y2="498" stroke="#cbd5e1"/>
    <circle cx="866" cy="288" r="6" fill="#0f766e"/><text x="880" y="293" font-size="13" fill="#334155">Net Revenue</text>
    <circle cx="866" cy="314" r="6" fill="#be123c"/><text x="880" y="319" font-size="13" fill="#334155">Denied Amount</text>
    <rect x="1076" y="258" width="490" height="286" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="1100" y="292" font-size="20" font-weight="700" fill="#0f172a">AR Aging by Payer</text>
    <text x="1100" y="336" font-size="14" font-weight="700" fill="#64748b">Payer</text><text x="1320" y="336" font-size="14" font-weight="700" fill="#64748b">90+ AR</text><text x="1440" y="336" font-size="14" font-weight="700" fill="#64748b">Risk</text>
    <line x1="1100" y1="350" x2="1538" y2="350" stroke="#e2e8f0"/>
    <text x="1100" y="388" font-size="15" fill="#0f172a">Self Pay</text><text x="1320" y="388" font-size="15" fill="#be123c">$1.2M</text><text x="1440" y="388" font-size="15" fill="#be123c">High</text>
    <text x="1100" y="434" font-size="15" fill="#0f172a">State Medicaid</text><text x="1320" y="434" font-size="15" fill="#b45309">$860K</text><text x="1440" y="434" font-size="15" fill="#b45309">Watch</text>
    <text x="1100" y="480" font-size="15" fill="#0f172a">Medicare Adv.</text><text x="1320" y="480" font-size="15" fill="#b45309">$740K</text><text x="1440" y="480" font-size="15" fill="#b45309">Watch</text>
    <rect x="34" y="578" width="732" height="278" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="58" y="612" font-size="20" font-weight="700" fill="#0f172a">Denial Root Cause Mix</text>
    <rect x="78" y="652" width="580" height="28" fill="#be123c"/><text x="674" y="672" font-size="14" fill="#334155">Authorization</text>
    <rect x="78" y="696" width="480" height="28" fill="#f97316"/><text x="574" y="716" font-size="14" fill="#334155">Eligibility</text>
    <rect x="78" y="740" width="388" height="28" fill="#f59e0b"/><text x="482" y="760" font-size="14" fill="#334155">Clinical Docs</text>
    <rect x="78" y="784" width="300" height="28" fill="#14b8a6"/><text x="394" y="804" font-size="14" fill="#334155">Coding</text>
    <rect x="800" y="578" width="766" height="278" rx="6" fill="#ffffff" stroke="#d8e1ea"/>
    <text x="824" y="612" font-size="20" font-weight="700" fill="#0f172a">Department Performance Drillthrough</text>
    <text x="824" y="660" font-size="14" font-weight="700" fill="#64748b">Department</text><text x="1045" y="660" font-size="14" font-weight="700" fill="#64748b">Net Revenue</text><text x="1225" y="660" font-size="14" font-weight="700" fill="#64748b">Denial Rate</text><text x="1400" y="660" font-size="14" font-weight="700" fill="#64748b">Action</text>
    <line x1="824" y1="674" x2="1518" y2="674" stroke="#e2e8f0"/>
    <text x="824" y="712" font-size="15" fill="#0f172a">Emergency Medicine</text><text x="1045" y="712" font-size="15" fill="#0f766e">$2.4M</text><text x="1225" y="712" font-size="15" fill="#be123c">16.8%</text><text x="1400" y="712" font-size="15" fill="#334155">Auth workflow</text>
    <text x="824" y="758" font-size="15" fill="#0f172a">Orthopedics</text><text x="1045" y="758" font-size="15" fill="#0f766e">$2.1M</text><text x="1225" y="758" font-size="15" fill="#b45309">11.7%</text><text x="1400" y="758" font-size="15" fill="#334155">Coding review</text>
    <text x="824" y="804" font-size="15" fill="#0f172a">Radiology</text><text x="1045" y="804" font-size="15" fill="#0f766e">$1.5M</text><text x="1225" y="804" font-size="15" fill="#0f766e">7.9%</text><text x="1400" y="804" font-size="15" fill="#334155">Healthy</text>
  </g>
</svg>
"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "dashboard_mockup.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dimensions = build_dimensions()
    patients = build_patients()
    facts = generate_facts(dimensions, patients)

    write_csv(DATA_DIR / "dim_department.csv", [dept.__dict__ for dept in dimensions["departments"]], ["department_id", "department_name", "service_line", "region"])
    write_csv(DATA_DIR / "dim_provider.csv", [provider.__dict__ for provider in dimensions["providers"]], ["provider_id", "provider_name", "department_id", "specialty"])
    write_csv(DATA_DIR / "dim_payer.csv", [payer.__dict__ for payer in dimensions["payers"]], ["payer_id", "payer_name", "payer_type", "base_denial_rate", "lag_mean"])
    write_csv(DATA_DIR / "dim_procedure.csv", [procedure.__dict__ for procedure in dimensions["procedures"]], ["procedure_id", "procedure_code", "procedure_group", "description", "base_charge", "complexity"])
    write_csv(DATA_DIR / "dim_denial_reason.csv", [reason.__dict__ for reason in dimensions["denial_reasons"]], ["denial_reason_id", "denial_reason", "denial_category", "preventable_default"])
    write_csv(DATA_DIR / "dim_patient_masked.csv", patients, ["patient_id", "patient_segment", "age_band", "risk_band", "zip3"])
    write_csv(DATA_DIR / "dim_date.csv", build_date_dimension(date(2025, 1, 1), date(2025, 12, 31)), ["date", "year", "month_number", "month_name", "year_month", "quarter", "week_start_date", "day_of_week", "is_weekend"])
    write_csv(DATA_DIR / "fact_claims.csv", facts["claims"], ["claim_id", "patient_id", "provider_id", "department_id", "payer_id", "procedure_id", "service_date", "claim_submit_date", "claim_status", "claim_type", "gross_charge", "allowed_amount", "expected_patient_responsibility", "clean_claim_flag", "length_of_stay"])
    write_csv(DATA_DIR / "fact_payments.csv", facts["payments"], ["payment_id", "claim_id", "payment_date", "payer_payment", "patient_payment", "contractual_adjustment", "writeoff_amount", "payment_lag_days"])
    write_csv(DATA_DIR / "fact_denials.csv", facts["denials"], ["denial_id", "claim_id", "denial_date", "denial_reason_id", "denial_amount", "preventable_flag", "appeal_status", "recovered_amount"])
    write_csv(DATA_DIR / "fact_ar_snapshot.csv", facts["ar_snapshot"], ["snapshot_date", "claim_id", "payer_id", "department_id", "ar_balance", "aging_bucket", "age_days"])
    build_mockup()
    print(f"Generated {len(facts['claims'])} claims, {len(facts['payments'])} payments, {len(facts['denials'])} denials, and {len(facts['ar_snapshot'])} AR rows.")


if __name__ == "__main__":
    main()
