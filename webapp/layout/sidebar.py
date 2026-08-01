"""Professional single-navigation sidebar for the DairyVision AI dashboard."""
from __future__ import annotations

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
    """Render the permanent left sidebar navigation and return the selected key."""
    options = [item["label"] for item in MENU_ITEMS]
    icons = [item["icon"] for item in MENU_ITEMS]
    current_section = st.session_state.get("active_section", "dashboard")
    default_index = next(
        (index for index, item in enumerate(MENU_ITEMS) if item["key"] == current_section),
        0,
    )

    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] > div {
            width: 260px !important;
            padding: 0.9rem 0.7rem 0.9rem 0.7rem;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .sidebar-shell {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
            padding: 0.2rem 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-shell'>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=options,
        icons=icons,
        default_index=default_index,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0.2rem 0.1rem 0.1rem",
                "background-color": "transparent",
                "border-radius": "18px",
                "border": "none",
                "margin-bottom": "0.2rem",
            },
            "icon": {
                "color": "#475569",
                "font-size": "16px",
            },
            "nav-link": {
                "color": "#334155",
                "font-size": "14px",
                "font-weight": "600",
                "padding": "11px 12px",
                "margin": "4px 0",
                "border-radius": "12px",
                "text-align": "left",
                "min-height": "44px",
            },
            "nav-link-selected": {
                "background-color": "#f3f4f6",
                "color": "#0f172a",
                "font-weight": "700",
                "border-radius": "12px",
                "padding": "11px 12px",
                "margin": "4px 0",
                "box-shadow": "inset 0 0 0 1px rgba(148, 163, 184, 0.14)",
            },
            "menu-icon": {
                "font-size": "16px",
            },
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    selected_key = next((item["key"] for item in MENU_ITEMS if item["label"] == selected), "dashboard")
    st.session_state.active_section = selected_key
    return selected_key
