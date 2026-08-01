"""KPI card helpers for the analytics workspace."""
from __future__ import annotations

from typing import Any

import streamlit as st

from webapp.components.cards import info_card


def render_summary_cards(summary: dict[str, Any]) -> None:
    """Render KPI cards for the analytics workspace."""
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
            info_card(f"{icon} {title}", str(value))
