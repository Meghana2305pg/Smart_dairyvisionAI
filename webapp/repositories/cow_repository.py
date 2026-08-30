"""Repository for cow persistence operations."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from .supabase_client import SupabaseClient


class CowRepository:
    """CRUD repository for cows using the shared Supabase client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def _matches_identifier(self, item: dict[str, Any], cow_id: str) -> bool:
        return any(str(item.get(key) or "") == cow_id for key in ("id", "cow_id", "cow_tag"))

    def _is_uuid(self, value: str) -> bool:
        try:
            UUID(value)
            return True
        except (TypeError, ValueError):
            return False

    def _unwrap_response(self, response: Any) -> dict[str, Any] | None:
        if getattr(response, "error", None):
            raise RuntimeError(f"Supabase cow repository operation failed: {response.error}")
        data = getattr(response, "data", None)
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return None

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.insert("cows", payload)

    def get(self, cow_id: str) -> dict[str, Any] | None:

        if self.client._remote_available():
            # Remote cows table stores UUID in `id` and human tag in `cow_tag`.
            if self._is_uuid(cow_id):
                records = self.client.list_by("cows", {"id": cow_id})

                if records:
                    result = records[0]

                    return result

            records = self.client.list_by("cows", {"cow_tag": cow_id})

            if records:
                result = records[0]

                return result

            records = self.client.list_by("cows", {"cow_id": cow_id})

            if records:
                result = records[0]

                return result

        for item in self.client.get_table("cows"):
            if self._matches_identifier(item, cow_id):

                return item


        return None

    def update(self, cow_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.client._remote_available():
            response = self.client.client.table("cows").update(payload).eq("cow_tag", cow_id).execute()
            record = self._unwrap_response(response)
            if record is None:
                raise RuntimeError(f"Supabase cow update failed: cow_tag {cow_id} not found")
            return record

        for item in self.client.get_table("cows"):
            if self._matches_identifier(item, cow_id):
                item.update(payload)
                return item

        raise RuntimeError(f"Cow with ID {cow_id} not found")

    def delete(self, cow_id: str) -> bool:
        if self.client._remote_available():
            response = self.client.client.table("cows").delete().eq("cow_tag", cow_id).execute()
            if getattr(response, "error", None):
                raise RuntimeError(f"Supabase cow delete failed: {response.error}")
            data = getattr(response, "data", None)
            if isinstance(data, list) and data:
                return True
            if isinstance(data, dict):
                return bool(data)
            return False

        table = self.client.get_table("cows")
        for index, item in enumerate(table):
            if self._matches_identifier(item, cow_id):
                table.pop(index)
                return True

        return False

    def list(self) -> list[dict[str, Any]]:
        return self.client.list("cows")
