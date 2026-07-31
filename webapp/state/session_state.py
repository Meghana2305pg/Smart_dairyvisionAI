"""Helpers for managing Streamlit session state across the app-shell workflow."""

from __future__ import annotations

from typing import Any

import streamlit as st

APP_STATE_NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
APP_STATE_AUTHENTICATED_NO_FARM = "AUTHENTICATED_NO_FARM"
APP_STATE_AUTHENTICATED_WITH_FARM = "AUTHENTICATED_WITH_FARM"
APP_STATE_AUTHENTICATED_WITH_COWS = "AUTHENTICATED_WITH_COWS"


def init_session_defaults(defaults: dict[str, Any]) -> None:
    """Initialize keys in Streamlit session state if they are missing."""
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def bootstrap_session_state(defaults: dict[str, Any]) -> None:
    """Initialize the app session only once per Streamlit session."""
    if st.session_state.get("_session_bootstrapped", False):
        return

    init_session_defaults(defaults)
    st.session_state["_session_bootstrapped"] = True


def get_session_value(key: str, default: Any = None) -> Any:
    """Read a value from Streamlit session state safely."""
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any) -> None:
    """Set a value in Streamlit session state."""
    st.session_state[key] = value
