"""Command centre screen."""
from __future__ import annotations

import streamlit as st


def render_command_centre() -> None:
    """Render the command centre screen."""
    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Command Centre</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Advanced control and monitoring dashboard.</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Overview", "Controls", "Monitoring"])

    with tab1:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>System Overview</div>", unsafe_allow_html=True)

        from webapp.components.cards import info_card
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            info_card("Active Connections", "8")
        with col2:
            info_card("Uptime", "99.9%")
        with col3:
            info_card("Data Rate", "2.3 MB/s")
        with col4:
            info_card("Requests/min", "145")

    with tab2:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Advanced Controls</div>", unsafe_allow_html=True)

        if st.button("Trigger Model Retraining", use_container_width=True):
            st.info("Model retraining initiated. This will take approximately 30 minutes.")

        if st.button("Refresh Digital Twin Cache", use_container_width=True):
            st.success("Twin cache refreshed!")

        if st.button("Export Full Dataset", use_container_width=True):
            st.info("Export functionality coming soon.")

    with tab3:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>System Monitoring</div>", unsafe_allow_html=True)

        st.markdown("**CPU Usage**: 34%")
        st.progress(0.34)

        st.markdown("**Memory Usage**: 62%")
        st.progress(0.62)

        st.markdown("**Database**: 89%")
        st.progress(0.89)

        st.markdown("**API Response Time**: 142ms")
