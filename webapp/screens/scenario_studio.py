"""Interactive Scenario Studio screen wired to the existing scenario engine.

The layout remains additive and visual-only in the sense that it does not alter
navigation or the existing twin runtime. It reuses the existing scenario engine
and the underlying prediction, health, explainability, and recommendation
services without duplicating that logic in the UI layer.
"""

from __future__ import annotations

from typing import Any

from html import escape

import streamlit as st

from webapp.backend_services.weather_service import get_current_weather
from webapp.components.cards import info_card, metric_card, recommendation_card
from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.scenario_engine import Scenario, ScenarioComparison, ScenarioEngine
from webapp.ui.section_header import render_page_header, render_section_header


def _build_changed_features(live_context: dict[str, Any], scenario: Scenario | None) -> list[str]:
    """Return a human-readable list of the attributes changed in the scenario."""
    if scenario is None:
        return []

    changed_features: list[str] = []
    modified_inputs = scenario.modified_inputs or {}

    feature_labels = {
        "feed_intake": "Feed Intake",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "body_weight": "Weight",
        "age": "Age",
        "weather": "Weather",
    }

    for key in ("feed_intake", "temperature", "humidity", "body_weight", "age", "weather"):
        if key in modified_inputs:
            changed_features.append(feature_labels.get(key, key.replace("_", " ").title()))

    if live_context.get("observation") and scenario.modified_inputs:
        obs = live_context["observation"]
        if "feed_intake" in modified_inputs and obs.get("feed") is not None:
            if float(modified_inputs["feed_intake"]) != float(obs["feed"]):
                changed_features.append("Feed Intake")
        if "body_weight" in modified_inputs and obs.get("weight") is not None:
            if float(modified_inputs["body_weight"]) != float(obs["weight"]):
                changed_features.append("Weight")

    return sorted(set(changed_features), key=lambda item: ["Feed Intake", "Temperature", "Humidity", "Weight", "Age", "Weather"].index(item) if item in ["Feed Intake", "Temperature", "Humidity", "Weight", "Age", "Weather"] else len(["Feed Intake", "Temperature", "Humidity", "Weight", "Age", "Weather"]))


def _build_scenario_summary(live_context: dict[str, Any], scenario: Scenario | None, milk_difference: float | None) -> str:
    """Build a simple natural-language scenario summary from comparison data."""
    if scenario is None:
        return "Run a scenario to generate a summary."

    observation = live_context.get("observation") or {}
    latest_prediction = (live_context.get("latest_prediction") or {}).get("prediction")
    scenario_prediction = (scenario.prediction or {}).get("prediction")
    feed_current = observation.get("feed")
    feed_scenario = scenario.modified_inputs.get("feed_intake")
    health_status = scenario.health_assessment.get("severity") if scenario.health_assessment else None

    if feed_current is not None and feed_scenario is not None:
        if scenario_prediction is not None:
            if latest_prediction is not None:
                return (
                    f"Increasing feed intake from {feed_current:.1f} kg/day to {feed_scenario:.1f} kg/day "
                    f"is predicted to increase milk yield from {latest_prediction:.1f} L/day to {scenario_prediction:.1f} L/day "
                    f"({milk_difference:+.1f} L/day) while maintaining a {health_status or 'Stable'} status."
                )
            return (
                f"Increasing feed intake from {feed_current:.1f} kg/day to {feed_scenario:.1f} kg/day "
                f"is predicted to reach {scenario_prediction:.1f} L/day "
                f"with a {health_status or 'Stable'} status."
            )
        return (
            f"Increasing feed intake from {feed_current:.1f} kg/day to {feed_scenario:.1f} kg/day "
            f"is predicted to change milk yield by {milk_difference:+.1f} L/day"
            f" and maintain a {health_status or 'Stable'} status."
        )

    return (
        f"The scenario is projected to deliver {scenario_prediction if scenario_prediction is not None else 'n/a'} L/day "
        f"with a {health_status or 'Stable'} health status."
    )



def _get_cow_service() -> Any | None:
    """Return the current cow service from Streamlit session state if present."""
    return st.session_state.get("cow_service")


