"""Repository for twin snapshot persistence operations."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .supabase_client import SupabaseClient


class SnapshotRepository:
    """Repository for twin snapshot persistence to Supabase twin_snapshots table."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()

    def _serialize_snapshot_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Serialize snapshot data for safe JSON storage in JSONB columns."""
        serialized: dict[str, Any] = {
            "cow_id": payload.get("cow_id"),
            "observation_id": payload.get("observation_id"),
            "twin_status": payload.get("twin_status"),
        }

        # Serialize JSONB fields with safe conversion
        for jsonb_field in ["prediction", "health", "weather", "explanation", "recommendations"]:
            if jsonb_field in payload:
                value = payload[jsonb_field]
                # If already dict/list, keep as-is (Supabase will handle JSONB conversion)
                # If it's a complex object, convert to dict
                if value is not None:
                    if isinstance(value, (dict, list)):
                        serialized[jsonb_field] = value
                    else:
                        # Try to convert to dict representation
                        try:
                            serialized[jsonb_field] = self._to_serializable(value)
                        except Exception:
                            serialized[jsonb_field] = None
                else:
                    serialized[jsonb_field] = None

        return serialized

    def _to_serializable(self, obj: Any) -> Any:
        """Convert non-JSON-serializable objects to JSON-safe format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._to_serializable(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # Handle dataclass objects
            return self._to_serializable(obj.__dict__)
        else:
            # For other types (int, float, str, bool, None), return as-is
            return obj

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist a twin snapshot to Supabase twin_snapshots table.
        
        Expected payload fields:
        - cow_id: UUID (required)
        - observation_id: UUID (optional, if snapshot is associated with specific observation)
        - prediction: dict/JSONB (optional)
        - health: dict/JSONB (optional)
        - weather: dict/JSONB (optional)
        - explanation: list/JSONB (optional)
        - recommendations: list/JSONB (optional)
        - twin_status: str (required)
        """
        serialized = self._serialize_snapshot_payload(payload)
        return self.client.insert("twin_snapshots", serialized)

    def get_latest_for_cow(self, cow_id: str) -> dict[str, Any] | None:
        """Retrieve the most recent snapshot for a cow.
        
        Returns the snapshot with the latest created_at timestamp.
        """
        snapshots = self.client.list_by("twin_snapshots", {"cow_id": cow_id})
        if not snapshots:
            return None
        
        # Sort by created_at descending and return most recent
        sorted_snapshots = sorted(
            snapshots,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        return sorted_snapshots[0] if sorted_snapshots else None

    def get_for_observation(self, observation_id: str) -> dict[str, Any] | None:
        """Retrieve snapshot associated with a specific observation."""
        snapshots = self.client.list_by("twin_snapshots", {"observation_id": observation_id})
        return snapshots[0] if snapshots else None

    def list_for_cow(self, cow_id: str) -> list[dict[str, Any]]:
        """Retrieve all snapshots for a cow, ordered by created_at descending."""
        snapshots = self.client.list_by("twin_snapshots", {"cow_id": cow_id})
        # Sort by created_at descending (most recent first)
        return sorted(
            snapshots,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

    def list(self) -> list[dict[str, Any]]:
        """Retrieve all snapshots."""
        return self.client.list("twin_snapshots")

    def delete(self, snapshot_id: str) -> bool:
        """Delete a snapshot by ID."""
        return self.client.delete("twin_snapshots", snapshot_id)

    def update(self, snapshot_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Update an existing snapshot."""
        serialized = self._serialize_snapshot_payload(payload)
        return self.client.update("twin_snapshots", snapshot_id, serialized)
