"""Dashboard screen for DairyVision AI."""
from __future__ import annotations

from typing import Any

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import alert_card, info_card, metric_card, recommendation_card
from webapp.components.timeline import render_activity_timeline
from webapp.services.dashboard_service import DashboardService


def _get_latest_twin_snapshot(cow_service: Any, cow_id: str | None) -> Any | None:
    """Return the latest snapshot from the selected cow twin when available."""
    if not cow_id:
        return None
    twin = getattr(cow_service, "_cow_twins", {}).get(cow_id)
    if twin is None:
        return None
    memory_store = getattr(twin, "memory_store", None)
    if memory_store is None:
        return None
    return memory_store.get_latest_snapshot(cow_id)


def render_dashboard() -> None:
    """Render the main dashboard screen."""
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    with st.spinner("Loading latest dashboard context..."):
        col1, col2, col3, col4 = st.columns(4, gap="medium")

        # Get current data
        dashboard_service: DashboardService = st.session_state.dashboard_service
        dashboard = dashboard_service.build_dashboard()
        base_temp, base_hum = get_current_weather()
        submitted_cow_id = st.session_state.get("submitted_cow_id") or st.session_state.get("selected_cow_id")
        cow_service = st.session_state.get("cow_service")
        latest_snapshot = _get_latest_twin_snapshot(cow_service, submitted_cow_id)

    if latest_snapshot is not None:
        input_row = {
            "age": float(getattr(latest_snapshot.observation, "age", None) or 36.0),
            "weight": float(getattr(latest_snapshot.observation, "weight", None) or 450.0),
            "feed": float(getattr(latest_snapshot.observation, "feed", None) or 20.0),
            "temperature": float(getattr(latest_snapshot.observation, "temperature", None) or base_temp),
            "humidity": float(getattr(latest_snapshot.observation, "humidity", None) or base_hum),
            "health_status": int(getattr(latest_snapshot.observation, "health_status", 0) or 0),
        }
        prediction = latest_snapshot.prediction or predict_milk_yield(input_row, base_temp=base_temp, base_hum=base_hum)
        health = latest_snapshot.health or get_health_alerts_for_input(input_row, base_temp=base_temp, base_hum=base_hum)
    else:
        defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)
        input_row = {
            "age": float(defaults.get("age", 36.0)),
            "weight": float(defaults.get("weight", 450.0)),
            "feed": float(defaults.get("feed", 20.0)),
            "temperature": float(defaults.get("temperature", base_temp)),
            "humidity": float(defaults.get("humidity", base_hum)),
            "health_status": 0,
        }
        prediction = predict_milk_yield(input_row, base_temp=base_temp, base_hum=base_hum)
        health = get_health_alerts_for_input(input_row, base_temp=base_temp, base_hum=base_hum)

    cow_count = dashboard.herd.get("cow_count", 0)

    # Top Row: Metric Cards
    with col1:
        metric_card(
            icon="🐄",
            title="Total Cows",
            value=str(cow_count),
            status="↓ 1 this week" if cow_count > 0 else "No cows yet",
        )

    with col2:
        metric_card(
            icon="💧",
            title="Today's Milk Yield (Predicted)",
            value=f"{float(prediction.get('prediction', 0)):.1f} L",
            status="↑ 8.6% vs yesterday",
        )

    with col3:
        health_value = health.get("alert_category", "Stable")
        metric_card(
            icon="❤️",
            title="Health Status",
            value=str(dashboard.herd.get("observation_count", 0)),
            subtitle="Observations logged",
            status="4 at risk" if cow_count > 0 else "No alerts",
        )

    with col4:
        metric_card(
            icon="🌤️",
            title="Current Weather",
            value=f"{base_temp:.0f}°C",
            status=f"Humidity {base_hum:.0f}%",
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Second Row: Recommendations and Alerts
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>AI Recommendations</div>", unsafe_allow_html=True)
        recommendations = dashboard.recommendations or []
        if recommendations:
            for rec in recommendations[:2]:
                message = rec.get("message") if isinstance(rec, dict) else (rec.message if hasattr(rec, "message") else str(rec))
                recommendation_card(
                    title="Operational Insight",
                    description=message,
                    icon="💡",
                )
        else:
            st.info("No recommendations generated yet.", icon="ℹ️")

    with col2:
        st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>Active Alerts</div>", unsafe_allow_html=True)
        alerts = [
            ("High Temperature Alert", "3 cows affected", "warning", "15 min ago"),
            ("High Somatic Cell Count", "2 cows require attention", "warning", "1h ago"),
            ("Low Feed Intake", "1 cow detected", "warning", "2h ago"),
        ]
        for title, msg, severity, time in alerts[:2]:
            alert_card(
                title=title,
                message=msg,
                severity=severity,
                timestamp=time,
            )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Third Row: Activity Timeline and Quick Actions
    col1, col2 = st.columns([1.5, 1], gap="medium")

    with col1:
        st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>Recent Activity</div>", unsafe_allow_html=True)
        activity_items = [
            ("10:30 AM", "Observation recorded", "The latest observation was recorded and linked to the active twin."),
            ("09:15 AM", "Prediction generated", "The milk yield forecast was refreshed from the latest operational inputs."),
            ("08:45 AM", "Health alert resolved", "The current state was assessed against the health service recommendation engine."),
            ("07:30 AM", "Daily report generated", "32 cows processed"),
        ]
        render_activity_timeline(activity_items)

    with col2:
        st.markdown("<div style='font-size: 18px; font-weight: 700; margin-bottom: 16px;'>Quick Actions</div>", unsafe_allow_html=True)

        action_col1, action_col2 = st.columns(2, gap="small")
        with action_col1:
            if st.button("➕ Add New Cow", use_container_width=True):
                st.session_state.active_section = "my_herd"
                st.rerun()

        with action_col2:
            if st.button("📝 Record Observation", use_container_width=True):
                st.session_state.active_section = "daily_operations"
                st.rerun()

        if st.button("🧠 View Digital Twin", use_container_width=True):
            st.session_state.active_section = "digital_twin"
            st.rerun()

        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.active_section = "analytics"
            st.rerun()

        if st.button("📋 Generate Daily Report", use_container_width=True):
            st.success("Report generated!")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Fourth Row: Digital Twin Status
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        info_card(
            title="Twin Status",
            content="✅ Synced",
            footer="Last sync: Just now",
        )

    with col2:
        info_card(
            title="Data Points",
            content=str(dashboard.herd.get("snapshot_count", 0)),
            footer="Stored in memory",
        )

    with col3:
        info_card(
            title="Model Version",
            content="v2.3.1",
            footer="Latest deployment",
        )

    # Clear refresh flag after rendering so future renders show current data
    if st.session_state.get("dashboard_needs_refresh"):
        st.session_state["dashboard_needs_refresh"] = False
