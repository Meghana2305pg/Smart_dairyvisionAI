"""Feature contribution helpers for the explainability workspace."""
from __future__ import annotations

from typing import Any

import pandas as pd


def build_feature_table(contributions: list[dict[str, Any]]) -> pd.DataFrame:
    """Create a tabular view of feature contributions."""
    if not contributions:
        return pd.DataFrame(columns=["feature", "contribution", "impact"])
    frame = pd.DataFrame(contributions)
    frame["impact"] = frame["contribution"].apply(lambda value: "positive" if float(value) >= 0 else "negative")
    return frame[["feature", "contribution", "impact"]]
