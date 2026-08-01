"""Daily operations screen with a phase-based observation submission flow."""
from __future__ import annotations

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.services.observation_service import ObservationService
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_daily_operations_form


def _build_input_row(age: float, weight: float, feed: float, temperature: float, humidity: float, health_status: int) -> dict[str, float | int]:
    return {
        "age": float(age),
        "weight": float(weight),
        "feed": float(feed),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "health_status": int(health_status),
    }


def render_daily_operations() -> None:
    """Render a form-first workflow that transitions to a read-only results view after submission."""
    st.markdown("<div class='section-heading'>Daily Operations: Record Observation</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-caption'>Select a cow and record a fresh observation to update the digital twin.</div>", unsafe_allow_html=True)

    cow_service: CowService = st.session_state.cow_service
    observation_service: ObservationService = st.session_state.observation_service
    cows = cow_service.get_cows()
    if not cows:
        st.warning("No cows registered. Register a cow first from Herd Management.")
        return

    cow_ids = [cow.get("cow", {}).get("cow_id", "unknown") for cow in cows]
    phase = st.session_state.get("daily_ops_phase", "form")
    last_result = st.session_state.get("daily_ops_last_result")

    if phase == "results" and last_result:
        st.success("Observation recorded and twin updated successfully.")
        st.markdown("---")
        st.markdown("<div class='section-heading'>Processing Results</div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Prediction", f"{float(last_result['prediction'].get('prediction', 0)):.2f} L/day")
        with col2:
            st.metric("Health", last_result["health"].get("alert_category", "Healthy"))
        with col3:
            st.metric("Twin", "Updated")
        with col4:
            st.metric("Cow", last_result["cow_id"])

        if st.button("Record Another Observation", use_container_width=True):
            st.session_state.daily_ops_phase = "form"
            st.session_state.daily_ops_last_result = None
            st.session_state.daily_ops_last_submitted_cow = None
            st.rerun()
        return

    selected_cow_id = st.selectbox("Select Cow", cow_ids, key="daily_ops_cow")
    st.markdown("---")
    st.markdown("<div class='section-heading'>Observation Form</div>", unsafe_allow_html=True)

    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

    with st.form("daily_operations_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age (months)", min_value=1.0, max_value=300.0, value=defaults.get("age", 36.0), step=1.0)
            weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=defaults.get("weight", 450.0), step=10.0)
        with col2:
            feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=defaults.get("feed", 20.0), step=1.0)
            temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=defaults.get("temperature", base_temp), step=1.0)
        with col3:
            humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=defaults.get("humidity", base_hum), step=1.0)
            health_status = st.selectbox("Health status", [0, 1], format_func=lambda v: "Healthy" if v == 0 else "Diseased")
        notes = st.text_area("Observation notes", value="Routine farm observation")
        submitted = st.form_submit_button("Record & Process Observation", use_container_width=True)

    if submitted:
        validation_errors = validate_daily_operations_form({
            "cow_id": selected_cow_id,
            "age": age,
            "weight": weight,
            "feed": feed,
            "temperature": temperature,
            "humidity": humidity,
            "notes": notes,
        })
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            try:
                observation = Observation(
                    cow_id=selected_cow_id,
                    age=float(age),
                    weight=float(weight),
                    feed=float(feed),
                    temperature=float(temperature),
                    humidity=float(humidity),
                    health_status=int(health_status),
                    notes=notes,
                )
                result = observation_service.record_observation(
                    cow_id=selected_cow_id,
                    age=float(age),
                    weight=float(weight),
                    feed=float(feed),
                    temperature=float(temperature),
                    humidity=float(humidity),
                    health_status=int(health_status),
                    notes=notes,
                )
                input_row = _build_input_row(float(age), float(weight), float(feed), float(temperature), float(humidity), int(health_status))
                prediction = predict_milk_yield(input_row, base_temp=float(temperature), base_hum=float(humidity))
                health = get_health_alerts_for_input(input_row, base_temp=float(temperature), base_hum=float(humidity))
                st.session_state.daily_ops_phase = "results"
                st.session_state.daily_ops_last_result = {
                    "cow_id": selected_cow_id,
                    "prediction": prediction,
                    "health": health,
                    "snapshot": result.get("snapshot"),
                }
                st.session_state.daily_ops_last_submitted_cow = selected_cow_id
                st.session_state.submitted_cow_id = selected_cow_id
                st.session_state.selected_cow_id = selected_cow_id
                st.session_state.last_selected_cow = selected_cow_id
                st.session_state.observation_submitted = True
                st.session_state.active_section = "dashboard"
                st.session_state.dashboard_needs_refresh = True
                log_event("observation_recorded", cow_id=selected_cow_id)
                st.rerun()
            except Exception as exc:
                log_error("observation_processing_failed", cow_id=selected_cow_id, error=str(exc))
                st.error("The observation could not be processed. Please try again shortly.")
