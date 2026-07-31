from __future__ import annotations

import streamlit as st


def render_activity_timeline(items: list[tuple[str, str, str]]) -> None:
    """Render a simple vertical activity timeline."""
    if not items:
        st.info("No recent activity yet. Start with a cow registration or observation update.")
        return
    for title, detail, stamp in items:
        st.markdown(
            f"""
            <div class="timeline-item">
              <div class="timeline-title">{title}</div>
              <div class="timeline-detail">{detail}</div>
              <div class="timeline-stamp">{stamp}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
