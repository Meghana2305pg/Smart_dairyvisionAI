"""Command centre screen."""
from __future__ import annotations

from typing import Any

import streamlit as st

from webapp.components.cards import info_card
from webapp.screens.activity_feed import build_activity_feed
from webapp.screens.live_alerts import build_alert_groups
from webapp.screens.system_health import build_system_health_payload
from webapp.screens.weather_monitor import build_weather_payload
from webapp.ui.section_header import render_page_header, render_section_header


def _normalise_cows(cows: Any) -> list[dict[str, Any]]:
    """Normalise cow records from session state or repository payloads."""
    if not cows:
        return []
    if isinstance(cows, dict):
        cows = [cows]
    normalised: list[dict[str, Any]] = []
    for item in cows:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("cow"), dict):
            normalised.append(dict(item["cow"]))
        else:
            normalised.append(dict(item))
    return normalised


def _normalise_observations(observations: Any) -> list[dict[str, Any]]:
    """Normalise observations to dictionaries."""
    if not observations:
        return []
    normalised: list[dict[str, Any]] = []
    for item in observations:
        if isinstance(item, dict):
            if isinstance(item.get("observation"), dict):
                normalised.append(dict(item["observation"]))
            else:
                normalised.append(dict(item))
    return normalised


def build_command_centre_context(
    cows: Any = None,
    observations: Any = None,
    predictions: Any = None,
    health: Any = None,
    recommendations: Any = None,
    twin_states: Any = None,
    weather: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Build a dashboard payload for the command centre workspace."""
    cow_list = _normalise_cows(cows)
    observation_list = _normalise_observations(observations)
    prediction_list = [item for item in (predictions or []) if isinstance(item, dict)]
    health_list = [item for item in (health or []) if isinstance(item, dict)]
    recommendation_list = [item for item in (recommendations or []) if isinstance(item, dict)]
    twin_state_list = [item for item in (twin_states or []) if isinstance(item, dict)]

    weather_payload = build_weather_payload(weather)
    alerts = build_alert_groups(health_list)
    activity_feed = build_activity_feed(observation_list)

    twin_monitor: list[dict[str, Any]] = []
    for cow in cow_list:
        cow_id = str(cow.get("cow_id") or "")
        twin_state = next((item for item in twin_state_list if str(item.get("cow_id") or "") == cow_id), None)
        twin_monitor.append(
            {
                "cow_id": cow_id,
                "name": cow.get("name") or cow_id or "Unassigned",
                "status": (twin_state or {}).get("status") or "stable",
                "health_status": cow.get("health_status", 0),
            }
        )
    if not twin_monitor and cow_list:
        twin_monitor = [
            {
                "cow_id": str(cow.get("cow_id") or ""),
                "name": cow.get("name") or "Cow",
                "status": "stable",
                "health_status": cow.get("health_status", 0),
            }
            for cow in cow_list
        ]

    healthy_cows = sum(1 for cow in cow_list if int(cow.get("health_status", 0) or 0) == 0)
    recommendations_payload: dict[str, list[dict[str, Any]]] = {"health": [], "ops": []}
    for item in recommendation_list:
        if item.get("priority") or item.get("message"):
            recommendations_payload["health"].append(item)
    if not recommendations_payload["health"] and cow_list:
        recommendations_payload["health"].append(
            {
                "cow_id": str(cow_list[0].get("cow_id") or ""),
                "message": "Maintain monitoring for the current herd conditions.",
                "priority": "Low",
            }
        )
    if activity_feed:
        recommendations_payload["ops"].append(
            {"message": "Review the latest observations and update follow-up actions.", "priority": "Medium"}
        )

    return {
        "summary": {
            "total_cows": len(cow_list),
            "healthy_cows": healthy_cows,
            "active_predictions": len(prediction_list),
            "alert_count": len(health_list),
        },
        "twin_monitor": twin_monitor,
        "alerts": alerts,
        "weather": weather_payload,
        "activity_feed": activity_feed,
        "recommendations": recommendations_payload,
        "system_health": build_system_health_payload(),
    }


def render_command_centre() -> None:
    """Render the command centre screen."""
    render_page_header(
        "Command Centre",
        "Monitor the herd, twin health, weather, and operational alerts in one workspace.",
        badge="Operations",
    )

    dashboard_service = st.session_state.get("dashboard_service")
    cows = st.session_state.get("cows", [])
    observations = []
    predictions = []
    health = []
    recommendations = []
    twin_states = []
    weather = None

    if dashboard_service is not None:
        try:
            dashboard = dashboard_service.build_dashboard()
            cows = cows or dashboard_service.repository.get_cows()
            observations = dashboard_service.repository.get_observations()
            predictions = dashboard.predictions
            health = dashboard.health
            recommendations = dashboard.recommendations
            twin_states = [{"cow_id": item.get("cow_id"), "status": "stable"} for item in predictions]
        except Exception:
            cows = cows or []

    context = build_command_centre_context(
        cows=cows,
        observations=observations,
        predictions=predictions,
        health=health,
        recommendations=recommendations,
        twin_states=twin_states,
        weather=weather,
    )

    search_term = st.text_input("Search cows", placeholder="Filter by cow ID or name")
    if search_term:
        filtered_monitor = [item for item in context["twin_monitor"] if search_term.lower() in str(item.get("cow_id", "")).lower() or search_term.lower() in str(item.get("name", "")).lower()]
        context["twin_monitor"] = filtered_monitor

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        info_card("Herd Size", str(context["summary"]["total_cows"]))
    with col2:
        info_card("Healthy Cows", str(context["summary"]["healthy_cows"]))
    with col3:
        info_card("Active Predictions", str(context["summary"]["active_predictions"]))
    with col4:
        info_card("Alerts", str(context["summary"]["alert_count"]))

    tab1, tab2, tab3 = st.tabs(["Overview", "Controls", "Monitoring"])

    with tab1:
        left_col, right_col = st.columns([1.4, 1], gap="medium")
        with left_col:
            render_section_header("Twin Monitor", "Track the live twin status for each cow.")
            if context["twin_monitor"]:
                for item in context["twin_monitor"]:
                    st.info(f"{item['name']} • {item['cow_id']} • {item['status']}", icon="🧠")
            else:
                st.info("No twin data is available yet.", icon="ℹ️")
        with right_col:
            render_section_header("Weather Snapshot", "Current ambient conditions and heat stress signals.")
            st.metric("Temperature", f"{context['weather']['temperature']:.1f} °C")
            st.metric("Humidity", f"{context['weather']['humidity']:.1f} %")
            st.metric("THI", f"{context['weather']['thi']:.1f}")
            st.metric("Heat Stress", context["weather"]["heat_stress"])

    with tab2:
        render_section_header("Operations Controls", "Refresh the workspace or review generated actions.")
        if st.button("Refresh Workspace", use_container_width=True):
            st.session_state["dashboard_needs_refresh"] = True
            st.success("Workspace refreshed.")
            st.rerun()
        if st.button("Review Recommendations", use_container_width=True):
            st.info("Open the recommendation centre below for the latest actions.")
        if st.button("Export Command Centre Snapshot", use_container_width=True):
            st.info("Snapshot export will be enabled in a future release.")

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        render_section_header("Recommendation Centre", "Operational guidance and follow-up actions.")
        if context["recommendations"]["health"]:
            for item in context["recommendations"]["health"]:
                st.warning(f"{item.get('priority', 'Low')} • {item.get('message', 'Keep monitoring')}", icon="💡")
        else:
            st.info("No recommendations were generated yet.", icon="ℹ️")

    with tab3:
        alert_col, activity_col = st.columns([1, 1], gap="medium")
        with alert_col:
            render_section_header("Alert Groups", "Grouped alerts by severity and source.")
            for label, items in context["alerts"].items():
                if items:
                    st.caption(f"{label.title()} alerts")
                    for item in items:
                        st.error(f"{item.get('cow_id', 'System')} • {item.get('severity', 'Unknown')}", icon="🚨")
                else:
                    st.info(f"No {label} alerts", icon="ℹ️")
        with activity_col:
            render_section_header("Recent Activity", "Recent events and operational updates.")
            if context["activity_feed"]:
                for item in context["activity_feed"]:
                    st.success(f"{item['cow_id']} • {item['summary']}", icon="📝")
            else:
                st.info("No recent activity is available yet.", icon="ℹ️")

            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
            render_section_header("System Health", "Summary state of the supporting services.")
            for key, value in context["system_health"].items():
                st.caption(f"{key.replace('_', ' ').title()}: {value}")
