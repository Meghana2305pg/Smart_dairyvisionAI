"""Reusable Supabase client wrapper for the application service layer."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client

from webapp.utils.logging import log_event, log_error

try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception


class SupabaseClient:
    """Wrapper around the official Supabase Python client."""

    _instance: "SupabaseClient | None" = None

    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_ANON_KEY", "")
        self._client = None
        self._store: dict[str, Any] = {}
        self._tables: dict[str, list[dict[str, Any]]] = {}
        if self.url and self.key:
            self._client = create_client(self.url, self.key)

    @classmethod
    def from_env(cls) -> "SupabaseClient":
        """Load configuration from .env and reuse a singleton client."""
        env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=env_path, override=False)
        env_url = os.getenv("SUPABASE_URL", "")
        env_key = os.getenv("SUPABASE_ANON_KEY", "")

        if cls._instance is None:
            cls._instance = cls(url=env_url, key=env_key)
        elif cls._instance.url != env_url or cls._instance.key != env_key:
            cls._instance = cls(url=env_url, key=env_key)
        return cls._instance

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    def reset_in_memory_store(self) -> None:
        """Clear all in-memory mock tables and state (useful for test isolation)."""
        self._tables.clear()
        self._store.clear()

    @property
    def client(self) -> Any:
        if self._client is None:
            raise RuntimeError("Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        return self._client

    def get_table(self, table_name: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(table_name, [])

    def _remote_available(self) -> bool:
        return self._client is not None and hasattr(self._client, "table")

    def _identifier_fields(self) -> list[str]:
        return ["id", "farm_id", "cow_id"]

    def _remote_select(self, table_name: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        query = self.client.table(table_name).select("*")
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        try:
            response = query.execute()
        except APIError as exc:
            self._logger_remote_select_failure(table_name, exc)
            return self._fallback_local_select(table_name, filters)

        if getattr(response, "error", None):
            raise RuntimeError(f"Supabase select failed: {response.error}")
        return getattr(response, "data", []) or []

    def insert(self, table_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized_payload = self._normalize_payload(payload)
        log_event("supabase_insert_attempt", table=table_name, insert_payload=normalized_payload)
        if self._remote_available():
            try:
                response = (
                    self.client
                    .table(table_name)
                    .insert(normalized_payload)
                    .execute()
                )
            except APIError as exc:
                log_error(
                    "supabase_insert_api_error",
                    table=table_name,
                    insert_payload=normalized_payload,
                    error=str(exc),
                )
                raise RuntimeError(f"Supabase insert failed: {exc}") from exc

            response_error = getattr(response, "error", None)
            response_data = getattr(response, "data", None)
            if response_error:
                log_error(
                    "supabase_insert_response_error",
                    table=table_name,
                    insert_payload=normalized_payload,
                    response_error=str(response_error),
                    response_data=response_data,
                )
                raise RuntimeError(f"Supabase insert failed: {response_error}")

            log_event(
                "supabase_insert_response",
                table=table_name,
                response_data=response_data,
            )
            if isinstance(response_data, list) and response_data:
                return response_data[0]
            if isinstance(response_data, dict):
                return response_data
            return normalized_payload

        table = self.get_table(table_name)
        table.append(normalized_payload)
        log_event("supabase_local_insert", table=table_name, insert_payload=normalized_payload)
        return normalized_payload

    def _fallback_local_select(self, table_name: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if filters is None:
            return list(self.get_table(table_name))
        return [item for item in self.get_table(table_name) if all(item.get(column) == value for column, value in filters.items())]

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, datetime):
                normalized[key] = value.isoformat()
            else:
                normalized[key] = value
        return normalized

    def _logger_remote_insert_failure(self, table_name: str, exc: Exception) -> None:
        pass

    def _logger_remote_select_failure(self, table_name: str, exc: Exception) -> None:
        pass

    def _logger_remote_update_failure(self, table_name: str, key: str, exc: Exception) -> None:
        pass

    def _logger_remote_delete_failure(self, table_name: str, key: str, exc: Exception) -> None:
        pass

    def _logger_remote_get_failure(self, table_name: str, key: str, exc: Exception) -> None:
        pass

    def update(self, table_name: str, identifier: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._remote_available():
            last_error: Exception | None = None
            for key in self._identifier_fields():
                try:
                    response = self.client.table(table_name).update(payload).eq(key, identifier).execute()
                except APIError as exc:
                    self._logger_remote_update_failure(table_name, key, exc)
                    return self._fallback_local_update(table_name, identifier, payload)

                if getattr(response, "error", None):
                    error = RuntimeError(f"Supabase update failed for {key}: {response.error}")
                    last_error = error
                    if "does not exist" in str(response.error).lower() or "could not find" in str(response.error).lower():
                        continue
                    raise error
                data = getattr(response, "data", None)
                if isinstance(data, list) and data:
                    return data[0]
                if isinstance(data, dict):
                    return data
                return payload
            if last_error is not None:
                raise last_error

        return self._fallback_local_update(table_name, identifier, payload)

    def _fallback_local_update(self, table_name: str, identifier: str, payload: dict[str, Any]) -> dict[str, Any]:
        table = self.get_table(table_name)
        for item in table:
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                item.update(payload)
                return item
        raise RuntimeError(f"Local update failed: {identifier} not found in {table_name}")

    def delete(self, table_name: str, identifier: str) -> bool:
        if self._remote_available():
            last_error: Exception | None = None
            for key in self._identifier_fields():
                try:
                    response = self.client.table(table_name).delete().eq(key, identifier).execute()
                except APIError as exc:
                    self._logger_remote_delete_failure(table_name, key, exc)
                    return self._fallback_local_delete(table_name, identifier)

                if getattr(response, "error", None):
                    error = RuntimeError(f"Supabase delete failed for {key}: {response.error}")
                    last_error = error
                    if "does not exist" in str(response.error).lower() or "could not find" in str(response.error).lower():
                        continue
                    raise error
                data = getattr(response, "data", None)
                if isinstance(data, list) and data:
                    return True
                if isinstance(data, dict):
                    return bool(data)
                return False
            if last_error is not None:
                raise last_error

        return self._fallback_local_delete(table_name, identifier)

    def _fallback_local_delete(self, table_name: str, identifier: str) -> bool:
        table = self.get_table(table_name)
        for index, item in enumerate(table):
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                table.pop(index)
                return True
        return False

    def list(self, table_name: str) -> list[dict[str, Any]]:
        if self._remote_available():
            return self._remote_select(table_name)

        return list(self.get_table(table_name))

    def list_by(self, table_name: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        if self._remote_available():
            return self._remote_select(table_name, filters)

        return [item for item in self.get_table(table_name) if all(item.get(column) == value for column, value in filters.items())]

    def get(self, table_name: str, identifier: str) -> dict[str, Any] | None:
        if self._remote_available():
            last_error: Exception | None = None
            for key in self._identifier_fields():
                try:
                    response = self.client.table(table_name).select("*").eq(key, identifier).execute()
                except APIError as exc:
                    self._logger_remote_get_failure(table_name, key, exc)
                    return self._fallback_local_get(table_name, identifier)

                if getattr(response, "error", None):
                    error = RuntimeError(f"Supabase get failed for {key}: {response.error}")
                    last_error = error
                    if "does not exist" in str(response.error).lower() or "could not find" in str(response.error).lower():
                        continue
                    raise error
                items = getattr(response, "data", []) or []
                if items:
                    return items[0]
            if last_error is not None:
                raise last_error
            return None

        return self._fallback_local_get(table_name, identifier)

    def _fallback_local_get(self, table_name: str, identifier: str) -> dict[str, Any] | None:
        for item in self.get_table(table_name):
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                return item
        return None
