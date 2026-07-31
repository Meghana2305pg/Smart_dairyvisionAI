from __future__ import annotations

import streamlit as st


def render_recommendations(recommendations: list[dict[str, object]]) -> None:
    """Render recommendations if any are available; otherwise hide the section gracefully."""
    if not recommendations:
        return
    st.markdown("<div class='section-heading'>Recommendations</div>", unsafe_allow_html=True)
    for item in recommendations[:3]:
        message = item.get("message") or item.get("recommendation") or "No recommendation available"
        st.markdown(
            f"""
            <div class="dashboard-card">
              <div class="card-title">Operational insight</div>
              <div class="card-caption">{message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
