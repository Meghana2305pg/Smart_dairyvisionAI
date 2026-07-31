from __future__ import annotations

import runpy
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
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.services.auth_service import AuthService
from webapp.services.cow_service import CowService
from webapp.services.dashboard_service import DashboardService
from webapp.services.farm_service import FarmService
from webapp.state.session_state import (
    APP_STATE_AUTHENTICATED_NO_FARM,
    APP_STATE_AUTHENTICATED_WITH_COWS,
    APP_STATE_AUTHENTICATED_WITH_FARM,
    APP_STATE_NOT_AUTHENTICATED,
    init_session_defaults,
)
from webapp.ui.activity_timeline import render_activity_timeline
from webapp.ui.analytics_views import render_analytics
from webapp.ui.cow_profile import render_cow_profile
from webapp.ui.daily_operations import render_daily_operations
from webapp.ui.dashboard_cards import action_button, info_card, timeline_item
from webapp.ui.herd_management import render_herd_management
from webapp.ui.navigation import render_shell, render_top_navigation
from webapp.ui.recommendation_panel import render_recommendations
from webapp.ui.section_header import apply_app_theme, render_page_header
from webapp.ui.twin_status_card import render_twin_status_card

PAGE_FILES = {
    "dashboard": None,
    "prediction": "01_Prediction.py",
    "digital_twin": "02_Digital_Twin.py",
    "health": "03_Health_Alerts.py",
    "explainability": "04_Explainability.py",
    "command_centre": "05_Command_Centre.py",
}


def initialize_app_state() -> None:
    """Create the session defaults used by the controlled app-shell workflow."""
    init_session_defaults(
        {
            "app_state": APP_STATE_NOT_AUTHENTICATED,
            "active_view": "login",
            "active_section": "dashboard",
            "authenticated": False,
            "user": None,
            "farm": None,
            "farm_twin": None,
            "cows": [],
            "auth_service": AuthService(),
            "farm_service": FarmService(),
            "cow_service": CowService(),
            "dashboard_service": DashboardService(),
            "sidebar_rendered": False,
        }
    )


def resolve_app_state() -> str:
    """Resolve the current application state from the session state."""
    if not st.session_state.get("authenticated"):
        return APP_STATE_NOT_AUTHENTICATED
    if not st.session_state.get("farm"):
        return APP_STATE_AUTHENTICATED_NO_FARM
    if st.session_state.get("cows"):
        return APP_STATE_AUTHENTICATED_WITH_COWS
    return APP_STATE_AUTHENTICATED_WITH_FARM


def update_app_state() -> None:
    """Keep the derived application state in sync with the live session state."""
    st.session_state["app_state"] = resolve_app_state()


def render_login_screen() -> None:
    """Render the authentication entry screen for unauthenticated users."""
    st.set_page_config(page_title="DairyVision AI", page_icon="🐄", layout="wide")
    apply_app_theme()
    render_top_navigation()

    render_page_header(
        "Welcome back",
        "Sign in to continue into your DairyVision workspace.",
        badge="Authentication",
        caption="The onboarding and application flow are managed centrally from this shell.",
    )

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        service: AuthService = st.session_state.auth_service
        try:
            if service.login(email=email, password=password):
                st.session_state.user = service.current_user()
                st.session_state.authenticated = True
                st.session_state.active_view = "login"
                st.session_state.farm = None
                st.session_state.farm_twin = None
                st.session_state.cows = []
                st.success("Signed in successfully")
                st.rerun()
            else:
                st.error("Invalid email or password")
        except Exception as exc:
            st.error(f"Supabase authentication failed: {exc}")

    st.markdown("---")
    st.info("New here? Create an account to begin onboarding your farm workspace.")
    if st.button("Create Account"):
        st.session_state.active_view = "register"
        st.rerun()


