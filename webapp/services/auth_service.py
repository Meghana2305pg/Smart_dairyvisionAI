"""Application service for authentication workflows backed by Supabase Auth."""

from __future__ import annotations

import traceback
from typing import Any

from webapp.repositories.supabase_client import SupabaseClient


class AuthService:
    """Authenticate users with the official Supabase Python client."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient.from_env()
        self._current_user: dict[str, Any] | None = None
        self._session: dict[str, Any] | None = None

    def _build_user_payload(self, user: Any) -> dict[str, Any]:
        payload = {
            "id": getattr(user, "id", None) or getattr(user, "user_id", None) or "",
            "email": getattr(user, "email", "") or "",
            "full_name": "",
            "phone": "",
        }
        metadata = getattr(user, "user_metadata", None) or getattr(user, "app_metadata", None) or {}
        if isinstance(metadata, dict):
            payload["full_name"] = metadata.get("full_name") or metadata.get("name") or payload["full_name"]
            payload["phone"] = metadata.get("phone") or payload["phone"]
        if getattr(user, "full_name", None):
            payload["full_name"] = getattr(user, "full_name")
        return payload

    def _load_session(self, session_data: dict[str, Any] | None) -> None:
        if session_data is None:
            return
        self._session = session_data
        # Apply session to supabase auth and ensure PostgREST uses the
        # authenticated access token for subsequent requests (RLS requires this).
        if hasattr(self.client.client.auth, "set_session"):
            try:
                self.client.client.auth.set_session(session_data)
            except Exception:
                pass

        # Extract access token from the session object/dict and apply it to
        # the PostgREST/http client Authorization header. Do this in one
        # place only to avoid duplicating session state.
        access_token = None
        try:
            if isinstance(session_data, dict):
                access_token = session_data.get("access_token") or session_data.get("accessToken")
            else:
                access_token = getattr(session_data, "access_token", None) or getattr(session_data, "accessToken", None)
        except Exception:
            access_token = None

        if access_token:
            try:
                postgrest = getattr(self.client.client, "postgrest", None)
                if postgrest is not None:
                    # postgrest.headers (SyncPostgrestClient.headers) and
                    # postgrest.session.headers (httpx.Client) both propagate
                    # to outgoing requests; set both where available.
                    try:
                        if getattr(postgrest, "headers", None) is not None:
                            postgrest.headers["Authorization"] = f"Bearer {access_token}"
                    except Exception:
                        pass
                    try:
                        if getattr(postgrest, "session", None) is not None and hasattr(postgrest.session, "headers"):
                            postgrest.session.headers["Authorization"] = f"Bearer {access_token}"
                    except Exception:
                        pass
                    # Also update client-level default headers (SyncClientOptions)
                    try:
                        opts = getattr(self.client.client, "options", None)
                        if opts is not None and getattr(opts, "headers", None) is not None:
                            opts.headers["Authorization"] = f"Bearer {access_token}"
                    except Exception:
                        pass
            except Exception:
                pass

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
        if hasattr(response, "session") and response.session is not None:
            self._load_session(response.session.model_dump() if hasattr(response.session, "model_dump") else response.session)
        return user_payload

    def login(self, email: str, password: str) -> bool:
        normalized_email = email.strip().lower()
        response = self.client.client.auth.sign_in_with_password({
            "email": normalized_email,
            "password": password,
        })
        if response.user is None:
            return False
        self._current_user = {
            "id": response.user.id,
            "email": response.user.email,
            "session": response.session.model_dump() if hasattr(response.session, "model_dump") else response.session,
        }
        self._load_session(self._current_user.get("session"))
        return True

    def logout(self) -> None:
        try:
            self.client.client.auth.sign_out()
        finally:
            # Clear in-memory user/session and remove any Authorization header
            # we previously set on the PostgREST/http client so subsequent
            # requests are anonymous.
            try:
                postgrest = getattr(self.client.client, "postgrest", None)
                if postgrest is not None:
                    try:
                        if getattr(postgrest, "headers", None) is not None and "Authorization" in postgrest.headers:
                            del postgrest.headers["Authorization"]
                    except Exception:
                        pass
                    try:
                        if getattr(postgrest, "session", None) is not None and hasattr(postgrest.session, "headers") and "Authorization" in postgrest.session.headers:
                            del postgrest.session.headers["Authorization"]
                    except Exception:
                        pass
            except Exception:
                pass
            self._current_user = None
            self._session = None

    def current_user(self) -> dict[str, Any] | None:
        if self._current_user is not None:
            return self._current_user

        if self._session is not None:
            self._load_session(self._session)

        if not self.client.is_configured:
            return None

        try:
            if hasattr(self.client.client.auth, "get_user"):
                response = self.client.client.auth.get_user()
                user = getattr(response, "user", None)
                if user is not None:
                    self._current_user = self._build_user_payload(user)
                    return self._current_user

            if hasattr(self.client.client.auth, "get_session"):
                response = self.client.client.auth.get_session()
                user = getattr(response, "user", None)
                if user is not None:
                    self._current_user = self._build_user_payload(user)
                    if hasattr(response, "session") and response.session is not None:
                        self._load_session(response.session.model_dump() if hasattr(response.session, "model_dump") else response.session)
                    return self._current_user
        except Exception:
            pass

        return None
