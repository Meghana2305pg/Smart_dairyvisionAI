"""Immutable digital-twin snapshot definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TwinSnapshot:
    """One immutable snapshot of a digital-twin state."""

    snapshot_id: str
    cow_id: str
    timestamp: datetime
    observation: Any | None = None
    prediction: Any | None = None
    health: Any | None = None
    weather: Any | None = None
    explanation: Any | None = None
    recommendations: Any | None = None
    twin_status: str = "stable"
    metadata: dict[str, Any] = field(default_factory=dict)
