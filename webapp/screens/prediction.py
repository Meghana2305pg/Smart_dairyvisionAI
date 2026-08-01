"""Prediction center screen backed by the existing prediction and explainability services."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.explainability_service import get_explanation_for_input
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import info_card, recommendation_card
from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService


def _normalize_observation(observation: Any) -> dict[str, Any]:
    """Normalize observation records from repository data into a display-friendly structure."""
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


def build_prediction_context(
    *,
    cow_twin: CowTwin,
    cow_record: dict[str, Any] | None,
    observations: list[dict[str, Any]],
    weather: tuple[float, float] | None,
    prediction: dict[str, Any] | None,
    health: dict[str, Any] | None,
    explanation: list[dict[str, Any]] | None,
    history: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
    model_version: str | None = None,
) -> dict[str, Any]:
    """Assemble the backend-driven prediction workspace payload."""
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

    input_row = {
        "age": float(cow_record.get("age_months") or 24.0) if cow_record else 24.0,
        "weight": float(latest_observation.get("weight") or 500.0) if latest_observation else 500.0,
        "feed": float(latest_observation.get("feed") or 20.0) if latest_observation else 20.0,
        "temperature": temperature,
        "humidity": humidity,
        "health_status": int(latest_observation.get("health_status") or 0) if latest_observation else 0,
    }
    model_inputs = dict(input_row)

    return {
        "cow_id": cow_record.get("cow_id") if cow_record else cow_twin.cow_id,
        "cow_name": cow_record.get("name") if cow_record else cow_twin.name or cow_twin.cow_id,
        "cow_record": cow_record or {},
        "latest_observation": latest_observation,
        "weather": weather_payload,
        "thi": thi,
        "health_status": latest_health,
        "prediction": float((latest_prediction or {}).get("prediction", 0.0) or 0.0),
        "model_inputs": model_inputs,
        "model_version": model_version,
        "feature_importance": latest_explanation,
        "history": history,
        "recommendations": recommendations,
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


def render_prediction() -> None:
    """Render the prediction workspace for the selected cow."""
    cow_service: CowService = st.session_state.cow_service
    observation_service = st.session_state.observation_service
    selected_cow_id = st.session_state.get("selected_cow_id")

    if not selected_cow_id:
        st.warning("No cow selected. Open My Herd and choose a cow to view the prediction workspace.", icon="ℹ️")
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
    latest_observation_payload = None
    if observations:
        latest_observation_payload = _normalize_observation(observations[-1])

    weather = None
    try:
        weather = get_current_weather()
    except Exception:
        weather = None

    input_row = {
        "age": float(cow_record.get("age_months") or 24.0),
        "weight": float(latest_observation_payload.get("weight") or 500.0) if latest_observation_payload else 500.0,
        "feed": float(latest_observation_payload.get("feed") or 20.0) if latest_observation_payload else 20.0,
        "temperature": float(weather[0]) if weather else 28.0,
        "humidity": float(weather[1]) if weather else 65.0,
        "health_status": int(latest_observation_payload.get("health_status") or 0) if latest_observation_payload else 0,
    }

    prediction = predict_milk_yield(input_row, base_temp=float(input_row["temperature"]), base_hum=float(input_row["humidity"]))
    health = get_health_alerts_for_input(input_row, base_temp=float(input_row["temperature"]), base_hum=float(input_row["humidity"]), predicted_yield=prediction.get("prediction"))
    explanation = get_explanation_for_input(input_row, base_temp=float(input_row["temperature"]), base_hum=float(input_row["humidity"]))
    history = [
        {"step": index + 1, "value": float(item.get("prediction", 0.0) or 0.0)}
        for index, item in enumerate(twin.state.predictions if twin.state.predictions else [])
        if item.get("cow_id") == selected_cow_id
    ]
    recommendations = [
        {"message": health.get("recommendation", "Continue monitoring"), "priority": health.get("severity", "Low")}
    ]
    if twin.recommendations:
        for item in twin.recommendations:
            if isinstance(item, dict) and item.get("message"):
                recommendations.append({"message": item.get("message"), "priority": item.get("priority", "Low")})

    payload = build_prediction_context(
        cow_twin=twin,
        cow_record=cow_record,
        observations=observations,
        weather=weather,
        prediction=prediction,
        health=health,
        explanation=explanation,
        history=history,
        recommendations=recommendations,
        model_version="1.0.0",
    )

    st.markdown(
        f"<div style='font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 8px;'>{payload['cow_name']} · Prediction Center</div>",
        unsafe_allow_html=True,
    )
    st.caption("Live milk-yield prediction workspace using the existing backend prediction and explainability services.")

    if st.button("Refresh", use_container_width=True):
        st.rerun()

    header_col1, header_col2, header_col3, header_col4 = st.columns(4, gap="medium")
    with header_col1:
        info_card("Predicted milk yield", f"{payload['prediction']:.1f} L/day")
    with header_col2:
        info_card("Confidence", f"{max(0.6, min(0.95, 0.8 + (payload['prediction'] / 100.0))):.2f}")
    with header_col3:
        info_card("Health risk", str(health.get("severity", "Low")))
    with header_col4:
        info_card("Weather impact", f"THI {payload['thi']:.1f}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.1, 0.9], gap="medium")
    with left_col:
        info_card("Current weather", f"{payload['weather']['temperature']:.1f}°C • {payload['weather']['humidity']:.0f}% humidity" if payload['weather'] else "Weather unavailable")
        info_card("Latest observation", payload['latest_observation']['notes'] if payload['latest_observation'] else "No observations yet")
        info_card("Current health", str(health.get("alert_category", "Healthy")))
        info_card("Selected cow", f"{payload['cow_name']} · {payload['cow_id']}")

    with right_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Model inputs</div>", unsafe_allow_html=True)
        for key, value in payload['model_inputs'].items():
            info_card(key.replace('_', ' ').title(), f"{value}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Feature importance</div>", unsafe_allow_html=True)
    if payload['feature_importance']:
        for item in payload['feature_importance'][:5]:
            recommendation_card("SHAP feature", f"{item.get('feature', 'feature')}: {item.get('contribution', 0.0):.3f}", icon="🔍")
    else:
        st.info("No explainability output is available for this cow yet.", icon="ℹ️")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    chart_col, report_col = st.columns([1.1, 0.9], gap="medium")
    with chart_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Prediction history</div>", unsafe_allow_html=True)
        if payload['history']:
            history_df = pd.DataFrame(payload['history'])
            st.line_chart(history_df.set_index("step")["value"])
        else:
            st.info("No prediction history is available yet for this cow.", icon="ℹ️")

    with report_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>AI recommendations</div>", unsafe_allow_html=True)
        if payload['recommendations']:
            for item in payload['recommendations']:
                recommendation_card("Recommendation", item.get("message", "No guidance available"), icon="💡")
        else:
            st.info("No recommendations are available for this cow yet.", icon="ℹ️")

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="Export CSV",
            data=pd.DataFrame([payload]).to_csv(index=False).encode("utf-8"),
            file_name=f"prediction_{selected_cow_id}.csv",
            mime="text/csv",
            use_container_width=True,
        )
