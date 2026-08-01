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
    """Render the individual cow profile screen."""
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
    health_badge = "🟢 Healthy" if str(health_category).lower() != "severe" else "🔴 High risk"

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown(
            f"""
            <div style='font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 8px;'>{cow_dict.get('name', 'Unknown')}</div>
            <div style='font-size: 14px; color: #64748b; margin-bottom: 8px;'>Cow ID: {selected_cow_id}</div>
            <div style='display: flex; gap: 8px; flex-wrap: wrap;'>
                <span style='background: #ecfdf3; color: #166534; border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600;'>{health_badge}</span>
                <span style='background: #eff6ff; color: #1d4ed8; border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600;'>Twin: {current_status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("← Back to Herd"):
            st.session_state.selected_cow_id = None
            st.session_state.active_section = "my_herd"
            st.rerun()

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    header_col1, header_col2, header_col3, header_col4 = st.columns(4, gap="medium")
    with header_col1:
        info_card("Cow ID", selected_cow_id)
    with header_col2:
        info_card("Breed", cow_dict.get("breed", "N/A"))
    with header_col3:
        info_card("Age (months)", str(cow_dict.get("age_months", "N/A")))
    with header_col4:
        info_card("Current milk yield", f"{current_prediction:.1f} L/day")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    tab_names = ["Overview", "Prediction History", "Observation History", "Health", "Digital Twin", "Recommendations"]
    selected_tab = st.session_state.get("profile_tab", "Overview")
    if selected_tab not in tab_names:
        selected_tab = "Overview"
    selected_tab = st.radio("", tab_names, index=tab_names.index(selected_tab), key="profile_tab", horizontal=True)

    if selected_tab == "Overview":
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            info_card("Current details", f"Name: {cow_dict.get('name', 'Unknown')}\nBreed: {cow_dict.get('breed', 'N/A')}\nAge: {cow_dict.get('age_months', 'N/A')} months")
            info_card("Current prediction", f"{current_prediction:.1f} L/day")
        with col2:
            info_card("Weather", f"{base_temp:.1f}°C, {base_hum:.0f}% humidity")
            info_card("Health", health_category)
            latest_observation = observations[-1] if observations else None
            if latest_observation:
                info_card("Latest observation", f"{latest_observation['notes']} • {latest_observation['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            else:
                info_card("Latest observation", "No observations recorded yet")
    elif selected_tab == "Prediction History":
        prediction_history = [
            {"step": index + 1, "value": float(item.get("prediction", 0.0) or 0.0)}
            for index, item in enumerate(twin.state.predictions if twin.state.predictions else [])
            if item.get("cow_id") == selected_cow_id
        ]
        if prediction_history:
            chart_df = pd.DataFrame(prediction_history)
            st.line_chart(chart_df.set_index("step")["value"])
            for entry in prediction_history:
                st.caption(f"Step {entry['step']}: {entry['value']:.1f} L/day")
        else:
            st.info("No prediction history is available yet for this cow.", icon="ℹ️")
    elif selected_tab == "Observation History":
        if observations:
            for observation in reversed(observations):
                st.markdown(
                    f"""
                    <div style='background: white; border: 1px solid #e5ebf2; border-radius: 12px; padding: 14px; margin-bottom: 10px;'>
                        <div style='font-size: 14px; font-weight: 700; color: #0f172a;'>{observation['timestamp'].strftime('%Y-%m-%d %H:%M')}</div>
                        <div style='font-size: 13px; color: #475569; margin-top: 6px;'>{observation['notes']}</div>
                        <div style='font-size: 12px; color: #64748b; margin-top: 8px;'>Temp: {observation['temperature'] if observation['temperature'] is not None else 'n/a'} °C • Humidity: {observation['humidity'] if observation['humidity'] is not None else 'n/a'} % • Feed: {observation['feed'] if observation['feed'] is not None else 'n/a'} kg</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No observations recorded yet for this cow.", icon="ℹ️")
    elif selected_tab == "Health":
        health_summary = twin.latest_health or {}
        risk_level = str(health_summary.get("severity", "Low")).capitalize()
        info_card("Current health", health_summary.get("alert_category", health_category))
        info_card("Risk", risk_level)
        info_card("Recommendation", health_summary.get("recommendation", health.get("recommendation", "Continue monitoring")))
        if twin.recommendations:
            for rec in twin.recommendations:
                recommendation_card(title="Recommendation", description=rec.get("message") if isinstance(rec, dict) else str(rec), icon="💡")
        else:
            st.info("No health recommendations have been generated yet.", icon="ℹ️")
    elif selected_tab == "Digital Twin":
        info_card("Current state", twin.state.status if twin.state.status else "Stable")
        info_card("Memory", f"{len(twin.memory_store.list_snapshot_history(selected_cow_id))} snapshots stored")
        info_card("Synchronization", f"Latest observation: {twin.latest_observation.notes if twin.latest_observation and twin.latest_observation.notes else 'None'}")
        info_card("Twin health", health_category)
        snapshot_history = twin.memory_store.list_snapshot_history(selected_cow_id)
        if snapshot_history:
            for snapshot in snapshot_history[-3:]:
                st.caption(f"{snapshot.snapshot_id} • {snapshot.timestamp.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No digital twin snapshots have been created yet.", icon="ℹ️")
    elif selected_tab == "Recommendations":
        if twin.recommendations:
            for rec in twin.recommendations:
                recommendation_card(title="Backend recommendation", description=rec.get("message") if isinstance(rec, dict) else str(rec), icon="🌿")
        else:
            st.info("No backend recommendations are available yet for this cow.", icon="ℹ️")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    if st.button("📝 Record Observation for This Cow", use_container_width=True):
        st.session_state.selected_cow_id = selected_cow_id
        st.session_state.daily_ops_cow = selected_cow_id
        st.session_state.active_section = "daily_operations"
        st.rerun()

    if st.button("📈 Open Prediction Center", use_container_width=True):
        st.session_state.selected_cow_id = selected_cow_id
        st.session_state.active_section = "prediction_center"
        st.rerun()

    if st.button("🗑️ Delete This Cow", use_container_width=True):
        st.session_state.confirm_delete_for = selected_cow_id

    if st.session_state.get("confirm_delete_for") == selected_cow_id:
        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            if st.button("Confirm Delete", key=f"confirm_delete_profile_{selected_cow_id}"):
                if cow_service.delete_cow(selected_cow_id):
                    st.session_state.selected_cow_id = None
                    st.session_state.active_section = "my_herd"
                    st.session_state.confirm_delete_for = None
                    st.success("Cow deleted successfully!")
                    st.rerun()
        with c2:
            if st.button("Cancel", key=f"cancel_delete_profile_{selected_cow_id}"):
                st.session_state.confirm_delete_for = None
                st.rerun()
