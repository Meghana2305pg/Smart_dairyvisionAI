"""Wrapper service for loading and caching the trained milk-yield model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.config.settings import MODEL_PATH

ensure_project_on_path()


@st.cache_resource(show_spinner=False)
def load_model() -> Any:
    """Load the trained model once and reuse it across the app session."""
    print("STEP 8 load_model")
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("The 'joblib' package is required to load the trained model.") from exc

    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found at {model_path}. Run the existing training pipeline first."
        )
    return joblib.load(model_path)


def get_model_status() -> dict[str, object]:
    """Return the model path and whether it exists."""
    path = Path(MODEL_PATH)
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }
