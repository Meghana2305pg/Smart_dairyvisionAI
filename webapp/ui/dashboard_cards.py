from __future__ import annotations

from typing import Any

import streamlit as st


def info_card(title: str, value: str, caption: str, tone: str = "neutral") -> None:
    """Render a compact dashboard card with a soft SaaS look."""
    tone_styles = {
        "neutral": ("#eff6ff", "#2563eb"),
        "success": ("#ecfdf3", "#166534"),
        "warning": ("#fffbeb", "#92400e"),
        "danger": ("#fef2f2", "#991b1b"),
    }
    bg, color = tone_styles.get(tone, tone_styles["neutral"])
    st.markdown(
        f"""
        <div class="dashboard-card">
          <div class="card-title">{title}</div>
          <div class="card-value">{value}</div>
          <div class="card-caption">{caption}</div>
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
          <div class="timeline-title">{title}</div>
          <div class="timeline-detail">{detail}</div>
          <div class="timeline-stamp">{stamp}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
