"""SQLite-backed prediction logging for local development and demos."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS prediction_log (
    request_id TEXT PRIMARY KEY,
    customer_hash TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_decision TEXT NOT NULL,
    top_factors TEXT NOT NULL,
    scored_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prediction_log_model_version
ON prediction_log(model_version);
CREATE INDEX IF NOT EXISTS idx_prediction_log_decision
ON prediction_log(risk_decision);
"""


class PredictionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.executescript(SCHEMA)

    def insert_prediction(self, prediction: dict[str, Any], customer_hash: str) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO prediction_log (
                    request_id,
                    customer_hash,
                    model_name,
                    model_version,
                    risk_score,
                    risk_decision,
                    top_factors,
                    scored_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prediction["request_id"],
                    customer_hash,
                    prediction["model_name"],
                    prediction["model_version"],
                    prediction["risk_score"],
                    prediction["risk_decision"],
                    json.dumps(prediction["top_factors"]),
                    prediction["scored_at"].isoformat(),
                ),
            )

    def summary(self) -> dict[str, Any]:
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute("SELECT COUNT(*) AS value FROM prediction_log").fetchone()["value"]
            by_decision = {
                row["risk_decision"]: row["count"]
                for row in connection.execute(
                    "SELECT risk_decision, COUNT(*) AS count FROM prediction_log GROUP BY risk_decision"
                )
            }
            average_score = connection.execute("SELECT AVG(risk_score) AS value FROM prediction_log").fetchone()["value"]
        return {"total_predictions": total, "by_decision": by_decision, "average_risk_score": average_score or 0.0}

