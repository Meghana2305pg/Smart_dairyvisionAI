"""Application service for farm operations."""

from __future__ import annotations

from typing import Any

from webapp.digital_twin.farm_twin import FarmTwin
from webapp.repositories.farm_repository import FarmRepository


class FarmService:
    """Business logic for farm creation, reading, updates, and deletion."""

    def __init__(self, repository: FarmRepository | None = None) -> None:
        self.repository = repository or FarmRepository()
        self._farm_twins: dict[str, FarmTwin] = {}

    def create_farm(self, farm_id: str, name: str, location: str | None = None, farm_size: str | None = None) -> dict[str, Any]:
        payload = {"farm_id": farm_id, "name": name, "location": location or "", "farm_size": farm_size or ""}
        self.repository.create(payload)
        twin = FarmTwin(farm_id=farm_id)
        twin.state.context["farm_name"] = name
        twin.state.context["location"] = location or ""
        twin.state.context["farm_size"] = farm_size or ""
        self._farm_twins[farm_id] = twin
        return {"farm": payload, "farm_twin": twin.snapshot()}

    def get_farm(self, farm_id: str) -> dict[str, Any] | None:
        record = self.repository.get(farm_id)
        if record is None:
            return None
        return {"farm": record}

    def update_farm(self, farm_id: str, **updates: Any) -> dict[str, Any]:
        record = self.repository.update(farm_id, updates)
        return {"farm": record}

    def delete_farm(self, farm_id: str) -> bool:
        return self.repository.delete(farm_id)
