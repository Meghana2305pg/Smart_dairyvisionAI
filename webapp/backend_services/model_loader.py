"""Wrapper service for loading and caching the trained milk-yield model."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.config.settings import MODEL_PATH

ensure_project_on_path()


@lru_cache(maxsize=1)
def load_model() -> Any:
    """Load the trained model once and cache it for the application."""
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
