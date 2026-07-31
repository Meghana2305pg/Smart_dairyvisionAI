"""Wrapper service for the existing health alert generation logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.backend_services.feature_service import build_feature_row
from webapp.backend_services.model_loader import load_model
from webapp.config.settings import DEFAULT_BASE_HUM, DEFAULT_BASE_TEMP, OUTPUT_DIR

ensure_project_on_path()


def _classify_alert(thi: float, decline_pct: float) -> tuple[str, str, str]:
    if thi >= 90 or decline_pct > 20:
        return ("Health Risk Alert", "Critical", "Critical heat stress or productivity decline detected. Consider emergency cooling, veterinary assessment, and hydration.")
    if thi >= 79:
        return ("Heat Stress Alert", "High", "High heat stress detected. Consider active cooling, shading, and improved hydration measures.")
    if decline_pct > 20:
        return ("Productivity Alert", "Critical", "Predicted yield decline exceeds 20%. Evaluate nutrition and heat mitigation immediately.")
    if decline_pct > 10:
        return ("Productivity Alert", "High", "Predicted yield decline exceeds 10%. Review feeding and environmental conditions to prevent further drop.")
    if thi >= 70:
        return ("Heat Stress Alert", "Medium", "Moderate heat stress detected. Monitor cattle closely and provide ventilation and water access.")
    return ("No Alert", "Low", "Conditions are within expected range; continue routine monitoring.")


def generate_health_alerts(df_full: Any | None = None, base_temp: float | None = None, base_hum: float | None = None) -> dict[str, str]:
    """Wrap the existing health alert generation module."""
    try:
        import health_alerts
    except ImportError as exc:
        raise RuntimeError("The existing health-alert backend could not be imported.") from exc

    return health_alerts.generate_health_alerts(df_full, base_temp=base_temp, base_hum=base_hum)


def get_health_alert_outputs() -> dict[str, Path]:
    """Return health alert artifact paths if they exist."""
    return {
        "csv": Path(OUTPUT_DIR) / "health_alerts.csv",
        "summary": Path(OUTPUT_DIR) / "health_alert_summary.md",
    }


def get_health_alerts_for_input(
    input_row: dict[str, Any],
    base_temp: float = DEFAULT_BASE_TEMP,
    base_hum: float = DEFAULT_BASE_HUM,
    predicted_yield: float | None = None,
) -> dict[str, Any]:
    """Compute a fresh health-alert assessment for the current input row."""
    try:
        from feature_engineering import thi_stress_label
    except ImportError as exc:
        raise RuntimeError("The existing feature-engineering backend could not be imported.") from exc

    df_full, X, _ = build_feature_row(input_row, base_temp=base_temp, base_hum=base_hum)
    model = load_model()

    if predicted_yield is None:
        predicted_yield = float(model.predict(X)[0])
    baseline_row = dict(input_row)
    baseline_row["temperature"] = 20.0
    baseline_row["humidity"] = 50.0
    baseline_df, baseline_X, _ = build_feature_row(baseline_row, base_temp=20.0, base_hum=50.0)
    baseline_yield = float(model.predict(baseline_X)[0])

    decline_pct = 100.0 * (baseline_yield - predicted_yield) / baseline_yield if baseline_yield > 0 else 0.0
    thi = float(df_full["thi"].iloc[0])
    stress_category = str(thi_stress_label(pd.Series([thi])).iloc[0])
    alert_category, severity, recommendation = _classify_alert(thi, decline_pct)

    return {
        "predicted_yield": predicted_yield,
        "baseline_yield": baseline_yield,
        "predicted_decline_pct": decline_pct,
        "stress_category": stress_category,
        "alert_category": alert_category,
        "severity": severity,
        "recommendation": recommendation,
    }
