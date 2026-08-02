"""Repository for farm persistence operations."""

from __future__ import annotations

from typing import Any

from .supabase_client import SupabaseClient


class FarmRepository:
    """CRUD repository for farms using the shared Supabase client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.insert("farms", payload)

    def get(self, farm_id: str) -> dict[str, Any] | None:
        return self.client.get("farms", farm_id)

    def list_by_owner(self, owner_id: str) -> list[dict[str, Any]]:
        response = self.client.client.table("farms").select("*").eq("owner_id", owner_id).execute()
        data = getattr(response, "data", None)
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []

    def update(self, farm_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.update("farms", farm_id, payload)

    def delete(self, farm_id: str) -> bool:
        return self.client.delete("farms", farm_id)

    def list(self) -> list[dict[str, Any]]:
        return self.client.list("farms")
