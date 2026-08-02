"""Conceptual state container for digital-twin entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


class PersistencePort(Protocol):
    """A lightweight persistence abstraction for future storage layers."""

    def save(self, entity: Any, key: str | None = None) -> None:
        """Persist an entity."""

    def load(self, key: str) -> Any:
        """Load an entity by key."""


@dataclass(slots=True)
class TwinState:
    """The evolving state of a digital-twin entity."""

    status: str = "stable"
    last_updated: datetime | None = None
    context: dict[str, Any] = field(default_factory=dict)
    observations: list[dict[str, Any]] = field(default_factory=list)
    predictions: list[dict[str, Any]] = field(default_factory=list)
    simulations: list[dict[str, Any]] = field(default_factory=list)
    health_assessments: list[dict[str, Any]] = field(default_factory=list)
    explanations: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    timeline_events: list[dict[str, Any]] = field(default_factory=list)
    playback_state: dict[str, Any] | None = None

    def refresh_timestamp(self) -> None:
        """Update the last-updated timestamp."""
        self.last_updated = datetime.utcnow()

    def to_persistence_payload(self) -> dict[str, Any]:
        """Produce a serialisable payload for future persistence layers."""
        return {
            "status": self.status,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "context": self.context,
            "observations": self.observations,
            "predictions": self.predictions,
            "simulations": self.simulations,
            "health_assessments": self.health_assessments,
            "explanations": self.explanations,
            "recommendations": self.recommendations,
            "timeline_events": self.timeline_events,
            "playback_state": self.playback_state,
        }
