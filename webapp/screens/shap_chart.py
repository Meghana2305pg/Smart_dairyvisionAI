"""SHAP chart helpers for the explainability workspace."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_shap_bar_chart(contributions: list[dict[str, Any]]) -> go.Figure:
    """Render a horizontal bar chart for the top feature contributions."""
    if not contributions:
        return go.Figure()
    frame = pd.DataFrame(contributions)
    frame = frame.sort_values("contribution", ascending=False)
    figure = px.bar(frame, x="contribution", y="feature", orientation="h", color="contribution", title="SHAP Feature Contributions")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure


def build_contribution_timeline(contributions: list[dict[str, Any]]) -> go.Figure:
    """Render a simple contribution timeline from feature rows."""
    if not contributions:
        return go.Figure()
    frame = pd.DataFrame(contributions)
    frame = frame.sort_values("contribution", ascending=False)
    figure = px.line(frame, x="feature", y="contribution", markers=True, title="Contribution Timeline")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure
