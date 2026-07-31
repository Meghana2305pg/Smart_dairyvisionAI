from __future__ import annotations

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.ui.dashboard_cards import info_card


def render_daily_operations() -> None:
    """Render the daily operations workflow for recording observations."""
    st.markdown("<div class='section-heading'>Daily Operations: Record Observation</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-caption'>Select a cow and record a fresh observation to update the digital twin.</div>", unsafe_allow_html=True)

    cow_service: CowService = st.session_state.cow_service
    cows = cow_service.get_cows()

    if not cows:
        st.warning("No cows registered. Register a cow first from Herd Management.")
        return

    cow_ids = [cow.get("cow", {}).get("cow_id", "unknown") for cow in cows]
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

            cow_twin = cow_service._cow_twins.get(selected_cow_id)
            if not cow_twin:
                from webapp.digital_twin.cow_twin import CowTwin
                cow_twin = CowTwin(cow_id=selected_cow_id)
                cow_service._cow_twins[selected_cow_id] = cow_twin

            cow_twin.record_observation(observation)
            cow_twin.refresh_from_ai(base_temp=float(temperature), base_hum=float(humidity))

            st.success("Observation recorded and twin updated successfully!")

            st.markdown("---")
            st.markdown("<div class='section-heading'>Processing Results</div>", unsafe_allow_html=True)

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

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                info_card("Prediction", f"{float(prediction.get('prediction', 0)):.2f} L/day", "Expected milk yield", "success")
            with col2:
                info_card("Health Assessment", health.get("alert_category", "Healthy"), health.get("severity", "Good"), "success" if health.get("severity") == "Good" else "warning")
            with col3:
                info_card("Twin Status", "Updated", "Twin state synchronized", "success")
            with col4:
                info_card("Recommendation", "Generated", "AI recommendations ready", "success")

            if cow_twin.recommendations:
                st.markdown("---")
                st.markdown("<div class='section-heading'>AI Recommendations</div>", unsafe_allow_html=True)
                for rec in cow_twin.recommendations[:3]:
                    st.markdown(
                        f"""
                        <div class="dashboard-card">
                          <div class="card-title">Insight</div>
                          <div class="card-caption">{rec.message if hasattr(rec, 'message') else str(rec)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        except Exception as exc:
            st.error(f"Failed to process observation: {exc}")
