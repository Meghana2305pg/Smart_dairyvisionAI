"""History helpers for observation snapshots."""

from __future__ import annotations

from typing import Any

from .snapshot import TwinSnapshot


def build_observation_history(snapshot: TwinSnapshot) -> dict[str, Any]:
    """Return observation-specific history data."""
    return {"snapshot_id": snapshot.snapshot_id, "cow_id": snapshot.cow_id, "observation": snapshot.observation}
