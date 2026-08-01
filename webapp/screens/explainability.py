"""Explainability screen for SHAP and feature importance."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.explainability_service import get_explanation_for_input, get_explainability_artifacts
from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import info_card
from webapp.screens.comparison_panel import build_comparison_payload
from webapp.screens.explanation_card import build_explanations
from webapp.screens.feature_importance import build_feature_table
from webapp.screens.shap_chart import build_contribution_timeline, build_shap_bar_chart


def _normalise_observation(observation: Any) -> dict[str, Any]:
    """Normalise observations from repository data into a display-friendly structure."""
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
        "timestamp": timestamp_value,
        "notes": observation.get("notes") or "No notes recorded",
        "temperature": observation.get("temperature"),
        "humidity": observation.get("humidity"),
        "feed": observation.get("feed"),
        "weight": observation.get("weight"),
        "health_status": observation.get("health_status"),
    }


def build_explainability_context(
    *,
    cow_record: dict[str, Any] | None = None,
    observations: list[dict[str, Any]] | None = None,
    prediction: dict[str, Any] | None = None,
    explanation: list[dict[str, Any]] | None = None,
    weather: tuple[float, float] | None = None,
    model_version: str | None = None,
    risk_level: str | None = None,
) -> dict[str, Any]:
    """Assemble the explainability workspace payload from existing backend data."""
    normalized_observations = [_normalise_observation(item) for item in (observations or [])]
    latest_observation = normalized_observations[-1] if normalized_observations else {}
    weather_payload = {"temperature": weather[0], "humidity": weather[1]} if weather else None
    current_prediction = float((prediction or {}).get("prediction", 0.0) or 0.0)
    current_explanation = list(explanation or [])
    feature_table = build_feature_table(current_explanation).to_dict("records")
    explanations = build_explanations(current_explanation)
    comparison = build_comparison_payload(current_prediction, comparison_prediction=current_prediction)
    return {
        "summary": {
            "predicted_milk_yield": current_prediction,
            "confidence_score": max(0.6, min(0.95, 0.8 + (current_prediction / 100.0))),
            "prediction_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "model_version": model_version or "1.0.0",
            "risk_level": risk_level or "Low",
        },
        "feature_table": feature_table,
        "explanations": explanations,
        "comparison": comparison,
        "history": normalized_observations,
        "weather": weather_payload,
        "cow_record": cow_record or {},
        "observations": normalized_observations,
    }


def render_explainability() -> None:
    """Render the explainability screen with existing SHAP-derived insights."""
    cow_service = st.session_state.get("cow_service")
    observation_service = st.session_state.get("observation_service")
    selected_cow_id = st.session_state.get("selected_cow_id")

    st.markdown("<div style='font-size: 24px; font-weight: 700; margin-bottom: 8px;'>Explainable AI Workspace</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #475569; margin-bottom: 20px;'>Inspect the model's feature contributions and how they shape the current prediction.</div>", unsafe_allow_html=True)

    if not selected_cow_id:
        st.info("Select a cow from My Herd or the Prediction Center to inspect explainability details.", icon="ℹ️")
        return

    cow_record = None
    if cow_service is not None:
        for item in cow_service.get_cows():
            cow = item.get("cow", item)
            if cow.get("cow_id") == selected_cow_id:
                cow_record = cow
                break

    observations = []
    if observation_service is not None:
        try:
            observations = observation_service.repository.list_for_cow(selected_cow_id)
        except Exception:
            observations = []

    weather = None
    try:
        weather = get_current_weather()
    except Exception:
        weather = None

    defaults = get_feature_defaults(base_temp=weather[0] if weather else 28.0, base_hum=weather[1] if weather else 65.0)
    input_row = {
        "age": float(cow_record.get("age_months") or defaults.get("age", 36.0)) if cow_record else float(defaults.get("age", 36.0)),
        "weight": float((observations[-1].get("weight") if observations and isinstance(observations[-1], dict) else None) or defaults.get("weight", 450.0)) if observations else float(defaults.get("weight", 450.0)),
        "feed": float((observations[-1].get("feed") if observations and isinstance(observations[-1], dict) else None) or defaults.get("feed", 20.0)) if observations else float(defaults.get("feed", 20.0)),
        "temperature": float(weather[0]) if weather else float(defaults.get("temperature", 28.0)),
        "humidity": float(weather[1]) if weather else float(defaults.get("humidity", 65.0)),
        "health_status": int((observations[-1].get("health_status") if observations and isinstance(observations[-1], dict) else None) or 0) if observations else 0,
    }
    prediction = predict_milk_yield(input_row, base_temp=float(input_row["temperature"]), base_hum=float(input_row["humidity"]))
    explanation = get_explanation_for_input(input_row, base_temp=float(input_row["temperature"]), base_hum=float(input_row["humidity"]))
    artifacts = get_explainability_artifacts()

    context = build_explainability_context(
        cow_record=cow_record,
        observations=observations,
        prediction=prediction,
        explanation=explanation,
        weather=weather,
        model_version="1.0.0",
        risk_level="Low" if prediction.get("prediction", 0.0) >= 20 else "High",
    )

    summary = context["summary"]
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        info_card("Predicted Milk Yield", f"{summary['predicted_milk_yield']:.1f} L/day")
    with col2:
        info_card("Confidence Score", f"{summary['confidence_score']:.2f}")
    with col3:
        info_card("Prediction Time", summary["prediction_time"])
    with col4:
        info_card("Model Version", summary["model_version"])

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    risk_col, artifact_col = st.columns([1, 2], gap="medium")
    with risk_col:
        info_card("Risk Level", summary["risk_level"])
    with artifact_col:
        st.info("SHAP artifacts are sourced from the existing outputs directory when available.", icon="ℹ️")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    left_col, right_col = st.columns(2, gap="medium")
    with left_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>SHAP Feature Contributions</div>", unsafe_allow_html=True)
        st.plotly_chart(build_shap_bar_chart(explanation), use_container_width=True)
    with right_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Feature Contribution Table</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(context["feature_table"]), use_container_width=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    explanation_col, comparison_col = st.columns(2, gap="medium")
    with explanation_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Human-Readable Explanations</div>", unsafe_allow_html=True)
        for item in context["explanations"]:
            st.info(f"{item['title']}: {item['description']}", icon="💡")
    with comparison_col:
        st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Prediction Comparison</div>", unsafe_allow_html=True)
        st.metric("Current Prediction", f"{context['comparison']['current_prediction']:.1f} L/day")
        st.metric("Compared To", f"{context['comparison']['comparison_prediction']:.1f} L/day")
        st.metric("Delta", f"{context['comparison']['delta']:.1f} L/day")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 16px; font-weight: 700; margin-bottom: 10px;'>Historical Explainability Timeline</div>", unsafe_allow_html=True)
    st.plotly_chart(build_contribution_timeline(context["feature_table"]), use_container_width=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.download_button("Download SHAP Report", data=(artifacts.get("report").read_text() if artifacts.get("report") and artifacts.get("report").exists() else "No SHAP report generated yet."), file_name="shap_report.md", mime="text/markdown", use_container_width=True)
    st.download_button("Export PDF", data="Explainability report", file_name="explainability_report.pdf", mime="application/pdf", use_container_width=True)
