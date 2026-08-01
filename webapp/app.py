"""DairyVision AI - Professional Dashboard Application."""
from __future__ import annotations

import os
import sys
import traceback
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

from webapp.layout.shell import render_app_shell
from webapp.screens.analytics import render_analytics
from webapp.screens.command_centre import render_command_centre
from webapp.screens.cow_profile import render_cow_profile
from webapp.screens.dashboard import render_dashboard
from webapp.screens.digital_twin import render_digital_twin
from webapp.screens.explainability import render_explainability
from webapp.screens.health import render_health
from webapp.screens.herd import render_herd
from webapp.screens.operations import render_daily_operations
from webapp.screens.prediction import render_prediction
from webapp.screens.settings import render_settings
from webapp.services.auth_service import AuthService
from webapp.services.cow_service import CowService
from webapp.services.dashboard_service import DashboardService
from webapp.services.farm_service import FarmService
from webapp.services.observation_service import ObservationService
from webapp.state.session_state import (
    APP_STATE_AUTHENTICATED_NO_FARM,
    APP_STATE_AUTHENTICATED_WITH_COWS,
    APP_STATE_AUTHENTICATED_WITH_FARM,
    APP_STATE_NOT_AUTHENTICATED,
    bootstrap_session_state,
)
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_farm_setup_form, validate_login_form, validate_registration_form


def _reset_auth_state() -> None:
    """Reset the user-facing auth and farm state while preserving the service objects."""
    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state.farm = None
    st.session_state.farm_twin = None
    st.session_state.cows = []
    st.session_state.selected_cow_id = None
    st.session_state.last_selected_cow = None
    st.session_state.active_view = "login"
    st.session_state.active_section = "dashboard"
    st.session_state.app_state = APP_STATE_NOT_AUTHENTICATED


def initialize_app_state() -> None:
    """Initialize application state."""
    cow_service = CowService()
    observation_service = ObservationService(cow_service=cow_service)
    dashboard_service = DashboardService(cow_service=cow_service, observation_service=observation_service)

    bootstrap_session_state(
        {
            "app_state": APP_STATE_NOT_AUTHENTICATED,
            "active_view": "login",
            "active_section": "dashboard",
            "authenticated": False,
            "user": None,
            "farm": None,
            "farm_twin": None,
            "cows": [],
            "selected_cow_id": None,
            "show_herd_form": False,
            "observation_submitted": False,
            "submitted_cow_id": None,
            "dashboard_needs_refresh": False,
            "herd_search_term": "",
            "herd_status_filter": "All",
            "herd_breed_filter": "All",
            "last_selected_cow": None,
            "profile_tab": "Overview",
            "daily_ops_age": 36.0,
            "daily_ops_weight": 450.0,
            "daily_ops_feed": 20.0,
            "daily_ops_temperature": 20.0,
            "daily_ops_humidity": 50.0,
            "daily_ops_health_status": 0,
            "daily_ops_notes": "Routine farm observation",
            "daily_ops_cow": None,
            "daily_ops_phase": "form",
            "daily_ops_last_result": None,
            "daily_ops_last_submitted_cow": None,
            "auth_service": AuthService(),
            "farm_service": FarmService(),
            "cow_service": cow_service,
            "observation_service": observation_service,
            "dashboard_service": dashboard_service,
        }
    )


def resolve_app_state() -> str:
    """Resolve the current application state."""
    if not st.session_state.get("authenticated"):
        return APP_STATE_NOT_AUTHENTICATED
    if not st.session_state.get("farm"):
        return APP_STATE_AUTHENTICATED_NO_FARM
    if st.session_state.get("cows"):
        return APP_STATE_AUTHENTICATED_WITH_COWS
    return APP_STATE_AUTHENTICATED_WITH_FARM


def update_app_state() -> None:
    """Update the derived application state."""
    st.session_state["app_state"] = resolve_app_state()


