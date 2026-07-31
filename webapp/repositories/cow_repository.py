"""Repository for cow persistence operations."""

from __future__ import annotations

from typing import Any

from .supabase_client import SupabaseClient


class CowRepository:
    """CRUD repository for cows using the shared Supabase client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.insert("cows", payload)

    def get(self, cow_id: str) -> dict[str, Any] | None:
        return self.client.get("cows", cow_id)

    def update(self, cow_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.update("cows", cow_id, payload)

    def delete(self, cow_id: str) -> bool:
        return self.client.delete("cows", cow_id)

    def list(self) -> list[dict[str, Any]]:
        return self.client.list("cows")
