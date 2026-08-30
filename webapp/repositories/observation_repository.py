"""Repository for observation persistence operations."""

from __future__ import annotations

from typing import Any

from .supabase_client import SupabaseClient


class ObservationRepository:
    """Simple repository for observations using the shared Supabase client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:

        return self.client.insert("observations", payload)

    def list_for_cow(self, cow_id: str) -> list[dict[str, Any]]:
        return [item for item in self.client.list("observations") if item.get("cow_id") == cow_id]

    def list(self) -> list[dict[str, Any]]:
        return self.client.list("observations")
