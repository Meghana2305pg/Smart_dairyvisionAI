"""Wrapper service for using the existing trained model for predictions."""

from __future__ import annotations

from typing import Any

from webapp.backend_services.feature_service import build_feature_row
from webapp.backend_services.model_loader import load_model
from webapp.config.settings import DEFAULT_BASE_HUM, DEFAULT_BASE_TEMP


def predict_milk_yield(input_row: dict[str, Any], base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> dict[str, Any]:
    """Generate a prediction by reusing the existing model and feature pipeline for the current inputs."""
    print("STEP 6 predict_milk_yield")
    _, X, _ = build_feature_row(input_row, base_temp=base_temp, base_hum=base_hum)
    model = load_model()

    prediction = float(model.predict(X)[0])
    return {
        "prediction": prediction,
        "feature_names": list(X.columns),
        "feature_values": X.iloc[0].to_dict(),
    }
