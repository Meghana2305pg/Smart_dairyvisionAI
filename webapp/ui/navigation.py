from __future__ import annotations

import streamlit as st

NAV_ITEMS = [
    {"key": "dashboard", "label": "Dashboard", "icon": "◉"},
    {"key": "herd", "label": "Herd", "icon": "🐄"},
    {"key": "daily_operations", "label": "Daily Operations", "icon": "📝"},
    {"key": "digital_twin", "label": "Digital Twin", "icon": "🧠"},
    {"key": "health", "label": "Health Alerts", "icon": "🚨"},
    {"key": "explainability", "label": "Explainability", "icon": "🔍"},
    {"key": "command_centre", "label": "Command Centre", "icon": "🧭"},
    {"key": "analytics", "label": "Analytics", "icon": "📈"},
    {"key": "settings", "label": "Settings", "icon": "⚙"},
]


def render_top_navigation() -> None:
    """Render the persistent SaaS-style top bar."""
    farm_name = st.session_state.get("farm", {}).get("name", "Current Farm") if st.session_state.get("farm") else "Current Farm"
    user_name = st.session_state.get("user", {}).get("full_name") if st.session_state.get("user") else "User"
    if not user_name:
        user_name = "User"

    st.markdown(
        f"""
        <div class="app-topbar">
          <div class="topbar-brand">
            <div class="brand-mark">🐄</div>
            <div>
              <div class="brand-title">DairyVision AI</div>
              <div class="brand-subtitle">Operational intelligence workspace</div>
            </div>
          </div>
          <div class="topbar-actions">
            <div class="topbar-pill">🏡 {farm_name}</div>
            <div class="topbar-pill">🔔 2</div>
            <div class="topbar-pill">👤 {user_name}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_left_navigation(active_section: str) -> None:
    """Render the custom left navigation panel."""
    st.markdown("<div class='app-nav-card'>", unsafe_allow_html=True)
    for item in NAV_ITEMS:
        section_key = item["key"]
        label = f"{item['icon']} {item['label']}"
        is_active = section_key == active_section
        button_class = "nav-action active" if is_active else "nav-action"
        if st.button(label, key=f"shell_nav_{section_key}", use_container_width=True):
            st.session_state.active_section = section_key
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.farm = None
        st.session_state.farm_twin = None
        st.session_state.cows = []
        st.session_state.active_view = "login"
        st.session_state.active_section = "dashboard"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_shell(active_section: str, main_renderer) -> None:
    """Render the full composited SaaS shell around the selected screen."""
    render_top_navigation()

    authenticated = bool(st.session_state.get("authenticated"))
    has_farm = bool(st.session_state.get("farm"))

    if authenticated and has_farm:
        nav_col, main_col = st.columns([0.20, 0.80], gap="medium")
        with nav_col:
            render_left_navigation(active_section)
        with main_col:
            main_renderer()
    else:
        main_renderer()
