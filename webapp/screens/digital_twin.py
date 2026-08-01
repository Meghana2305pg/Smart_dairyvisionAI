"""Digital twin screen."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import info_card, recommendation_card
from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.ui.section_header import render_page_header, render_section_header


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
    """Render the digital twin screen backed by the existing services."""
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

    if not twin.latest_observation and not observations:
        st.info("No observations are available yet for this cow. Record one from Daily Operations to populate the twin workspace.", icon="ℹ️")

    render_page_header(
        f"{dashboard['cow_name']} · Digital Twin",
        "Live twin state, recent observations, memory snapshots, and explainability insights for the selected cow.",
        badge="Twin",
    )

    refresh_col1, refresh_col2 = st.columns([1, 3], gap="small")
    with refresh_col1:
        if st.button("Refresh", use_container_width=True):
            if twin.latest_observation is not None:
                twin.refresh_from_ai(base_temp=twin.latest_observation.temperature, base_hum=twin.latest_observation.humidity)
            st.rerun()
    with refresh_col2:
        st.info("Refreshing reloads the current twin data without resetting authentication or farm state.", icon="ℹ️")

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        info_card("Twin state", dashboard["twin_state"].capitalize())
    with col2:
        info_card("Latest prediction", f"{(dashboard['latest_prediction'] or {}).get('prediction', 'n/a')} L/day")
    with col3:
        info_card("Health", str((dashboard['health_status'] or {}).get('alert_category', 'Unknown')))
    with col4:
        info_card("THI", f"{dashboard['thi']:.1f}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    render_section_header("Live twin workspace", "At-a-glance status and supporting detail for the active cow.")

    left_col, right_col = st.columns([1.1, 0.9], gap="medium")
    with left_col:
        if dashboard["latest_observation"]:
            info_card("Latest observation", f"{dashboard['latest_observation']['notes']} • {dashboard['latest_observation']['timestamp'].strftime('%Y-%m-%d %H:%M')}", footer="Temperature / humidity / feed captured from the latest record")
        else:
            info_card("Latest observation", "No observations recorded yet")
        if dashboard["weather"]:
            info_card("Weather", f"{dashboard['weather']['temperature']:.1f}°C • {dashboard['weather']['humidity']:.0f}% humidity")
        else:
            info_card("Weather", "Weather unavailable")

    with right_col:
        if dashboard["recommendations"]:
            for item in dashboard["recommendations"]:
                recommendation_card("Recommendation", item.get("message", "No guidance available"), icon="💡")
        else:
            st.info("No recommendations are available for this cow yet.", icon="ℹ️")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    timeline_col, memory_col = st.columns([1.2, 0.8], gap="medium")
    with timeline_col:
        render_section_header("Observation timeline", "Chronological observation history for the selected cow.")
        if dashboard["timeline"]:
            for item in reversed(dashboard["timeline"]):
                st.markdown(
                    f"""
                    <div style='background: white; border: 1px solid #e5ebf2; border-radius: 12px; padding: 14px; margin-bottom: 10px;'>
                        <div style='font-size: 14px; font-weight: 700; color: #0f172a;'>{item['timestamp']}</div>
                        <div style='font-size: 13px; color: #475569; margin-top: 6px;'>{item['notes']}</div>
                        <div style='font-size: 12px; color: #64748b; margin-top: 8px;'>Temp: {item['temperature'] if item['temperature'] is not None else 'n/a'} °C • Humidity: {item['humidity'] if item['humidity'] is not None else 'n/a'} % • Feed: {item['feed'] if item['feed'] is not None else 'n/a'} kg</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No observations have been recorded for this cow yet.", icon="ℹ️")

    with memory_col:
        render_section_header("Twin Memory", "Stored snapshots and memory state for the twin.")
        info_card("Snapshots", str(dashboard['memory_info']['snapshot_count']))
        info_card("Latest snapshot", dashboard['memory_info']['latest_snapshot_id'] or "None")
        info_card("Last updated", dashboard['last_updated'].strftime('%Y-%m-%d %H:%M') if dashboard['last_updated'] else "Awaiting updates")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Explainability summary</div>", unsafe_allow_html=True)
    if dashboard["explainability_summary"]:
        for item in dashboard["explainability_summary"][:5]:
            recommendation_card("SHAP feature", f"{item.get('feature', 'feature')}: {item.get('contribution', 0.0):.3f}", icon="🔍")
    else:
        st.info("Explainability outputs are not available for this cow yet.", icon="ℹ️")
