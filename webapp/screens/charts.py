"""Plotly chart builders for the analytics dashboard."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _coerce_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=["timestamp", "value", "cow_id", "health_status", "temperature", "humidity", "yield"])
    frame = pd.DataFrame(records)
    if "timestamp" in frame.columns:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    return frame


def build_milk_production_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    frame["yield"] = pd.to_numeric(frame.get("yield", pd.Series([None] * len(frame))), errors="coerce")
    if "yield" not in frame.columns:
        frame["yield"] = frame.get("feed", pd.Series([0] * len(frame)))
    frame["yield"] = frame["yield"].fillna(0)
    figure = px.line(frame, x="timestamp", y="yield", markers=True, title="Milk Production Trend")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure


def build_health_trend_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    if "health_status" not in frame.columns:
        frame["health_status"] = 0
    frame["health_status"] = frame["health_status"].astype(int)
    figure = px.line(frame, x="timestamp", y="health_status", markers=True, title="Health Trend")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    figure.update_yaxes(title="Health status (0=healthy, 1=sick)")
    return figure


def build_weather_vs_milk_chart(observations: list[dict[str, Any]]) -> go.Figure:
    frame = _coerce_frame(observations)
    if frame.empty:
        return go.Figure()
    frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
    if "temperature" not in frame.columns:
        frame["temperature"] = 0
    if "humidity" not in frame.columns:
        frame["humidity"] = 0
    if "yield" not in frame.columns:
        frame["yield"] = 0
    frame["yield"] = pd.to_numeric(frame["yield"], errors="coerce").fillna(0)
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
    if "value" in frame.columns:
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    else:
        frame["value"] = [0] * len(frame)
    figure = px.line(frame, x="step", y="value", markers=True, title="Prediction History")
    figure.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    return figure
