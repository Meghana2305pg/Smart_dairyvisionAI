"""Main application shell orchestrating layout and routing."""
from __future__ import annotations

from typing import Callable

import streamlit as st

from webapp.layout.sidebar import render_sidebar
from webapp.layout.topbar import render_topbar


def render_app_shell(main_renderer: Callable[[], None]) -> None:
    """
    Render the complete application shell with topbar, sidebar, and main content.

    Args:
        main_renderer: Callable that renders the selected screen's content.
    """
    st.set_page_config(
        page_title="DairyVision AI",
        page_icon="🐄",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Apply professional styling
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stSidebarContent"] {
            display: none !important;
        }
        .st-emotion-cache-uf99v0 {
            display: none !important;
        }
        .stApp {
            background: #f8fafc;
        }
        .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
            padding-top: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render top bar
    render_topbar()
    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    authenticated = bool(st.session_state.get("authenticated"))
    has_farm = bool(st.session_state.get("farm"))

    if authenticated and has_farm:
        # Two-column layout: sidebar + main content
        sidebar_col, main_col = st.columns([0.18, 0.82], gap="medium")

        with sidebar_col:
            selected = render_sidebar()
            st.session_state.active_section = selected

        with main_col:
            main_renderer()
    else:
        # Full width for login/register/farm setup
        main_renderer()
