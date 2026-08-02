"""Main application shell orchestrating layout, navigation, and page rendering."""

from __future__ import annotations

from typing import Callable

import streamlit as st

from webapp.layout.sidebar import render_sidebar
from webapp.layout.topbar import render_topbar
from webapp.ui.design_system import apply_global_theme


def render_app_shell(main_renderer: Callable[[], None]) -> None:
    """
    Render the complete SaaS application shell with topbar, fixed sidebar, and content area.

    Args:
        main_renderer: Callable that renders the selected screen's content.
    """
    apply_global_theme()

    authenticated = bool(st.session_state.get("authenticated"))
    has_farm = bool(st.session_state.get("farm"))

    if authenticated and has_farm:
        # Render clean topbar header
        render_topbar()

        # Render sidebar and pass selected section to state
        with st.sidebar:
            selected = render_sidebar()
            st.session_state.active_section = selected

        # Render main screen content
        main_renderer()
    else:
        # Render pre-auth screens (Login, Register, Farm Setup) in clean full-width container
        main_renderer()
