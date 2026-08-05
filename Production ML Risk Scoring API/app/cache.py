"""Optional cache layer with an in-memory fallback for local development."""

from __future__ import annotations

import json
from typing import Any


class PredictionCache:
    def __init__(self) -> None:
        self._memory: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        return self._memory.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        json.dumps(value, default=str)
        self._memory[key] = value

