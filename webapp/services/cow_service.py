"""Application service for cow operations."""

from __future__ import annotations

from typing import Any

from webapp.digital_twin.cow_twin import CowTwin
from webapp.repositories.cow_repository import CowRepository


class CowService:
    """Business logic for cow registration and updates."""

    def __init__(self, repository: CowRepository | None = None) -> None:
        self.repository = repository or CowRepository()
        self._cow_twins: dict[str, CowTwin] = {}

    def register_cow(self, cow_id: str, name: str | None = None, **metadata: Any) -> dict[str, Any]:
        payload = {"cow_id": cow_id, "name": name or cow_id}
        payload.update(metadata)
        self.repository.create(payload)
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        self._cow_twins[cow_id] = twin
        return {"cow": payload, "cow_twin": twin.snapshot()}

    def update_cow(self, cow_id: str, **updates: Any) -> dict[str, Any]:
        record = self.repository.update(cow_id, updates)
        return {"cow": record}

    def delete_cow(self, cow_id: str) -> bool:
        deleted = self.repository.delete(cow_id)
        if deleted:
            self._cow_twins.pop(cow_id, None)
        return deleted

    def get_cows(self) -> list[dict[str, Any]]:
        return [{"cow": item} for item in self.repository.list()]
