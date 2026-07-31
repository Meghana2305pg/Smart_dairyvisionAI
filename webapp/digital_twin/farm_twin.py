"""Conceptual Farm Digital Twin."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .herd_twin import HerdTwin
from .twin_state import TwinState


@dataclass(slots=True)
class FarmTwin:
    """Represents the entire farm as a digital-twin context."""

    farm_id: str
    state: TwinState = field(default_factory=TwinState)
    herds: dict[str, HerdTwin] = field(default_factory=dict)

    def register_herd(self, herd: HerdTwin) -> None:
        """Register a herd within the farm."""
        self.herds[herd.herd_id] = herd
        self.state.context.setdefault("herd_count", len(self.herds))

    def refresh_state(self) -> None:
        """Refresh the farm-level state from the registered herds."""
        statuses = [herd.state.status for herd in self.herds.values()]
        if any(status in {"emerging_risk", "stressed"} for status in statuses):
            self.state.status = "stressed"
        elif any(status in {"normal", "stable"} for status in statuses):
            self.state.status = "stable"
        else:
            self.state.status = "watch"
        self.state.context["herd_count"] = len(self.herds)
        self.state.refresh_timestamp()

    def aggregate_herd_summaries(self) -> dict[str, Any]:
        """Aggregate herd-level summaries into a simple farm view."""
        herd_summaries = {herd_id: herd.aggregate_snapshot_summary() for herd_id, herd in self.herds.items()}
        return {
            "farm_id": self.farm_id,
            "herd_count": len(self.herds),
            "herd_summaries": herd_summaries,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return a farm-level snapshot."""
        return {
            "farm_id": self.farm_id,
            "state": {
                "status": self.state.status,
                "last_updated": self.state.last_updated.isoformat() if self.state.last_updated else None,
                "context": self.state.context,
            },
            "herd_ids": sorted(self.herds.keys()),
        }
