"""Wrapper service for using the existing weather integration."""

from __future__ import annotations

from webapp.backend_services._bootstrap import ensure_project_on_path

ensure_project_on_path()

from weather import fetch_weather


def get_current_weather() -> tuple[float, float]:
    """Return current weather using the existing weather module."""
    try:
        from weather import fetch_weather
    except ImportError as exc:
        raise RuntimeError("The existing weather backend could not be imported.") from exc

    return fetch_weather()
