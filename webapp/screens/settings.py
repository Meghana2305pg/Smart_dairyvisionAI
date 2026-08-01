"""Settings screen."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import info_card
from webapp.ui.section_header import render_page_header, render_section_header


def render_settings() -> None:
    """Render the settings page as a read-only preferences workspace for existing account and machine state."""
    st.markdown(
        """
        <style>
        .settings-shell { padding-top: 0.35rem; }
        .settings-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.9rem; margin-bottom: 1rem; }
        .settings-panel { background: rgba(255,255,255,0.96); border: 1px solid rgba(148,163,184,0.14); border-radius: 18px; padding: 1rem; box-shadow: 0 10px 22px rgba(15,23,42,0.04); margin-top: 1rem; }
        .settings-title { font-size: 0.74rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #475569; margin-bottom: 0.75rem; }
        @media (max-width: 900px) { .settings-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_page_header("Settings", "Review farm and application preferences for the current DairyVision workspace.", badge="Preferences")

    user = st.session_state.get("user", {})
    farm = st.session_state.get("farm", {})
    farm_name = st.session_state.get("farm_name") or farm.get("name") or "No farm selected"

    st.markdown('<div class="settings-shell">', unsafe_allow_html=True)

    st.markdown('<div class="settings-grid">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="settings-panel">
            <div class="settings-title">Farm Information</div>
            <div style='font-size: 1.25rem; font-weight: 800; letter-spacing: -0.04em; color: #0f172a;'>{farm_name}</div>
            <div style='margin-top: 0.8rem; color: #475569;'>Location: {farm.get('location', 'Not set')}</div>
            <div style='margin-top: 0.3rem; color: #475569;'>Farm ID: {farm.get('farm_id', 'Not set')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="settings-panel">
            <div class="settings-title">User Profile</div>
            <div style='font-size: 1.25rem; font-weight: 800; letter-spacing: -0.04em; color: #0f172a;'>{user.get('full_name', 'Current user')}</div>
            <div style='margin-top: 0.8rem; color: #475569;'>Email: {user.get('email', 'Not set')}</div>
            <div style='margin-top: 0.3rem; color: #475569;'>Phone: {user.get('phone', 'Not set')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Application Preferences", "Notifications", "About"])

    with tab1:
        st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
        st.markdown('<div class="settings-title">Application Preferences</div>', unsafe_allow_html=True)
        st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
        st.selectbox("Layout Density", ["Comfortable", "Compact"], index=0)
        st.selectbox("Default Landing Page", ["Dashboard", "Analytics", "Health Alerts"], index=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
        st.markdown('<div class="settings-title">Notifications</div>', unsafe_allow_html=True)
        st.checkbox("Enable notifications", value=True)
        st.checkbox("Email alerts for critical events", value=True)
        st.checkbox("Daily summary reports", value=True)
        st.checkbox("Weekly system health snapshot", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
        st.markdown('<div class="settings-title">About</div>', unsafe_allow_html=True)
        st.write("DairyVision AI")
        st.write("Application version: 2.3.1")
        st.write("Model version: v2.3.1")
        st.write("Environment: Current workspace configuration")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
