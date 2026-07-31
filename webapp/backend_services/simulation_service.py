"""Wrapper service for the existing what-if simulation pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.backend_services.feature_service import build_feature_row, prepare_feature_frame
from webapp.backend_services.model_loader import load_model
from webapp.config.settings import DEFAULT_BASE_HUM, DEFAULT_BASE_TEMP, OUTPUT_DIR

ensure_project_on_path()


def run_simulation() -> pd.DataFrame:
    """Reuse the existing simulation entry point logic through the module wrapper."""
    try:
        from simulate import main as sim_main
    except ImportError as exc:
        raise RuntimeError("The existing simulation backend could not be imported.") from exc

    sim_main()
    return pd.read_csv(Path(OUTPUT_DIR) / "simulation_results.csv")


def get_simulation_results() -> pd.DataFrame:
    """Research-artifact helper; interactive pages should use run_dynamic_simulation instead."""
    raise RuntimeError("Saved simulation artifacts are reserved for research/model-performance views. Interactive pages recompute from current inputs via run_dynamic_simulation().")


def run_dynamic_simulation(input_row: dict[str, Any], feed_range: list[float] | None = None, temp_range: list[float] | None = None, base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> pd.DataFrame:
    """Generate fresh simulation results for the current user inputs and a chosen scenario grid."""
    try:
        from feature_engineering import compute_thi
        from simulate import build_interval_model
    except ImportError as exc:
        raise RuntimeError("The existing simulation backend could not be imported.") from exc

    if feed_range is None:
        feed_range = [10, 15, 20, 25, 30, 35]
    if temp_range is None:
        temp_range = [18, 24, 30, 36, 42]

    _, X_train, y_train = prepare_feature_frame(base_temp=base_temp, base_hum=base_hum)
    model = load_model()
    interval_rf = build_interval_model(X_train, y_train)

    records: list[dict[str, Any]] = []
    for temp in temp_range:
        humidity = float(input_row.get("humidity", base_hum))
        thi_val = float(compute_thi(pd.Series([temp]), pd.Series([humidity])).iloc[0])
        for feed in feed_range:
            scenario = dict(input_row)
            scenario["feed"] = float(feed)
            scenario["temperature"] = float(temp)
            scenario["humidity"] = humidity
            _, X_row, _ = build_feature_row(scenario, base_temp=base_temp, base_hum=base_hum)
            point_pred = float(model.predict(X_row)[0])
            tree_preds = np.array([estimator.predict(X_row.values)[0] for estimator in interval_rf.estimators_])
            lo = float(np.percentile(tree_preds, 5))
            hi = float(np.percentile(tree_preds, 95))
            records.append({
                "Temp_C": float(temp),
                "Feed_kg": float(feed),
                "THI": round(thi_val, 1),
                "Pred_L": round(max(point_pred, 0.0), 3),
                "Lower_L": round(max(lo, 0.0), 3),
                "Upper_L": round(max(hi, 0.0), 3),
            })

    return pd.DataFrame(records)