def _get_selected_cow() -> dict[str, Any] | None:
    """Resolve the currently selected cow from the existing app state."""
    cow_service = _get_cow_service()
    if cow_service is None:
        return None

    selected_cow_id = st.session_state.get("selected_cow_id")
    if not selected_cow_id:
        return None

    for item in cow_service.get_cows():
        cow_record = item.get("cow", item)
        if cow_record.get("cow_id") == selected_cow_id:
            return cow_record

    return None


def _get_live_twin() -> tuple[CowTwin | None, dict[str, Any] | None]:
    """Resolve the live CowTwin and its current cow record from session state."""
    cow_service = _get_cow_service()
    selected_cow_id = st.session_state.get("selected_cow_id")
    if cow_service is None or not selected_cow_id:
        return None, None

    twin = cow_service._cow_twins.get(selected_cow_id)
    cow_record = _get_selected_cow()
    if twin is None and cow_record is not None:
        twin = CowTwin(cow_id=selected_cow_id, name=cow_record.get("name") or selected_cow_id)
        cow_service._cow_twins[selected_cow_id] = twin
    return twin, cow_record


def _get_current_weather() -> tuple[float | None, float | None]:
    """Resolve current weather or return None values for graceful fallback."""
    try:
        temperature, humidity = get_current_weather()
        return float(temperature), float(humidity)
    except Exception:
        return None, None


def _compute_thi(temperature: float | None, humidity: float | None) -> float | None:
    """Calculate a simple THI value from temperature and humidity if available."""
    if temperature is None or humidity is None:
        return None
    return round((0.8 * temperature) + ((humidity / 100.0) * (temperature - 14.4)) + 16.4, 1)


def _format_prediction(prediction: dict[str, Any] | None) -> str:
    """Render a prediction payload in a human-readable form."""
    if not prediction:
        return "n/a"
    value = prediction.get("prediction")
    if value is None:
        return "n/a"
    return f"{float(value):.1f} L/day"


def _format_health(health: dict[str, Any] | None) -> str:
    """Render the health payload in a simple display string."""
    if not health:
        return "No data"
    return str(health.get("severity") or health.get("alert_category") or "Stable")


def _format_recommendation(recommendations: list[dict[str, Any]] | None) -> str:
    """Render a recommendation list in a compact string."""
    if not recommendations:
        return "No recommendation"
    first = recommendations[0]
    if isinstance(first, dict):
        return str(first.get("message") or "No recommendation")
    return str(first)


def _get_default_inputs(twin: CowTwin | None, cow_record: dict[str, Any] | None) -> dict[str, float | str]:
    """Create scenario control defaults from the latest live snapshot or observation."""
    snapshot = twin.memory_store.get_latest_snapshot(twin.cow_id) if twin else None
    observation = None
    if snapshot is not None:
        observation = snapshot.observation
    elif twin is not None and twin.latest_observation is not None:
        observation = twin.latest_observation

    temperature = getattr(observation, "temperature", None) if observation is not None else None
    humidity = getattr(observation, "humidity", None) if observation is not None else None
    feed = getattr(observation, "feed", None) if observation is not None else None
    weight = getattr(observation, "weight", None) if observation is not None else None
    age = getattr(observation, "age", None) if observation is not None else cow_record.get("age_months") if cow_record else None

    if snapshot and snapshot.weather:
        weather_temperature = snapshot.weather.get("temperature")
        weather_humidity = snapshot.weather.get("humidity")
        if weather_temperature is not None:
            temperature = weather_temperature
        if weather_humidity is not None:
            humidity = weather_humidity

    return {
        "temperature": float(temperature or 28.0),
        "humidity": float(humidity or 65.0),
        "feed_intake": float(feed or 22.0),
        "body_weight": float(weight or 490.0),
        "age": float(age or 24.0),
    }


