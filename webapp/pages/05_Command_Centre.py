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
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.farm_twin import FarmTwin
from webapp.digital_twin.herd_twin import HerdTwin
from webapp.digital_twin.observation import Observation
from webapp.ui.section_header import apply_app_theme, metric_card, recommendation_panel, render_page_header, render_sidebar, status_badge, warning_banner

st.set_page_config(page_title="Farm Command Centre", page_icon="🏡", layout="wide")
apply_app_theme()
render_sidebar()

base_temp, base_hum = get_current_weather()
render_page_header(
    "Farm Command Centre",
    "Coordinate the digital twin experience around the farm, the herd, and the cow lifecycle.",
    badge="Twin operations",
    caption="Observations create snapshots, and each snapshot becomes part of the twin memory for the cow and the wider farm context.",
)

defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

st.markdown("<div class='section-card'><strong>Capture a fresh observation and update the cow twin.</strong></div>", unsafe_allow_html=True)
with st.form("command_centre_form"):
    col1, col2, col3 = st.columns([1, 1, 1.2])
    with col1:
        cow_id = st.text_input("Cow ID", value="cow-001")
        age = st.number_input("Age (months)", min_value=1.0, max_value=200.0, value=float(defaults.get("age", 36.0)), step=1.0)
        weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(defaults.get("weight", 450.0)), step=10.0)
    with col2:
        feed = st.number_input("Feed intake (kg/day)", min_value=5.0, max_value=60.0, value=float(defaults.get("feed", 20.0)), step=1.0)
        temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(defaults.get("temperature", base_temp)), step=1.0)
        humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(defaults.get("humidity", base_hum)), step=1.0)
    with col3:
        health_status = st.selectbox("Health status", [0, 1], format_func=lambda value: "Healthy" if value == 0 else "Diseased")
        notes = st.text_area("Observation notes", value="Routine farm observation")
    submitted = st.form_submit_button("Update twin", use_container_width=True)

if submitted:
    observation = Observation(
        cow_id=cow_id,
        age=float(age),
        weight=float(weight),
        feed=float(feed),
        temperature=float(temperature),
        humidity=float(humidity),
        health_status=int(health_status),
        notes=notes,
    )

    cow = CowTwin(cow_id=cow_id)
    cow.record_observation(observation)
    cow.refresh_from_ai(base_temp=float(temperature), base_hum=float(humidity))

    herd = HerdTwin(herd_id="herd-1")
    herd.register_cow(cow)
    herd.refresh_state()

    farm = FarmTwin(farm_id="farm-1")
    farm.register_herd(herd)
    farm.refresh_state()

    st.markdown("---")
    st.subheader("Farm Overview")
    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
    with overview_col1:
        metric_card("Weather", f"{temperature:.0f}°C / {humidity:.0f}%", "Current environment", "Live")
    with overview_col2:
        metric_card("Farm Status", farm.state.status.title(), "Current farm state", "Updated")
    with overview_col3:
        metric_card("Active Cow Twins", str(len(herd.cows)), "Tracked cow entities", "Live")
    with overview_col4:
        metric_card("Snapshots", str(cow.state.context.get("snapshot_count", 0)), "Stored in memory", "Ready")

    st.markdown("---")
    st.subheader("Cow Twin Overview")
    cow_col1, cow_col2, cow_col3 = st.columns([1.1, 1.1, 1.2])
    with cow_col1:
        status_badge(cow.state.status.title(), "success" if cow.state.status == "stable" else "warning")
        st.markdown(f"**Cow ID:** {cow.cow_id}")
        st.markdown(f"**Last Updated:** {cow.state.last_updated.strftime('%Y-%m-%d %H:%M:%S') if cow.state.last_updated else 'n/a'}")
        st.markdown(f"**Snapshot Count:** {cow.state.context.get('snapshot_count', 0)}")
    with cow_col2:
        st.markdown(f"**Latest Prediction:** {cow.latest_prediction['prediction']:.2f} L/day" if cow.latest_prediction else "**Latest Prediction:** n/a")
        st.markdown(f"**Latest Health:** {cow.latest_health.get('severity', 'n/a')}" if cow.latest_health else "**Latest Health:** n/a")
        st.markdown(f"**Weather:** {cow.latest_intelligence.weather if cow.latest_intelligence and cow.latest_intelligence.weather else 'n/a'}")
    with cow_col3:
        st.markdown(f"**Recommendations:** {len(cow.recommendations)}")
        if cow.recommendations:
            for item in cow.recommendations[:3]:
                st.markdown(f"- {item.message}")
        else:
            st.markdown("- No recommendations yet")

    st.markdown("---")
    st.subheader("Twin Lifecycle")
    st.markdown(
        """
        <div class='section-card'>
          <div style='display:flex;flex-direction:column;gap:0.35rem;'>
            <div>Observation → Twin Updated → AI Analysis → Snapshot Saved → Recommendations</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("Twin Timeline")
    latest_snapshot = cow.memory_store.get_latest_snapshot(cow.cow_id)
    if latest_snapshot is not None:
        st.write(f"Latest snapshot: {latest_snapshot.snapshot_id}")
        st.write(f"Twin status: {latest_snapshot.twin_status}")
        if latest_snapshot.prediction is not None:
            st.write(f"Prediction: {latest_snapshot.prediction}")
    else:
        warning_banner("No snapshots have been stored for this cow yet.")

    st.markdown("---")
    st.subheader("Operational shortcuts")
    shortcut_col1, shortcut_col2, shortcut_col3 = st.columns(3)
    with shortcut_col1:
        st.link_button("Open Prediction", "/Prediction")
    with shortcut_col2:
        st.link_button("Open Health", "/Health_Alerts")
    with shortcut_col3:
        st.link_button("Open Explainability", "/Explainability")
else:
    st.info("Enter the observation details and update the twin to populate the command centre.")
