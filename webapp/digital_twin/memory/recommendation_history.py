"""History helpers for recommendation snapshots."""

from __future__ import annotations

from typing import Any

from .snapshot import TwinSnapshot


def build_recommendation_history(snapshot: TwinSnapshot) -> dict[str, Any]:
    """Return recommendation-specific history data."""
    return {"snapshot_id": snapshot.snapshot_id, "cow_id": snapshot.cow_id, "recommendations": snapshot.recommendations}
