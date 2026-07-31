"""Wrapper service for analytics and evaluation outputs from the existing backend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.config.settings import OUTPUT_DIR

ensure_project_on_path()

import pandas as pd


def get_evaluation_outputs() -> dict[str, Path]:
    """Return evaluation artifact paths if they exist."""
    return {
        "test_metrics": Path(OUTPUT_DIR) / "test_metrics.csv",
        "feature_importance": Path(OUTPUT_DIR) / "feature_importance.csv",
        "cv_results": Path(OUTPUT_DIR) / "cv_results.csv",
        "predicted_vs_actual": Path(OUTPUT_DIR) / "predicted_vs_actual.png",
    }


def get_anomaly_outputs() -> dict[str, Path]:
    """Return anomaly artifact paths if they exist."""
    return {
        "report": Path(OUTPUT_DIR) / "anomaly_report.csv",
        "summary": Path(OUTPUT_DIR) / "anomaly_summary.md",
        "visualization": Path(OUTPUT_DIR) / "anomaly_visualization.png",
    }


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    """Read a CSV if it exists; otherwise return None."""
    if not path.exists():
        return None
    return pd.read_csv(path)
