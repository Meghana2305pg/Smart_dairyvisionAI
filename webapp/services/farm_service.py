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
        self._current_farm: dict[str, Any] | None = None
        self._current_farm_twin: dict[str, Any] | None = None

    def _normalize_farm_record(self, record: dict[str, Any] | None) -> dict[str, Any] | None:
        if record is None:
            return None
        normalized = dict(record)
        normalized["farm_id"] = record.get("id") or record.get("farm_id")
        normalized["name"] = record.get("farm_name") or record.get("name") or ""
        return normalized

    def create_farm(
        self,
        farm_id: str,
        name: str,
        location: str | None = None,
        farm_size: str | None = None,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "id": farm_id,
            "owner_id": owner_id,
            "farm_name": name,
            "location": location or "",
            "farm_size": farm_size or "",
        }
        self.repository.create(payload)
        twin = FarmTwin(farm_id=farm_id)
        twin.state.context["farm_name"] = name
        twin.state.context["location"] = location or ""
        twin.state.context["farm_size"] = farm_size or ""
        self._farm_twins[farm_id] = twin
        normalized = self._normalize_farm_record(payload)
        self._current_farm = normalized
        self._current_farm_twin = twin.snapshot()
        return {"farm": normalized, "farm_twin": twin.snapshot()}

    def get_current_farm(self) -> dict[str, Any] | None:
        if self._current_farm is not None:
            return self._current_farm
        return None

    def get_farm_for_owner(self, owner_id: str) -> dict[str, Any] | None:
        records = self.repository.list_by_owner(owner_id)
        if not records:
            return None
        record = records[0]
        normalized = self._normalize_farm_record(record)
        self._current_farm = normalized
        return normalized

    def get_farm(self, farm_id: str) -> dict[str, Any] | None:
        record = self.repository.get(farm_id)
        if record is None:
            return None
        normalized = self._normalize_farm_record(record)
        self._current_farm = normalized
        return {"farm": normalized}

    def update_farm(self, farm_id: str, **updates: Any) -> dict[str, Any]:
        record = self.repository.update(farm_id, updates)
        return {"farm": record}

    def delete_farm(self, farm_id: str) -> bool:
        return self.repository.delete(farm_id)