def _render_controls(defaults: dict[str, float | str]) -> dict[str, Any]:
    """Render slider and select controls for scenario values."""
    with st.container():
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            feed_intake = st.slider("Feed Intake", min_value=10, max_value=30, value=float(defaults["feed_intake"]), key="scenario_feed")
            temperature = st.slider("Temperature", min_value=20, max_value=40, value=float(defaults["temperature"]), key="scenario_temp")
            humidity = st.slider("Humidity", min_value=40, max_value=95, value=float(defaults["humidity"]), key="scenario_humidity")
        with col2:
            body_weight = st.slider("Body Weight", min_value=400, max_value=650, value=float(defaults["body_weight"]), key="scenario_weight")
            age = st.slider("Age", min_value=18, max_value=60, value=float(defaults["age"]), key="scenario_age")
            weather_override = st.selectbox("Weather Override", ["None", "Heat Wave", "Rainy", "Cold Front"], index=0, key="scenario_weather_override")

        button_row = st.columns([1, 1], gap="small")
        with button_row[0]:
            if st.button("Reset", use_container_width=True):
                st.session_state.pop("scenario_feed", None)
                st.session_state.pop("scenario_temp", None)
                st.session_state.pop("scenario_humidity", None)
                st.session_state.pop("scenario_weight", None)
                st.session_state.pop("scenario_age", None)
                st.session_state.pop("scenario_weather_override", None)
                st.rerun()
        with button_row[1]:
            run_clicked = st.button("Run Scenario", use_container_width=True)

    return {
        "feed_intake": feed_intake,
        "temperature": temperature,
        "humidity": humidity,
        "body_weight": body_weight,
        "age": age,
        "weather_override": weather_override,
        "run_clicked": run_clicked,
    }


def _render_shap_panel(title: str) -> None:
    """Render placeholder explainability panels for future SHAP integration."""
    with st.container():
        st.markdown(
            f"""
            <div style="border:1px solid #e2e8f0;border-radius:16px;padding:1rem;background:linear-gradient(180deg,#ffffff,#f8fafc);min-height:220px;">
                <div style="font-size:0.85rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:#64748b;">{escape(title)}</div>
                <div style="margin-top:0.75rem;color:#334155;line-height:1.6;">
                    Current explainability content will be connected here in a future release.<br><br>
                    • Feature contribution preview<br>
                    • Scenario-specific insight card<br>
                    • Future SHAP integration point
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_comparison_table(live_context: dict[str, Any], scenario: Scenario | None, comparison: ScenarioComparison | None) -> None:
    """Render the comparison table using the scenario comparison object when available."""
    if scenario is None or comparison is None:
        st.info("Run a scenario to populate the comparison table.", icon="ℹ️")
        return

    weather = live_context.get("weather") or {}
    observation = live_context.get("observation") or {}
    scenario_weather = scenario.weather or {}
    modified_inputs = scenario.modified_inputs or {}

    live_thi = live_context.get("thi")
    scenario_thi = live_context.get("scenario_thi")

    table_rows = [
        ("Milk", _format_prediction(live_context.get("latest_prediction")), _format_prediction(scenario.prediction), _format_difference(comparison.milk_difference)),
        ("Health", _format_health(live_context.get("latest_health")), _format_health(scenario.health_assessment), comparison.health_difference or "-"),
        ("THI", _format_metric(live_thi), _format_metric(scenario_thi), _format_difference((scenario_thi - live_thi) if live_thi is not None and scenario_thi is not None else None)),
        ("Temperature", f"{weather.get('temperature', 'n/a')}°C" if weather else "n/a", f"{scenario_weather.get('temperature', 'n/a')}°C" if scenario_weather else "n/a", _format_difference((scenario_weather.get("temperature") - weather.get("temperature")) if weather and scenario_weather and scenario_weather.get("temperature") is not None and weather.get("temperature") is not None else None)),
        ("Humidity", f"{weather.get('humidity', 'n/a')}%" if weather else "n/a", f"{scenario_weather.get('humidity', 'n/a')}%" if scenario_weather else "n/a", _format_difference((scenario_weather.get("humidity") - weather.get("humidity")) if weather and scenario_weather and scenario_weather.get("humidity") is not None and weather.get("humidity") is not None else None)),
        ("Feed", f"{observation.get('feed', 'n/a')} kg" if observation else "n/a", f"{modified_inputs.get('feed_intake', 'n/a')} kg" if modified_inputs else "n/a", _format_difference((modified_inputs.get("feed_intake") - observation.get("feed")) if observation.get("feed") is not None and modified_inputs.get("feed_intake") is not None else None)),
        ("Weight", f"{observation.get('weight', 'n/a')} kg" if observation else "n/a", f"{modified_inputs.get('body_weight', 'n/a')} kg" if modified_inputs else "n/a", _format_difference((modified_inputs.get("body_weight") - observation.get("weight")) if observation.get("weight") is not None and modified_inputs.get("body_weight") is not None else None)),
    ]

    st.markdown(
        """
        <div style="border:1px solid #e2e8f0;border-radius:16px;overflow:hidden;background:#fff;">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:#f8fafc;">
                        <th style="padding:0.8rem 1rem;text-align:left;color:#475569;">Metric</th>
                        <th style="padding:0.8rem 1rem;text-align:left;color:#475569;">Live</th>
                        <th style="padding:0.8rem 1rem;text-align:left;color:#475569;">Scenario</th>
                        <th style="padding:0.8rem 1rem;text-align:left;color:#475569;">Difference</th>
                    </tr>
                </thead>
                <tbody>
        """,
        unsafe_allow_html=True,
    )
    for metric, live_value, scenario_value, diff in table_rows:
        st.markdown(
            f"""
            <tr style="border-top:1px solid #f1f5f9;">
                <td style="padding:0.8rem 1rem;color:#0f172a;font-weight:600;">{escape(metric)}</td>
                <td style="padding:0.8rem 1rem;color:#334155;">{escape(str(live_value))}</td>
                <td style="padding:0.8rem 1rem;color:#334155;">{escape(str(scenario_value))}</td>
                <td style="padding:0.8rem 1rem;color:#0f172a;font-weight:700;">{escape(str(diff))}</td>
            </tr>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if comparison and comparison.changed_features:
        st.markdown("")
        st.caption(f"Changed features: {', '.join(_build_changed_features(live_context, scenario))}")


def _format_metric(value: Any) -> str:
    """Format metric values for the comparison table."""
    if value is None:
        return "n/a"
    return str(value)


def _format_difference(value: Any) -> str:
    """Format numeric differences for the comparison table."""
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:+.1f}"
    return str(value)


