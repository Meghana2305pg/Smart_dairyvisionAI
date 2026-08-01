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

    st.markdown(
        """
        <style>
        .twin-shell { padding-top: 0.3rem; }
        .twin-header {
            margin-bottom: 1rem;
        }
        .twin-title {
            font-size: clamp(1.9rem, 2vw, 2.6rem);
            font-weight: 800;
            letter-spacing: -0.06em;
            margin: 0;
            color: #0f172a;
        }
        .twin-subtitle {
            color: #64748b;
            font-size: 0.96rem;
            margin-top: 0.25rem;
        }
        .twin-summary-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.8rem;
            margin-bottom: 1rem;
        }
        .twin-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem;
            min-height: 128px;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04);
        }
        .twin-card .label {
            color: #64748b;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 800;
        }
        .twin-card .value {
            font-size: clamp(1.2rem, 1.6vw, 1.8rem);
            font-weight: 800;
            letter-spacing: -0.05em;
            color: #0f172a;
            margin: 0.5rem 0 0.2rem;
        }
        .twin-card .meta {
            font-size: 0.8rem;
            color: #475569;
        }
        .twin-panel {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04);
            padding: 1rem;
            margin-top: 1rem;
        }
        .twin-panel-title {
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            font-weight: 800;
            color: #475569;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }
        .twin-recommendation {
            background: linear-gradient(180deg, rgba(255,255,255,1), rgba(248,250,252,0.98));
            border: 1px solid rgba(148,163,184,0.14);
            border-radius: 14px;
            padding: 0.9rem;
            margin-bottom: 0.8rem;
        }
        .twin-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.34rem 0.64rem;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .twin-pill.success { background: rgba(21,128,61,0.12); color: #15803d; }
        .twin-pill.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .twin-pill.danger { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .twin-pill.neutral { background: rgba(148,163,184,0.12); color: #475569; }
        @media (max-width: 1100px) { .twin-summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 620px) { .twin-summary-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="twin-shell">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="twin-header">
            <h1 class="twin-title">{dashboard['cow_name']} · Digital Twin</h1>
            <div class="twin-subtitle">Live status, recent behavior, predictive insights, and AI-guided recommendations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not twin.latest_observation and not observations:
        st.info("No observations are available yet for this cow. Record one from Daily Operations to populate the twin workspace.", icon="ℹ️")

    refresh_col1, refresh_col2 = st.columns([1, 3], gap="small")
    with refresh_col1:
        if st.button("Refresh", use_container_width=True):
            if twin.latest_observation is not None:
                twin.refresh_from_ai(base_temp=twin.latest_observation.temperature, base_hum=twin.latest_observation.humidity)
            st.rerun()
    with refresh_col2:
        st.info("This refresh keeps the same backend logic and only reloads the current twin state.", icon="ℹ️")

    st.markdown('<div class="twin-summary-grid">', unsafe_allow_html=True)
    status_key = str((dashboard['health_status'] or {}).get('alert_category', 'Healthy')).lower()
    if "critical" in status_key or "risk" in status_key or "severe" in status_key:
        badge_class = "danger"
        badge_text = "Critical"
    elif "warning" in status_key or "medium" in status_key or "high" in status_key:
        badge_class = "warning"
        badge_text = "Warning"
    elif "healthy" in status_key or "low" in status_key or "normal" in status_key:
        badge_class = "success"
        badge_text = "Healthy"
    else:
        badge_class = "neutral"
        badge_text = "Stable"

    summary_cards = [
        ("Twin Status", dashboard['twin_state'].capitalize(), "Current twin state"),
        ("Current Health", badge_text, "Health classification"),
        ("Milk Yield", f"{(dashboard['latest_prediction'] or {}).get('prediction', 'n/a')} L/day", "Latest prediction"),
        ("Feed Status", f"{(dashboard['latest_observation'] or {}).get('feed', 'n/a')} kg/day", "Most recent feed intake"),
        ("Environment", f"{dashboard['thi']:.1f} THI", "Thermal humidity index"),
    ]
    for label, value, meta in summary_cards:
        st.markdown(
            f"""
            <div class="twin-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="meta">{meta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.15, 0.85], gap="medium")

    with left_col:
        st.markdown('<div class="twin-panel"><div class="twin-panel-title">Current State</div>', unsafe_allow_html=True)
        if dashboard["latest_observation"]:
            st.write(f"Latest observation: {dashboard['latest_observation']['notes']}")
            st.write(f"Temperature: {dashboard['latest_observation']['temperature']} °C")
            st.write(f"Humidity: {dashboard['latest_observation']['humidity']} %")
            st.write(f"Weight: {dashboard['latest_observation']['weight']} kg")
        else:
            st.write("No latest observation is available yet.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="twin-panel"><div class="twin-panel-title">Prediction Summary</div>', unsafe_allow_html=True)
        prediction_value = (dashboard['latest_prediction'] or {}).get('prediction', 'n/a')
        st.metric("Predicted Milk Yield", f"{prediction_value} L/day" if prediction_value != 'n/a' else 'n/a')
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="twin-panel"><div class="twin-panel-title">Recent Behaviour</div>', unsafe_allow_html=True)
        if dashboard['timeline']:
            for item in reversed(dashboard['timeline'][-3:]):
                st.write(f"- {item['timestamp']} • {item['notes']}")
        else:
            st.write("No recent behavior data has been recorded yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="twin-panel"><div class="twin-panel-title">AI Insights</div>', unsafe_allow_html=True)
        if dashboard['health_status']:
            st.write(f"Alert category: {dashboard['health_status'].get('alert_category', 'Healthy')}")
            st.write(f"Severity: {dashboard['health_status'].get('severity', 'Low')}")
            st.write(f"Stress category: {dashboard['health_status'].get('stress_category', 'Normal')}")
        else:
            st.write("No AI health insight is available yet.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="twin-panel"><div class="twin-panel-title">Recommendations</div>', unsafe_allow_html=True)
        if dashboard['recommendations']:
            for item in dashboard['recommendations'][:4]:
                st.markdown(
                    f"""
                    <div class="twin-recommendation">
                        <div class="twin-pill {badge_class}">{badge_text}</div>
                        <div style="margin-top: 0.55rem; color: #334155;">{item.get('message', 'No guidance available')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No recommendations have been generated yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="twin-panel"><div class="twin-panel-title">Timeline</div>', unsafe_allow_html=True)
    if dashboard['timeline']:
        for item in reversed(dashboard['timeline'][:6]):
            st.write(f"- {item['timestamp']} • {item['notes']}")
    else:
        st.write("No twin timeline entries are available yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
