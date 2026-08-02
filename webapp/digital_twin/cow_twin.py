"""Conceptual Cow Digital Twin."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .decision_support import build_recommendations
from .memory.memory_store import InMemorySnapshotStore
from .memory.playback import PlaybackEngine
from .memory.snapshot_engine import SnapshotEngine
from .memory.timeline import TimelineEngine, TimelineEvent
from .observation import Observation
from .twin_intelligence import TwinIntelligence, TwinIntelligenceResult
from .twin_state import TwinState


@dataclass(slots=True)
class CowTwin:
    """Represents an individual cow inside the digital-twin architecture.

    The class keeps conceptual state around observations, AI results, and
    recommendations without duplicating existing backend logic.
    """

    cow_id: str
    name: str | None = None
    state: TwinState = field(default_factory=TwinState)
    observation_history: list[Observation] = field(default_factory=list)
    latest_observation: Observation | None = None
    intelligence: TwinIntelligence = field(default_factory=TwinIntelligence)
    memory_store: InMemorySnapshotStore = field(default_factory=InMemorySnapshotStore)
    snapshot_engine: SnapshotEngine = field(default_factory=SnapshotEngine)
    timeline_engine: TimelineEngine = field(default_factory=TimelineEngine)
    latest_prediction: dict[str, Any] | None = None
    latest_health: dict[str, Any] | None = None
    latest_explanation: list[dict[str, Any]] | None = None
    latest_simulation: dict[str, Any] | None = None
    latest_intelligence: TwinIntelligenceResult | None = None
    recommendations: list[dict[str, Any]] = field(default_factory=list)

    def record_observation(self, observation: Observation) -> None:
        """Store a new observation and update the cow twin state."""
        self.observation_history.append(observation)
        self.latest_observation = observation
        self.state.observations.append(
            {
                "cow_id": observation.cow_id,
                "timestamp": observation.timestamp.isoformat(),
                "notes": observation.notes,
            }
        )
        self.state.refresh_timestamp()

    def refresh_from_ai(self, base_temp: float | None = None, base_hum: float | None = None) -> None:
        """Delegate AI orchestration to the Twin Intelligence layer."""
        if self.latest_observation is None:
            return

        intelligence_result = self.intelligence.analyze_observation(
            self.latest_observation,
            base_temp=base_temp,
            base_hum=base_hum,
        )

        self.latest_intelligence = intelligence_result
        self.latest_prediction = intelligence_result.prediction
        self.latest_health = intelligence_result.health
        self.latest_explanation = intelligence_result.explanation

        if intelligence_result.prediction is not None:
            self.state.predictions.append({"cow_id": self.cow_id, **intelligence_result.prediction})
        if intelligence_result.health is not None:
            self.state.health_assessments.append({"cow_id": self.cow_id, **intelligence_result.health})
        if intelligence_result.explanation is not None:
            self.state.explanations.append({"cow_id": self.cow_id, "explanation": intelligence_result.explanation})
        self.recommendations = build_recommendations(self)
        self.state.recommendations = [
            {
                "cow_id": self.cow_id,
                "message": recommendation.message,
                "priority": recommendation.priority,
            }
            for recommendation in self.recommendations
        ]
        self.state.status = self._classify_status()
        self._store_snapshot(intelligence_result)
        self.state.refresh_timestamp()

    def _classify_status(self) -> str:
        """Map current AI results to a conceptual twin status."""
        if self.latest_health is None:
            return "stable"

        severity = str(self.latest_health.get("severity", "Low")).lower()
        if severity in {"critical", "high"}:
            return "stressed"
        if severity == "medium":
            return "at_risk"
        return "stable"

    def _store_snapshot(self, intelligence_result: TwinIntelligenceResult) -> None:
        """Create and save an immutable snapshot for the current AI analysis."""
        snapshot = self.snapshot_engine.create_snapshot(
            cow_id=self.cow_id,
            observation=intelligence_result.observation,
            prediction=intelligence_result.prediction,
            health_assessment=intelligence_result.health,
            explainability=intelligence_result.explanation,
            recommendations=self.recommendations,
            twin_status=self.state.status,
            weather=intelligence_result.weather,
            metadata={
                **intelligence_result.metadata,
                "recommendation_count": len(self.recommendations),
            },
            timestamp=datetime.utcnow(),
            snapshot_id=f"{self.cow_id}:{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        )
        self.memory_store.save_snapshot(snapshot)
        self._append_timeline_events(snapshot, intelligence_result)
        self.state.context["latest_snapshot_id"] = snapshot.snapshot_id
        self.state.context["snapshot_count"] = len(self.memory_store.list_snapshot_history(self.cow_id))

    def _append_timeline_events(self, snapshot: Any, intelligence_result: TwinIntelligenceResult) -> None:
        """Create timeline events for a newly created snapshot.

        The events are additive and do not replace the existing twin state.
        They are intended to provide a chronological record of what changed.
        """
        timestamp = snapshot.timestamp or datetime.utcnow()
        events = [
            (
                "observation_recorded",
                "Observation Recorded",
                "A new observation was captured for the cow twin.",
                {
                    "observation": (
                        intelligence_result.observation.to_input_row()
                        if intelligence_result.observation is not None
                        else None
                    )
                },
            ),
            (
                "prediction_updated",
                "Prediction Updated",
                "The twin received a refreshed prediction.",
                {"prediction": intelligence_result.prediction},
            ),
            (
                "health_status_changed",
                "Health Status Changed",
                "The latest AI health assessment was recorded.",
                {"health": intelligence_result.health},
            ),
            (
                "recommendation_updated",
                "Recommendation Updated",
                "The recommendation set was refreshed.",
                {"recommendations": self.recommendations},
            ),
            (
                "weather_updated",
                "Weather Updated",
                "The latest weather context was captured.",
                {"weather": intelligence_result.weather},
            ),
        ]

        for event_type, title, summary, payload in events:
            severity = "high" if event_type == "health_status_changed" and intelligence_result.health else "info"
            event = self.timeline_engine.create_event(
                cow_id=self.cow_id,
                snapshot_id=snapshot.snapshot_id,
                timestamp=timestamp,
                event_type=event_type,
                severity=severity,
                title=title,
                summary=summary,
                payload=payload,
                metadata={"source": "cow_twin"},
            )
            self.timeline_engine.append_event(event)
            self.state.timeline_events.append(event.to_payload())

    def get_playback(self) -> PlaybackEngine:
        """Return a read-only playback engine for the cow's historical snapshots."""
        return PlaybackEngine(self.memory_store, self.cow_id)

    def snapshot(self) -> dict[str, Any]:
        """Return a conceptual snapshot for future persistence or UI display."""
        return {
            "cow_id": self.cow_id,
            "name": self.name,
            "state": {
                "status": self.state.status,
                "last_updated": self.state.last_updated.isoformat() if self.state.last_updated else None,
                "context": self.state.context,
            },
            "latest_prediction": self.latest_prediction,
            "latest_health": self.latest_health,
            "latest_explanation": self.latest_explanation,
            "recommendations": self.recommendations,
        }
