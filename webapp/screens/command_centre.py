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
    """Render the operations centre as a dashboard for daily herd monitoring."""
    st.markdown(
        """
        <style>
        .ops-shell { padding-top: 0.35rem; }
        .ops-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.8rem; margin-bottom: 1rem; }
        .ops-panel { background: rgba(255,255,255,0.96); border: 1px solid rgba(148,163,184,0.14); border-radius: 18px; padding: 1rem; box-shadow: 0 10px 22px rgba(15,23,42,0.04); margin-top: 1rem; }
        .ops-title { font-size: 0.76rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #475569; margin-bottom: 0.7rem; }
        .ops-card { background: rgba(248,250,252,0.96); border: 1px solid rgba(148,163,184,0.14); border-radius: 14px; padding: 0.85rem; margin-bottom: 0.7rem; }
        .ops-card strong { color: #0f172a; }
        .nav-button { width: 100%; margin-bottom: 0.5rem; }
        @media (max-width: 980px) { .ops-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 620px) { .ops-kpis { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_page_header(
        "Operations Center",
        "A daily operations dashboard for monitoring herd activity, alerts, weather, and next actions.",
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

    st.markdown('<div class="ops-shell">', unsafe_allow_html=True)
    st.markdown('<div class="ops-kpis">', unsafe_allow_html=True)
    summary_cards = [
        ("Herd Size", str(context["summary"]["total_cows"])),
        ("Healthy Cows", str(context["summary"]["healthy_cows"])),
        ("Active Predictions", str(context["summary"]["active_predictions"])),
        ("Alerts", str(context["summary"]["alert_count"])),
    ]
    for label, value in summary_cards:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="panel-title">{label}</div>
                <div style="font-size: clamp(1.5rem, 1.8vw, 2rem); font-weight: 800; letter-spacing: -0.08em; color: #0f172a;">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    search_term = st.text_input("Search cows", placeholder="Filter by cow ID or name")
    if search_term:
        filtered_monitor = [item for item in context["twin_monitor"] if search_term.lower() in str(item.get("cow_id", "")).lower() or search_term.lower() in str(item.get("name", "")).lower()]
        context["twin_monitor"] = filtered_monitor

    overview_col, side_col = st.columns([1.5, 0.9], gap="medium")
    with overview_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">Today\'s Overview</div>', unsafe_allow_html=True)
        if context["twin_monitor"]:
            for item in context["twin_monitor"]:
                st.markdown(
                    f"""
                    <div class="ops-card">
                        <strong>{item.get('name', 'Cow')}</strong><br>
                        Cow ID: {item.get('cow_id', 'Unknown')}<br>
                        Status: {item.get('status', 'stable')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No twin data is available yet.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    with side_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">Weather</div>', unsafe_allow_html=True)
        if context["weather"]:
            st.metric("Temperature", f"{context['weather']['temperature']:.1f} °C")
            st.metric("Humidity", f"{context['weather']['humidity']:.1f} %")
            st.metric("THI", f"{context['weather']['thi']:.1f}")
            st.metric("Heat Stress", context["weather"]["heat_stress"])
        else:
            st.info("Weather data is unavailable.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    alert_col, activity_col = st.columns([1.1, 0.9], gap="medium")
    with alert_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">Critical Alerts</div>', unsafe_allow_html=True)
        if context["alerts"].get("critical"):
            for item in context["alerts"]["critical"]:
                st.warning(f"{item.get('cow_id', 'System')} • {item.get('severity', 'Unknown')} • {item.get('message', 'Alert details available')}", icon="🚨")
        else:
            st.info("No critical alerts are active at this time.", icon="✅")
        st.markdown('</div>', unsafe_allow_html=True)

    with activity_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">Recent Activity</div>', unsafe_allow_html=True)
        if context["activity_feed"]:
            for item in context["activity_feed"][:5]:
                st.info(f"{item['cow_id']} • {item['summary']}", icon="📝")
        else:
            st.info("No recent activity is available yet.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    pending_col, recommend_col = st.columns([1.1, 0.9], gap="medium")
    with pending_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">Pending Actions</div>', unsafe_allow_html=True)
        if context["recommendations"]["health"]:
            for item in context["recommendations"]["health"][:5]:
                st.markdown(
                    f"""
                    <div class="ops-card">
                        <strong>{item.get('priority', 'Low')}</strong><br>
                        {item.get('message', 'Maintain monitoring for current conditions.')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("There are no pending actions for the current herd state.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    with recommend_col:
        st.markdown('<div class="ops-panel"><div class="ops-title">AI Recommendations</div>', unsafe_allow_html=True)
        if context["recommendations"]["ops"]:
            for item in context["recommendations"]["ops"]:
                st.success(f"{item.get('priority', 'Medium')} • {item.get('message', 'Continue current operations.')}", icon="💡")
        else:
            st.info("No AI recommendations are available for the current context.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ops-panel"><div class="ops-title">Quick Navigation</div>', unsafe_allow_html=True)
    quick_cols = st.columns(4, gap="small")
    navigation_targets = [
        ("Dashboard", "dashboard"),
        ("My Herd", "my_herd"),
        ("Health Alerts", "health_alerts"),
        ("Analytics", "analytics"),
    ]
    for index, (label, section_key) in enumerate(navigation_targets):
        with quick_cols[index % 4]:
            if st.button(label, key=f"ops_nav_{section_key}", use_container_width=True):
                st.session_state.active_section = section_key
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
