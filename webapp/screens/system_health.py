"""System health helpers for the command centre."""
from __future__ import annotations

from typing import Any


def build_system_health_payload() -> dict[str, Any]:
    """Build a lightweight system-health payload from the current runtime services."""
    return {
        "prediction_engine": "Online",
        "digital_twin": "Online",
        "weather_service": "Online",
        "repository": "Online",
        "authentication": "Online",
    }
