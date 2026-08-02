"""Reusable Supabase client wrapper for the application service layer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client


class SupabaseClient:
    """Wrapper around the official Supabase Python client."""

    _instance: "SupabaseClient | None" = None

    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_ANON_KEY", "")
        self._client = None
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

    @property
    def client(self) -> Any:
        if self._client is None:
            raise RuntimeError("Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        return self._client

    def _extract_record(self, response: Any) -> dict[str, Any] | None:
        data = getattr(response, "data", None)
        if isinstance(data, list):
            if not data:
                return None
            record = data[0]
            return record if isinstance(record, dict) else None
        if isinstance(data, dict):
            return data
        return None

    def insert(self, table_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table(table_name).insert(payload).execute()
        record = self._extract_record(response)
        return record or payload

    def update(self, table_name: str, identifier: str, payload: dict[str, Any]) -> dict[str, Any]:
        query = self.client.table(table_name).update(payload)
        for column in ("id", "farm_id", "cow_id"):
            response = query.eq(column, identifier).execute()
            record = self._extract_record(response)
            if record is not None:
                return record
        return payload

    def delete(self, table_name: str, identifier: str) -> bool:
        query = self.client.table(table_name).delete()
        for column in ("id", "farm_id", "cow_id"):
            response = query.eq(column, identifier).execute()
            if getattr(response, "data", None) not in (None, []):
                return True
        return False

    def list(self, table_name: str) -> list[dict[str, Any]]:
        response = self.client.table(table_name).select("*").execute()
        data = getattr(response, "data", None)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def get(self, table_name: str, identifier: str) -> dict[str, Any] | None:
        for column in ("id", "farm_id", "cow_id"):
            response = self.client.table(table_name).select("*").eq(column, identifier).execute()
            record = self._extract_record(response)
            if record is not None:
                return record
        return None
