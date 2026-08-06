"""Application service for cow operations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import streamlit as st

from webapp.digital_twin.cow_twin import CowTwin
from webapp.repositories.cow_repository import CowRepository
from webapp.utils.logging import log_event


class CowService:
    """Business logic for cow registration and updates."""

    def __init__(self, repository: CowRepository | None = None) -> None:
        self.repository = repository or CowRepository()
        self._cow_twins: dict[str, CowTwin] = {}

    def _normalize_cow_record(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {
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
        print("--------------------------------")
        print("DEBUG COW INSERT")
        print("--------------------------------")

        print("Current user:", st.session_state.get("user"))

        print("Current farm_id:", st.session_state.get("farm_id"))

        print("Current farm:", st.session_state.get("farm"))

        print("Payload:", payload)

        auth_service = st.session_state.get("auth_service")
        try:
            auth_val = auth_service.current_user() if auth_service else None
        except Exception as e:
            auth_val = f"ERROR: {e}"
        print("Auth session:", auth_val)

        record = self.repository.create(payload)
        cow_record = self._normalize_cow_record(record)
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

    def get_cows(self) -> list[dict[str, Any]]:
        print("[DEBUG] CowService.get_cows() called")
        cows = [self._normalize_cow_record(item) for item in self.repository.list()]
        log_event("debug_cow_service_get_cows", cow_count=len(cows))
        return cows
