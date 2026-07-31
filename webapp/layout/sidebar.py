"""Professional sidebar navigation using streamlit-option-menu."""
from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu


def render_sidebar() -> str:
    """Render the professional left sidebar navigation.

    Returns the selected menu item key.
    """
    options = ["Dashboard", "My Herd", "Daily Operations", "Digital Twin", "Health Alerts", "Analytics", "Explainability", "Command Centre", "Settings"]
    current_section = st.session_state.get("active_section", "dashboard")
    current_label = current_section.replace("_", " ").title()
    default_index = options.index(current_label) if current_label in options else 0

    selected = option_menu(
        menu_title="DairyVision AI",
        options=options,
        icons=["🏠", "🐄", "📝", "🧠", "🚨", "📈", "🔍", "🧭", "⚙️"],
        menu_icon="🐄",
        default_index=default_index,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0.5rem",
                "background-color": "#ffffff",
                "box-shadow": "0 4px 12px rgba(15, 23, 42, 0.08)",
                "margin-bottom": "1rem",
            },
            "icon": {
                "color": "#2f7d32",
                "font-size": "20px",
            },
            "nav-link": {
                "color": "#475569",
                "font-size": "14px",
                "font-weight": "500",
                "padding": "10px 12px",
                "margin": "4px 0",
                "border-radius": "8px",
                "--hover-color": "#f0f9ff",
            },
            "nav-link-selected": {
                "background-color": "#2f7d32",
                "color": "white",
                "font-weight": "600",
                "border-radius": "8px",
                "padding": "10px 12px",
                "margin": "4px 0",
            },
            "menu-icon": {
                "font-size": "20px",
            },
        },
    )

    return selected.lower().replace(" ", "_")
