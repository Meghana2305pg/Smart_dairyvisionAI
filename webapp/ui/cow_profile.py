from __future__ import annotations

from typing import Any

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.services.cow_service import CowService
from webapp.ui.dashboard_cards import info_card


def render_cow_profile() -> None:
    """Render the cow profile screen for a selected cow."""
    cow_id = st.session_state.get("selected_cow_id")
    if not cow_id:
        st.warning("No cow selected. Please select a cow from the herd.")
        return

    cow_service: CowService = st.session_state.cow_service
    cow_twin = cow_service._cow_twins.get(cow_id)

    st.markdown(f"<div class='section-heading'>Cow Profile: {cow_id}</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.3, 0.35, 0.35])
    with col1:
        if st.button("← Back to Herd", use_container_width=True):
            st.session_state.selected_cow_id = None
            st.rerun()
    with col2:
        st.caption("Profile last updated: Today")
    with col3:
        if st.button("Record Observation", use_container_width=True):
            st.session_state.show_observation_form = True
            st.rerun()

    st.markdown("---")

    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

    default_input = {
        "age": float(defaults.get("age", 36.0)),
        "weight": float(defaults.get("weight", 450.0)),
        "feed": float(defaults.get("feed", 20.0)),
        "temperature": float(defaults.get("temperature", base_temp)),
        "humidity": float(defaults.get("humidity", base_hum)),
        "health_status": 0,
    }

    prediction = predict_milk_yield(default_input, base_temp=base_temp, base_hum=base_hum)
    health = get_health_alerts_for_input(default_input, base_temp=base_temp, base_hum=base_hum)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("Milk Yield", f"{float(prediction.get('prediction', 0)):.2f} L/day", "Expected today", "success")
    with col2:
        info_card("Health", health.get("alert_category", "Healthy"), health.get("severity", "Good"), "success" if health.get("severity") == "Good" else "warning")
    with col3:
        info_card("Weather", f"{base_temp:.0f}°C / {base_hum:.0f}%", "Current environment", "neutral")
    with col4:
        info_card("Twin Status", "Synced", "Connected to digital twin", "success")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Observation History</div>", unsafe_allow_html=True)

    if cow_twin and cow_twin.memory_store:
        snapshots = [cow_twin.memory_store.get_latest_snapshot(cow_id)]
        snapshots = [s for s in snapshots if s is not None]
        if snapshots:
            for snapshot in snapshots[:5]:
                st.markdown(
                    f"""
                    <div class="dashboard-card">
                      <div class="card-title">Snapshot {snapshot.snapshot_id}</div>
                      <div class="card-caption">Status: {snapshot.twin_status} · Prediction: {snapshot.prediction} L/day</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No observations recorded yet for this cow.")
    else:
        st.info("No observation history available.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Recommendations</div>", unsafe_allow_html=True)

    if cow_twin and cow_twin.recommendations:
        for rec in cow_twin.recommendations[:3]:
            st.markdown(
                f"""
                <div class="dashboard-card">
                  <div class="card-title">AI Insight</div>
                  <div class="card-caption">{rec.message if hasattr(rec, 'message') else str(rec)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No recommendations available yet.")

    if st.session_state.get("show_observation_form"):
        st.markdown("---")
        st.markdown("<div class='section-heading'>Record Observation</div>", unsafe_allow_html=True)
        with st.form("observation_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.number_input("Age (months)", min_value=1.0, max_value=300.0, value=defaults.get("age", 36.0), key="obs_age")
                weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=defaults.get("weight", 450.0), key="obs_weight")
            with col2:
                feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=defaults.get("feed", 20.0), key="obs_feed")
                temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=base_temp, key="obs_temp")
            with col3:
                humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=base_hum, key="obs_hum")
                health_status = st.selectbox("Health status", [0, 1], format_func=lambda v: "Healthy" if v == 0 else "Diseased", key="obs_health")
            notes = st.text_area("Notes", value="Routine observation", key="obs_notes")
            submitted = st.form_submit_button("Save Observation")

        if submitted:
            st.success("Observation recorded successfully.")
            st.session_state.show_observation_form = False
            st.rerun()
