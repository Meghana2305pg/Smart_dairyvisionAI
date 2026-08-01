"""Professional sidebar navigation using streamlit-option-menu."""
from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu


def render_sidebar() -> str:
    """Render the professional left sidebar navigation.

    Returns the selected menu item key.
    """
    options = ["Dashboard", "My Herd", "Daily Operations", "Digital Twin", "Health Alerts", "Analytics", "Explainability", "Settings"]
    current_section = st.session_state.get("active_section", "dashboard")
    current_label = current_section.replace("_", " ").title()
    default_index = options.index(current_label) if current_label in options else 0

    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] > div {
            width: 286px !important;
            padding: 1rem 0.85rem 1rem 0.9rem;
        }
        .sidebar-shell {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid rgba(16, 185, 129, 0.12);
            border-radius: 22px;
            box-shadow: 0 14px 40px rgba(15, 23, 42, 0.06);
            padding: 0.95rem;
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.9rem;
            padding: 0.15rem 0.1rem 0.85rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
        }
        .sidebar-brand-mark {
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 18px rgba(22, 163, 74, 0.22);
        }
        .sidebar-brand-title {
            font-size: 0.98rem;
            font-weight: 750;
            color: #0f172a;
            line-height: 1.2;
        }
        .sidebar-brand-subtitle {
            color: #64748b;
            font-size: 0.78rem;
            margin-top: 0.12rem;
        }
        .sidebar-footer {
            margin-top: 0.9rem;
            padding-top: 0.9rem;
            border-top: 1px solid rgba(148, 163, 184, 0.16);
        }
        .sidebar-footer .stButton > button {
            border-radius: 14px !important;
            border: 1px solid rgba(220, 38, 38, 0.18) !important;
            background: #ffffff !important;
            color: #dc2626 !important;
            box-shadow: none !important;
        }
        .sidebar-footer .stButton > button:hover {
            background: #fef2f2 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='sidebar-shell'>
          <div class='sidebar-brand'>
            <div class='sidebar-brand-mark'>🐄</div>
            <div>
              <div class='sidebar-brand-title'>DairyVision AI</div>
              <div class='sidebar-brand-subtitle'>Farm operations navigation</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = option_menu(
        menu_title=None,
        options=options,
        icons=["house", "people", "journal-text", "cpu", "exclamation-triangle", "bar-chart", "search", "gear"],
        default_index=default_index,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0.4rem 0.15rem 0.15rem",
                "background-color": "transparent",
                "border-radius": "18px",
                "border": "none",
                "margin-bottom": "0.35rem",
            },
            "icon": {
                "color": "#16a34a",
                "font-size": "18px",
            },
            "nav-link": {
                "color": "#334155",
                "font-size": "14px",
                "font-weight": "600",
                "padding": "11px 12px",
                "margin": "5px 0",
                "border-radius": "14px",
                "--hover-color": "#f0fdf4",
            },
            "nav-link-selected": {
                "background-color": "#ecfdf5",
                "color": "#166534",
                "font-weight": "700",
                "border-radius": "14px",
                "padding": "11px 12px",
                "margin": "5px 0",
            },
            "menu-icon": {
                "font-size": "18px",
            },
        },
    )

    st.markdown("<div class='sidebar-footer'>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
        try:
            st.session_state.auth_service.logout()
        except Exception:
            pass
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.farm = None
        st.session_state.farm_twin = None
        st.session_state.cows = []
        st.session_state.active_view = "login"
        st.session_state.active_section = "dashboard"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    return selected.lower().replace(" ", "_")
