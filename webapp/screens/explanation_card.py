"""Human-readable explanation builders for the explainability workspace."""
from __future__ import annotations

from typing import Any


def build_explanations(contributions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate feature contributions into short, human-readable explanation bullets."""
    explanations: list[dict[str, Any]] = []
    for item in contributions[:5]:
        feature = str(item.get("feature") or "feature")
        contribution = float(item.get("contribution") or 0.0)
        if contribution >= 0:
            description = f"{feature} is increasing the predicted milk yield outlook."
        else:
            description = f"{feature} is reducing the predicted milk yield outlook."
        explanations.append({"title": "Feature Driver", "description": description})
    return explanations
