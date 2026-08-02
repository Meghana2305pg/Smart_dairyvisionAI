"""Professional single-navigation sidebar for the DairyVision AI dashboard."""

from __future__ import annotations

from html import escape

import streamlit as st
from streamlit_option_menu import option_menu

MENU_ITEMS = [
    {"key": "dashboard", "label": "Dashboard", "icon": "house"},
    {"key": "my_herd", "label": "My Herd", "icon": "people"},
    {"key": "daily_operations", "label": "Daily Operations", "icon": "journal-text"},
    {"key": "digital_twin", "label": "Digital Twin", "icon": "cpu"},
    {"key": "health_alerts", "label": "Health Alerts", "icon": "exclamation-triangle"},
    {"key": "analytics", "label": "Analytics", "icon": "bar-chart"},
    {"key": "explainability", "label": "Explainability", "icon": "search"},
    {"key": "command_centre", "label": "Command Center", "icon": "broadcast"},
    {"key": "settings", "label": "Settings", "icon": "gear"},
]


def render_sidebar() -> str:
    """Render the permanent left sidebar navigation using the design system."""
    current_section = st.session_state.get("active_section", "dashboard")

    # Match active section by key or label
    default_index = 0
    for idx, item in enumerate(MENU_ITEMS):
        if item["key"] == current_section or item["label"].lower() == str(current_section).lower():
            default_index = idx
            break

    # Get farm and user context for branding & profile
    farm_info = st.session_state.get("farm", {}) or {}
    farm_name = farm_info.get("name") or st.session_state.get("farm_name") or "Green Pastures Farm"

    user = st.session_state.get("user", {}) or {}
    user_name = user.get("full_name") or st.session_state.get("user_name") or "Farmer User"
    user_email = user.get("email") or st.session_state.get("user_email") or "farm@dairyvision.ai"
    initial = user_name[0].upper() if user_name else "?"

    st.markdown(
        f"""
        <style>
        .sidebar-brand-card {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.65rem 0.75rem;
            margin-bottom: 0.85rem;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.06) 0%, rgba(248, 250, 252, 0.95) 100%);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            box-shadow: var(--dv-shadow-sm);
        }}

        .sidebar-brand-icon {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--dv-accent), #1d4ed8);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.22);
            flex-shrink: 0;
        }}

        .sidebar-brand-title {{
            font-weight: 800;
            font-size: 1rem;
            color: var(--dv-text);
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}

        .sidebar-brand-subtitle {{
            font-size: 0.76rem;
            color: var(--dv-muted);
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 0.15rem;
        }}

        .sidebar-shell {{
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            box-shadow: var(--dv-shadow-sm);
            padding: 0.35rem 0.25rem;
            margin-bottom: 0.85rem;
        }}

        .sidebar-nav-button {{
            width: 100%;
            margin: 0.25rem 0;
            padding: 0.68rem 0.8rem;
            border-radius: 10px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--dv-text);
            text-align: left;
            font-weight: 600;
            font-size: 0.92rem;
            display: flex;
            align-items: center;
            gap: 0.55rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .sidebar-nav-button:hover {{
            background: var(--dv-surface-alt);
            border-color: var(--dv-border);
        }}

        .sidebar-nav-button.active {{
            background: var(--dv-info-bg);
            color: var(--dv-accent);
            border-color: rgba(37, 99, 235, 0.18);
            box-shadow: inset 3px 0 0 0 var(--dv-accent);
        }}

        .sidebar-profile-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 0.75rem 0.85rem;
            margin-top: 0.65rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            box-shadow: var(--dv-shadow-sm);
        }}

        .sidebar-profile-avatar {{
            width: 34px;
            height: 34px;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--dv-accent), #22c55e);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }}

        .sidebar-profile-name {{
            font-weight: 700;
            font-size: 0.88rem;
            color: var(--dv-text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .sidebar-profile-email {{
            font-size: 0.75rem;
            color: var(--dv-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        </style>

        <div class="sidebar-brand-card">
            <div class="sidebar-brand-icon">🐄</div>
            <div style="flex:1; min-width:0;">
                <div class="sidebar-brand-title">DairyVision AI</div>
                <div class="sidebar-brand-subtitle">🏡 {escape(farm_name)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-shell'>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=[item["label"] for item in MENU_ITEMS],
        icons=[item["icon"] for item in MENU_ITEMS],
        default_index=default_index,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0.1rem",
                "background-color": "transparent",
                "border-radius": "14px",
                "border": "none",
                "margin-bottom": "0.1rem",
            },
            "icon": {
                "color": "#475569",
                "font-size": "16px",
            },
            "nav-link": {
                "color": "#0f172a",
                "font-size": "13.5px",
                "font-weight": "600",
                "padding": "11px 14px",
                "margin": "5px 0",
                "border-radius": "10px",
                "text-align": "left",
                "min-height": "42px",
                "transition": "all 180ms ease",
            },
            "nav-link-selected": {
                "background-color": "#eff6ff",
                "color": "#2563eb",
                "font-weight": "700",
                "border-radius": "10px",
                "padding": "11px 14px",
                "margin": "5px 0",
                "box-shadow": "inset 3.5px 0 0 0 #2563eb, inset 0 0 0 1px rgba(37, 99, 235, 0.18)",
            },
            "menu-icon": {
                "font-size": "16px",
            },
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Render User Profile & Quick Logout in Sidebar Footer
    st.markdown(
        f"""
        <div class="sidebar-profile-card">
            <div class="sidebar-profile-avatar">{escape(initial)}</div>
            <div style="flex:1; min-width:0;">
                <div class="sidebar-profile-name">{escape(user_name)}</div>
                <div class="sidebar-profile-email">{escape(user_email)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 0.45rem;'></div>", unsafe_allow_html=True)
    if st.button("Logout", key="sidebar_logout_btn", use_container_width=True, type="secondary"):
        try:
            if hasattr(st.session_state, "auth_service"):
                st.session_state.auth_service.logout()
        except Exception:
            pass
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.authenticated = False
        st.session_state.farm = None
        st.session_state.farm_id = None
        st.session_state.farm_name = None
        st.session_state.farm_twin = None
        st.session_state.pending_farm_setup = False
        st.session_state.cows = []
        st.session_state.active_view = "login"
        st.session_state.active_section = "dashboard"
        st.query_params.clear()
        st.rerun()

    selected_key = next((item["key"] for item in MENU_ITEMS if item["label"] == selected), current_section)
    st.session_state.active_section = selected_key
    return selected_key
