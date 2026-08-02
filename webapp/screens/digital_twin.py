"""Digital twin screen."""
from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.ui.digital_twin_ui import (
    render_ai_decision_center,
    render_digital_twin_hero,
    render_horizontal_timeline,
    render_kpi_row,
    render_playback_controls,
    render_scenario_studio_card,
    render_snapshot_cards,
    render_status_panel,
    render_trend_chart_card,
)


def _normalize_observation(observation: Any) -> dict[str, Any]:
    """Normalize observation data from different sources into a display-friendly dict."""
    if isinstance(observation, dict) and "observation" in observation:
        observation = observation["observation"]
    if not isinstance(observation, dict):
        return {}

    timestamp = observation.get("timestamp")
    if isinstance(timestamp, datetime):
        timestamp_value = timestamp
    elif isinstance(timestamp, str):
        try:
            timestamp_value = datetime.fromisoformat(timestamp)
        except ValueError:
            timestamp_value = datetime.utcnow()
    else:
        timestamp_value = datetime.utcnow()

    return {
        "cow_id": observation.get("cow_id"),
        "notes": observation.get("notes") or "No notes recorded",
        "temperature": observation.get("temperature"),
        "humidity": observation.get("humidity"),
        "feed": observation.get("feed"),
        "weight": observation.get("weight"),
        "health_status": observation.get("health_status"),
        "timestamp": timestamp_value,
    }


