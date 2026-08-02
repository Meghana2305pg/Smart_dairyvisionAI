from __future__ import annotations

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.ui import render_empty_state, render_loading_skeleton, render_metric_card, render_section_title


def render_daily_operations() -> None:
    """Render the daily operations workflow for recording observations."""
    st.markdown("<div class='section-heading'>Daily Operations: Record Observation</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-caption'>Select a cow, capture the latest signals, and refresh the live digital twin in one guided step.</div>", unsafe_allow_html=True)
    st.caption("Tip: a complete observation helps keep predictions, health status, and recommendations aligned.")

    cow_service: CowService = st.session_state.cow_service
    cows = cow_service.get_cows()

    if not cows:
        render_empty_state(
            title="No cows available for daily operations",
            message="Register your first cow so you can record observations and update the digital twin workflow.",
            icon="🐄",
            action_label="Register Cow",
            action_key="daily_ops_register_cow",
        )
        return

    cow_ids = [cow.get("cow", {}).get("cow_id", "unknown") for cow in cows]
    selected_cow_id = st.selectbox("Select Cow", cow_ids, key="daily_ops_cow")

    st.markdown("---")
    render_section_title("Observation Form", "Capture the latest live indicators for the selected cow")

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
        notes = st.text_area("Observation notes", value="Routine farm observation", placeholder="Add a short note for the team")
        submitted = st.form_submit_button("Record & Process Observation", use_container_width=True, type="primary")

    if submitted:
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

            with st.spinner("Refreshing the digital twin and generating guidance..."):
                cow_twin = cow_service._cow_twins.get(selected_cow_id)
                if not cow_twin:
                    from webapp.digital_twin.cow_twin import CowTwin
                    cow_twin = CowTwin(cow_id=selected_cow_id)
                    cow_service._cow_twins[selected_cow_id] = cow_twin

                cow_twin.record_observation(observation)
                cow_twin.refresh_from_ai(base_temp=float(temperature), base_hum=float(humidity))

            st.success("Observation recorded and twin updated successfully.")

            st.markdown("---")
            render_section_title("Processing Results", "Live outputs generated from the latest observation")

            input_row = {
                "age": float(age),
                "weight": float(weight),
                "feed": float(feed),
                "temperature": float(temperature),
                "humidity": float(humidity),
                "health_status": int(health_status),
            }
            prediction = predict_milk_yield(input_row, base_temp=float(temperature), base_hum=float(humidity))
            health = get_health_alerts_for_input(input_row, base_temp=float(temperature), base_hum=float(humidity))

            col1, col2, col3, col4 = st.columns(4, gap="small")
            with col1:
                render_metric_card("Prediction", f"{float(prediction.get('prediction', 0)):.2f} L/day", "Expected milk yield", icon="💧", tone="success")
            with col2:
                render_metric_card("Health Assessment", health.get("alert_category", "Healthy"), health.get("severity", "Good"), icon="🩺", tone="success" if health.get("severity") == "Good" else "warning")
            with col3:
                render_metric_card("Twin Status", "Updated", "Twin state synchronized", icon="🧠", tone="success")
            with col4:
                render_metric_card("Recommendation", "Generated", "AI recommendations ready", icon="✨", tone="info")

            if cow_twin.recommendations:
                st.markdown("---")
                render_section_title("AI Recommendations", "The latest guidance compiled for this cow")
                for rec in cow_twin.recommendations[:3]:
                    st.markdown(
                        f"""
                        <div class="dashboard-card" style="padding:0.9rem 1rem; margin-bottom:0.7rem;">
                          <div class="metric-title">Insight</div>
                          <div class="metric-subtitle" style="margin-top:0.25rem;">{rec.message if hasattr(rec, 'message') else str(rec)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                render_loading_skeleton("Preparing recommendation guidance...")

        except Exception as exc:
            st.error("The observation could not be processed cleanly. Please try again in a moment.")
            st.caption(str(exc))
