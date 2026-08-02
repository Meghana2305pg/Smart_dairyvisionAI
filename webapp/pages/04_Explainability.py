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
import pandas as pd
import plotly.express as px

from webapp.backend_services.explainability_service import get_explanation_for_input
from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.weather_service import get_current_weather
from webapp.ui.section_header import apply_app_theme, metric_card, recommendation_panel, render_page_header, render_sidebar, status_badge, warning_banner

st.set_page_config(page_title="Prediction Insights", page_icon="🧠", layout="wide")
apply_app_theme()
render_sidebar()

base_temp, base_hum = get_current_weather()
render_page_header(
    "Prediction Insights",
    "Inspect how the current scenario shifts the model's feature contributions.",
    badge="Decision support",
    caption="Explanation values are computed fresh for the current scenario using the trained model and current inputs.",
)

defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Top feature", "—", "Highest impact", "Live")
with col2:
    metric_card("Contribution", "—", "Model influence", "Pending")
with col3:
    metric_card("Scenario", "Current", "Active inputs", "Ready")
with col4:
    metric_card("Model", "Trained", "Existing backend", "Stable")

st.markdown("---")

with st.form("explainability_form"):
    st.markdown("<div class='section-card'><strong>Scenario inputs</strong></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (months)", min_value=1.0, max_value=200.0, value=float(defaults.get("age", 36.0)), step=1.0)
        weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(defaults.get("weight", 450.0)), step=10.0)
        feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=float(defaults.get("feed", 20.0)), step=1.0)
    with col2:
        temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(defaults.get("temperature", base_temp)), step=1.0)
        humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(defaults.get("humidity", base_hum)), step=1.0)
        health_status = st.selectbox("Health status", [0, 1], format_func=lambda value: "Healthy" if value == 0 else "Diseased")
    submitted = st.form_submit_button("Explain current scenario", use_container_width=True)

if submitted:
    input_row = {
        "age": age,
        "weight": weight,
        "feed": feed,
        "temperature": temperature,
        "humidity": humidity,
        "health_status": health_status,
    }
    contributions = get_explanation_for_input(input_row, base_temp=temperature, base_hum=humidity)

    st.markdown("---")
    status_badge("Insights refreshed", "success")
    warning_banner("The contribution ranking is recomputed for the latest scenario values.")

    chart_data = pd.DataFrame(
        [{"feature": item["feature"], "contribution": round(float(item["contribution"]), 4)} for item in contributions[:10]]
    )
    if not chart_data.empty:
        fig = px.bar(
            chart_data.sort_values("contribution", ascending=True),
            x="contribution",
            y="feature",
            orientation="h",
            color="contribution",
            color_continuous_scale="Greens",
        )
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor="white", plot_bgcolor="#f8fafc")
        st.plotly_chart(fig, use_container_width=True, key="explainability_contribution_chart")

    st.dataframe(
        [{"feature": item["feature"], "contribution": round(item["contribution"], 4)} for item in contributions],
        use_container_width=True,
    )
    recommendation_panel("AI recommendations", "Focus on the strongest drivers for the current scenario before adjusting operations.", improvement="Actionable insight")
