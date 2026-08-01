from __future__ import annotations

from html import escape

from typing import Any

import streamlit as st


def info_card(title: str, value: str, caption: str, tone: str = "neutral") -> None:
    """Render a compact dashboard card with a soft SaaS look."""
    tone_styles = {"neutral": "neutral", "success": "success", "warning": "warning", "danger": "danger"}
    safe_tone = tone_styles.get(tone, "neutral")
    st.markdown(
        f"""
        <div class="dashboard-card">
          <div class="card-title">{escape(title)}</div>
          <div class="card-value">{escape(value)}</div>
          <div class="card-caption">{escape(caption)}</div>
          <div class="status-badge {safe_tone}" style='margin-top:0.65rem;'>Updated</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_button(label: str, section_key: str) -> None:
    """Render a quick action button that navigates inside the shell."""
    if st.button(label, use_container_width=True):
        st.session_state.active_section = section_key
        st.rerun()


def timeline_item(title: str, detail: str, stamp: str) -> None:
    """Render a lightweight activity item."""
    st.markdown(
        f"""
        <div class="timeline-item">
                    <div class="timeline-title">{escape(title)}</div>
                    <div class="timeline-detail">{escape(detail)}</div>
                    <div class="timeline-stamp">{escape(stamp)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
