"""Digital twin screen."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import info_card


def render_digital_twin() -> None:
    """Render the digital twin screen."""
    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Digital Twin Visualization</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Real-time digital representation of your herd.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        info_card("Twin Status", "✅ Synced")
    with col2:
        info_card("Data Points", "1,247")
    with col3:
        info_card("Last Sync", "Just now")
    with col4:
        info_card("Model Version", "v2.3.1")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>Twin Memory</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("**Snapshots stored**: 4,521")
        st.markdown("**Memory usage**: 2.3 MB")
        st.markdown("**Last update**: 5 minutes ago")
    with col2:
        st.markdown("**Active twins**: 32")
        st.markdown("**Synced cows**: 32 / 32 (100%)")
        st.markdown("**Data freshness**: < 1 hour")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.info("Interactive 3D twin visualization coming soon.", icon="ℹ️")
