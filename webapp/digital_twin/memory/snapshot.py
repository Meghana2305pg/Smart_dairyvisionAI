"""Immutable digital-twin snapshot definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TwinSnapshot:
    """One immutable snapshot of a digital-twin state.

    The class preserves the original snapshot shape for existing callers while
    also supporting the richer Phase 7.1 contract with dedicated fields for
    health assessment, explainability, and schema versioning.
    """

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
    health_assessment: Any | None = None
    explainability: Any | None = None
    version: int = 1
