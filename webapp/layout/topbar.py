"""Professional top bar component for DairyVision AI dashboard."""
from __future__ import annotations

import streamlit as st


def render_topbar() -> None:
    """Render the professional top navigation bar."""
    col1, col2, col3, col4, col5, col6 = st.columns([2.4, 1.35, 1.05, 1.0, 1.2, 0.75], gap="small")
    weather_value = None
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
                gap: 0.8rem;
                padding: 0.15rem 0;
            '>
                <div style='
                    width: 2.65rem;
                    height: 2.65rem;
                    border-radius: 999px;
                    background: linear-gradient(135deg, #2563eb 0%, #22c55e 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    box-shadow: 0 10px 24px rgba(37, 99, 235, 0.25);
                '>🐄</div>
                <div style='
                    font-weight: 750;
                    font-size: 18px;
                    color: #0f172a;
                '>DairyVision AI</div>
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
                gap: 0.45rem;
                padding: 0.2rem 0;
                font-size: 14px;
            '>
                <span class='topbar-pill'>🏡 {farm_name}</span>
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
                    gap: 0.45rem;
                    padding: 0.2rem 0;
                    font-size: 14px;
                '>
                    <span class='topbar-pill'>🌤️ {temp:.1f}°C · {humidity:.0f}%</span>
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
                    gap: 0.45rem;
                    padding: 0.2rem 0;
                    font-size: 14px;
                '>
                    <span class='topbar-pill'>🌤️ Weather unavailable</span>
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
                gap: 0.45rem;
                padding: 0.2rem 0;
                font-size: 14px;
            '>
                <span class='topbar-pill'>🔔 2 alerts</span>
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
                gap: 0.45rem;
                padding: 0.2rem 0;
                font-size: 13px;
            '>
                <div style='
                    width: 30px;
                    height: 30px;
                    border-radius: 999px;
                    background: linear-gradient(135deg, #2563eb 0%, #22c55e 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    font-size: 12px;
                '>{initial}</div>
                <span class='topbar-pill'>{user_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        if st.button("Logout", use_container_width=True, key="topbar_logout"):
            try:
                st.session_state.auth_service.logout()
            except Exception:
                pass
            st.session_state.user = None
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.authenticated = False
            st.session_state.farm = None
            st.session_state.farm_id = None
            st.session_state.farm_name = None
            st.session_state.farm_twin = None
            st.session_state.pending_farm_setup = False
            st.session_state.cows = []
            st.session_state.active_view = "login"
            st.session_state.active_section = "dashboard"
            st.query_params.clear()
            st.rerun()
