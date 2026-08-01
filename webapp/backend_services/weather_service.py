"""Wrapper service for using the existing weather integration."""

from __future__ import annotations

import streamlit as st

from webapp.backend_services._bootstrap import ensure_project_on_path

ensure_project_on_path()

from weather import fetch_weather


@st.cache_data(ttl=300, show_spinner=False)
def get_current_weather() -> tuple[float, float]:
    """Return current weather using the existing weather module with a short-lived cache."""
    try:
        from weather import fetch_weather
    except ImportError as exc:
        raise RuntimeError("The existing weather backend could not be imported.") from exc

    return fetch_weather()
