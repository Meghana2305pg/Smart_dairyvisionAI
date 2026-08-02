"""Compact, professional top navigation bar using design system tokens."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_topbar() -> None:
    """Render the top navbar with app logo, farm context, weather, notification badge, user avatar, and logout."""
    weather_value = None
    try:
        from webapp.backend_services.weather_service import get_current_weather

        weather_value = get_current_weather()
    except Exception:
        weather_value = None

    farm_name = (
        st.session_state.get("farm", {}).get("name") or st.session_state.get("farm_name") or "Green Pastures Farm"
        if st.session_state.get("authenticated")
        else "Not Connected"
    )

    user_name = "User"
    if st.session_state.get("user"):
        user_name = st.session_state.get("user", {}).get("full_name") or st.session_state.get("user_name") or "User"
    initial = user_name[0].upper() if user_name else "?"

    weather_text = f"{weather_value[0]:.1f}°C · {weather_value[1]:.0f}%" if weather_value else "28.0°C · 65%"

    col1, col2, col3, col4, col5 = st.columns([1.6, 1.4, 0.8, 1.2, 0.6], gap="small")

    with col1:
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:0.6rem; padding:0.1rem 0;'>
                <div style='display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg, var(--dv-accent), #1d4ed8); color:white; font-size:1.1rem; box-shadow:0 4px 12px rgba(37,99,235,0.25);'>🐄</div>
                <div style='display:flex; flex-direction:column;'>
                    <span style='font-weight:800; font-size:0.98rem; color:var(--dv-text); letter-spacing:-0.02em;'>DairyVision AI</span>
                    <span style='font-size:0.75rem; color:var(--dv-muted); font-weight:600;'>{escape(farm_name)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; justify-content:center; gap:0.45rem; padding:0.25rem 0.6rem; border-radius:999px; background:var(--dv-surface-alt); border:1px solid var(--dv-border); font-size:0.8rem; font-weight:600; color:var(--dv-text);'>
                <span>🌤️</span>
                <span>{escape(weather_text)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style='display:flex; align-items:center; justify-content:center; padding:0.2rem 0;'>
                <div class="status-badge info" style="cursor:pointer; font-size:0.78rem;">🔔 2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:0.5rem; justify-content:flex-end; padding:0.15rem 0;'>
                <div style='width:30px; height:30px; border-radius:999px; background:linear-gradient(135deg,var(--dv-accent),#22c55e); color:white; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; box-shadow:0 2px 8px rgba(37,99,235,0.2);'>{escape(initial)}</div>
                <span style='font-weight:700; font-size:0.88rem; color:var(--dv-text);'>{escape(user_name)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        if st.button("Logout", key="topbar_logout_compact", use_container_width=True, type="secondary"):
            try:
                if hasattr(st.session_state, "auth_service"):
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
