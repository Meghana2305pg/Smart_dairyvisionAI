"""Professional top navigation bar for the DairyVision AI dashboard."""
from __future__ import annotations

import streamlit as st


def render_topbar() -> None:
    """Render the clean top navigation bar with farm, weather, alerts, profile and logout."""
    col1, col2, col3, col4, col5 = st.columns([1.8, 1.2, 1.0, 1.2, 0.7], gap="small")
    weather_value = None
    try:
        from webapp.backend_services.weather_service import get_current_weather

        weather_value = get_current_weather()
    except Exception:
        weather_value = None

    with col1:
        farm_name = st.session_state.get("farm", {}).get("name", "No Farm") if st.session_state.get("authenticated") else "Not Connected"
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:0.55rem; padding:0.2rem 0; font-size:14px;'>
                <span style='display:inline-flex; align-items:center; justify-content:center; height:2rem; width:2rem; border-radius:10px; background:#eef2ff; color:#1f2937; font-size:0.95rem;'>🏡</span>
                <span style='font-weight:600; color:#0f172a; white-space:nowrap;'>{farm_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if weather_value is not None:
            temp, humidity = weather_value
            st.markdown(
                f"""
                <div style='display:flex; align-items:center; justify-content:center; gap:0.45rem; padding:0.2rem 0; font-size:13px; color:#475569;'>
                    <span>🌤️</span>
                    <span>{temp:.1f}°C · {humidity:.0f}%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style='display:flex; align-items:center; justify-content:center; gap:0.45rem; padding:0.2rem 0; font-size:13px; color:#475569;'>
                    <span>🌤️</span>
                    <span>Weather unavailable</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col3:
        st.markdown(
            """
            <div style='display:flex; align-items:center; justify-content:center; padding:0.2rem 0; font-size:15px; color:#475569;'>
                <span>🔔</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        user_name = "User"
        if st.session_state.get("user"):
            user_name = st.session_state.get("user", {}).get("full_name", "User") or "User"
        initial = user_name[0].upper() if user_name else "?"
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:0.5rem; justify-content:flex-end; padding:0.2rem 0; font-size:13px; color:#0f172a;'>
                <div style='width:28px; height:28px; border-radius:999px; background:linear-gradient(135deg,#2563eb,#22c55e); color:white; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:11px;'>{initial}</div>
                <span style='font-weight:600;'>{user_name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
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
