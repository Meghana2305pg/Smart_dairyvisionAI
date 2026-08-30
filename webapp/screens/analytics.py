"""Analytics screen."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.weather_service import get_current_weather
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


def build_analytics_context(
    cow_records: list[dict[str, Any]] | None = None,
    observations: list[dict[str, Any]] | None = None,
    predictions: list[dict[str, Any]] | None = None,
    health: list[dict[str, Any]] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    weather: tuple[float, float] | None = None,
    date_range: tuple[str, str] | None = None,
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
    for prediction in prediction_list:
        if not isinstance(prediction, dict):
            continue
        predicted_value = prediction.get("prediction")
        if predicted_value is None:
            continue
        raw_cow_id = prediction.get("cow_id") or prediction.get("cow_tag") or ""
        resolved_cow_id = alias_lookup.get(str(raw_cow_id), str(raw_cow_id))
        prediction_lookup[resolved_cow_id] = float(predicted_value)

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
            obs_time = pd.Timestamp(timestamp).tz_localize(None)
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
            if start_date and obs_time < start:
                continue
            if end_date and obs_time > end:
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
        health_status_value = cow.get("health_status")
        health_value = str(health_status_value or "")
        if health_filter and health_filter != "All" and health_value not in {health_filter, health_filter.lower()}:
            continue
        prediction_value = prediction_lookup.get(cow_id)
        filtered_cows.append({
            **cow,
            "cow_id": cow_id,
            "name": cow.get("name") or cow.get("cow_name") or cow_id,
            "breed": cow.get("breed") or "Unknown",
            "predicted_yield": prediction_value if prediction_value is not None else 0.0,
            "prediction": prediction_value,
            "yield": prediction_value if prediction_value is not None else 0.0,
            "health_status": int(health_status_value) if health_status_value is not None else 0,
            "health_label": "healthy" if not health_status_value else "sick",
        })

    total_cows = len(filtered_cows) if filtered_cows else len(cow_list)
    healthy_cows = sum(1 for cow in filtered_cows if cow.get("health_label") == "healthy")
    sick_cows = sum(1 for cow in filtered_cows if cow.get("health_label") == "sick")
    average_yield = round(sum(float(cow.get("yield", 0.0)) for cow in filtered_cows) / total_cows, 1) if total_cows else 0.0
    today_prediction = round(sum(float(cow.get("predicted_yield", 0.0)) for cow in filtered_cows) / total_cows, 1) if total_cows else 0.0
    active_alerts = sum(1 for item in health_list if str(item.get("severity", "")).lower() in {"high", "critical"})

    top_performing = sorted(filtered_cows, key=lambda item: float(item.get("yield", 0.0)), reverse=True)[:3]
    poor_performing = sorted(filtered_cows, key=lambda item: float(item.get("yield", 0.0)))[:3]

    for ranked in top_performing + poor_performing:
        ranked["predicted_yield"] = float(ranked.get("predicted_yield", ranked.get("yield", 0.0)) or 0.0)
        ranked["health_status"] = int(ranked.get("health_status", 0) or 0)

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
        payload["yield"] = prediction_value if prediction_value is not None else float(payload.get("yield") or payload.get("feed") or 0.0)
        payload["temperature"] = payload.get("temperature", current_weather[0])
        payload["humidity"] = payload.get("humidity", current_weather[1])
        payload["health_status"] = int(payload.get("health_status", 0) or 0)
        chart_observations.append(payload)

    history = [
        {"step": index + 1, "value": float(item.get("prediction", 0.0))}
        for index, item in enumerate(prediction_list)
        if item.get("prediction") is not None
    ]

    insights: list[dict[str, Any]] = []
    if recommendation_list:
        first_recommendation = recommendation_list[0]
        insights.append({
            "title": "AI Insight",
            "description": str(first_recommendation.get("message") or first_recommendation.get("recommendation") or "Review the latest observations to improve herd performance."),
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
                "predicted_yield": float(item.get("predicted_yield", item.get("yield", 0.0)) or 0.0),
                "health_status": int(item.get("health_status", 0) or 0),
            }
            for item in top_performing
        ],
        "poor_performing": [
            {
                "cow_id": item.get("cow_id"),
                "name": item.get("name") or item.get("cow_id"),
                "breed": item.get("breed") or "Unknown",
                "predicted_yield": float(item.get("predicted_yield", item.get("yield", 0.0)) or 0.0),
                "health_status": int(item.get("health_status", 0) or 0),
            }
            for item in poor_performing
        ],
        "chart_observations": chart_observations,
        "history": history,
        "insights": insights,
        "weather": current_weather,
        "observations": filtered_observations,
    }


def render_analytics() -> None:
    """Render a professional executive analytics dashboard based on the live project data."""
    dashboard_service: DashboardService = st.session_state.dashboard_service
    dashboard = dashboard_service.build_dashboard()
    cow_records = dashboard_service.cow_service.get_cows()
    observations = dashboard_service.repository.get_observations()

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
        predictions=dashboard.predictions,
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
        st.plotly_chart(build_prediction_history_chart(context["history"]), use_container_width=True, key="prediction_chart")
        st.caption("Prediction history supports confidence checks and short-interval monitoring decisions.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    ranking_col1, ranking_col2 = st.columns(2, gap="medium")
    with ranking_col1:
        render_section_header("Top Performing Cows", "Highest-yield cows in the current filter set.")
        if context["top_performing"]:
            top_df = pd.DataFrame(context["top_performing"])[["cow_id", "name", "breed", "predicted_yield", "health_status"]]
            st.dataframe(top_df, use_container_width=True)
        else:
            st.info("No performance data available yet.", icon="ℹ️")
    with ranking_col2:
        render_section_header("Poor Performing Cows", "Cows that may need closer review or intervention.")
        if context["poor_performing"]:
            poor_df = pd.DataFrame(context["poor_performing"])[["cow_id", "name", "breed", "predicted_yield", "health_status"]]
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
