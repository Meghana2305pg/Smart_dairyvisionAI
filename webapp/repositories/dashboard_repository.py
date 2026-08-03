"""Repository for dashboard aggregation data."""

from __future__ import annotations

from typing import Any

from .supabase_client import SupabaseClient


class DashboardRepository:
    """Thin repository that exposes persisted data for dashboard assembly."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def get_farms(self) -> list[dict[str, Any]]:
        return self.client.list("farms")

    def get_cows(self) -> list[dict[str, Any]]:
        return self.client.list("cows")

    def get_observations(self) -> list[dict[str, Any]]:
        return self.client.list("observations")

    def get_snapshots(self) -> list[dict[str, Any]]:
        return self.client.list("twin_snapshots")
