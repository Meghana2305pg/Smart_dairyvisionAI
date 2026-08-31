"""Plotly chart builders for the analytics dashboard."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _coerce_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "value",
                "cow_id",
                "health_status",
                "temperature",
                "humidity",
                "yield",
            ]
        )

    frame = pd.DataFrame(records)

    # Use whichever timestamp column exists
    if "timestamp" not in frame.columns:
        if "created_at" in frame.columns:
            frame["timestamp"] = frame["created_at"]
        elif "observation_date" in frame.columns:
            frame["timestamp"] = frame["observation_date"]

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        errors="coerce",
    )

    return frame


def build_milk_production_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    if "yield" not in frame.columns:
        return go.Figure()
    frame["yield"] = pd.to_numeric(frame["yield"], errors="coerce")
    frame = frame.dropna(subset=["timestamp", "yield"]).sort_values("timestamp")
    if frame.empty:
        return go.Figure()
    figure = px.line(frame, x="timestamp", y="yield", markers=True, title="Milk Production Trend")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure


def build_health_trend_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    if "health_status" not in frame.columns:
        return go.Figure()
    frame["health_status"] = pd.to_numeric(frame["health_status"], errors="coerce")
    frame = frame.dropna(subset=["timestamp", "health_status"]).sort_values("timestamp")
    if frame.empty:
        return go.Figure()
    figure = px.line(frame, x="timestamp", y="health_status", markers=True, title="Health Trend")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    figure.update_yaxes(title="Health status (0=healthy, 1=sick)")
    return figure


def build_weather_vs_milk_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    required_columns = {"timestamp", "temperature", "humidity", "yield"}
    if not required_columns.issubset(frame.columns):
        return go.Figure()
    for column in ("temperature", "humidity", "yield"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=list(required_columns)).sort_values("timestamp")
    if frame.empty:
        return go.Figure()
    figure = px.scatter(
        frame,
        x="temperature",
        y="yield",
        size="humidity",
        color="humidity",
        hover_data={"timestamp": True, "cow_id": True},
        title="Weather vs Milk Yield",
    )
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure


def build_prediction_history_chart(history: list[dict[str, Any]]) -> go.Figure:
    if not history:
        return go.Figure()
    frame = pd.DataFrame(history)
    if "step" not in frame.columns or "value" not in frame.columns:
        return go.Figure()
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["step", "value"])
    if frame.empty:
        return go.Figure()
    figure = px.line(frame, x="step", y="value", markers=True, title="Prediction History")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure
