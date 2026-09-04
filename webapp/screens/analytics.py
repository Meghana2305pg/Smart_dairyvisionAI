"""Analytics screen."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.weather_service import get_current_weather
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.screens.analytics_cards import render_summary_cards
from webapp.screens.charts import (
    build_health_trend_chart,
    build_milk_production_chart,
    build_prediction_history_chart,
    build_weather_vs_milk_chart,
)
from webapp.screens.export_panel import render_export_panel
from webapp.screens.filter_panel import render_filter_panel
from webapp.services.dashboard_service import DashboardService
from webapp.ui.section_header import render_page_header, render_section_header


def _normalise_cow_records(cow_records: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalise cow data from either the repository or session state payloads."""
    if not cow_records:
        return []
    normalised: list[dict[str, Any]] = []
    for item in cow_records:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("cow"), dict):
            payload = dict(item["cow"])
        else:
            payload = dict(item)
        normalised.append(payload)
    return normalised


def _build_cow_alias_lookup(cow_records: list[dict[str, Any]] | None) -> dict[str, str]:
    """Map any record identifier back to the canonical cow tag used for analytics joins."""
    lookup: dict[str, str] = {}
    for record in cow_records or []:
        if not isinstance(record, dict):
            continue
        canonical_id = str(record.get("cow_id") or record.get("cow_tag") or record.get("id") or "").strip()
        if not canonical_id:
            continue
        for candidate in (record.get("id"), record.get("cow_id"), record.get("cow_tag")):
            value = str(candidate or "").strip()
            if value:
                lookup[value] = canonical_id
        lookup[canonical_id] = canonical_id
    return lookup


def _observation_timestamp(observation: dict[str, Any]) -> pd.Timestamp | None:
    """Return a comparable timestamp from a persisted observation."""
    value = observation.get("timestamp") or observation.get("created_at") or observation.get("observation_date")
    if value is None:
        return None
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return None
    return timestamp.tz_localize(None) if timestamp.tzinfo is not None else timestamp


def _latest_observations_by_cow(
    observations: list[dict[str, Any]], alias_lookup: dict[str, str]
) -> dict[str, dict[str, Any]]:
    """Select the latest timestamped persisted observation for every cow."""
    latest: dict[str, tuple[pd.Timestamp, dict[str, Any]]] = {}
    for observation in observations:
        if not isinstance(observation, dict):
            continue
        timestamp = _observation_timestamp(observation)
        if timestamp is None:
            continue
        raw_cow_id = str(observation.get("cow_id") or "")
        cow_id = alias_lookup.get(raw_cow_id, raw_cow_id)
        if not cow_id or cow_id not in latest or timestamp > latest[cow_id][0]:
            payload = dict(observation)
            payload["cow_id"] = cow_id
            latest[cow_id] = (timestamp, payload)
    return {cow_id: payload for cow_id, (_, payload) in latest.items()}


