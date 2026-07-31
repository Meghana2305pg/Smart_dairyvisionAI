"""Wrapper service around the existing explainability module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.backend_services.feature_service import build_feature_row
from webapp.backend_services.model_loader import load_model
from webapp.config.settings import DEFAULT_BASE_HUM, DEFAULT_BASE_TEMP, OUTPUT_DIR

ensure_project_on_path()


def generate_explainability_outputs(X: Any, df_full: Any | None = None) -> dict[str, str]:
    """Wrap the existing SHAP report generation logic."""
    try:
        import explainability
    except ImportError as exc:
        raise RuntimeError("The existing explainability backend could not be imported.") from exc

    return explainability.generate_shap_reports(X, df_full=df_full)


def get_explainability_artifacts() -> dict[str, Path]:
    """Return the output paths for explainability artifacts if they exist."""
    out_dir = Path(OUTPUT_DIR) / "shap"
    return {
        "summary": out_dir / "shap_summary.png",
        "bar": out_dir / "shap_bar.png",
        "csv": out_dir / "shap_feature_importance.csv",
        "report": out_dir / "shap_report.md",
    }


def get_explanation_for_input(input_row: dict[str, Any], base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> list[dict[str, Any]]:
    """Compute fresh feature-contribution values for the current input row."""
    _, X, _ = build_feature_row(input_row, base_temp=base_temp, base_hum=base_hum)
    model = load_model()

    try:
        import shap
    except Exception:
        shap = None

    if shap is not None:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        values = np.array(shap_values)
        if values.ndim == 3:
            values = values[0]
        if values.ndim == 2 and values.shape[0] == 1:
            values = values[0]
        contributions = values.tolist()
    else:
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            contributions = [0.0] * len(X.columns)
        else:
            contributions = [float(value) for value in importances]

    feature_names = list(X.columns)
    ranked = [
        {
            "feature": feature_name,
            "contribution": float(contribution),
            "absolute_contribution": abs(float(contribution)),
        }
        for feature_name, contribution in zip(feature_names, contributions)
    ]
    ranked.sort(key=lambda item: item["absolute_contribution"], reverse=True)
    return ranked
