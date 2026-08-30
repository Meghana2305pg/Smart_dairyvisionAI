"""Phase 1.5 - Guided Daily Operations Workflow for DairyVision AI."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any
import traceback

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.observation import Observation
from webapp.services.cow_service import CowService
from webapp.services.observation_service import ObservationService
from webapp.ui.design_system import render_empty_state, render_section_title
from webapp.utils.logging import log_error, log_event
from webapp.utils.validation import validate_daily_operations_form


def _build_input_row(age: float, weight: float, feed: float, temperature: float, humidity: float, health_status: int) -> dict[str, float | int]:
    return {
        "age": float(age),
        "weight": float(weight),
        "feed": float(feed),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "health_status": int(health_status),
    }


def _render_stepper(current_step: int) -> None:
    """Render a guided progress stepper across 5 steps."""
    steps = [
        ("1. Select Cow", 1),
        ("2. Observation", 2),
        ("3. Review", 3),
        ("4. Generate", 4),
        ("5. Results", 5),
    ]

    st.markdown(
        """
        <style>
        .ops-stepper-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.65rem;
            margin-bottom: 1.25rem;
        }
        .ops-stepper-card {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 0.75rem 0.5rem;
            text-align: center;
            box-shadow: var(--dv-shadow-sm);
            transition: all 180ms ease;
        }
        .ops-stepper-card.done {
            background: var(--dv-success-bg);
            border-color: var(--dv-success);
        }
        .ops-stepper-card.active {
            background: var(--dv-accent-bg);
            border-color: var(--dv-accent);
            box-shadow: var(--dv-shadow-md);
        }
        .ops-stepper-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 999px;
            font-weight: 800;
            font-size: 0.78rem;
            background: var(--dv-surface-alt);
            color: var(--dv-muted);
            margin-bottom: 0.25rem;
        }
        .ops-stepper-card.active .ops-stepper-num {
            background: var(--dv-accent);
            color: #ffffff;
        }
        .ops-stepper-card.done .ops-stepper-num {
            background: var(--dv-success);
            color: #ffffff;
        }
        .ops-stepper-lbl {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--dv-text);
        }
        @media (max-width: 768px) {
            .ops-stepper-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ops-stepper-grid">', unsafe_allow_html=True)
    for label, step_num in steps:
        state_cls = "done" if step_num < current_step else "active" if step_num == current_step else "pending"
        icon_symbol = "✓" if step_num < current_step else str(step_num)
        st.markdown(
            f"""
            <div class="ops-stepper-card {state_cls}">
                <div class="ops-stepper-num">{icon_symbol}</div>
                <div class="ops-stepper-lbl">{escape(label)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_daily_operations() -> None:
    """Render the 5-step guided Daily Operations workflow."""
    st.markdown(
        """
        <style>
        .ops-panel-card {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 1.2rem;
            box-shadow: var(--dv-shadow-sm);
            margin-bottom: 1.25rem;
        }
        .ops-field-section {
            background: var(--dv-surface-alt);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-sm);
            padding: 0.9rem 1rem;
            margin-bottom: 0.85rem;
        }
        .ops-section-hdr {
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--dv-muted);
            margin-bottom: 0.65rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    observation_service: ObservationService = st.session_state.observation_service
    cows = cow_service.get_cows()

    if not cows:
        render_empty_state(
            title="No cows available for daily operations",
            message="Register a cow in My Herd first to begin recording daily observations and generating predictions.",
            icon="🐄",
            action_label="Go to My Herd",
            action_key="btn_ops_goto_herd",
        )
        if st.session_state.get("btn_ops_goto_herd"):
            st.session_state.active_section = "my_herd"
            st.rerun()
        return

    cow_payloads = [cow.get("cow", cow) if isinstance(cow, dict) and "cow" in cow else cow for cow in cows]
    cow_ids = [str(item.get("cow_id") or "unknown") for item in cow_payloads]



    selected_cow_id = st.session_state.get("daily_ops_cow") or cow_ids[0]
    if selected_cow_id not in cow_ids:
        selected_cow_id = cow_ids[0]
    st.session_state.daily_ops_cow = selected_cow_id

    # Current Step in Workflow
    current_step = st.session_state.get("daily_ops_step", 1)
    last_result = st.session_state.get("daily_ops_last_result")

    # Header
    st.markdown(
        """
        <div style="margin-bottom:0.85rem;">
            <div style="font-size:0.8rem; font-weight:700; color:var(--dv-accent); text-transform:uppercase; letter-spacing:0.06em;">
                GUIDED OPERATIONAL WORKFLOW
            </div>
            <h1 style="font-size:clamp(1.5rem, 2.2vw, 2rem); font-weight:800; color:var(--dv-text); margin:0.1rem 0;">
                Daily Operations
            </h1>
            <div style="color:var(--dv-muted); font-size:0.92rem;">
                Record observations, review inputs, and generate real-time milk yield forecasts & health assessments.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render 5-Step Stepper
    _render_stepper(current_step)

    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)

    # ==============================================================================
    # STEP 5 / RESULTS DISPLAY
    # ==============================================================================
    if current_step == 5 and last_result:
        st.markdown('<div class="ops-panel-card">', unsafe_allow_html=True)
        st.success("✅ Observation recorded successfully! Digital Twin memory updated.")

        # Result Cards Grid
        res_cols = st.columns(4, gap="small")
        pred_val = float(last_result["prediction"].get("prediction", 0.0) or 0.0)
        health_cat = str(last_result["health"].get("alert_category", "Healthy"))

        with res_cols[0]:
            st.markdown(
                f"""
                <div class="dash-kpi-card">
                    <div class="dash-kpi-label">Milk Yield Forecast</div>
                    <div class="dash-kpi-val">{pred_val:.1f} L/day</div>
                    <div class="dash-kpi-desc">Generated by XGBoost</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with res_cols[1]:
            st.markdown(
                f"""
                <div class="dash-kpi-card">
                    <div class="dash-kpi-label">Health Summary</div>
                    <div class="dash-kpi-val">{escape(health_cat)}</div>
                    <div class="dash-kpi-desc">Alert assessment</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with res_cols[2]:
            st.markdown(
                f"""
                <div class="dash-kpi-card">
                    <div class="dash-kpi-label">Twin Status</div>
                    <div class="dash-kpi-val">Synced</div>
                    <div class="dash-kpi-desc">Snapshot memory updated</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with res_cols[3]:
            st.markdown(
                f"""
                <div class="dash-kpi-card">
                    <div class="dash-kpi-label">Selected Cow</div>
                    <div class="dash-kpi-val">#{escape(last_result['cow_id'])}</div>
                    <div class="dash-kpi-desc">Active record</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)

        # AI Recommendations
        st.markdown(
            f"""
            <div class="ops-field-section">
                <div class="ops-section-hdr">💡 AI Recommendations</div>
                <div style="font-size:0.88rem; color:var(--dv-text); font-weight:600;">
                    {escape(last_result['health'].get('recommendation', 'Routine monitoring recommended for current operational parameters.'))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick Actions
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        qa_cols = st.columns(4, gap="small")

        with qa_cols[0]:
            if st.button("📝 Record Another", key="btn_ops_res_record_another", type="primary", use_container_width=True):
                st.session_state.daily_ops_step = 1
                st.session_state.daily_ops_last_result = None
                st.rerun()

        with qa_cols[1]:
            if st.button("👤 View Cow Profile", key="btn_ops_res_profile", type="secondary", use_container_width=True):
                st.session_state.selected_cow_id = last_result['cow_id']
                st.session_state.active_section = "cow_profile"
                st.rerun()

        with qa_cols[2]:
            if st.button("💻 Digital Twin", key="btn_ops_res_dtwin", type="secondary", use_container_width=True):
                st.session_state.selected_cow_id = last_result['cow_id']
                st.session_state.active_section = "digital_twin"
                st.rerun()

        with qa_cols[3]:
            if st.button("🏠 Dashboard", key="btn_ops_res_dash", type="secondary", use_container_width=True):
                st.session_state.active_section = "dashboard"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ==============================================================================
    # STEP 1: SELECT COW
    # ==============================================================================
    if current_step == 1:
        st.markdown('<div class="ops-panel-card">', unsafe_allow_html=True)
        render_section_title("Step 1 · Select Target Cow", "Choose a registered cow to log today's observations")

        selected_cow_id = st.selectbox(
            "Select Cow ID",
            cow_ids,
            index=cow_ids.index(selected_cow_id),
            key="daily_ops_cow",
        )


        selected_payload = next((c for c in cow_payloads if str(c.get("cow_id")) == selected_cow_id), {})
        cname = selected_payload.get("name") or selected_cow_id
        cbreed = selected_payload.get("breed") or "Unknown"
        cage = selected_payload.get("age_months") or 24

        st.markdown(
            f"""
            <div class="ops-field-section" style="margin-top:0.85rem;">
                <div style="font-weight:700; color:var(--dv-text);">Selected: {escape(cname)} (#{escape(selected_cow_id)})</div>
                <div style="font-size:0.82rem; color:var(--dv-muted); margin-top:0.25rem;">
                    Breed: {escape(cbreed)} · Age: {cage} months
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Next: Record Observation ➡️", key="btn_ops_step1_next", type="primary", use_container_width=True):
            st.session_state.daily_ops_step = 2
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ==============================================================================
    # STEP 2: RECORD OBSERVATION FORM (Grouped Sections)
    # ==============================================================================
    if current_step == 2:
        st.markdown('<div class="ops-panel-card">', unsafe_allow_html=True)
        render_section_title("Step 2 · Enter Observation Parameters", f"Logging data for Cow #{selected_cow_id}")

        with st.form("ops_observation_guided_form"):
            # Section: Cow Information
            st.markdown('<div class="ops-field-section">', unsafe_allow_html=True)
            st.markdown('<div class="ops-section-hdr">1. Cow Information</div>', unsafe_allow_html=True)
            st.info(f"Logging record for Cow ID: #{selected_cow_id}", icon="🐄")
            st.markdown("</div>", unsafe_allow_html=True)

            # Section: Physical Parameters
            st.markdown('<div class="ops-field-section">', unsafe_allow_html=True)
            st.markdown('<div class="ops-section-hdr">2. Milk & Physical Parameters</div>', unsafe_allow_html=True)
            p_cols = st.columns(2, gap="medium")
            with p_cols[0]:
                age = st.number_input("Age (months)", min_value=1.0, max_value=300.0, value=float(st.session_state.get("daily_ops_age", defaults.get("age", 36.0))), step=1.0)
            with p_cols[1]:
                weight = st.number_input("Weight (kg)", min_value=100.0, max_value=1000.0, value=float(st.session_state.get("daily_ops_weight", defaults.get("weight", 450.0))), step=5.0)
            st.markdown("</div>", unsafe_allow_html=True)

            # Section: Health Status
            st.markdown('<div class="ops-field-section">', unsafe_allow_html=True)
            st.markdown('<div class="ops-section-hdr">3. Health Assessment</div>', unsafe_allow_html=True)
            health_status = st.selectbox("Health status", [0, 1], index=int(st.session_state.get("daily_ops_health_status", 0)), format_func=lambda v: "Healthy (0)" if v == 0 else "Diseased / Alert (1)")
            st.markdown("</div>", unsafe_allow_html=True)

            # Section: Feed & Environment
            st.markdown('<div class="ops-field-section">', unsafe_allow_html=True)
            st.markdown('<div class="ops-section-hdr">4. Feed & Ambient Climate</div>', unsafe_allow_html=True)
            f_cols = st.columns(3, gap="medium")
            with f_cols[0]:
                feed = st.number_input("Feed Intake (kg/day)", min_value=5.0, max_value=60.0, value=float(st.session_state.get("daily_ops_feed", defaults.get("feed", 20.0))), step=1.0)
            with f_cols[1]:
                temperature = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=float(st.session_state.get("daily_ops_temp", defaults.get("temperature", base_temp))), step=0.5)
            with f_cols[2]:
                humidity = st.number_input("Humidity (%)", min_value=20.0, max_value=100.0, value=float(st.session_state.get("daily_ops_hum", defaults.get("humidity", base_hum))), step=1.0)
            st.markdown("</div>", unsafe_allow_html=True)

            # Section: Notes
            st.markdown('<div class="ops-field-section">', unsafe_allow_html=True)
            st.markdown('<div class="ops-section-hdr">5. Notes</div>', unsafe_allow_html=True)
            notes = st.text_area("Observation Notes", value=st.session_state.get("daily_ops_notes", "Routine daily observation"), height=80)
            st.markdown("</div>", unsafe_allow_html=True)

            btn_cols = st.columns([1, 1], gap="small")
            with btn_cols[0]:
                back_step1 = st.form_submit_button("⬅️ Back", type="secondary", use_container_width=True)
            with btn_cols[1]:
                proceed_review = st.form_submit_button("Review Inputs ➡️", type="primary", use_container_width=True)

            if back_step1:
                st.session_state.daily_ops_step = 1
                st.rerun()

            if proceed_review:
                # Save draft inputs into session state for review
                st.session_state.daily_ops_age = age
                st.session_state.daily_ops_weight = weight
                st.session_state.daily_ops_feed = feed
                st.session_state.daily_ops_temp = temperature
                st.session_state.daily_ops_hum = humidity
                st.session_state.daily_ops_health_status = health_status
                st.session_state.daily_ops_notes = notes
                st.session_state.daily_ops_step = 3
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ==============================================================================
    # STEP 3 & 4: REVIEW & GENERATE PREDICTION
    # ==============================================================================
    if current_step == 3:
        st.markdown('<div class="ops-panel-card">', unsafe_allow_html=True)
        render_section_title("Step 3 · Review Observation Summary", f"Confirm inputs before submitting for Cow #{selected_cow_id}")

        age = st.session_state.get("daily_ops_age", 36.0)
        weight = st.session_state.get("daily_ops_weight", 450.0)
        feed = st.session_state.get("daily_ops_feed", 20.0)
        temperature = st.session_state.get("daily_ops_temp", base_temp)
        humidity = st.session_state.get("daily_ops_hum", base_hum)
        health_status = st.session_state.get("daily_ops_health_status", 0)
        notes = st.session_state.get("daily_ops_notes", "Routine observation")

        # Display Review Summary Cards
        rev_cols = st.columns(3, gap="small")
        with rev_cols[0]:
            st.markdown(
                f"""
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Physical</div>
                    <div class="cow-metric-val">{age:.0f} mo / {weight:.0f} kg</div>
                    <div class="cow-metric-desc">Age & Weight</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rev_cols[1]:
            st.markdown(
                f"""
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Feed & Climate</div>
                    <div class="cow-metric-val">{feed:.0f} kg / {temperature:.1f}°C</div>
                    <div class="cow-metric-desc">Intake & Temperature ({humidity:.0f}% RH)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rev_cols[2]:
            st.markdown(
                f"""
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Health Status</div>
                    <div class="cow-metric-val">{'Healthy' if health_status == 0 else 'Alert'}</div>
                    <div class="cow-metric-desc">Assessment code {health_status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="ops-field-section" style="margin-top:1rem;">
                <div class="ops-section-hdr">Notes</div>
                <div style="font-size:0.85rem; color:var(--dv-text);">{escape(notes)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
        act_cols = st.columns([1, 1.5], gap="small")

        with act_cols[0]:
            if st.button("✏️ Edit Inputs", key="btn_ops_edit_inputs", type="secondary", use_container_width=True):
                st.session_state.daily_ops_step = 2
                st.rerun()

        with act_cols[1]:
            if st.button("🚀 Confirm & Generate Prediction", key="btn_ops_confirm_submit", type="primary", use_container_width=True):
                validation_errors = validate_daily_operations_form({
                    "cow_id": selected_cow_id,
                    "age": age,
                    "weight": weight,
                    "feed": feed,
                    "temperature": temperature,
                    "humidity": humidity,
                    "notes": notes,
                })
                if validation_errors:
                    for err in validation_errors:
                        st.error(err)
                else:
                    try:

                        Observation(
                            cow_id=selected_cow_id,
                            age=float(age),
                            weight=float(weight),
                            feed=float(feed),
                            temperature=float(temperature),
                            humidity=float(humidity),
                            health_status=int(health_status),
                            notes=notes,
                        )

                        result = observation_service.record_observation(
                            cow_id=selected_cow_id,
                            age=float(age),
                            weight=float(weight),
                            feed=float(feed),
                            temperature=float(temperature),
                            humidity=float(humidity),
                            health_status=int(health_status),
                            notes=notes,
                        )
                        input_row = _build_input_row(float(age), float(weight), float(feed), float(temperature), float(humidity), int(health_status))
                        prediction = predict_milk_yield(input_row, base_temp=float(temperature), base_hum=float(humidity))
                        health = get_health_alerts_for_input(input_row, base_temp=float(temperature), base_hum=float(humidity))

                        st.session_state.daily_ops_step = 5
                        st.session_state.daily_ops_last_result = {
                            "cow_id": selected_cow_id,
                            "prediction": prediction,
                            "health": health,
                            "snapshot": result.get("snapshot"),
                        }
                        st.session_state.submitted_cow_id = selected_cow_id
                        st.session_state.selected_cow_id = selected_cow_id
                        st.session_state.dashboard_needs_refresh = True
                        log_event("observation_recorded", cow_id=selected_cow_id)
                        st.toast("Observation recorded & prediction generated!", icon="✅")
                        st.rerun()
                    except Exception as exc:
                        error_trace = traceback.format_exc()
                        log_error(
                            "observation_processing_failed",
                            cow_id=selected_cow_id,
                            error=str(exc),
                            traceback=error_trace,
                        )
                        st.error(f"Failed to process observation: {exc}")
                        st.error("Traceback:")
                        st.error(error_trace)

        st.markdown("</div>", unsafe_allow_html=True)
