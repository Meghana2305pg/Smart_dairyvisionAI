"""Professional top bar component for DairyVision AI dashboard."""
from __future__ import annotations

import streamlit as st


def render_topbar() -> None:
    """Render the professional top navigation bar."""
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1.5, 1.2, 1, 0.8, 0.8])
    weather_value = None
    with st.spinner("Loading navigation context..."):
        try:
            from webapp.backend_services.weather_service import get_current_weather
            weather_value = get_current_weather()
        except Exception:
            weather_value = None

    with col1:
        st.markdown(
            """
            <div style='
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 0;
            '>
                <div style='
                    font-weight: 700;
                    font-size: 18px;
                    color: #0f172a;
                '>🐄 DairyVision AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        farm_name = st.session_state.get("farm", {}).get("name", "No Farm") if st.session_state.get("authenticated") else "Not Connected"
        st.markdown(
            f"""
            <div style='
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 0;
                font-size: 14px;
            '>
                <span style='color: #64748b;'>🏡</span>
                <span style='color: #0f172a; font-weight: 600;'>{farm_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        if weather_value is not None:
            temp, humidity = weather_value
            st.markdown(
                f"""
                <div style='
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 0;
                    font-size: 14px;
                '>
                    <span>🌤️</span>
                    <span style='color: #0f172a; font-weight: 600;'>{temp:.1f}°C</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style='
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 0;
                    font-size: 14px;
                '>
                    <span>🌤️</span>
                    <span style='color: #0f172a;'>—</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col4:
        st.markdown(
            """
            <div style='
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 8px 0;
                font-size: 14px;
            '>
                <span>🔔</span>
                <span style='
                    background: #dc2626;
                    color: white;
                    border-radius: 999px;
                    padding: 2px 6px;
                    font-weight: 700;
                    font-size: 12px;
                '>2</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        user_name = "User"
        if st.session_state.get("user"):
            user_name = st.session_state.get("user", {}).get("full_name", "User") or "User"
        initial = user_name[0].upper() if user_name else "?"
        st.markdown(
            f"""
            <div style='
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 0;
                font-size: 13px;
            '>
                <div style='
                    width: 28px;
                    height: 28px;
                    border-radius: 999px;
                    background: #2f7d32;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    font-size: 12px;
                '>{initial}</div>
                <span style='color: #0f172a; font-weight: 600;'>{user_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        if st.button("Logout", use_container_width=True, key="topbar_logout"):
            st.session_state.user = None
            st.session_state.authenticated = False
            st.session_state.farm = None
            st.session_state.farm_twin = None
            st.session_state.cows = []
            st.session_state.active_view = "login"
            st.session_state.active_section = "dashboard"
            st.rerun()
