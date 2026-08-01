"""Activity feed helpers for the command centre."""
from __future__ import annotations

from typing import Any


def build_activity_feed(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create a recent activity feed from the most recent observations."""
    items: list[dict[str, Any]] = []
    for observation in observations[:8]:
        items.append({
            "cow_id": observation.get("cow_id"),
            "summary": observation.get("notes") or "Observation recorded",
        })
    return items
