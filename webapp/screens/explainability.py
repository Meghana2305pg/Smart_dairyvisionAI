"""Explainability screen for SHAP and feature importance."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import info_card


def render_explainability() -> None:
    """Render the explainability screen."""
    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Model Explainability (SHAP)</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Understand why the model makes predictions using SHAP analysis.</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Feature Importance", "SHAP Values", "Model Insights"])

    with tab1:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Top Features Affecting Milk Yield</div>", unsafe_allow_html=True)

        features = [
            ("Feed Intake", 0.28),
            ("Temperature", 0.22),
            ("Weight", 0.19),
            ("Age", 0.15),
            ("Humidity", 0.12),
            ("Health Status", 0.04),
        ]

        for feature, importance in features:
            col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
            with col1:
                st.markdown(feature)
            with col2:
                st.markdown(f"<div style='background: #e8f5e9; height: 20px; border-radius: 4px; width: {importance * 100}%; display: flex; align-items: center;'></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"{importance * 100:.0f}%")

    with tab2:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>SHAP Impact Analysis</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            info_card("Mean Absolute SHAP", "0.23")
        with col2:
            info_card("Max SHAP Value", "1.47")
        with col3:
            info_card("Min SHAP Value", "-0.85")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("SHAP value visualization charts coming soon.", icon="ℹ️")

    with tab3:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Model Performance Insights</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            info_card("Cross-Val Score", "94%")
        with col2:
            info_card("MAE", "1.23 L/day")
        with col3:
            info_card("RMSE", "1.89 L/day")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.info("Detailed model diagnostics available in Analytics section.", icon="ℹ️")
