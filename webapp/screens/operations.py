"""Daily operations screen with a guided observation workflow."""
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


def _render_workflow_steps(current_step: int) -> None:
    """Render a guided progress indicator for the daily operations workflow."""
    steps = [
        ("Select Cow", "1"),
        ("Observation", "2"),
        ("Review", "3"),
        ("Generate", "4"),
        ("Results", "5"),
    ]
    cols = st.columns(len(steps))
    for index, ((label, value), col) in enumerate(zip(steps, cols)):
        status = "done" if index < current_step else "active" if index == current_step else "pending"
        with col:
            st.markdown(
                f"""
                <div class='ops-step {status}'>
                    <div class='ops-step-number'>{value}</div>
                    <div class='ops-step-label'>{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_daily_operations() -> None:
    """Render the daily-operations workflow as a guided, card-based experience."""
    st.markdown(
        """
        <style>
        .ops-shell {
            padding-top: 0.25rem;
        }
        .ops-header {
            margin-bottom: 1rem;
        }
        .ops-title {
            font-size: clamp(1.85rem, 2vw, 2.35rem);
            font-weight: 800;
            letter-spacing: -0.05em;
            margin: 0;
            color: #0f172a;
        }
        .ops-subtitle {
            color: #64748b;
            font-size: 0.96rem;
            margin-top: 0.35rem;
        }
        .ops-stepper {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 1rem 0 1.5rem;
        }
        .ops-step {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 18px;
            padding: 0.75rem 0.55rem;
            text-align: center;
            min-height: 82px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03);
        }
        .ops-step.done {
            background: rgba(219, 234, 254, 0.7);
            border-color: rgba(59, 130, 246, 0.25);
        }
        .ops-step.active {
            background: rgba(37,99,235,0.08);
            border-color: rgba(37,99,235,0.30);
        }
        .ops-step.pending {
            background: rgba(248,250,252,0.9);
        }
        .ops-step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            font-weight: 800;
            font-size: 0.8rem;
            background: rgba(15, 23, 42, 0.06);
            color: #0f172a;
            margin-bottom: 0.4rem;
        }
        .ops-step.active .ops-step-number {
            background: #2563eb;
            color: white;
        }
        .ops-step-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #475569;
        }
        .ops-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 20px;
            padding: 1rem;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }
        .ops-card-header {
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #475569;
            font-weight: 800;
            margin-bottom: 0.8rem;
        }
        .ops-summary-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.95));
            border: 1px solid rgba(148,163,184,0.15);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 18px rgba(15, 23, 42, 0.04);
            min-height: 120px;
        }
        .ops-summary-card .label {
            color: #64748b;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
            font-weight: 800;
        }
        .ops-summary-card .value {
            font-size: clamp(1.25rem, 1.8vw, 1.8rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #0f172a;
        }
        .ops-summary-card .meta {
            color: #475569;
            font-size: 0.82rem;
            margin-top: 0.45rem;
        }
        .ops-result-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        .ops-result-list {
            margin: 0;
            padding-left: 1.1rem;
            color: #334155;
            line-height: 1.7;
        }
        .ops-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.34rem 0.62rem;
            font-size: 0.72rem;
            font-weight: 700;
        }
        .ops-badge.success { background: rgba(21,128,61,0.1); color: #15803d; }
        .ops-badge.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .ops-badge.danger { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .ops-badge.neutral { background: rgba(148,163,184,0.12); color: #475569; }
        @media (max-width: 900px) {
            .ops-stepper, .ops-result-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 620px) {
            .ops-stepper, .ops-result-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    observation_service: ObservationService = st.session_state.observation_service
    cows = cow_service.get_cows()
    if not cows:
        st.warning("No cows registered. Register a cow first from Herd Management.")
        return

    cow_payloads = [cow.get("cow", cow) if isinstance(cow, dict) and "cow" in cow else cow for cow in cows]
    cow_ids = [str(item.get("cow_id") or "unknown") for item in cow_payloads]
    selected_cow_id = st.session_state.get("daily_ops_cow") or cow_ids[0]
    if selected_cow_id not in cow_ids:
        selected_cow_id = cow_ids[0]
    st.session_state.daily_ops_cow = selected_cow_id

    phase = st.session_state.get("daily_ops_phase", "form")
    last_result = st.session_state.get("daily_ops_last_result")

    st.markdown('<div class="ops-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ops-header">
            <h1 class="ops-title">Daily Operations</h1>
            <div class="ops-subtitle">Record observation data for a cow and review the live prediction and health status.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if phase == "results" and last_result:
        _render_workflow_steps(4)
        st.success("Observation recorded and twin updated successfully.")

        summary_cols = st.columns(4)
        with summary_cols[0]:
            st.markdown(
                """
                <div class='ops-summary-card'>
                    <div class='label'>Prediction</div>
                    <div class='value'>%.2f L/day</div>
                    <div class='meta'>Milk yield forecast</div>
                </div>
                """ % float(last_result["prediction"].get("prediction", 0)),
                unsafe_allow_html=True,
            )
        with summary_cols[1]:
            health_label = str(last_result["health"].get("alert_category", "Healthy"))
            st.markdown(
                f"""
                <div class='ops-summary-card'>
                    <div class='label'>Health Summary</div>
                    <div class='value'>{health_label}</div>
                    <div class='meta'>Current alert band</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with summary_cols[2]:
            twin_status = "Updated" if last_result.get("snapshot") else "Ready"
            st.markdown(
                f"""
                <div class='ops-summary-card'>
                    <div class='label'>Twin Status</div>
                    <div class='value'>{twin_status}</div>
                    <div class='meta'>Digital twin state</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with summary_cols[3]:
            st.markdown(
                f"""
                <div class='ops-summary-card'>
                    <div class='label'>Cow</div>
                    <div class='value'>{last_result['cow_id']}</div>
                    <div class='meta'>Selected observation record</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="ops-card"><div class="ops-card-header">Prediction Summary</div>', unsafe_allow_html=True)
        st.write(f"Predicted milk yield: {float(last_result['prediction'].get('prediction', 0)):.2f} L/day")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ops-card"><div class="ops-card-header">Health Summary</div>', unsafe_allow_html=True)
        health = last_result["health"]
        st.write(f"Alert category: {health.get('alert_category', 'Healthy')}")
        st.write(f"Stress category: {health.get('stress_category', 'Normal')}")
        st.write(f"Severity: {health.get('severity', 'Low')}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ops-card"><div class="ops-card-header">AI Recommendations</div>', unsafe_allow_html=True)
        st.write(health.get("recommendation", "Continue routine monitoring."))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ops-card"><div class="ops-card-header">Twin Status</div>', unsafe_allow_html=True)
        if last_result.get("snapshot"):
            st.write("The digital twin has been refreshed with the latest observation.")
            st.json(last_result["snapshot"], expanded=False)
        else:
            st.write("Twin update was completed without a snapshot payload.")
        st.markdown('</div>', unsafe_allow_html=True)

        history = observation_service.repository.list_for_cow(last_result["cow_id"])
        recent_history = history[-3:][::-1] if history else []
        st.markdown('<div class="ops-card"><div class="ops-card-header">Recent Observation History</div>', unsafe_allow_html=True)
        if recent_history:
            for item in recent_history:
                st.markdown(
                    f"- {item.get('cow_id')} • {item.get('temperature', 'N/A')}°C • {item.get('feed', 'N/A')} kg/day • {item.get('notes', 'No notes')}"
                )
        else:
            st.write("No recent observation history is available yet.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ops-card">', unsafe_allow_html=True)
        if st.button("Record Another Observation", use_container_width=True):
            st.session_state.daily_ops_phase = "form"
            st.session_state.daily_ops_last_result = None
            st.session_state.daily_ops_last_submitted_cow = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    _render_workflow_steps(0)
    st.markdown('<div class="ops-card"><div class="ops-card-header">Step 1 · Select Cow</div>', unsafe_allow_html=True)
    selected_cow_id = st.selectbox("Select Cow", cow_ids, index=cow_ids.index(selected_cow_id), key="daily_ops_cow")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ops-card"><div class="ops-card-header">Step 2 · Enter Today\'s Observation</div>', unsafe_allow_html=True)
    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

    with st.form("daily_operations_form"):
        health_cols = st.columns(2)
        with health_cols[0]:
            st.markdown('<div class="ops-card-header">Health</div>', unsafe_allow_html=True)
            health_status = st.selectbox("Health status", [0, 1], format_func=lambda v: "Healthy" if v == 0 else "Diseased")
        with health_cols[1]:
            st.markdown('<div class="ops-card-header">Milk</div>', unsafe_allow_html=True)
            age = st.number_input("Age (months)", min_value=1.0, max_value=300.0, value=defaults.get("age", 36.0), step=1.0)
            weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=defaults.get("weight", 450.0), step=10.0)

        feed_env_cols = st.columns(2)
        with feed_env_cols[0]:
            st.markdown('<div class="ops-card-header">Feed</div>', unsafe_allow_html=True)
            feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=defaults.get("feed", 20.0), step=1.0)
        with feed_env_cols[1]:
            st.markdown('<div class="ops-card-header">Environment</div>', unsafe_allow_html=True)
            temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=defaults.get("temperature", base_temp), step=1.0)
            humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=defaults.get("humidity", base_hum), step=1.0)

        st.markdown('<div class="ops-card-header">Notes</div>', unsafe_allow_html=True)
        notes = st.text_area("Observation notes", value="Routine farm observation", height=120)

        st.markdown('<div class="ops-card-header">Step 3 · Review Inputs</div>', unsafe_allow_html=True)
        review_cols = st.columns(4)
        with review_cols[0]:
            st.metric("Age", f"{age:.0f} mo")
        with review_cols[1]:
            st.metric("Weight", f"{weight:.0f} kg")
        with review_cols[2]:
            st.metric("Temperature", f"{temperature:.1f}°C")
        with review_cols[3]:
            st.metric("Humidity", f"{humidity:.0f}%")

        submitted = st.form_submit_button("Generate Prediction", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

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
                Observation(
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

    st.markdown('</div>', unsafe_allow_html=True)
