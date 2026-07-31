"""Conceptual Herd Digital Twin."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cow_twin import CowTwin
from .twin_state import TwinState


@dataclass(slots=True)
class HerdTwin:
    """Represents a herd as an aggregate digital-twin entity."""

    herd_id: str
    state: TwinState = field(default_factory=TwinState)
    cows: dict[str, CowTwin] = field(default_factory=dict)

    def register_cow(self, cow: CowTwin) -> None:
        """Register a cow within the herd."""
        self.cows[cow.cow_id] = cow
        self.state.context.setdefault("cow_count", len(self.cows))

    def refresh_state(self) -> None:
        """Refresh herd-level state from the current cow twins."""
        statuses = [cow.state.status for cow in self.cows.values()]
        if any(status in {"stressed", "at_risk"} for status in statuses):
            self.state.status = "emerging_risk"
        elif any(status == "stable" for status in statuses):
            self.state.status = "normal"
        else:
            self.state.status = "stable"
        self.state.context["cow_count"] = len(self.cows)
        self.state.refresh_timestamp()

    def aggregate_snapshot_summary(self) -> dict[str, Any]:
        """Return a simple summarised view of the latest cow snapshots."""
        latest_snapshots = [cow.memory_store.get_latest_snapshot(cow.cow_id) for cow in self.cows.values()]
        latest_snapshots = [snapshot for snapshot in latest_snapshots if snapshot is not None]

        if not latest_snapshots:
            return {
                "average_prediction": None,
                "average_health": None,
                "average_thi": None,
                "risk_summary": {"stable": 0, "at_risk": 0, "stressed": 0},
            }

        predictions = [float(snapshot.prediction.get("prediction", 0.0)) for snapshot in latest_snapshots if snapshot.prediction and isinstance(snapshot.prediction, dict)]
        health_levels = [str(snapshot.health.get("severity", "Low")).lower() for snapshot in latest_snapshots if snapshot.health and isinstance(snapshot.health, dict)]
        average_thi = None
        for snapshot in latest_snapshots:
            if snapshot.weather and isinstance(snapshot.weather, dict):
                if snapshot.weather.get("temperature") is not None and snapshot.weather.get("humidity") is not None:
                    average_thi = sum(
                        [value.get("temperature", 0.0) for value in []]
                    )
                    break

        risk_summary = {"stable": 0, "at_risk": 0, "stressed": 0}
        for level in health_levels:
            if level in {"critical", "high"}:
                risk_summary["stressed"] += 1
            elif level == "medium":
                risk_summary["at_risk"] += 1
            else:
                risk_summary["stable"] += 1

        return {
            "average_prediction": sum(predictions) / len(predictions) if predictions else None,
            "average_health": sum(1 for level in health_levels if level in {"critical", "high", "medium"}) / len(health_levels) if health_levels else None,
            "average_thi": average_thi,
            "risk_summary": risk_summary,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return a conceptual herd-level snapshot."""
        return {
            "herd_id": self.herd_id,
            "state": {
                "status": self.state.status,
                "last_updated": self.state.last_updated.isoformat() if self.state.last_updated else None,
                "context": self.state.context,
            },
            "cow_ids": sorted(self.cows.keys()),
        }
