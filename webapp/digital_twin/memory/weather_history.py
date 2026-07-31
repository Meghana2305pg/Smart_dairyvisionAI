"""History helpers for weather snapshots."""

from __future__ import annotations

from typing import Any

from .snapshot import TwinSnapshot


def build_weather_history(snapshot: TwinSnapshot) -> dict[str, Any]:
    """Return weather-specific history data."""
    return {"snapshot_id": snapshot.snapshot_id, "cow_id": snapshot.cow_id, "weather": snapshot.weather}
