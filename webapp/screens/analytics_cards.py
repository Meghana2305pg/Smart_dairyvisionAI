"""KPI card helpers for the analytics workspace."""
from __future__ import annotations

from typing import Any

import streamlit as st


class _UnavailableMetric:
    """Formats unavailable numeric metrics without fabricating a zero."""

    def __format__(self, format_spec: str) -> str:
        return "Unavailable"


def render_summary_cards(summary: dict[str, Any]) -> None:
    """Render KPI cards for the analytics workspace."""
    summary = dict(summary)
    for key in ("average_milk_yield", "today_prediction"):
        if summary.get(key) is None:
            summary[key] = _UnavailableMetric()
    columns = st.columns(6, gap="small")
    card_specs = [
        ("🐄", "Total Cows", summary.get("total_cows", 0)),
        ("❤️", "Healthy Cows", summary.get("healthy_cows", 0)),
        ("🚨", "Sick Cows", summary.get("sick_cows", 0)),
        ("🥛", "Average Milk Yield", f"{summary.get('average_milk_yield', 0):.1f} L"),
        ("🔮", "Today's Prediction", f"{summary.get('today_prediction', 0):.1f} L"),
        ("📢", "Active Alerts", summary.get("active_alerts", 0)),
    ]
    for column, (icon, title, value) in zip(columns, card_specs):
        with column:
            st.metric(label=f"{icon} {title}", value=str(value))
