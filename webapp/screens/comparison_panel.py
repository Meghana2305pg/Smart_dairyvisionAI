"""Prediction comparison helpers for the explainability workspace."""
from __future__ import annotations

from typing import Any


def build_comparison_payload(current_prediction: float, comparison_prediction: float | None = None) -> dict[str, Any]:
    """Build a simple comparison payload for the current and alternate prediction values."""
    comparison_prediction = comparison_prediction if comparison_prediction is not None else current_prediction
    delta = round(current_prediction - comparison_prediction, 2)
    return {
        "current_prediction": current_prediction,
        "comparison_prediction": comparison_prediction,
        "delta": delta,
        "direction": "higher" if delta > 0 else "lower" if delta < 0 else "equal",
    }
