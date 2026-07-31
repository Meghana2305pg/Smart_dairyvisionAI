"""Analytics screen."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import info_card
from webapp.services.dashboard_service import DashboardService


def render_analytics() -> None:
    """Render the analytics screen."""
    dashboard_service: DashboardService = st.session_state.dashboard_service
    dashboard = dashboard_service.build_dashboard()

    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Analytics & Insights</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Monitor herd performance and trends over time.</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Milk Production", "Health", "Weather", "Model", "Explainability"])

    with tab1:
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            info_card("Total Cows", str(dashboard.herd.get("cow_count", 0)))
        with col2:
            info_card("Avg Yield", "28.5 L/day")
        with col3:
            info_card("Peak Yield", "34.2 L/day")
        with col4:
            info_card("Low Yield", "12.1 L/day")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("Production trend charts coming soon.", icon="ℹ️")

    with tab2:
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            info_card("Healthy Cows", str(dashboard.herd.get("cow_count", 0)))
        with col2:
            info_card("At Risk", "4")
        with col3:
            info_card("Under Review", "2")
        with col4:
            info_card("Alerts This Week", "8")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("Health trend analysis coming soon.", icon="ℹ️")

    with tab3:
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1:
            info_card("Avg Temp", "22°C")
        with col2:
            info_card("Humidity", "65%")
        with col3:
            info_card("Heat Stress Days", "12")
        with col4:
            info_card("Optimal Days", "48")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("Weather correlation charts coming soon.", icon="ℹ️")

    with tab4:
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            info_card("Model Accuracy", "94%")
        with col2:
            info_card("Last Training", "2 days ago")
        with col3:
            info_card("Model Version", "v2.3.1")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("Model performance metrics coming soon.", icon="ℹ️")

    with tab5:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Feature Importance (SHAP)</div>", unsafe_allow_html=True)
        st.info("SHAP explainability charts coming soon. See Explainability section for detailed analysis.", icon="ℹ️")
