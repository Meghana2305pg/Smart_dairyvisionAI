"""Timeline event definitions and event-history helpers for digital twins."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class TimelineEvent:
    """A single chronological event in a cow twin's evolution.

    Timeline events are intentionally additive: they describe what changed in a
    snapshot without altering the existing twin fields or UI state.
    """

    event_id: str
    snapshot_id: str | None
    cow_id: str
    timestamp: datetime
    event_type: str
    severity: str = "info"
    title: str | None = None
    summary: str | None = None
    payload: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        """Return a serialisable payload for persistence or UI consumption."""
        return {
            "event_id": self.event_id,
            "snapshot_id": self.snapshot_id,
            "cow_id": self.cow_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "severity": self.severity,
            "title": self.title,
            "summary": self.summary,
            "payload": self.payload or {},
            "metadata": dict(self.metadata or {}),
        }


class TimelineEngine:
    """Store and query chronological timeline events for each cow.

    The engine is intentionally simple and in-memory, matching the existing
    snapshot store strategy. It preserves the current runtime model while adding
    a clean timeline history abstraction for future playback or auditing.
    """

    def __init__(self) -> None:
        self._events: dict[str, list[TimelineEvent]] = {}

    def create_event(
        self,
        *,
        cow_id: str,
        snapshot_id: str | None,
        timestamp: datetime | None = None,
        event_type: str,
        severity: str = "info",
        title: str | None = None,
        summary: str | None = None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        event_id: str | None = None,
    ) -> TimelineEvent:
        """Create a timeline event with a UUID and timestamp if needed."""
        resolved_timestamp = timestamp or datetime.utcnow()
        return TimelineEvent(
            event_id=event_id or str(uuid4()),
            snapshot_id=snapshot_id,
            cow_id=cow_id,
            timestamp=resolved_timestamp,
            event_type=event_type,
            severity=severity,
            title=title or event_type,
            summary=summary,
            payload=payload or {},
            metadata=dict(metadata or {}),
        )

    def append_event(self, event: TimelineEvent) -> TimelineEvent:
        """Append an event to the cow-specific timeline history."""
        history = self._events.setdefault(event.cow_id, [])
        history.append(event)
        history.sort(key=lambda item: item.timestamp)
        return event

    def get_history(self, cow_id: str) -> list[TimelineEvent]:
        """Return the ordered history for the requested cow."""
        return list(self._events.get(cow_id, []))

    def get_latest_event(self, cow_id: str) -> TimelineEvent | None:
        """Return the latest event for the requested cow, if any."""
        history = self._events.get(cow_id, [])
        if not history:
            return None
        return history[-1]

    def get_events_between(self, cow_id: str, start_time: datetime, end_time: datetime) -> list[TimelineEvent]:
        """Return events for a cow that fall within the supplied range."""
        history = self._events.get(cow_id, [])
        return [item for item in history if start_time <= item.timestamp <= end_time]

    def count_events(self, cow_id: str) -> int:
        """Return the number of stored timeline events for a cow."""
        return len(self._events.get(cow_id, []))