def render_scenario_studio() -> None:
    """Render the Scenario Studio interface with live data and scenario engine integration."""
    render_page_header(
        "🧪 Scenario Studio",
        "Explore hypothetical farm conditions without affecting the live Digital Twin.",
        badge="Interactive",
    )

    twin, cow_record = _get_live_twin()
    if twin is None or cow_record is None:
        st.warning("Select a cow from the existing application state to load the live digital twin view.", icon="ℹ️")
        return

    live_weather_temp, live_weather_hum = _get_current_weather()
    live_weather = {"temperature": live_weather_temp, "humidity": live_weather_hum} if live_weather_temp is not None and live_weather_hum is not None else None
    latest_prediction = twin.latest_prediction or {}
    latest_health = twin.latest_health or {}
    latest_recommendations = twin.recommendations or []
    latest_snapshot = twin.memory_store.get_latest_snapshot(twin.cow_id) if twin else None
    live_thi = _compute_thi(live_weather.get("temperature") if live_weather else None, live_weather.get("humidity") if live_weather else None)
    if live_thi is None and latest_snapshot is not None and latest_snapshot.weather:
        live_thi = _compute_thi(latest_snapshot.weather.get("temperature"), latest_snapshot.weather.get("humidity"))

    live_context = {
        "cow_id": cow_record.get("cow_id") or twin.cow_id,
        "cow_name": cow_record.get("name") or twin.name or twin.cow_id,
        "breed": cow_record.get("breed") or "Unknown",
        "age": cow_record.get("age_months") or (latest_snapshot.observation.age if latest_snapshot and latest_snapshot.observation else None),
        "latest_prediction": latest_prediction,
        "latest_health": latest_health,
        "latest_recommendation": latest_recommendations[0] if latest_recommendations else None,
        "weather": live_weather,
        "thi": live_thi,
        "observation": {
            "feed": getattr(latest_snapshot.observation, "feed", None) if latest_snapshot and latest_snapshot.observation else None,
            "weight": getattr(latest_snapshot.observation, "weight", None) if latest_snapshot and latest_snapshot.observation else None,
            "temperature": getattr(latest_snapshot.observation, "temperature", None) if latest_snapshot and latest_snapshot.observation else None,
            "humidity": getattr(latest_snapshot.observation, "humidity", None) if latest_snapshot and latest_snapshot.observation else None,
        },
    }

    with st.container():
        header_cols = st.columns([1.1, 1, 1], gap="medium")
        with header_cols[0]:
            info_card(
                "Selected Cow",
                f"{live_context['cow_id']} • {live_context['cow_name']}",
                f"Breed: {live_context['breed']} • Age: {live_context['age']}",
            )
        with header_cols[1]:
            info_card("Latest Prediction", _format_prediction(live_context["latest_prediction"]), "Current live estimate")
        with header_cols[2]:
            info_card(
                "Latest Health & Recommendation",
                _format_health(live_context["latest_health"]),
                _format_recommendation(latest_recommendations),
            )

    st.markdown("")
    render_section_header("Scenario Workspace", "Compare a hypothetical condition against the live digital twin state.")

    live_col, controls_col, result_col = st.columns([1.15, 1.0, 1.0], gap="medium")

    with live_col:
        st.markdown("### Live Digital Twin")
        metric_card("🧪", "Milk Prediction", _format_prediction(live_context["latest_prediction"]), "Current live estimate")
        metric_card("🩺", "Health Score", _format_health(live_context["latest_health"]), "Current health state")
        metric_card("🌡️", "THI", str(live_context["thi"]) if live_context["thi"] is not None else "n/a", "Thermal humidity index")
        metric_card("☁️", "Weather", f"{live_context['weather']['temperature']}°C / {live_context['weather']['humidity']}%" if live_context["weather"] else "n/a", "Current environment")
        metric_card("⚠️", "Risk Level", "Low" if str(_format_health(live_context["latest_health"])).lower() not in {"high", "critical", "medium"} else "Elevated", "Live risk view")
        recommendation_card("Latest Recommendation", _format_recommendation(latest_recommendations))

    with controls_col:
        st.markdown("### Scenario Controls")
        defaults = _get_default_inputs(twin, cow_record)
        controls = _render_controls(defaults)
        if controls["run_clicked"]:
            if latest_snapshot is None:
                st.warning("No live snapshot is available for this cow, so a scenario cannot be created yet.", icon="ℹ️")
            else:
                scenario_engine = st.session_state.setdefault("scenario_engine", ScenarioEngine())
                modified_inputs = {
                    "temperature": float(controls["temperature"]),
                    "humidity": float(controls["humidity"]),
                    "feed_intake": float(controls["feed_intake"]),
                    "body_weight": float(controls["body_weight"]),
                    "age": float(controls["age"]),
                }
                weather_override = controls.get("weather_override")
                if weather_override not in {None, "None"}:
                    weather_map = {
                        "Heat Wave": {"temperature": 35.0, "humidity": 80.0},
                        "Rainy": {"temperature": 24.0, "humidity": 85.0},
                        "Cold Front": {"temperature": 18.0, "humidity": 60.0},
                    }
                    modified_inputs["weather"] = weather_map[weather_override]

                scenario = scenario_engine.create_scenario(
                    cow_id=twin.cow_id,
                    base_snapshot_id=latest_snapshot.snapshot_id,
                    name="Scenario Studio run",
                    description="Interactive scenario generated from the current digital twin snapshot.",
                    modified_inputs=modified_inputs,
                )
                comparison = scenario_engine.compare_with_live(scenario, latest_snapshot)
                scenario_thi = _compute_thi(scenario.weather.get("temperature") if scenario.weather else None, scenario.weather.get("humidity") if scenario.weather else None)
                live_context["scenario_thi"] = scenario_thi
                live_context["scenario_recommendations"] = scenario.recommendations or []
                live_context["scenario_weather"] = scenario.weather
                st.session_state["current_scenario"] = scenario
                st.session_state["current_comparison"] = comparison
                st.session_state["current_live_context"] = live_context
                st.rerun()

    with result_col:
        st.markdown("### Scenario Result")
        scenario = st.session_state.get("current_scenario")
        comparison = st.session_state.get("current_comparison")
        if scenario is None:
            st.info("Run a scenario to populate the result cards.", icon="ℹ️")
        else:
            scenario_weather = live_context.get("scenario_weather") or scenario.weather or {}
            metric_card("🥛", "Predicted Milk", _format_prediction(scenario.prediction), "Scenario output")
            metric_card("🩺", "Health Score", _format_health(scenario.health_assessment), "Scenario health")
            metric_card("🌡️", "THI", str(live_context.get("scenario_thi")) if live_context.get("scenario_thi") is not None else "n/a", "Scenario THI")
            metric_card("☁️", "Weather", f"{scenario_weather.get('temperature', 'n/a')}°C / {scenario_weather.get('humidity', 'n/a')}%" if scenario_weather else "n/a", "Scenario environment")
            metric_card("⚠️", "Risk", "High" if str(_format_health(scenario.health_assessment)).lower() in {"high", "critical"} else "Medium" if str(_format_health(scenario.health_assessment)).lower() == "medium" else "Low", "Scenario risk")
            recommendation_card("Recommendation", _format_recommendation(scenario.recommendations))
            info_card("Difference from Live", _format_difference(comparison.milk_difference) if comparison else "n/a", "Milk delta")

    st.markdown("")
    render_section_header("Comparison Table", "A structured comparison view for the live state and the hypothetical scenario.")
    _render_comparison_table(live_context, st.session_state.get("current_scenario"), st.session_state.get("current_comparison"))

    st.markdown("")
    render_section_header("SHAP Comparison", "Explainability panels will be connected to the existing explainability service in a future release.")
    shap_left, shap_right = st.columns(2, gap="medium")
    with shap_left:
        # Future integration point: attach the current explainability output and SHAP feature contributions here.
        _render_shap_panel("Current SHAP")
    with shap_right:
        # Future integration point: compare the scenario explainability output with the live SHAP profile.
        _render_shap_panel("Scenario SHAP")

    st.markdown("")
    render_section_header("AI Decision Summary", "Scenario-level guidance will be surfaced here for future review.")
    scenario = st.session_state.get("current_scenario")
    summary = _build_scenario_summary(live_context, scenario, getattr(st.session_state.get("current_comparison"), "milk_difference", None) if st.session_state.get("current_comparison") else None)
    st.markdown(
        f"""
        <div style="border:1px solid #e2e8f0;border-radius:20px;padding:1.2rem 1.25rem;background:linear-gradient(135deg,#ffffff,#f8fafc);box-shadow:0 10px 24px rgba(15,23,42,0.04);">
            <div style="font-size:1.05rem;font-weight:700;color:#0f172a;">Scenario summary</div>
            <div style="margin-top:0.55rem;color:#475569;line-height:1.7;">{escape(summary)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    render_section_header("Scenario History", "Recent hypothetical runs will appear here as a list in a future release.")
    # Future integration point: populate this section from ScenarioEngine.list_scenarios() and tie it to playback history.
    history_items = [
        "Latest run from the current digital twin snapshot",
        "Future scenario history entries will appear here",
        "Playback integration will be added later",
    ]
    for item in history_items:
        st.markdown(
            f"""
            <div style="padding:0.8rem 0.95rem;border:1px solid #e2e8f0;border-radius:14px;background:#fff;margin-bottom:0.6rem;color:#334155;">{escape(item)}</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.caption("The UI now calls the existing scenario engine and reuses the existing prediction, health, explainability, and recommendation services without duplicating their logic.")
