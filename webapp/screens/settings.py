"""Settings screen."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import info_card


def render_settings() -> None:
    """Render the settings screen."""
    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Manage your account and application preferences.</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Account", "Preferences", "System"])

    with tab1:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Account Information</div>", unsafe_allow_html=True)

        user = st.session_state.get("user", {})
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            info_card("Full Name", user.get("full_name", "Not set"))
            info_card("Email", user.get("email", "Not set"))
        with col2:
            info_card("Phone", user.get("phone", "Not set"))
            info_card("Status", "Active ✅")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Edit Profile", use_container_width=True):
            st.info("Profile edit functionality coming soon.")

    with tab2:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>Application Preferences</div>", unsafe_allow_html=True)

        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], value="Light")
        notifications = st.checkbox("Enable notifications", value=True)
        email_alerts = st.checkbox("Email alerts for critical events", value=True)
        daily_report = st.checkbox("Daily summary report", value=True)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Save Preferences", use_container_width=True):
            st.success("Preferences saved!")

    with tab3:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 16px;'>System Information</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            info_card("App Version", "2.3.1")
            info_card("Model Version", "v2.3.1")
        with col2:
            info_card("API Status", "Operational ✅")
            info_card("Last Backup", "2 hours ago")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Refresh System", use_container_width=True):
            st.success("System refreshed!")

        if st.button("Export Data", use_container_width=True):
            st.info("Data export coming soon.")
