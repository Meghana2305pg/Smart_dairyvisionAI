"""Snapshot creation and export helpers for the digital-twin memory layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from .snapshot import TwinSnapshot


class SnapshotEngine:
    """Create, validate, and export richer digital-twin snapshots.

    The engine is intentionally additive: it builds on the existing
    :class:`TwinSnapshot` type and preserves the old field names for backward
    compatibility while exposing the richer snapshot contract required by
    Phase 7.1.
    """

    def create_snapshot(
        self,
        *,
        cow_id: str,
        observation: Any | None = None,
        prediction: Any | None = None,
        health_assessment: Any | None = None,
        explainability: Any | None = None,
        recommendations: Any | None = None,
        twin_status: str = "stable",
        weather: Any | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
        snapshot_id: str | None = None,
        version: int = 1,
        health: Any | None = None,
        explanation: Any | None = None,
    ) -> TwinSnapshot:
        """Create a snapshot with the richer Phase 7.1 contract.

        Parameters
        ----------
        cow_id:
            Identifier of the cow that owns the snapshot.
        observation, prediction, weather, recommendations:
            Runtime data captured for the current twin state.
        health_assessment, explainability:
            Richer field names used by the Phase 7.1 snapshot contract.
        twin_status:
            Conceptual status of the cow twin at the time of capture.
        metadata:
            Optional free-form metadata for tracing and future extensions.
        timestamp:
            Optional explicitly supplied timestamp. When omitted, UTC time is
            used.
        snapshot_id:
            Optional externally supplied identifier. When omitted, a UUID is
            generated.
        version:
            Snapshot schema version.
        health, explanation:
            Backward-compatible aliases for the legacy snapshot fields.
        """

        resolved_timestamp = timestamp or datetime.utcnow()
        resolved_snapshot_id = snapshot_id or str(uuid4())
        resolved_health_assessment = health_assessment if health_assessment is not None else health
        resolved_explainability = explainability if explainability is not None else explanation

        snapshot = TwinSnapshot(
            snapshot_id=resolved_snapshot_id,
            cow_id=cow_id,
            timestamp=resolved_timestamp,
            observation=observation,
            prediction=prediction,
            health=resolved_health_assessment,
            weather=weather,
            explanation=resolved_explainability,
            recommendations=recommendations,
            twin_status=twin_status,
            metadata=dict(metadata or {}),
            health_assessment=resolved_health_assessment,
            explainability=resolved_explainability,
            version=version,
        )
        self.validate_snapshot(snapshot)
        return snapshot

    def validate_snapshot(self, snapshot: TwinSnapshot) -> None:
        """Validate a snapshot before it is persisted or exported.

        The validation is intentionally lightweight and compatible with the
        existing in-memory store. It ensures the required shape exists without
        introducing strict schema enforcement that could break older callers.
        """

        if not isinstance(snapshot, TwinSnapshot):
            raise TypeError("snapshot must be an instance of TwinSnapshot")
        if not snapshot.snapshot_id:
            raise ValueError("snapshot_id is required")
        if not snapshot.cow_id:
            raise ValueError("cow_id is required")
        if snapshot.timestamp is None:
            raise ValueError("timestamp is required")
        if snapshot.version is None:
            raise ValueError("version is required")

    def export_snapshot(self, snapshot: TwinSnapshot) -> dict[str, Any]:
        """Serialize a snapshot into a dictionary for export or debugging."""
        self.validate_snapshot(snapshot)
        return {
            "snapshot_id": snapshot.snapshot_id,
            "cow_id": snapshot.cow_id,
            "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
            "twin_status": snapshot.twin_status,
            "observation": snapshot.observation,
            "prediction": snapshot.prediction,
            "health_assessment": snapshot.health_assessment,
            "explainability": snapshot.explainability,
            "recommendations": snapshot.recommendations,
            "weather": snapshot.weather,
            "metadata": dict(snapshot.metadata or {}),
            "version": snapshot.version,
            "health": snapshot.health,
            "explanation": snapshot.explanation,
        }
