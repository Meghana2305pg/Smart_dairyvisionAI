"""Application service for authentication workflows backed by Supabase Auth."""

from __future__ import annotations

from typing import Any

from webapp.repositories.supabase_client import SupabaseClient


class AuthService:
    """Authenticate users with the official Supabase Python client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()
        self._current_user: dict[str, Any] | None = None

    def register_user(self, email: str, password: str, full_name: str | None = None, phone: str | None = None) -> dict[str, Any]:
        response = self.client.client.auth.sign_up({"email": email, "password": password})
        if response.user is None:
            raise RuntimeError("Supabase registration did not return a user.")

        user_payload = {
            "id": response.user.id,
            "email": email,
            "full_name": full_name or "",
            "phone": phone or "",
            "profile": {
                "full_name": full_name or "",
                "phone": phone or "",
            },
        }
        self._current_user = user_payload
        return user_payload

    def login(self, email: str, password: str) -> bool:
        response = self.client.client.auth.sign_in_with_password({"email": email, "password": password})
        if response.user is None:
            return False
        self._current_user = {
            "id": response.user.id,
            "email": response.user.email,
            "full_name": getattr(response.user, "user_metadata", {}).get("full_name") or "",
            "session": response.session.model_dump() if hasattr(response.session, "model_dump") else response.session,
        }
        return True

    def logout(self) -> None:
        try:
            self.client.client.auth.sign_out()
        finally:
            self._current_user = None

    def current_user(self) -> dict[str, Any] | None:
        if self._current_user is not None:
            return self._current_user
        return self.get_authenticated_user()

    def get_authenticated_user(self) -> dict[str, Any] | None:
        """Restore the active user from the provider-backed Supabase session."""
        try:
            if not self.client.is_configured:
                return None

            response = self.client.client.auth.get_user()
            user = getattr(response, "user", None)
            if user is None:
                return None

            user_metadata = getattr(user, "user_metadata", {}) or {}
            full_name = user_metadata.get("full_name") or user_metadata.get("name") or getattr(user, "email", None) or ""
            self._current_user = {
                "id": getattr(user, "id", None),
                "email": getattr(user, "email", None),
                "full_name": full_name,
                "profile": {
                    "full_name": full_name,
                    "phone": user_metadata.get("phone") or "",
                },
                "session": getattr(response, "session", None),
            }
            return self._current_user
        except Exception:
            return None