def build_dashboard_context(
    *,
    cow_twin: CowTwin,
    cow_record: dict[str, Any] | None,
    observations: list[dict[str, Any]],
    weather: tuple[float, float] | None,
    prediction: dict[str, Any] | None,
    health: dict[str, Any] | None,
    explanation: list[dict[str, Any]] | None,
    memory_snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the backend-driven payload for the digital twin workspace."""
    normalized_observations = [_normalize_observation(item) for item in observations]
    latest_observation = normalized_observations[-1] if normalized_observations else None
    latest_prediction = prediction or (cow_twin.latest_prediction or {})
    latest_health = health or (cow_twin.latest_health or {})
    latest_explanation = explanation or (cow_twin.latest_explanation or [])
    weather_payload = {"temperature": weather[0], "humidity": weather[1]} if weather else None

    temperature = weather_payload["temperature"] if weather_payload else (latest_observation.get("temperature") if latest_observation else 28.0)
    humidity = weather_payload["humidity"] if weather_payload else (latest_observation.get("humidity") if latest_observation else 65.0)
    temperature = float(temperature or 28.0)
    humidity = float(humidity or 65.0)
    thi = round((0.8 * temperature) + ((humidity / 100.0) * (temperature - 14.4)) + 16.4, 1)

    recommendations = []
    if latest_health and latest_health.get("recommendation"):
        recommendations.append({"message": latest_health.get("recommendation"), "priority": latest_health.get("severity", "Low")})
    if cow_twin.recommendations:
        for item in cow_twin.recommendations:
            if isinstance(item, dict) and item.get("message"):
                recommendations.append({"message": item.get("message"), "priority": item.get("priority", "Low")})

    timeline = [
        {
            "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M") if item.get("timestamp") else "n/a",
            "notes": item.get("notes") or "No notes recorded",
            "temperature": item.get("temperature"),
            "humidity": item.get("humidity"),
            "feed": item.get("feed"),
        }
        for item in normalized_observations
    ]

    return {
        "cow_id": cow_record.get("cow_id") if cow_record else cow_twin.cow_id,
        "cow_name": cow_record.get("name") if cow_record else cow_twin.name or cow_twin.cow_id,
        "cow_record": cow_record or {},
        "latest_observation": latest_observation,
        "latest_prediction": latest_prediction,
        "health_status": latest_health,
        "weather": weather_payload,
        "thi": thi,
        "recommendations": recommendations,
        "timeline": timeline,
        "memory_info": {
            "snapshot_count": len(memory_snapshots),
            "latest_snapshot_id": memory_snapshots[-1].get("snapshot_id") if memory_snapshots else None,
            "latest_timestamp": memory_snapshots[-1].get("timestamp") if memory_snapshots else None,
        },
        "explainability_summary": latest_explanation,
        "twin_state": cow_twin.state.status,
        "last_updated": cow_twin.state.last_updated,
    }


def _get_or_create_twin(cow_service: CowService, cow_id: str, name: str | None = None) -> CowTwin:
    """Reuse an existing digital twin or create one from the current cow record."""
    twin = cow_service._cow_twins.get(cow_id)
    if twin is None:
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        cow_service._cow_twins[cow_id] = twin
    return twin


def render_digital_twin() -> None:
    """Render the digital twin workspace in a dashboard layout while preserving the existing underlying data flow."""
    cow_service: CowService = st.session_state.cow_service
    observation_service = st.session_state.observation_service
    selected_cow_id = st.session_state.get("selected_cow_id")

    if not selected_cow_id:
        st.warning("No cow selected. Open My Herd and choose a cow to view the digital twin workspace.", icon="ℹ️")
        return

    cows = cow_service.get_cows()
    cow_record = None
    for item in cows:
        cow = item.get("cow", item)
        if cow.get("cow_id") == selected_cow_id:
            cow_record = cow
            break

    if not cow_record:
        st.error(f"Cow {selected_cow_id} was not found.")
        return

    twin = _get_or_create_twin(cow_service, selected_cow_id, cow_record.get("name"))
    observations = observation_service.repository.list_for_cow(selected_cow_id)
    memory_snapshots = twin.memory_store.list_snapshot_history(selected_cow_id)
    memory_payload = [
        {
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": snapshot.timestamp,
            "twin_status": snapshot.twin_status,
        }
        for snapshot in memory_snapshots
    ]

    if not twin.latest_observation and observations:
        latest_observation_payload = Observation(
            cow_id=selected_cow_id,
            age=float(cow_record.get("age_months") or 24.0),
            weight=float(cow_record.get("weight") or 500.0),
            feed=float(cow_record.get("feed") or 20.0),
            temperature=float(cow_record.get("temperature") or 28.0),
            humidity=float(cow_record.get("humidity") or 65.0),
            health_status=int(cow_record.get("health_status") or 0),
            notes="Latest recorded observation",
        )
        twin.record_observation(latest_observation_payload)
        twin.refresh_from_ai(base_temp=latest_observation_payload.temperature, base_hum=latest_observation_payload.humidity)

    weather = None
    try:
        weather = get_current_weather()
    except Exception:
        weather = None

    prediction = twin.latest_prediction if twin.latest_prediction else None
    health = twin.latest_health if twin.latest_health else None
    explanation = twin.latest_explanation if twin.latest_explanation else None

    dashboard = build_dashboard_context(
        cow_twin=twin,
        cow_record=cow_record,
        observations=observations,
        weather=weather,
        prediction=prediction,
        health=health,
        explanation=explanation,
        memory_snapshots=memory_payload,
    )

    weather_payload = dashboard.get('weather') or {}

    st.markdown(
        """
        <style>
        .twin-shell { padding-top: 0.2rem; }
        .twin-section-stack { display: grid; gap: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="twin-shell">', unsafe_allow_html=True)

    if not twin.latest_observation and not observations:
        st.info("No observations are available yet for this cow. Record one from Daily Operations to populate the twin workspace.", icon="ℹ️")

    weather_label = f"Weather {weather_payload.get('temperature', 'n/a')}°C / {weather_payload.get('humidity', 'n/a')}%"
    render_digital_twin_hero(
        cow_name=dashboard['cow_name'],
        breed=str(cow_record.get("breed") or "Holstein"),
        age=f"{cow_record.get('age_months', 'n/a')} months",
        farm=str(cow_record.get("farm_name") or cow_record.get("farm") or "Farm Workspace"),
        twin_status=dashboard['twin_state'].capitalize(),
        last_updated=str(dashboard.get('last_updated') or datetime.now().strftime('%Y-%m-%d %H:%M')),
        weather=weather_label,
        weather_tone="info",
    )

    refresh_col1, refresh_col2 = st.columns([1, 3], gap="small")
    with refresh_col1:
        if st.button("Refresh", use_container_width=True):
            if twin.latest_observation is not None:
                twin.refresh_from_ai(base_temp=twin.latest_observation.temperature, base_hum=twin.latest_observation.humidity)
            st.rerun()
    with refresh_col2:
        st.info("This refresh keeps the same backend logic and only reloads the current twin state.", icon="ℹ️")

    health_status = dashboard['health_status'] or {}
    status_key = str(health_status.get('alert_category', 'Healthy')).lower()
    if "critical" in status_key or "risk" in status_key or "severe" in status_key:
        health_tone = "danger"
        health_label = "Critical"
    elif "warning" in status_key or "medium" in status_key or "high" in status_key:
        health_tone = "warning"
        health_label = "Warning"
    elif "healthy" in status_key or "low" in status_key or "normal" in status_key:
        health_tone = "success"
        health_label = "Healthy"
    else:
        health_tone = "neutral"
        health_label = "Stable"

    prediction_value = (dashboard['latest_prediction'] or {}).get('prediction', 'n/a')
    latest_observation = dashboard['latest_observation'] or {}
    weather_payload = dashboard.get('weather') or {}
    observed_temp = latest_observation.get('temperature', weather_payload.get('temperature', 'n/a'))
    observed_humidity = latest_observation.get('humidity', weather_payload.get('humidity', 'n/a'))
    observed_weight = latest_observation.get('weight', 'n/a')
    observed_feed = latest_observation.get('feed', 'n/a')

    render_kpi_row([
        {"title": "Health Score", "value": health_label, "subtitle": f"{health_status.get('stress_category', 'Stable')} · {health_status.get('severity', 'Low')}", "tone": health_tone, "icon": "🩺"},
        {"title": "Twin Score", "value": dashboard['twin_state'].capitalize(), "subtitle": "Current twin coherence", "tone": "info", "icon": "🧠"},
        {"title": "Milk Prediction", "value": f"{prediction_value} L/day" if prediction_value != 'n/a' else 'n/a', "subtitle": "Latest forecast", "tone": "success", "icon": "💧"},
        {"title": "Heat Risk", "value": f"{dashboard['thi']:.1f} THI", "subtitle": "Thermal humidity index", "tone": "warning", "icon": "🌡️"},
        {"title": "Prediction Confidence", "value": f"{health_status.get('confidence', 'High')}", "subtitle": "AI confidence signal", "tone": "neutral", "icon": "🎯"},
    ])

    render_status_panel(
        "Current Twin Status",
        [
            ("Temperature", f"{observed_temp} °C", "Live thermal reading", "🌡️"),
            ("Humidity", f"{observed_humidity} %", "Ambient moisture", "💧"),
            ("THI", f"{dashboard['thi']:.1f}", "Heat stress index", "📊"),
            ("Weight", f"{observed_weight} kg", "Body mass trend", "⚖️"),
            ("Feed Intake", f"{observed_feed} kg/day", "Daily nutrition", "🥣"),
            ("Weather", f"{weather_payload.get('temperature', 'n/a')}°C / {weather_payload.get('humidity', 'n/a')}%", "External environment", "🌤️"),
        ],
    )

    render_horizontal_timeline(dashboard['timeline'])
    render_snapshot_cards(dashboard['timeline'])
    render_ai_decision_center(dashboard['recommendations'])

    trend_df = pd.DataFrame(
        [
            {"step": "Start", "value": float(latest_observation.get('weight') or 0)},
            {"step": "Now", "value": float(latest_observation.get('weight') or 0)},
        ]
    )
    trend_df = trend_df if not trend_df.empty else pd.DataFrame(columns=["step", "value"])
    col_trend_left, col_trend_center, col_trend_right = st.columns(3, gap="small")
    with col_trend_left:
        render_trend_chart_card("Milk Trend", trend_df, "step", "value", empty_message="More milk observations will populate this trend view over time.")
    with col_trend_center:
        render_trend_chart_card("Health Trend", pd.DataFrame(columns=["step", "value"]), "step", "value", empty_message="Health signals will appear here as observations are added.")
    with col_trend_right:
        render_trend_chart_card("THI Trend", pd.DataFrame(columns=["step", "value"]), "step", "value", empty_message="Environmental history will be displayed once more data is available.")

    render_playback_controls()

    render_scenario_studio_card()
    if st.button("Launch Scenario Studio", use_container_width=True, type="primary"):
        st.session_state.active_section = "scenario_studio"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
