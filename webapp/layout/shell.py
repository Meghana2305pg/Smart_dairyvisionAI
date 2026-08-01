"""Main application shell orchestrating layout and routing."""
from __future__ import annotations

from typing import Callable

import streamlit as st

from webapp.layout.sidebar import render_sidebar
from webapp.layout.topbar import render_topbar
from webapp.ui.section_header import apply_app_theme


def render_app_shell(main_renderer: Callable[[], None]) -> None:
    """
    Render the complete application shell with topbar, sidebar, and main content.

    Args:
        main_renderer: Callable that renders the selected screen's content.
    """
    apply_app_theme()

    # Render top bar
    render_topbar()
    st.markdown("<div style='margin-bottom: 0.9rem;'></div>", unsafe_allow_html=True)

    authenticated = bool(st.session_state.get("authenticated"))
    has_farm = bool(st.session_state.get("farm"))

    if authenticated and has_farm:
        with st.sidebar:
            selected = render_sidebar()
            st.session_state.active_section = selected
        main_renderer()
    else:
        # Full width for login/register/farm setup
        main_renderer()
