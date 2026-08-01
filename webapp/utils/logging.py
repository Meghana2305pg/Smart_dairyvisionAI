"""Structured logging helpers for the Streamlit app."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("dairyvision")
logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)


def log_event(event: str, **details: Any) -> None:
    """Emit a structured log entry for a major workflow event."""
    payload = {key: value for key, value in details.items() if value is not None}
    logger.info("event=%s details=%s", event, payload)


def log_error(message: str, **details: Any) -> None:
    """Emit a structured error log entry."""
    payload = {key: value for key, value in details.items() if value is not None}
    logger.exception("error=%s details=%s", message, payload)
