"""Health alerts screen."""
from __future__ import annotations

import streamlit as st

from webapp.components.cards import alert_card


def render_health() -> None:
    """Render the health alerts screen."""
    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Health Alerts & Monitoring</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Monitor health status and receive alerts for your herd.</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        from webapp.components.cards import info_card
        info_card("Total Alerts", "8")
    with col2:
        info_card("Critical", "2")
    with col3:
        info_card("Warning", "4")
    with col4:
        info_card("Info", "2")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>Recent Alerts</div>", unsafe_allow_html=True)

    alerts = [
        ("High Temperature Alert", "3 cows affected - Implement cooling measures", "warning", "15 min ago"),
        ("High Somatic Cell Count", "2 cows require attention - Check milking hygiene", "warning", "1h ago"),
        ("Low Feed Intake", "1 cow detected - Monitor appetite and health", "warning", "2h ago"),
        ("Mastitis Risk", "Cow #C-012 showing signs - Schedule veterinary check", "danger", "3h ago"),
    ]

    for title, msg, severity, time in alerts:
        alert_card(
            title=title,
            message=msg,
            severity=severity,
            timestamp=time,
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    if st.button("View Detailed Health Report", use_container_width=True):
        st.info("Detailed health report functionality coming soon.")