def render_login_screen() -> None:
    """Render the login screen."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='
                text-align: center;
                padding: 40px 20px;
            '>
                <div style='
                    font-size: 48px;
                    margin-bottom: 16px;
                '>🐄</div>
                <div style='
                    font-size: 28px;
                    font-weight: 700;
                    color: #0f172a;
                    margin-bottom: 8px;
                '>DairyVision AI</div>
                <div style='
                    color: #475569;
                    font-size: 16px;
                    margin-bottom: 32px;
                '>Intelligent dairy farm management platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            service: AuthService = st.session_state.auth_service
            errors = validate_login_form(email, password)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    if service.login(email=email, password=password):
                        current_user = service.current_user()
                        st.session_state.user = current_user
                        st.session_state.authenticated = True
                        st.session_state.active_view = "login"
                        st.session_state.farm = None
                        st.session_state.farm_twin = None
                        st.session_state.cows = []
                        st.session_state.selected_cow_id = None
                        st.session_state.show_herd_form = False
                        st.session_state.active_section = "dashboard"
                        st.session_state.app_state = APP_STATE_AUTHENTICATED_NO_FARM
                        log_event("login_success", email=current_user.get("email") if current_user else email)
                        st.success("Signed in successfully")
                        st.rerun()
                    else:
                        log_event("login_failed", email=email)
                        st.error("Invalid email or password")
                except Exception as exc:
                    traceback.print_exc()
                    st.exception(exc)
                    log_error("authentication_failed", email=email, error=str(exc))
                    st.error(f"Authentication failed: {exc}")

        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True):
            st.session_state.active_view = "register"
            st.rerun()


def render_register_screen() -> None:
    """Render the registration screen."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='
                text-align: center;
                padding: 40px 20px;
            '>
                <div style='font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 8px;'>
                    Create Account
                </div>
                <div style='color: #475569; margin-bottom: 32px;'>
                    Join DairyVision AI and start managing your farm
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            errors = validate_registration_form(email, password, confirm_password, full_name)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                service: AuthService = st.session_state.auth_service
                try:
                    user = service.register_user(email=email, password=password, full_name=full_name, phone=phone)
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.session_state.farm = None
                    st.session_state.farm_twin = None
                    st.session_state.cows = []
                    st.session_state.selected_cow_id = None
                    st.session_state.active_view = "login"
                    st.session_state.active_section = "dashboard"
                    st.session_state.app_state = APP_STATE_AUTHENTICATED_NO_FARM
                    log_event("registration_success", email=email)
                    st.success("Account created successfully")
                    st.rerun()
                except Exception as exc:
                    # log_error("registration_failed", email=email, error=str(exc))
                    # st.error("Registration could not be completed. Please try again or contact support.")
                    import traceback

                    traceback.print_exc()          # prints full traceback in terminal
                    st.exception(exc)               # shows the actual exception in Streamlit
                    st.error(f"Registration failed: {exc}")
        if st.button("Back to Login", use_container_width=True):
            st.session_state.active_view = "login"
            st.rerun()


def render_farm_setup_screen() -> None:
    """Render the farm setup screen."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='
                text-align: center;
                padding: 40px 20px;
            '>
                <div style='font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 8px;'>
                    Create Your Farm
                </div>
                <div style='color: #475569; margin-bottom: 32px;'>
                    Set up your first farm workspace
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("farm_setup_form"):
            farm_name = st.text_input("Farm Name", placeholder="e.g., Green Pastures Farm")
            location = st.text_input("Location", placeholder="e.g., Bengaluru, IN")
            farm_size = st.text_input("Farm Size (hectares)", placeholder="e.g., 50")
            submitted = st.form_submit_button("Create Farm", use_container_width=True)

        if submitted:
            errors = validate_farm_setup_form(farm_name, location, farm_size)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                service: FarmService = st.session_state.farm_service
                farm_id = f"farm-{farm_name.lower().replace(' ', '-') }"
                try:
                    result = service.create_farm(farm_id=farm_id, name=farm_name, location=location, farm_size=farm_size)
                    st.session_state.farm = result["farm"]
                    st.session_state.farm_twin = result["farm_twin"]
                    st.session_state.cows = []
                    st.session_state.selected_cow_id = None
                    st.session_state.active_section = "dashboard"
                    log_event("farm_created", farm_id=farm_id)
                    st.success("Farm created successfully")
                    st.rerun()
                except Exception as exc:
                    log_error("farm_creation_failed", farm_id=farm_id, error=str(exc))
                    st.error("Farm setup could not be completed. Please try again shortly.")


def render_screen(section: str) -> None:
    """Render the requested screen."""
    section_map = {
        "dashboard": render_dashboard,
        "my_herd": render_herd,
        "daily_operations": render_daily_operations,
        "cow_profile": render_cow_profile,
        "prediction_center": render_prediction,
        "digital_twin": render_digital_twin,
        "health_alerts": render_health,
        "analytics": render_analytics,
        "explainability": render_explainability,
        "command_centre": render_command_centre,
        "settings": render_settings,
    }

    renderer = section_map.get(section, render_dashboard)
    renderer()


def main() -> None:
    """Main application entry point."""
    initialize_app_state()
    update_app_state()

    app_state = st.session_state.get("app_state")

    # Pre-authentication screens
    if app_state == APP_STATE_NOT_AUTHENTICATED:
        if st.session_state.get("active_view") == "register":
            render_register_screen()
        else:
            render_login_screen()
        return

    # Farm setup screen
    if app_state == APP_STATE_AUTHENTICATED_NO_FARM:
        render_farm_setup_screen()
        return

    # Main application with shell
    section = st.session_state.get("active_section", "dashboard")
    render_app_shell(lambda: render_screen(section))


if __name__ == "__main__":
    main()
