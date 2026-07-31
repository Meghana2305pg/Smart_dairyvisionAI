"""History helpers for health snapshots."""

from __future__ import annotations

from typing import Any

from .snapshot import TwinSnapshot


def build_health_history(snapshot: TwinSnapshot) -> dict[str, Any]:
    """Return health-specific history data."""
    return {"snapshot_id": snapshot.snapshot_id, "cow_id": snapshot.cow_id, "health": snapshot.health}
