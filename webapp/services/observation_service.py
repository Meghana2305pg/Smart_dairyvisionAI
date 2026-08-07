"""Application service for creating observations and updating the digital twin."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from webapp.digital_twin.observation import Observation
from webapp.utils.logging import log_event
from webapp.repositories.observation_repository import ObservationRepository
from webapp.services.cow_service import CowService
from webapp.digital_twin.cow_twin import CowTwin


class ObservationService:
    """Coordinates observation creation, twin updates, and snapshot persistence."""

    def __init__(self, repository: ObservationRepository | None = None, cow_service: CowService | None = None) -> None:
        self.repository = repository or ObservationRepository()
        self.cow_service = cow_service or CowService()

    def record_observation(
        self,
        cow_id: str,
        age: float | None = None,
        weight: float | None = None,
        feed: float | None = None,
        temperature: float | None = None,
        humidity: float | None = None,
        health_status: int | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        observation = Observation(
            cow_id=cow_id,
            age=age,
            weight=weight,
            feed=feed,
            temperature=temperature,
            humidity=humidity,
            health_status=health_status,
            notes=notes,
        )

        cow_record = self.cow_service.repository.get(cow_id)
        if cow_record is None:
            self.cow_service.register_cow(cow_id=cow_id, name=cow_id)
            cow_record = self.cow_service.repository.get(cow_id)

        if cow_record is None:
            raise RuntimeError(f"Cow record not found for observation insertion: {cow_id}")

        resolved_cow_uuid = str(cow_record.get("id") or cow_record.get("cow_id") or cow_record.get("cow_tag") or cow_id)
        log_event(
            "observation_cow_resolution",
            selected_cow=cow_id,
            resolved_cow_uuid=resolved_cow_uuid,
            cow_record=cow_record,
        )

        persistence_payload: dict[str, Any] = {}
        persistence_payload["cow_id"] = resolved_cow_uuid
        log_event("observation_persistence_payload", cow_id=resolved_cow_uuid, payload=persistence_payload)
        if feed is not None:
            persistence_payload["feed"] = float(feed)
        if temperature is not None:
            persistence_payload["temperature"] = float(temperature)
        if humidity is not None:
            persistence_payload["humidity"] = float(humidity)
        if health_status is not None:
            persistence_payload["health_status"] = int(health_status)
        if notes is not None:
            persistence_payload["notes"] = notes

        self.repository.create(persistence_payload)

        twin = self.cow_service._cow_twins.get(cow_id)

        if twin is None:
            twin = CowTwin(
                cow_id=cow_id,
                name=cow_record.get("cow_name") or cow_record.get("name") or cow_id,
            )
            self.cow_service._cow_twins[cow_id] = twin

        twin.record_observation(observation)
        twin.refresh_from_ai(base_temp=temperature, base_hum=humidity)
        snapshot = twin.memory_store.get_latest_snapshot(cow_id)
        return {
            "observation": asdict(observation),
            "cow_twin": twin.snapshot(),
            "snapshot": snapshot,
        }
