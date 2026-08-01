"""Filter helpers for the analytics workspace."""
from __future__ import annotations

import streamlit as st


def render_filter_panel(cow_options: list[str], breed_options: list[str], status_options: list[str]) -> tuple[str, str, str, str, str]:
    """Render filter controls in the content area instead of using the legacy sidebar."""
    with st.container():
        st.markdown("### Filters")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Date Range Start")
        with col2:
            end_date = st.date_input("Date Range End")
        col3, col4, col5 = st.columns(3)
        with col3:
            cow_filter = st.selectbox("Cow", ["All", *cow_options])
        with col4:
            breed_filter = st.selectbox("Breed", ["All", *breed_options])
        with col5:
            health_filter = st.selectbox("Health Status", ["All", *status_options])
    return str(start_date), str(end_date), cow_filter, breed_filter, health_filter
