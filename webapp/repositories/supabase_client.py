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

    def insert(self, table_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        table = self.get_table(table_name)
        table.append(payload)
        return payload

    def update(self, table_name: str, identifier: str, payload: dict[str, Any]) -> dict[str, Any]:
        table = self.get_table(table_name)
        for item in table:
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                item.update(payload)
                return item
        return payload

    def delete(self, table_name: str, identifier: str) -> bool:
        table = self.get_table(table_name)
        for index, item in enumerate(table):
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                table.pop(index)
                return True
        return False

    def list(self, table_name: str) -> list[dict[str, Any]]:
        return list(self.get_table(table_name))

    def get(self, table_name: str, identifier: str) -> dict[str, Any] | None:
        for item in self.list(table_name):
            if str(item.get("id") or item.get("farm_id") or item.get("cow_id")) == identifier:
                return item
        return None
