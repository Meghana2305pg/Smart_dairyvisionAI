"""Conceptual observations used to update the digital twin."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Observation:
    """A single observation snapshot for a cow or farm context.

    This class keeps the conceptual representation lightweight and independent
    from storage and UI concerns.
    """

    cow_id: str
    age: float | None = None
    weight: float | None = None
    feed: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    health_status: int | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: str | None = None

    def to_input_row(self) -> dict[str, Any]:
        """Return the input shape expected by the existing AI services."""
        return {
            "age": self.age,
            "weight": self.weight,
            "feed": self.feed,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "health_status": self.health_status,
        }
