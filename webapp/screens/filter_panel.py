"""Filter helpers for the analytics workspace."""
from __future__ import annotations

import streamlit as st


def render_filter_panel(cow_options: list[str], breed_options: list[str], status_options: list[str]) -> tuple[str, str, str, str, str]:
    """Render filter controls and return selected values."""
    with st.sidebar:
        st.markdown("### Filters")
        start_date = st.date_input("Date Range Start")
        end_date = st.date_input("Date Range End")
        cow_filter = st.selectbox("Cow", ["All", *cow_options])
        breed_filter = st.selectbox("Breed", ["All", *breed_options])
        health_filter = st.selectbox("Health Status", ["All", *status_options])
    return str(start_date), str(end_date), cow_filter, breed_filter, health_filter
