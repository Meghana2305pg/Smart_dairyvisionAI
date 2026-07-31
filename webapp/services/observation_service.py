"""Application service for creating observations and updating the digital twin."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from webapp.digital_twin.observation import Observation
from webapp.repositories.observation_repository import ObservationRepository
from webapp.services.cow_service import CowService


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
        self.repository.create(asdict(observation))

        twin = self.cow_service._cow_twins.get(cow_id)
        if twin is None:
            registered = self.cow_service.register_cow(cow_id=cow_id, name=cow_id)
            twin = self.cow_service._cow_twins.get(cow_id)
            if twin is None:
                raise RuntimeError("Cow twin was not initialized")

        twin.record_observation(observation)
        twin.refresh_from_ai(base_temp=temperature, base_hum=humidity)
        snapshot = twin.memory_store.get_latest_snapshot(cow_id)
        return {
            "observation": asdict(observation),
            "cow_twin": twin.snapshot(),
            "snapshot": snapshot,
        }
