"""History helpers for prediction snapshots."""

from __future__ import annotations

from typing import Any

from .snapshot import TwinSnapshot


def build_prediction_history(snapshot: TwinSnapshot) -> dict[str, Any]:
    """Return prediction-specific history data."""
    return {"snapshot_id": snapshot.snapshot_id, "cow_id": snapshot.cow_id, "prediction": snapshot.prediction}
