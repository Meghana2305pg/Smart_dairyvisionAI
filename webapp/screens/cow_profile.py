"""Cow profile screen."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import info_card, recommendation_card
from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService


def _normalize_observation(observation: Any) -> dict[str, Any]:
    """Normalize observation payloads from the repository into a display-friendly dict."""
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


def _get_or_create_twin(cow_service: CowService, cow_id: str, name: str | None = None) -> CowTwin:
    """Reuse an existing digital twin or create one from the current cow record."""
    twin = cow_service._cow_twins.get(cow_id)
    if twin is None:
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        cow_service._cow_twins[cow_id] = twin
    return twin


def render_cow_profile() -> None:
    """Render the individual cow profile in a structured, professional profile layout."""
    cow_service: CowService = st.session_state.cow_service
    observation_service = st.session_state.observation_service
    selected_cow_id = st.session_state.get("selected_cow_id")

    if not selected_cow_id:
        st.warning("No cow selected. Please select a cow from My Herd.")
        if st.button("Go to My Herd"):
            st.session_state.active_section = "my_herd"
            st.rerun()
        return

    cows = cow_service.get_cows()
    cow_dict = None
    for item in cows:
        cow = item.get("cow", item)
        if cow.get("cow_id") == selected_cow_id:
            cow_dict = cow
            break

    if not cow_dict:
        st.error(f"Cow {selected_cow_id} not found.")
        return

    twin = _get_or_create_twin(cow_service, selected_cow_id, cow_dict.get("name"))
    observations = [_normalize_observation(item) for item in observation_service.repository.list_for_cow(selected_cow_id)]

    base_temp, base_hum = get_current_weather()
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
    current_prediction = float(twin.latest_prediction.get("prediction", prediction.get("prediction", 0.0)) or 0.0) if twin.latest_prediction else float(prediction.get("prediction", 0.0) or 0.0)
    health_category = health.get("alert_category", "Healthy")
    if twin.latest_health:
        health_category = twin.latest_health.get("alert_category", health_category)
    current_status = "Synced" if twin.latest_observation else "Awaiting observation"
    latest_observation = observations[-1] if observations else None
    latest_observation_time = latest_observation["timestamp"].strftime("%Y-%m-%d %H:%M") if latest_observation else "No observation yet"

    health_badge = "Healthy"
    health_tone = "success"
    health_lower = str(health_category).lower()
    if "critical" in health_lower or "risk" in health_lower or "severe" in health_lower:
        health_badge = "Critical"
        health_tone = "danger"
    elif "warning" in health_lower or "medium" in health_lower or "high" in health_lower:
        health_badge = "Warning"
        health_tone = "warning"

    st.markdown(
        """
        <style>
        .cow-profile-shell { padding-top: 0.3rem; }
        .cow-header-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.99), rgba(239,246,255,0.88));
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 22px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .cow-header-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .cow-profile-main {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .cow-avatar {
            width: 72px;
            height: 72px;
            border-radius: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            box-shadow: inset 0 0 0 1px rgba(37,99,235,0.08);
        }
        .cow-name {
            margin: 0;
            font-size: clamp(1.8rem, 2.2vw, 2.6rem);
            font-weight: 800;
            letter-spacing: -0.06em;
            color: #0f172a;
        }
        .cow-meta {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.2rem;
        }
        .cow-badges {
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-top: 0.75rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.72rem;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .status-badge.success { background: rgba(21,128,61,0.12); color: #15803d; }
        .status-badge.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .status-badge.danger { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .status-badge.neutral { background: rgba(148,163,184,0.12); color: #475569; }
        .profile-action-bar {
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-bottom: 1rem;
        }
        .summary-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem;
            min-height: 128px;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
        }
        .summary-card .label {
            color: #64748b;
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 800;
        }
        .summary-card .value {
            font-size: clamp(1.2rem, 1.6vw, 1.8rem);
            font-weight: 800;
            letter-spacing: -0.05em;
            color: #0f172a;
            margin: 0.55rem 0 0.25rem;
        }
        .summary-card .meta {
            font-size: 0.8rem;
            color: #475569;
        }
        .profile-section {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
            margin-top: 1rem;
        }
        .profile-section-title {
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: 0.8rem;
        }
        .timeline-item {
            border-left: 2px solid rgba(148,163,184,0.35);
            padding-left: 1rem;
            margin-left: 0.4rem;
            position: relative;
            margin-bottom: 1rem;
        }
        .timeline-item::before {
            content: "";
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #2563eb;
            position: absolute;
            left: -6px;
            top: 4px;
        }
        .timeline-item .event {
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .timeline-item .meta {
            color: #64748b;
            font-size: 0.8rem;
        }
        @media (max-width: 900px) {
            .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 620px) {
            .summary-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cow-profile-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="cow-header-card">
            <div class="cow-header-inner">
                <div class="cow-profile-main">
                    <div class="cow-avatar">🐄</div>
                    <div>
                        <h1 class="cow-name">{}</h1>
                        <div class="cow-meta">Cow ID: {} • Breed: {} • Age: {} months</div>
                        <div class="cow-badges">
                            <span class="status-badge {}">{}</span>
                            <span class="status-badge neutral">Twin: {}</span>
                        </div>
                    </div>
                </div>
                <div class="profile-action-bar">
                    <button type="button" class="stButton" onclick="document.querySelector('button[kind=primary]').click()"> </button>
                </div>
            </div>
        </div>
        """.format(
            cow_dict.get("name", "Unknown"),
            selected_cow_id,
            cow_dict.get("breed", "N/A"),
            cow_dict.get("age_months", "N/A"),
            health_tone,
            health_badge,
            current_status,
        ),
        unsafe_allow_html=True,
    )

    action_cols = st.columns(3, gap="small")
    with action_cols[0]:
        if st.button("Edit Cow", use_container_width=True, type="secondary"):
            st.session_state.editing_cow_id = selected_cow_id
            st.session_state.active_section = "my_herd"
            st.rerun()
    with action_cols[1]:
        if st.button("Record Observation", use_container_width=True, type="primary"):
            st.session_state.selected_cow_id = selected_cow_id
            st.session_state.daily_ops_cow = selected_cow_id
            st.session_state.active_section = "daily_operations"
            st.rerun()
    with action_cols[2]:
        if st.button("Open Digital Twin", use_container_width=True, type="secondary"):
            st.session_state.selected_cow_id = selected_cow_id
            st.session_state.active_section = "digital_twin"
            st.rerun()

    st.markdown('<div class="summary-grid">', unsafe_allow_html=True)
    summary_cards = [
        ("Age", f"{cow_dict.get('age_months', 'N/A')} mo", "Lifecycle stage"),
        ("Weight", f"{cow_dict.get('weight', defaults.get('weight', 450.0))} kg", "Current body weight"),
        ("Breed", cow_dict.get("breed", "N/A"), "Genetic type"),
        ("Health Status", health_badge, "Alert band"),
    ]
    for label, value, meta in summary_cards:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="meta">{meta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="summary-grid">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="label">Today's Milk Prediction</div>
            <div class="value">{current_prediction:.1f} L/day</div>
            <div class="meta">Generated from the current model inputs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="label">Last Observation</div>
            <div class="value">{latest_observation_time}</div>
            <div class="meta">Latest captured record</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Overview", "Health", "Production", "History", "Twin"])

    with tabs[0]:
        st.markdown('<div class="profile-section"><div class="profile-section-title">Overview</div>', unsafe_allow_html=True)
        overview_cols = st.columns(3, gap="medium")
        with overview_cols[0]:
            st.metric("Age", f"{cow_dict.get('age_months', 'N/A')} months")
        with overview_cols[1]:
            st.metric("Weight", f"{cow_dict.get('weight', defaults.get('weight', 450.0))} kg")
        with overview_cols[2]:
            st.metric("Health", health_badge)

        latest_note = latest_observation["notes"] if latest_observation else "No observations recorded yet"
        st.write(f"Latest observation: {latest_note}")
        st.write(f"Current prediction: {current_prediction:.1f} L/day")
        st.write(f"Current weather: {base_temp:.1f}°C / {base_hum:.0f}% humidity")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="profile-section"><div class="profile-section-title">Health</div>', unsafe_allow_html=True)
        if observations:
            st.subheader("Recent observations")
            for item in observations[-3:][::-1]:
                st.write(f"- {item['timestamp'].strftime('%Y-%m-%d %H:%M')} • {item['notes']}")
        else:
            st.info("No observations recorded yet for this cow.", icon="ℹ️")

        st.subheader("Health alerts")
        st.write(f"Alert category: {health_category}")
        st.write(f"Recommendation: {health.get('recommendation', 'No recommendation available')}")

        st.subheader("Treatment / vaccination details")
        st.info("No vaccination or treatment records are available for this cow in the current dataset.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="profile-section"><div class="profile-section-title">Production</div>', unsafe_allow_html=True)
        st.metric("Milk prediction", f"{current_prediction:.1f} L/day")
        if twin.state.predictions:
            prediction_df = pd.DataFrame(twin.state.predictions)
            if not prediction_df.empty:
                st.line_chart(prediction_df.set_index("timestamp")["prediction"] if "timestamp" in prediction_df.columns else prediction_df.set_index(prediction_df.index)["prediction"])
        else:
            st.info("No prediction history available yet.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="profile-section"><div class="profile-section-title">History</div>', unsafe_allow_html=True)
        timeline_events = []
        for obs in reversed(observations):
            timeline_events.append((obs["timestamp"], "Observation recorded", obs["notes"]))
        if twin.latest_prediction:
            timeline_events.append((datetime.utcnow(), "Prediction generated", f"{float(twin.latest_prediction.get('prediction', current_prediction) or 0.0):.1f} L/day"))
        if twin.latest_health:
            timeline_events.append((datetime.utcnow(), "Health alert", str(twin.latest_health.get("alert_category", health_category))))
        if twin.latest_observation:
            timeline_events.append((datetime.utcnow(), "Twin updated", "Digital twin refreshed with latest observation"))

        if timeline_events:
            for ts, title, details in sorted(timeline_events, key=lambda item: item[0], reverse=True)[:8]:
                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <div class="event">{title}</div>
                        <div class="meta">{ts.strftime('%Y-%m-%d %H:%M') if isinstance(ts, datetime) else ts}</div>
                        <div class="meta">{details}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No history is available yet for this cow.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('<div class="profile-section"><div class="profile-section-title">Twin</div>', unsafe_allow_html=True)
        st.write(f"Twin status: {current_status}")
        if twin.latest_observation:
            st.write(f"Latest observation snapshot: {twin.latest_observation.notes}")
        if twin.latest_health:
            st.write(f"Health summary: {twin.latest_health.get('alert_category', health_category)}")
        if twin.recommendations:
            for rec in twin.recommendations[:3]:
                st.write(f"- {rec.get('message') if isinstance(rec, dict) else str(rec)}")
        else:
            st.info("No twin recommendations are available yet.", icon="ℹ️")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    secondary_actions = st.columns([1, 1], gap="small")
    with secondary_actions[0]:
        if st.button("Back to Herd", use_container_width=True, type="secondary"):
            st.session_state.selected_cow_id = None
            st.session_state.active_section = "my_herd"
            st.rerun()
    with secondary_actions[1]:
        if st.button("Open Prediction Center", use_container_width=True, type="secondary"):
            st.session_state.selected_cow_id = selected_cow_id
            st.session_state.active_section = "prediction_center"
            st.rerun()
