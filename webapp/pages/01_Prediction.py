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
import plotly.graph_objects as go

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.ui.section_header import apply_app_theme, metric_card, recommendation_panel, render_page_header, render_sidebar, status_badge, warning_banner

st.set_page_config(page_title="Milk Yield Prediction", page_icon="🥛", layout="wide")
apply_app_theme()
render_sidebar()

base_temp, base_hum = get_current_weather()
render_page_header(
    "Milk Yield Prediction",
    "Forecast expected milk yield from the current herd profile and environment conditions.",
    badge="Operational forecasting",
    caption="The prediction is recomputed from your current inputs for live decision support.",
)

defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Milk Yield", "—", "Expected output", "Pending")
with col2:
    metric_card("THI", f"{base_temp:.0f}", "Ambient stress index", "Baseline")
with col3:
    metric_card("Health", "Healthy", "Current status", "Stable")
with col4:
    metric_card("Feed", f"{defaults.get('feed', 20.0):.0f} kg/day", "Current intake", "Nominal")

st.markdown("---")

with st.form("prediction_form"):
    st.markdown("<div class='section-card'><strong>Cow profile</strong></div>", unsafe_allow_html=True)
    profile_col1, profile_col2, profile_col3 = st.columns([1, 1, 1.2])
    with profile_col1:
        age = st.number_input("Age (months)", min_value=1.0, max_value=200.0, value=float(defaults.get("age", 36.0)), step=1.0, help="Enter the cow age in months.")
        weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(defaults.get("weight", 450.0)), step=10.0, help="Current animal weight.")
    with profile_col2:
        feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=float(defaults.get("feed", 20.0)), step=1.0, help="Daily feed intake for the selected cow.")
        health_status = st.selectbox("Health status", [0, 1], format_func=lambda value: "Healthy" if value == 0 else "Diseased", help="Select the health state for this scenario.")
    with profile_col3:
        temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(defaults.get("temperature", base_temp)), step=1.0, help="Current or target ambient temperature.")
        humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(defaults.get("humidity", base_hum)), step=1.0, help="Current ambient humidity.")
    st.caption("The model uses the current values you enter and recomputes features on the fly.")
    submitted = st.form_submit_button("Run prediction", use_container_width=True)

if submitted:
    input_row = {
        "age": age,
        "weight": weight,
        "feed": feed,
        "temperature": temperature,
        "humidity": humidity,
        "health_status": health_status,
    }
    result = predict_milk_yield(input_row, base_temp=temperature, base_hum=humidity)

    prediction = float(result["prediction"])
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prediction,
            title={"text": "Predicted milk yield"},
            gauge={
                "axis": {"range": [0, max(35.0, prediction * 1.25)]},
                "bar": {"color": "#2f7d32"},
                "steps": [
                    {"range": [0, max(35.0, prediction * 1.25) * 0.6], "color": "#f1f5f9"},
                    {"range": [max(35.0, prediction * 1.25) * 0.6, max(35.0, prediction * 1.25) * 0.85], "color": "#e2e8f0"},
                    {"range": [max(35.0, prediction * 1.25) * 0.85, max(35.0, prediction * 1.25)], "color": "#cbd5e1"},
                ],
            },
        )
    )
    gauge_fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")

    st.markdown("---")
    st.markdown(
        """
        <div class="section-card">
          <div style="font-size:0.8rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">Prediction Summary</div>
          <div style="margin-top:0.7rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.75rem;">
            <div><div style="font-size:0.8rem;color:#64748b;">Cow Age</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{age:.0f} months</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">Weight</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{weight:.0f} kg</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">Feed Intake</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{feed:.0f} kg/day</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">Temperature</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{temperature:.0f} °C</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">Humidity</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{humidity:.0f} %</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">THI</div><div style="font-size:1.05rem;font-weight:700;color:#0f172a;">{thi:.1f}</div></div>
            <div><div style="font-size:0.8rem;color:#64748b;">Predicted Milk Yield</div><div style="font-size:1.05rem;font-weight:700;color:#2f7d32;">{prediction:.2f} L/day</div></div>
          </div>
        </div>
        """.format(
            age=age,
            weight=weight,
            feed=feed,
            temperature=temperature,
            humidity=humidity,
            thi=round(0.8 * temperature + (humidity / 100.0) * (temperature - 14.4) + 46.4, 1),
            prediction=prediction,
        ),
        unsafe_allow_html=True,
    )

    result_col1, result_col2 = st.columns([1.2, 0.8])
    with result_col1:
        st.plotly_chart(gauge_fig, use_container_width=True, key="prediction_gauge_chart")
    with result_col2:
        status_badge("Prediction ready", "success")
        warning_banner("The forecast is computed from live input values and refreshed with every run.")
        recommendation_panel("AI recommendations", "Maintain current intake and monitor ambient stress closely.", improvement="+0.7 L/day")

    with st.expander("Advanced Details (Developer Mode)", expanded=False):
        visible_feature_fields = [
            field for field in ["age", "weight", "feed", "temperature", "humidity", "health_status"]
            if field in result["feature_values"]
        ]
        visible_feature_table = {
            key: [result["feature_values"][key]] for key in visible_feature_fields
        }
        st.dataframe(visible_feature_table, use_container_width=True)
