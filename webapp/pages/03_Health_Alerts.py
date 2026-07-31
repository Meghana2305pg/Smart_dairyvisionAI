from __future__ import annotations

import sys
from pathlib import Path

current_path = Path(__file__).resolve()
project_root = None
for candidate in [current_path.parent, current_path.parent.parent]:
    if (candidate / "webapp").exists() and (candidate / "webapp" / "app.py").exists():
        project_root = candidate
        break
if project_root is None:
    project_root = current_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.weather_service import get_current_weather
from webapp.ui.section_header import apply_app_theme, metric_card, recommendation_panel, render_page_header, render_sidebar, status_badge, warning_banner

st.set_page_config(page_title="Health Alerts", page_icon="🚨", layout="wide")
apply_app_theme()
render_sidebar()

base_temp, base_hum = get_current_weather()
render_page_header(
    "Health Alerts",
    "Generate a fresh alert assessment from the values you enter now.",
    badge="Operational monitoring",
    caption="Health alerts and recommendations are recalculated from the current input values for live decision support.",
)

defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Alert", "Pending", "Current severity", "Monitoring")
with col2:
    metric_card("Predicted yield", "—", "Live estimate", "Pending")
with col3:
    metric_card("Decline", "—", "Expected productivity shift", "Pending")
with col4:
    metric_card("THI", "—", "Heat stress level", "Pending")

st.markdown("---")

with st.form("health_form"):
    st.markdown("<div class='section-card'><strong>Health inputs</strong></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (months)", min_value=1.0, max_value=200.0, value=float(defaults.get("age", 36.0)), step=1.0)
        weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(defaults.get("weight", 450.0)), step=10.0)
        feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=float(defaults.get("feed", 20.0)), step=1.0)
    with col2:
        temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(defaults.get("temperature", base_temp)), step=1.0)
        humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(defaults.get("humidity", base_hum)), step=1.0)
        health_status = st.selectbox("Health status", [0, 1], format_func=lambda value: "Healthy" if value == 0 else "Diseased")
    submitted = st.form_submit_button("Run alert check", use_container_width=True)

if submitted:
    input_row = {
        "age": age,
        "weight": weight,
        "feed": feed,
        "temperature": temperature,
        "humidity": humidity,
        "health_status": health_status,
    }
    result = get_health_alerts_for_input(input_row, base_temp=temperature, base_hum=humidity)

    st.markdown("---")
    status_badge(result["alert_category"], "warning" if result["severity"] != "Low" else "success")
    warning_banner(result["recommendation"])

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Predicted yield", f"{result['predicted_yield']:.2f} L/day", "Live estimate", "Updated")
    with col2:
        metric_card("Baseline yield", f"{result['baseline_yield']:.2f} L/day", "Reference output", "Benchmark")
    with col3:
        metric_card("Decline", f"{result['predicted_decline_pct']:.1f}%", "Expected productivity shift", "Review")

    recommendation_panel("AI recommendations", result["recommendation"], improvement=f"{max(result['predicted_decline_pct'] * -0.5, 0.0):.1f} L/day")
    st.caption(f"THI stress category: {result['stress_category']}")
