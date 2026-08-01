"""Lightweight dependency validation for deployment readiness."""
from __future__ import annotations

import importlib
from pathlib import Path

REQUIRED_PACKAGES = [
    "streamlit",
    "streamlit_option_menu",
    "streamlit_aggrid",
    "supabase",
    "dotenv",
    "pandas",
    "numpy",
    "scipy",
    "sklearn",
    "xgboost",
    "joblib",
    "shap",
    "matplotlib",
    "plotly",
    "seaborn",
    "requests",
]


def validate_requirements() -> list[str]:
    """Return missing package names for the runtime environment."""
    missing: list[str] = []
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except Exception:
            missing.append(package)
    return missing


def render_requirements_status() -> str:
    """Render a human-readable dependency status string."""
    missing = validate_requirements()
    if missing:
        return f"Missing packages: {', '.join(missing)}"
    return "All required packages are available."
