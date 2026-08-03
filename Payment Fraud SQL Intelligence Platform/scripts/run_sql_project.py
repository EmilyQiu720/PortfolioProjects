"""Run or validate the Payment Fraud SQL Intelligence Platform.

The project is intentionally PostgreSQL-first because it demonstrates database
features that matter in production: roles, triggers, materialized views,
indexes, and transactional workflows.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SQL_ORDER = [
    "schema/01_create_schema.sql",
    "schema/02_constraints.sql",
    "schema/03_indexes.sql",
    "schema/04_views.sql",
    "schema/05_materialized_views.sql",
    "schema/06_triggers_audit.sql",
    "schema/07_security_roles.sql",
    "data/seed_data.sql",
    "queries/fraud_detection_queries.sql",
    "queries/merchant_risk_analytics.sql",
    "queries/customer_behavior_analytics.sql",
    "queries/chargeback_analysis.sql",
    "queries/operations_dashboard_queries.sql",
    "tests/data_quality_tests.sql",
    "tests/transaction_integrity_tests.sql",
]

REQUIRED_KEYWORDS = {
    "schema/01_create_schema.sql": ["CREATE TABLE", "PRIMARY KEY", "REFERENCES"],
    "schema/03_indexes.sql": ["CREATE INDEX", "WHERE"],
    "schema/04_views.sql": ["CREATE OR REPLACE VIEW"],
    "schema/05_materialized_views.sql": ["CREATE MATERIALIZED VIEW"],
    "schema/06_triggers_audit.sql": ["CREATE TRIGGER", "audit_log"],
    "schema/07_security_roles.sql": ["CREATE ROLE", "GRANT"],
    "queries/fraud_detection_queries.sql": ["WITH", "OVER", "risk"],
    "tests/data_quality_tests.sql": ["SELECT", "test_name"],
}


def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_files() -> None:
    missing = [relative for relative in SQL_ORDER if not (PROJECT_ROOT / relative).exists()]
    if missing:
        raise SystemExit(f"Missing SQL files: {missing}")

    for relative, keywords in REQUIRED_KEYWORDS.items():
        body = read_sql(PROJECT_ROOT / relative).upper()
        absent = [keyword for keyword in keywords if keyword.upper() not in body]
        if absent:
            raise SystemExit(f"{relative} is missing expected SQL concepts: {absent}")

    print("Static validation passed.")
    print("Execution order:")
    for index, relative in enumerate(SQL_ORDER, start=1):
        print(f"{index:02d}. {relative}")


def execute_files(database_url: str) -> None:
    psql = shutil.which("psql")
    if not psql:
        raise SystemExit("psql was not found. Install PostgreSQL client tools or run --check-only.")

    for relative in SQL_ORDER:
        path = PROJECT_ROOT / relative
        print(f"Running {relative}")
        subprocess.run([psql, database_url, "-v", "ON_ERROR_STOP=1", "-f", str(path)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or execute the SQL portfolio project.")
    parser.add_argument("--check-only", action="store_true", help="Validate file structure without executing SQL.")
    parser.add_argument("--execute", action="store_true", help="Execute SQL files through psql.")
    parser.add_argument(
        "--database-url",
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://fraud_admin:fraud_admin_password@localhost:5433/fraud_platform",
        ),
        help="PostgreSQL connection string. Defaults to the docker-compose database.",
    )
    args = parser.parse_args()

    validate_files()

    if args.execute:
        execute_files(args.database_url)
    elif not args.check_only:
        print("No SQL executed. Use --execute to run against PostgreSQL.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
