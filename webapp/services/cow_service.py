"""Application service for cow operations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import streamlit as st

from webapp.digital_twin.cow_twin import CowTwin
from webapp.repositories.cow_repository import CowRepository


class CowService:
    """Business logic for cow registration and updates."""

    def __init__(self, repository: CowRepository | None = None) -> None:
        self.repository = repository or CowRepository()
        self._cow_twins: dict[str, CowTwin] = {}

    def _normalize_cow_record(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {
            "id": record.get("id"),
            "cow_id": record.get("cow_tag") or record.get("cow_id"),
            "name": record.get("cow_name") or record.get("name"),
            "breed": record.get("breed"),
            "weight": record.get("weight"),
            "farm_id": record.get("farm_id"),
            "created_at": record.get("created_at"),
        }
        date_of_birth = record.get("date_of_birth")
        if date_of_birth:
            normalized["age_months"] = self._calculate_age_months(date_of_birth)

        if "status" in record:
            normalized["status"] = record.get("status")
        if "notes" in record:
            normalized["notes"] = record.get("notes")

        return normalized

    def _calculate_age_months(self, date_of_birth: str | None) -> int | None:
        if not date_of_birth:
            return None

        try:
            dob = datetime.fromisoformat(str(date_of_birth)).date()
        except ValueError:
            return None

        age_days = (date.today() - dob).days
        return max(0, int(age_days / 30.4375))

    def _date_of_birth_from_age_months(self, age_months: int | float | None) -> str | None:
        if age_months is None:
            return None

        try:
            age_months_value = int(age_months)
        except (TypeError, ValueError):
            return None

        age_days = int(round(age_months_value * 30.4375))
        return (date.today() - timedelta(days=age_days)).isoformat()

    def _build_insert_payload(
        self,
        cow_id: str,
        name: str,
        farm_id: str | None = None,
        breed: str | None = None,
        age_months: int | float | None = None,
        weight: int | float | None = None,
        lactation_number: int | None = None,
        pregnant: bool | None = None,
        photo_url: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "cow_tag": cow_id,
            "cow_name": name,
            "breed": breed or "Unknown",
            "lactation_number": int(lactation_number) if lactation_number is not None else 1,
            "pregnant": bool(pregnant) if pregnant is not None else False,
            "photo_url": photo_url or "",
        }

        if farm_id is not None:
            payload["farm_id"] = farm_id
        if weight is not None:
            payload["weight"] = float(weight)
        if age_months is not None:
            date_of_birth = self._date_of_birth_from_age_months(age_months)
            if date_of_birth is not None:
                payload["date_of_birth"] = date_of_birth

        return payload

    def _build_update_payload(self, updates: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        if "name" in updates:
            payload["cow_name"] = updates["name"]
        if "breed" in updates:
            payload["breed"] = updates["breed"]
        if "weight" in updates:
            payload["weight"] = float(updates["weight"])
        if "farm_id" in updates:
            payload["farm_id"] = updates["farm_id"]
        if "age_months" in updates:
            date_of_birth = self._date_of_birth_from_age_months(updates["age_months"])
            if date_of_birth is not None:
                payload["date_of_birth"] = date_of_birth
        if "lactation_number" in updates:
            payload["lactation_number"] = int(updates["lactation_number"])
        if "pregnant" in updates:
            payload["pregnant"] = bool(updates["pregnant"])
        if "photo_url" in updates:
            payload["photo_url"] = updates["photo_url"]

        return payload

    def register_cow(
        self,
        cow_id: str,
        name: str | None = None,
        farm_id: str | None = None,
        **metadata: Any,
    ) -> dict[str, Any]:
        cow_name = name or cow_id
        current_farm_id = farm_id or st.session_state.get("farm_id")
        payload = self._build_insert_payload(
            cow_id=cow_id,
            name=cow_name,
            farm_id=current_farm_id,
            breed=metadata.get("breed"),
            age_months=metadata.get("age_months"),
            weight=metadata.get("weight"),
            lactation_number=metadata.get("lactation_number"),
            pregnant=metadata.get("pregnant"),
            photo_url=metadata.get("photo_url"),
        )

        auth_service = st.session_state.get("auth_service")
        try:
            auth_val = auth_service.current_user() if auth_service else None
        except Exception as e:
            auth_val = f"ERROR: {e}"

        record = self.repository.create(payload)
        cow_record = self._normalize_cow_record(record)
        cow_record["id"] = record.get("id")
        cow_record["cow_id"] = cow_id
        cow_record["name"] = cow_name

        if "status" in metadata:
            cow_record["status"] = metadata["status"]
        if "notes" in metadata:
            cow_record["notes"] = metadata["notes"]
        if "age_months" in metadata:
            cow_record["age_months"] = int(metadata["age_months"])

        twin = CowTwin(cow_id=cow_id, name=cow_name)
        self._cow_twins[cow_id] = twin
        return {"cow": cow_record, "cow_twin": twin.snapshot()}

    def update_cow(self, cow_id: str, **updates: Any) -> dict[str, Any]:
        payload = self._build_update_payload(updates)
        record = self.repository.update(cow_id, payload)
        return {"cow": self._normalize_cow_record(record)}

    def delete_cow(self, cow_id: str) -> bool:
        deleted = self.repository.delete(cow_id)
        if deleted:
            self._cow_twins.pop(cow_id, None)
        return deleted

    def load_twin_from_snapshots(self, cow_id: str) -> CowTwin | None:
        """Load and reconstruct a digital twin from persisted Supabase snapshots.
        
        This enables cross-session twin recovery. If the twin doesn't exist in memory,
        this method loads it from the twin_snapshots table and reconstructs the state.
        
        Args:
            cow_id: Cow UUID
            
        Returns:
            Reconstructed CowTwin with latest snapshot state, or None if no snapshots exist
        """
        # Check if already in memory
        existing_twin = self._cow_twins.get(cow_id)
        if existing_twin is not None:
            return existing_twin
        
        # Import here to avoid circular dependency
        from webapp.repositories.snapshot_repository import SnapshotRepository
        
        snapshot_repo = SnapshotRepository()
        latest_snapshot = snapshot_repo.get_latest_for_cow(cow_id)
        
        if latest_snapshot is None:
            # No persisted snapshots; create empty twin
            cow_record = self.repository.get(cow_id)
            twin = CowTwin(
                cow_id=cow_id,
                name=cow_record.get("cow_name") or cow_record.get("name") if cow_record else cow_id,
            )
            self._cow_twins[cow_id] = twin
            return twin
        
        # Reconstruct twin from latest snapshot
        cow_record = self.repository.get(cow_id)
        twin = CowTwin(
            cow_id=cow_id,
            name=cow_record.get("cow_name") or cow_record.get("name") if cow_record else cow_id,
        )
        
        # Restore latest state from snapshot
        snapshot_data = latest_snapshot
        
        # Restore prediction, health, explanation
        if snapshot_data.get("prediction"):
            twin.latest_prediction = snapshot_data["prediction"]
        if snapshot_data.get("health"):
            twin.latest_health = snapshot_data["health"]
        if snapshot_data.get("explanation"):
            twin.latest_explanation = snapshot_data["explanation"]
        if snapshot_data.get("recommendations"):
            twin.recommendations = snapshot_data["recommendations"]
        
        # Restore twin status
        if snapshot_data.get("twin_status"):
            twin.state.status = snapshot_data["twin_status"]
        
        # Restore last_updated from created_at
        if snapshot_data.get("created_at"):
            try:
                from datetime import datetime
                if isinstance(snapshot_data["created_at"], str):
                    twin.state.last_updated = datetime.fromisoformat(snapshot_data["created_at"])
                else:
                    twin.state.last_updated = snapshot_data["created_at"]
            except Exception:
                pass
        
        # Cache in memory
        self._cow_twins[cow_id] = twin
        return twin

    def get_cows(self) -> list[dict[str, Any]]:
        return [self._normalize_cow_record(item) for item in self.repository.list()]
