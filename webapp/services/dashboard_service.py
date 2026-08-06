"""Application service for building dashboard aggregates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from webapp.repositories.dashboard_repository import DashboardRepository
from webapp.services.cow_service import CowService
from webapp.services.farm_service import FarmService
from webapp.services.observation_service import ObservationService
from webapp.utils.logging import log_event


@dataclass(slots=True)
class DashboardView:
    """Simple dashboard data transfer object."""

    farm: dict[str, Any]
    herd: dict[str, Any]
    predictions: list[dict[str, Any]]
    health: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    snapshots: list[dict[str, Any]]


class DashboardService:
    """Assemble a single dashboard payload from farms, cows, observations, and snapshots."""

    def __init__(
        self,
        repository: DashboardRepository | None = None,
        farm_service: FarmService | None = None,
        cow_service: CowService | None = None,
        observation_service: ObservationService | None = None,
    ) -> None:
        self.repository = repository or DashboardRepository()
        self.farm_service = farm_service or FarmService()
        self.cow_service = cow_service or CowService()
        self.observation_service = observation_service or ObservationService(cow_service=self.cow_service)

    def build_dashboard(self) -> DashboardView:
        print("[DEBUG] DashboardService.build_dashboard() called")
        log_event("debug_dashboard_service_build", source="build_dashboard")
        farms = self.repository.get_farms()
        cows = self.repository.get_cows()
        observations = self.repository.get_observations()
        snapshots = self.repository.get_snapshots()

        farm_record = farms[0] if farms else {"farm_id": "", "name": "No Farm", "location": ""}
        service_cows = self.cow_service.get_cows()
        active_cow_ids = [cow.get("cow_id") for cow in service_cows if cow.get("cow_id")]
        if not active_cow_ids:
            active_cow_ids = [cow_id for cow_id in self.cow_service._cow_twins.keys() if cow_id]

        herd_payload = {
            "cow_count": len(active_cow_ids),
            "observation_count": len(observations),
            "snapshot_count": len(snapshots),
        }

        predictions: list[dict[str, Any]] = []
        health: list[dict[str, Any]] = []
        recommendations: list[dict[str, Any]] = []
        snapshot_payloads: list[dict[str, Any]] = []

        for cow_id in active_cow_ids:
            if not cow_id:
                continue
            twin = self.cow_service._cow_twins.get(cow_id)
            if twin is None:
                continue
            if twin.latest_prediction is not None:
                predictions.append({"cow_id": cow_id, **twin.latest_prediction})
            if twin.latest_health is not None:
                health.append({"cow_id": cow_id, **twin.latest_health})
            recommendations.extend(twin.recommendations)
            latest_snapshot = twin.memory_store.get_latest_snapshot(cow_id)
            if latest_snapshot is not None:
                snapshot_payloads.append({
                    "cow_id": cow_id,
                    "snapshot_id": latest_snapshot.snapshot_id,
                    "twin_status": latest_snapshot.twin_status,
                })

        return DashboardView(
            farm=farm_record,
            herd=herd_payload,
            predictions=predictions,
            health=health,
            recommendations=recommendations,
            snapshots=snapshot_payloads,
        )
