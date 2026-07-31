from __future__ import annotations

import streamlit as st


def render_twin_status_card(twin_state: dict[str, object]) -> None:
    """Render a compact twin health card using the existing twin state object."""
    st.markdown("<div class='section-heading'>Twin Status</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dashboard-card">
          <div class="card-title">Twin Synced</div>
          <div class="card-value">{twin_state.get('status', 'Stable')}</div>
          <div class="card-caption">Memory snapshots: {twin_state.get('snapshot_count', 0)} · Last observation: {twin_state.get('last_observation', 'n/a')} · Prediction: {twin_state.get('prediction', 'n/a')} · Health: {twin_state.get('health', 'n/a')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
