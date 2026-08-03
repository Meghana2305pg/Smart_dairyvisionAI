"""Application service for farm operations."""

from __future__ import annotations

import uuid
from typing import Any

from webapp.digital_twin.farm_twin import FarmTwin
from webapp.repositories.farm_repository import FarmRepository


class FarmService:
    """Business logic for farm creation, reading, updates, and deletion."""

    def __init__(self, repository: FarmRepository | None = None) -> None:
        self.repository = repository or FarmRepository()
        self._farm_twins: dict[str, FarmTwin] = {}

    def _normalize_farm_record(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(record)
        normalized["farm_id"] = str(record.get("farm_id") or record.get("id") or "")
        normalized["name"] = record.get("name") or record.get("farm_name") or ""
        size_value = record.get("farm_size")
        normalized["farm_size"] = str(size_value) if size_value is not None else ""
        normalized["location"] = record.get("location") or ""
        if record.get("id") and not record.get("farm_id"):
            normalized["farm_id"] = str(record.get("id"))
        return normalized

    def _build_insert_payload(
        self,
        farm_id: str,
        name: str,
        location: str | None = None,
        farm_size: str | None = None,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            farm_id_value = str(uuid.UUID(farm_id))
        except (ValueError, TypeError):
            farm_id_value = str(uuid.uuid4())

        payload: dict[str, Any] = {
            "id": farm_id_value,
            "farm_name": name,
            "location": location or "",
            "farm_size": int(farm_size) if farm_size is not None and str(farm_size).strip() != "" else 0,
        }
        if owner_id is not None:
            payload["owner_id"] = owner_id
        return payload

    def create_farm(
        self,
        farm_id: str,
        name: str,
        location: str | None = None,
        farm_size: str | None = None,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        payload = self._build_insert_payload(
            farm_id=farm_id,
            name=name,
            location=location,
            farm_size=farm_size,
            owner_id=owner_id,
        )

        record = self.repository.create(payload)
        normalized = self._normalize_farm_record(record)
        twin = FarmTwin(farm_id=farm_id)
        twin.state.context["farm_name"] = name
        twin.state.context["location"] = location or ""
        twin.state.context["farm_size"] = farm_size or ""
        self._farm_twins[farm_id] = twin
        return {"farm": normalized, "farm_twin": twin.snapshot()}

    def get_farm(self, farm_id: str) -> dict[str, Any] | None:
        record = self.repository.get(farm_id)
        if record is None:
            return None
        return {"farm": self._normalize_farm_record(record)}

    def get_farm_for_owner(self, owner_id: str) -> dict[str, Any] | None:
        farms = self.repository.list_by_owner(owner_id)
        if not farms:
            return None
        return {"farm": self._normalize_farm_record(farms[0])}

    def update_farm(self, farm_id: str, **updates: Any) -> dict[str, Any]:
        record = self.repository.update(farm_id, updates)
        return {"farm": record}

    def delete_farm(self, farm_id: str) -> bool:
        return self.repository.delete(farm_id)