@st.cache_data(show_spinner=False)
def _recompute_current_predictions(
    cow_records: list[dict[str, Any]], observations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Compute one current (not historical) prediction per latest observation."""
    cow_list = _normalise_cow_records(cow_records)
    aliases = _build_cow_alias_lookup(cow_list)
    latest_observations = _latest_observations_by_cow(observations, aliases)
    predictions: list[dict[str, Any]] = []

    for cow in cow_list:
        cow_id = str(cow.get("cow_id") or cow.get("cow_tag") or cow.get("id") or "")
        observation = latest_observations.get(cow_id)
        if not observation:
            continue
        required_fields = ("feed", "temperature", "humidity", "health_status")
        if any(observation.get(field) is None for field in required_fields):
            continue
        try:
            result = predict_milk_yield(
                {
                    "age": cow.get("age_months"),
                    "weight": cow.get("weight"),
                    "feed": observation["feed"],
                    "temperature": observation["temperature"],
                    "humidity": observation["humidity"],
                    "health_status": observation["health_status"],
                },
                base_temp=float(observation["temperature"]),
                base_hum=float(observation["humidity"]),
            )
        except (TypeError, ValueError, RuntimeError):
            continue
        predictions.append({"cow_id": cow_id, "prediction": float(result["prediction"]), "source": "current_recomputed"})
    return predictions


def build_analytics_context(
    cow_records: list[dict[str, Any]] | None = None,
    observations: list[dict[str, Any]] | None = None,
    predictions: list[dict[str, Any]] | None = None,
    health: list[dict[str, Any]] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    weather: tuple[float, float] | None = None,
    date_range: tuple[str | None, str | None] | None = None,
    cow_filter: str | None = None,
    breed_filter: str | None = None,
    health_filter: str | None = None,
) -> dict[str, Any]:
    """Assemble the analytics payload using the normalized Digital Twin and dashboard data."""
    cow_list = _normalise_cow_records(cow_records)
    alias_lookup = _build_cow_alias_lookup(cow_list)
    observation_list = list(observations or [])
    prediction_list = list(predictions or [])
    health_list = list(health or [])
    recommendation_list = list(recommendations or [])
    current_weather = weather or (0.0, 0.0)

    prediction_lookup: dict[str, float] = {}
    prediction_source_lookup: dict[str, str] = {}
    for prediction in prediction_list:
        if not isinstance(prediction, dict):
            continue
        predicted_value = prediction.get("prediction")
        if predicted_value is None:
            continue
        raw_cow_id = prediction.get("cow_id") or prediction.get("cow_tag") or ""
        resolved_cow_id = alias_lookup.get(str(raw_cow_id), str(raw_cow_id))
        prediction_lookup[resolved_cow_id] = float(predicted_value)
        prediction_source_lookup[resolved_cow_id] = str(prediction.get("source") or "current_session")

    latest_observations = _latest_observations_by_cow(observation_list, alias_lookup)

    filtered_observations: list[dict[str, Any]] = []
    for observation in observation_list:
        if not isinstance(observation, dict):
            continue
        timestamp = (
            observation.get("timestamp")
            or observation.get("created_at")
            or observation.get("observation_date")
        )
        if date_range:
            start_date, end_date = date_range
            if timestamp is None:
                continue
            obs_time = _observation_timestamp(observation)
            if obs_time is None:
                continue
            if start_date and obs_time.date() < pd.Timestamp(start_date).date():
                continue
            if end_date and obs_time.date() > pd.Timestamp(end_date).date():
                continue
        raw_cow_id = str(observation.get("cow_id") or "")
        resolved_cow_id = alias_lookup.get(raw_cow_id, raw_cow_id)
        if cow_filter and cow_filter != "All" and resolved_cow_id != cow_filter:
            continue
        payload = dict(observation)
        payload["cow_id"] = resolved_cow_id
        payload["cow_tag"] = resolved_cow_id
        filtered_observations.append(payload)

    filtered_cows: list[dict[str, Any]] = []
    for cow in cow_list:
        cow_id = str(cow.get("cow_id") or cow.get("cow_tag") or cow.get("id") or "")
        if cow_filter and cow_filter != "All" and cow_id != cow_filter:
            continue
        breed = str(cow.get("breed") or "")
        if breed_filter and breed_filter != "All" and breed and breed != breed_filter:
            continue
        latest_observation = latest_observations.get(cow_id)
        health_status_value = latest_observation.get("health_status") if latest_observation else None
        health_label = "unavailable"
        if health_status_value is not None:
            try:
                health_status_value = int(health_status_value)
                health_label = "healthy" if health_status_value == 0 else "sick"
            except (TypeError, ValueError):
                health_status_value = None
        if health_filter and health_filter != "All" and health_label != health_filter.lower():
            continue
        prediction_value = prediction_lookup.get(cow_id)
        filtered_cows.append({
            **cow,
            "cow_id": cow_id,
            "name": cow.get("name") or cow.get("cow_name") or cow_id,
            "breed": cow.get("breed") or "Unknown",
            "predicted_yield": prediction_value,
            "prediction": prediction_value,
            "prediction_source": prediction_source_lookup.get(cow_id),
            "yield": prediction_value,
            "health_status": health_status_value,
            "health_label": health_label,
        })

    total_cows = len(filtered_cows) if filtered_cows else len(cow_list)
    healthy_cows = sum(1 for cow in filtered_cows if cow.get("health_label") == "healthy")
    sick_cows = sum(1 for cow in filtered_cows if cow.get("health_label") == "sick")
    available_yields = [float(cow["yield"]) for cow in filtered_cows if cow.get("yield") is not None]
    average_yield = round(sum(available_yields) / len(available_yields), 1) if available_yields else None
    today_prediction = average_yield
    active_alerts = sum(1 for item in health_list if str(item.get("severity", "")).lower() in {"high", "critical"})

    ranked_cows = [cow for cow in filtered_cows if cow.get("yield") is not None]
    top_performing = sorted(ranked_cows, key=lambda item: float(item["yield"]), reverse=True)[:3]
    poor_performing = sorted(ranked_cows, key=lambda item: float(item["yield"]))[:3]

    chart_observations: list[dict[str, Any]] = []
    for observation in filtered_observations:
        payload = dict(observation)
        payload["timestamp"] = (
            payload.get("timestamp")
            or payload.get("created_at")
            or payload.get("observation_date")
        )
        resolved_cow_id = str(payload.get("cow_id") or payload.get("cow_tag") or "")
        prediction_value = prediction_lookup.get(resolved_cow_id)
        payload["yield"] = prediction_value
        payload["temperature"] = payload.get("temperature", current_weather[0])
        payload["humidity"] = payload.get("humidity", current_weather[1])
        payload["health_status"] = payload.get("health_status")
        chart_observations.append(payload)

    history = [
        {"step": index + 1, "value": float(item["prediction"])}
        for index, item in enumerate(prediction_list)
        if item.get("prediction") is not None and item.get("source") != "current_recomputed"
    ]

    insights: list[dict[str, Any]] = []
    if recommendation_list:
        first_recommendation = recommendation_list[0]
        # Support both Recommendation objects (with .message attr) and dict recommendations
        if hasattr(first_recommendation, "message"):
            # Recommendation dataclass object
            recommendation_text = first_recommendation.message
        elif isinstance(first_recommendation, dict):
            # Dictionary recommendation
            recommendation_text = first_recommendation.get("message") or first_recommendation.get("recommendation")
        else:
            recommendation_text = None

        recommendation_text = recommendation_text or "Review the latest observations to improve herd performance."
        insights.append({
            "title": "AI Insight",
            "description": str(recommendation_text),
        })
    if current_weather[0] > 30:
        insights.append({
            "title": "Weather Signal",
            "description": "Heat stress conditions are elevated; review hydration and shade coverage for the herd.",
        })
    if sick_cows:
        insights.append({
            "title": "Health Attention",
            "description": f"{sick_cows} cow(s) are currently flagged for follow-up monitoring.",
        })
    if not insights:
        insights.append({
            "title": "AI Insight",
            "description": "The workspace is ready for live analysis once new observations are recorded.",
        })

    return {
        "summary": {
            "total_cows": total_cows,
            "healthy_cows": healthy_cows,
            "sick_cows": sick_cows,
            "average_milk_yield": average_yield,
            "today_prediction": today_prediction,
            "active_alerts": active_alerts,
        },
        "top_performing": [
            {
                "cow_id": item.get("cow_id"),
                "name": item.get("name") or item.get("cow_id"),
                "breed": item.get("breed") or "Unknown",
                "predicted_yield": item.get("predicted_yield"),
                "prediction_source": item.get("prediction_source"),
                "health_status": item.get("health_status"),
            }
            for item in top_performing
        ],
        "poor_performing": [
            {
                "cow_id": item.get("cow_id"),
                "name": item.get("name") or item.get("cow_id"),
                "breed": item.get("breed") or "Unknown",
                "predicted_yield": item.get("predicted_yield"),
                "prediction_source": item.get("prediction_source"),
                "health_status": item.get("health_status"),
            }
            for item in poor_performing
        ],
        "chart_observations": chart_observations,
        "history": history,
        "insights": insights,
        "weather": current_weather,
        "observations": filtered_observations,
    }


def render_prediction_history(history: list[dict[str, Any]]) -> None:
    """Render genuine prediction history or a clear persistence-aware empty state."""
    if history:
        st.plotly_chart(build_prediction_history_chart(history), use_container_width=True, key="prediction_chart")
        st.caption("Prediction history supports confidence checks and short-interval monitoring decisions.")
    else:
        st.info("No prediction history available yet. Historical prediction points will appear after predictions are persisted.")


def render_analytics() -> None:
    """Render a professional executive analytics dashboard based on the live project data."""
    dashboard_service: DashboardService = st.session_state.dashboard_service
    dashboard = dashboard_service.build_dashboard()
    cow_records = dashboard_service.cow_service.get_cows()
    observations = dashboard_service.repository.get_observations()
    recomputed_predictions = _recompute_current_predictions(cow_records, observations)
    live_predictions = [
        {**prediction, "source": prediction.get("source") or "current_session"}
        for prediction in dashboard.predictions
    ]
    existing_prediction_cows = {str(item.get("cow_id") or "") for item in live_predictions}
    live_predictions.extend(
        prediction for prediction in recomputed_predictions if prediction["cow_id"] not in existing_prediction_cows
    )

    st.markdown(
        """
        <style>
        .analytics-shell { padding-top: 0.35rem; }
        .analytics-section {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 10px 22px rgba(15,23,42,0.04);
        }
        .analytics-section-title {
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: 0.7rem;
        }
        .chart-panel {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 0.75rem;
            min-height: 360px;
            box-shadow: 0 10px 20px rgba(15,23,42,0.04);
        }
        .chart-caption {
            color: #64748b;
            font-size: 0.82rem;
            margin-top: 0.5rem;
            margin-bottom: 0.25rem;
        }
        @media (max-width: 1100px) {
            .chart-panel { min-height: 310px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_page_header(
        "Analytics & Insights",
        "Monitor herd performance, health, weather, and AI-generated recommendations in one workspace.",
        badge="Workspace",
    )

    try:
        weather = get_current_weather()
    except Exception:
        weather = (0.0, 0.0)

    cow_options = sorted({str(item.get("cow_id") or "") for item in cow_records if item.get("cow_id")})
    breed_options = sorted({str(item.get("breed") or "") for item in cow_records if item.get("breed")})
    status_options = ["healthy", "sick"]

    start_date, end_date, cow_filter, breed_filter, health_filter = render_filter_panel(cow_options, breed_options, status_options)
    context = build_analytics_context(
        cow_records=cow_records,
        observations=observations,
        predictions=live_predictions,
        health=dashboard.health,
        recommendations=dashboard.recommendations,
        weather=weather,
        date_range=(start_date, end_date),
        cow_filter=cow_filter,
        breed_filter=breed_filter,
        health_filter=health_filter,
    )

    st.markdown('<div class="analytics-shell">', unsafe_allow_html=True)
    render_summary_cards(context["summary"])

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2, gap="medium")
    with chart_col1:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(build_milk_production_chart(context["chart_observations"]), use_container_width=True, key="milk_chart")
        st.caption("Monthly trend in milk output helps identify performance swings and production opportunities.")
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(build_health_trend_chart(context["chart_observations"]), use_container_width=True, key="health_chart")
        st.caption("Health signals provide a quick view of herd condition and change over time.")
        st.markdown('</div>', unsafe_allow_html=True)

    chart_col3, chart_col4 = st.columns(2, gap="medium")
    with chart_col3:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(build_weather_vs_milk_chart(context["chart_observations"]), use_container_width=True, key="weather_chart")
        st.caption("Temperature and humidity are compared with milk output to understand environmental influence.")
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_col4:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        render_prediction_history(context["history"])
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    ranking_col1, ranking_col2 = st.columns(2, gap="medium")
    with ranking_col1:
        render_section_header("Top Performing Cows", "Highest-yield cows in the current filter set.")
        if context["top_performing"]:
            top_df = pd.DataFrame(context["top_performing"])[["cow_id", "name", "breed", "predicted_yield", "prediction_source", "health_status"]]
            st.dataframe(top_df, use_container_width=True)
        else:
            st.info("No performance data available yet.", icon="ℹ️")
    with ranking_col2:
        render_section_header("Poor Performing Cows", "Cows that may need closer review or intervention.")
        if context["poor_performing"]:
            poor_df = pd.DataFrame(context["poor_performing"])[["cow_id", "name", "breed", "predicted_yield", "prediction_source", "health_status"]]
            st.dataframe(poor_df, use_container_width=True)
        else:
            st.info("No performance data available yet.", icon="ℹ️")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    insight_col, export_col = st.columns([2, 1], gap="medium")
    with insight_col:
        render_section_header("AI Insights", "Summarized actions and signals from the analytics engine.")
        if context["insights"]:
            for insight in context["insights"]:
                st.info(f"{insight['title']}: {insight['description']}", icon="💡")
        else:
            st.info("No insights are available for the current filter selection.", icon="ℹ️")
    with export_col:
        render_section_header("Export", "Download the filtered analytics output.")
        render_export_panel(pd.DataFrame(context["top_performing"] + context["poor_performing"]))

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("dashboard_needs_refresh"):
        st.session_state["dashboard_needs_refresh"] = False