def render_register_screen() -> None:
    """Render the registration screen as a guided onboarding step."""
    st.set_page_config(page_title="Register", page_icon="🧑‍🌾", layout="wide")
    apply_app_theme()
    render_top_navigation()

    render_page_header(
        "Create account",
        "Set up your DairyVision account and continue into farm onboarding.",
        badge="Registration",
        caption="This screen is only available from the login flow and never appears in the sidebar.",
    )

    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create account")

    if submitted:
        if not full_name or not email or not password:
            st.error("Please complete the required fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            service: AuthService = st.session_state.auth_service
            try:
                user = service.register_user(email=email, password=password, full_name=full_name, phone=phone)
                st.session_state.user = user
                st.session_state.authenticated = True
                st.session_state.active_view = "login"
                st.session_state.farm = None
                st.session_state.farm_twin = None
                st.session_state.cows = []
                st.success("Account created successfully")
                st.rerun()
            except Exception as exc:
                st.error(f"Supabase registration failed: {exc}")

    st.markdown("---")
    if st.button("Back to login"):
        st.session_state.active_view = "login"
        st.rerun()


def render_farm_setup_screen() -> None:
    """Render the farm onboarding screen after first sign-in."""
    st.set_page_config(page_title="Farm Setup", page_icon="🏡", layout="wide")
    apply_app_theme()
    render_top_navigation()

    render_page_header(
        "Farm onboarding",
        "Create the first farm for your DairyVision workspace.",
        badge="Onboarding",
        caption="Once the farm is created, the app will advance automatically to the dashboard.",
    )

    with st.form("farm_setup_form"):
        farm_name = st.text_input("Farm Name")
        location = st.text_input("Location")
        farm_size = st.text_input("Farm Size")
        submitted = st.form_submit_button("Create farm")

    if submitted:
        if not farm_name:
            st.error("Farm name is required.")
        else:
            service: FarmService = st.session_state.farm_service
            farm_id = f"farm-{farm_name.lower().replace(' ', '-') or 'default'}"
            result = service.create_farm(farm_id=farm_id, name=farm_name, location=location, farm_size=farm_size)
            st.session_state.farm = result["farm"]
            st.session_state.farm_twin = result["farm_twin"]
            st.session_state.cows = []
            st.success("Farm created successfully")
            st.session_state.active_section = "dashboard"
            st.rerun()

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.farm = None
        st.session_state.farm_twin = None
        st.session_state.cows = []
        st.session_state.active_view = "login"
        st.session_state.active_section = "dashboard"
        st.rerun()


def render_dashboard_body() -> None:
    """Render the modern SaaS dashboard home for authenticated farm users."""
    render_page_header(
        "Dashboard",
        "Monitor the herd, the environment, and the twin experience from a single professional workspace.",
        badge="Operations platform",
        caption="The dashboard combines existing prediction, weather, health, and twin services into a polished SaaS experience.",
    )

    dashboard_service: DashboardService = st.session_state.dashboard_service
    dashboard = dashboard_service.build_dashboard()
    farm_name = dashboard.farm.get("name") or st.session_state.get("farm", {}).get("name", "your farm") or "your farm"
    cow_count = dashboard.herd.get("cow_count", 0)

    if cow_count == 0:
        st.markdown(
            f"""
            <div class="hero-card">
              <div class="section-heading">Welcome to DairyVision AI</div>
              <div class="card-caption">Your farm is ready. You have not registered any cows yet.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Register First Cow", use_container_width=True):
            st.session_state.active_section = "command_centre"
            st.rerun()
        return

    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)
    input_row = {
        "age": float(defaults.get("age", 36.0)),
        "weight": float(defaults.get("weight", 450.0)),
        "feed": float(defaults.get("feed", 20.0)),
        "temperature": float(defaults.get("temperature", base_temp)),
        "humidity": float(defaults.get("humidity", base_hum)),
        "health_status": 0,
    }
    prediction = predict_milk_yield(input_row, base_temp=base_temp, base_hum=base_hum)
    health = get_health_alerts_for_input(input_row, base_temp=base_temp, base_hum=base_hum)

    st.markdown(
        f"""
        <div class="hero-card">
          <div class="section-heading">Farm Overview</div>
          <div class="card-caption">{farm_name} is operational with {cow_count} active cows and a live digital twin workflow.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("Farm Summary", farm_name, f"{cow_count} cows tracked", "success")
    with col2:
        info_card("Today's Prediction", f"{float(prediction.get('prediction', 0)):.2f} L/day", "Live yield estimate", "success")
    with col3:
        info_card("Weather", f"{base_temp:.0f}°C / {base_hum:.0f}%", "Current environment", "neutral")
    with col4:
        info_card("Health Summary", health.get("alert_category", "Stable"), health.get("recommendation", "No action required"), "warning")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Quick Actions</div>", unsafe_allow_html=True)
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    with quick_col1:
        action_button("Register Cow", "command_centre")
    with quick_col2:
        action_button("Record Observation", "command_centre")
    with quick_col3:
        action_button("Open Digital Twin", "digital_twin")
    with quick_col4:
        action_button("View Analytics", "analytics")

    st.markdown("---")
    recommendations = dashboard.recommendations or []
    if recommendations:
        render_recommendations(recommendations)
    else:
        st.markdown("<div class='section-heading'>Recommendations</div>", unsafe_allow_html=True)
        st.info("No recommendations have been generated yet for the current operational state.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Recent Activity Timeline</div>", unsafe_allow_html=True)
    activity_items = [
        ("Observation saved", "The latest observation was recorded and linked to the active twin.", "Just now"),
        ("Prediction updated", "The milk yield forecast was refreshed from the latest operational inputs.", "5 min ago"),
        ("Health alert", "The current state was assessed against the health service recommendation engine.", "10 min ago"),
        ("Twin snapshot created", "A fresh memory snapshot was prepared for the active animal profile.", "15 min ago"),
    ]
    render_activity_timeline(activity_items)

    st.markdown("---")
    twin_state = {
        "status": "Twin Synced",
        "snapshot_count": dashboard.herd.get("snapshot_count", 0),
        "last_observation": "Today",
        "prediction": f"{float(prediction.get('prediction', 0)):.2f} L/day",
        "health": health.get("alert_category", "Stable"),
    }
    render_twin_status_card(twin_state)

    st.markdown("---")
    st.markdown("<div class='section-heading'>System Status</div>", unsafe_allow_html=True)
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    with status_col1:
        info_card("Twin Status", "Healthy", "Connected to the digital twin workflow", "success")
    with status_col2:
        info_card("Memory Status", f"{dashboard.herd.get('snapshot_count', 0)} snapshots", "Stored in the twin memory layer", "neutral")
    with status_col3:
        info_card("Prediction Status", "Live", "Freshly refreshed from the backend service", "success")
    with status_col4:
        info_card("Last Sync", "Just now", "Dashboard view refreshed", "neutral")


def render_existing_page(page_name: str) -> None:
    """Render the existing Streamlit page module from the pages directory."""
    page_path = project_root / "webapp" / "pages" / PAGE_FILES[page_name]
    runpy.run_path(str(page_path), run_name="__main__")


def render_requested_section(section: str) -> None:
    """Render the requested application section inside the custom shell."""
    if section == "dashboard":
        render_dashboard_body()
    elif section == "herd":
        if st.session_state.get("selected_cow_id"):
            render_cow_profile()
        else:
            render_herd_management()
    elif section == "daily_operations":
        render_daily_operations()
    elif section == "prediction":
        render_existing_page("prediction")
    elif section == "digital_twin":
        render_existing_page("digital_twin")
    elif section == "health":
        render_existing_page("health")
    elif section == "explainability":
        render_existing_page("explainability")
    elif section == "command_centre":
        render_existing_page("command_centre")
    elif section == "analytics":
        render_analytics()
    elif section == "settings":
        st.markdown("<div class='section-heading'>Settings</div>", unsafe_allow_html=True)
        st.info("Settings page coming soon.")
    else:
        render_dashboard_body()


def render_app_shell() -> None:
    """Render the main application shell and route between onboarding and operational views."""
    st.set_page_config(page_title="DairyVision AI", page_icon="🐄", layout="wide")
    apply_app_theme()
    update_app_state()

    app_state = st.session_state.get("app_state")

    if app_state == APP_STATE_NOT_AUTHENTICATED:
        if st.session_state.get("active_view") == "register":
            render_register_screen()
        else:
            render_login_screen()
        return

    if app_state == APP_STATE_AUTHENTICATED_NO_FARM:
        render_farm_setup_screen()
        return

    section = st.session_state.get("active_section", "dashboard")
    render_shell(section, lambda: render_requested_section(section))


initialize_app_state()
render_app_shell()
