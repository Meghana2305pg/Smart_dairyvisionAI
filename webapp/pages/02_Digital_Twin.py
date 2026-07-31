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

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.simulation_service import run_dynamic_simulation
from webapp.backend_services.weather_service import get_current_weather
from webapp.ui.section_header import apply_app_theme, metric_card, recommendation_panel, render_page_header, render_sidebar, status_badge, warning_banner

st.set_page_config(page_title="Digital Twin Simulator", page_icon="🐄", layout="wide")
apply_app_theme()
render_sidebar()

base_temp, base_hum = get_current_weather()
render_page_header(
    "Digital Twin Simulator",
    "Evaluate how feed intake and temperature affect predicted milk yield for the current herd profile.",
    badge="Scenario planning",
    caption="Each scenario is recomputed from your current inputs for live operational analysis.",
)

defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Scenario set", "Live", "Fresh simulation run", "Active")
with col2:
    metric_card("Feed range", f"{defaults.get('feed', 20.0):.0f} kg/day", "Baseline intake", "Nominal")
with col3:
    metric_card("Temperature", f"{defaults.get('temperature', base_temp):.0f}°C", "Baseline environment", "Current")
with col4:
    metric_card("THI", "—", "Heat stress context", "Pending")

st.markdown("---")

with st.form("digital_twin_form"):
    st.markdown("<div class='section-card'><strong>Scenario inputs</strong></div>", unsafe_allow_html=True)
    profile_col1, profile_col2, profile_col3 = st.columns([1, 1, 1.2])
    with profile_col1:
        age = st.number_input("Age (months)", min_value=1.0, max_value=200.0, value=float(defaults.get("age", 36.0)), step=1.0)
        weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(defaults.get("weight", 450.0)), step=10.0)
    with profile_col2:
        feed = st.number_input("Starting feed intake (kg/day)", min_value=5.0, max_value=60.0, value=float(defaults.get("feed", 20.0)), step=1.0)
        health_status = st.selectbox("Health status", [0, 1], format_func=lambda value: "Healthy" if value == 0 else "Diseased")
    with profile_col3:
        temperature = st.number_input("Base temperature (°C)", min_value=10.0, max_value=50.0, value=float(defaults.get("temperature", base_temp)), step=1.0)
        humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(defaults.get("humidity", base_hum)), step=1.0)
        feed_range = st.text_input("Feed range", value="10,15,20,25,30,35", help="Comma-separated feed values")
        temp_range = st.text_input("Temperature range", value="18,24,30,36,42", help="Comma-separated temperature values")
    submitted = st.form_submit_button("Run digital twin", use_container_width=True)

if submitted:
    try:
        feed_values = [float(item.strip()) for item in feed_range.split(",") if item.strip()]
        temp_values = [float(item.strip()) for item in temp_range.split(",") if item.strip()]
    except ValueError:
        st.error("Please enter numeric comma-separated values for the simulation ranges.")
        st.stop()

    input_row = {
        "age": age,
        "weight": weight,
        "feed": feed,
        "temperature": temperature,
        "humidity": humidity,
        "health_status": health_status,
    }
    df = run_dynamic_simulation(input_row, feed_range=feed_values, temp_range=temp_values, base_temp=temperature, base_hum=humidity)

    st.markdown("---")
    status_badge("Simulation generated", "success")
    warning_banner("The scenario table is rebuilt from the latest input values for each run.")
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        chart_df = df.copy()
        chart_df["Scenario"] = chart_df["Temp_C"].astype(str) + "°C"
        fig = px.line(
            chart_df,
            x="Feed_kg",
            y="Pred_L",
            color="Scenario",
            markers=True,
            line_shape="spline",
        )
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=10), legend_title_text="Scenario", paper_bgcolor="white", plot_bgcolor="#f8fafc")
        st.plotly_chart(fig, use_container_width=True)

    recommendation_panel("AI recommendations", "Increase feed modestly during hotter conditions to protect yield stability.", improvement="+1.2 L/day")
