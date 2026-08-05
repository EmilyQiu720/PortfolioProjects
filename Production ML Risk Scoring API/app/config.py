"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Production ML Risk Scoring API"
    environment: str = os.getenv("APP_ENV", "local")
    api_key: str = os.getenv("API_KEY", "dev-local-key")
    database_path: Path = Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "data" / "prediction_log.sqlite"))
    model_registry_path: Path = Path(os.getenv("MODEL_REGISTRY_PATH", PROJECT_ROOT / "artifacts" / "model_registry.json"))
    reference_features_path: Path = Path(os.getenv("REFERENCE_FEATURES_PATH", PROJECT_ROOT / "data" / "reference_features.csv"))
    enable_cache: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "2.0"))


settings = Settings()

