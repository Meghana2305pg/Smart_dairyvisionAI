"""Phase 1.5 - Professional Cow Profile Workspace for DairyVision AI."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.digital_twin.cow_twin import CowTwin
from webapp.services.cow_service import CowService
from webapp.ui.design_system import render_empty_state, render_section_title


def _normalize_observation(observation: Any) -> dict[str, Any]:
    """Normalize observation payloads into a display-friendly dictionary."""
    if isinstance(observation, dict) and "observation" in observation:
        observation = observation["observation"]
    if not isinstance(observation, dict):
        return {}
    timestamp = observation.get("timestamp")
    if isinstance(timestamp, datetime):
        timestamp_value = timestamp
    elif isinstance(timestamp, str):
        try:
            timestamp_value = datetime.fromisoformat(timestamp)
        except ValueError:
            timestamp_value = datetime.utcnow()
    else:
        timestamp_value = datetime.utcnow()
    return {
        "cow_id": observation.get("cow_id"),
        "notes": observation.get("notes") or "No notes recorded",
        "temperature": observation.get("temperature"),
        "humidity": observation.get("humidity"),
        "feed": observation.get("feed"),
        "weight": observation.get("weight"),
        "health_status": observation.get("health_status"),
        "timestamp": timestamp_value,
    }


def _get_or_create_twin(cow_service: CowService, cow_id: str, name: str | None = None) -> CowTwin:
    """Reuse an existing digital twin or create one from the current cow record."""
    twin = cow_service._cow_twins.get(cow_id)
    if twin is None:
        twin = CowTwin(cow_id=cow_id, name=name or cow_id)
        cow_service._cow_twins[cow_id] = twin
    return twin


def render_cow_profile() -> None:
    """Render the individual cow profile with Header, 6 Tabs, Metrics, Timeline, and Quick Actions."""
    st.markdown(
        """
        <style>
        .cow-profile-shell {
            padding: 0.1rem 0;
        }

        /* Profile Header Card */
        .cow-header-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-lg);
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--dv-shadow-sm);
        }
        .cow-header-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .cow-profile-main {
            display: flex;
            align-items: center;
            gap: 1.1rem;
        }
        .cow-avatar-box {
            width: 68px;
            height: 68px;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--dv-accent), #1d4ed8);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.2rem;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.22);
            flex-shrink: 0;
        }
        .cow-profile-title {
            font-size: clamp(1.4rem, 2.2vw, 2rem);
            font-weight: 800;
            color: var(--dv-text);
            margin: 0;
            line-height: 1.15;
            letter-spacing: -0.03em;
        }
        .cow-profile-sub {
            color: var(--dv-muted);
            font-size: 0.9rem;
            margin-top: 0.25rem;
            font-weight: 500;
        }
        .cow-badges-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.45rem;
            flex-wrap: wrap;
        }

        /* Tab Content Card Panels */
        .cow-tab-panel {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 1.2rem;
            box-shadow: var(--dv-shadow-sm);
            margin-top: 0.85rem;
        }

        /* Overview Metric Cards Grid */
        .cow-metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        .cow-metric-card {
            background: var(--dv-surface-alt);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-sm);
            padding: 0.9rem 1rem;
        }
        .cow-metric-lbl {
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--dv-muted);
        }
        .cow-metric-val {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--dv-text);
            margin: 0.2rem 0 0.1rem;
            line-height: 1.15;
        }
        .cow-metric-desc {
            font-size: 0.78rem;
            color: var(--dv-muted-2);
        }

        /* History Timeline */
        .cow-timeline {
            position: relative;
            padding-left: 1.35rem;
            margin-top: 0.6rem;
        }
        .cow-timeline::before {
            content: '';
            position: absolute;
            left: 6px;
            top: 6px;
            bottom: 6px;
            width: 2px;
            background: var(--dv-border-strong);
        }
        .cow-timeline-item {
            position: relative;
            margin-bottom: 0.95rem;
        }
        .cow-timeline-item:last-child {
            margin-bottom: 0;
        }
        .cow-timeline-dot {
            position: absolute;
            left: -1.35rem;
            top: 2px;
            width: 14px;
            height: 14px;
            border-radius: 999px;
            background: var(--dv-accent);
            border: 2.5px solid var(--dv-surface);
            box-shadow: 0 0 0 1px var(--dv-border-strong);
        }
        .cow-timeline-evt {
            font-weight: 700;
            font-size: 0.88rem;
            color: var(--dv-text);
        }
        .cow-timeline-dt {
            font-size: 0.74rem;
            color: var(--dv-muted-2);
            margin-top: 0.1rem;
        }
        .cow-timeline-desc {
            font-size: 0.82rem;
            color: var(--dv-muted);
            margin-top: 0.15rem;
        }

        @media (max-width: 900px) {
            .cow-metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 576px) {
            .cow-metric-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cow_service: CowService = st.session_state.cow_service
    observation_service = st.session_state.observation_service
    selected_cow_id = st.session_state.get("selected_cow_id")

    if not selected_cow_id:
        render_empty_state(
            title="No cow selected",
            message="Select a cow from My Herd to view full profile details, health history, and digital twin state.",
            icon="🐄",
            action_label="Go to My Herd",
            action_key="btn_goto_herd_empty",
        )
        if st.session_state.get("btn_goto_herd_empty"):
            st.session_state.active_section = "my_herd"
            st.rerun()
        return

    cows = cow_service.get_cows()
    cow_dict = None
    for item in cows:
        cow = item.get("cow", item)
        if str(cow.get("cow_id")) == str(selected_cow_id):
            cow_dict = cow
            break

    if not cow_dict:
        st.error(f"Cow '{selected_cow_id}' not found in current farm database.")
        if st.button("Back to My Herd", type="secondary"):
            st.session_state.active_section = "my_herd"
            st.rerun()
        return

    twin = _get_or_create_twin(cow_service, selected_cow_id, cow_dict.get("name"))
    observations = [_normalize_observation(item) for item in observation_service.repository.list_for_cow(selected_cow_id)]

    base_temp, base_hum = get_current_weather()
    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)
    input_row = {
        "age": float(cow_dict.get("age_months") or defaults.get("age", 36.0)),
        "weight": float(cow_dict.get("weight") or defaults.get("weight", 450.0)),
        "feed": float(defaults.get("feed", 20.0)),
        "temperature": float(defaults.get("temperature", base_temp)),
        "humidity": float(defaults.get("humidity", base_hum)),
        "health_status": 0,
    }
    prediction = predict_milk_yield(input_row, base_temp=base_temp, base_hum=base_hum)
    health = get_health_alerts_for_input(input_row, base_temp=base_temp, base_hum=base_hum)

    current_prediction = float(twin.latest_prediction.get("prediction", prediction.get("prediction", 0.0)) or 0.0) if twin.latest_prediction else float(prediction.get("prediction", 0.0) or 0.0)
    health_category = health.get("alert_category", "Healthy")
    if twin.latest_health:
        health_category = twin.latest_health.get("alert_category", health_category)

    current_status = "Synced" if twin.latest_observation else "Awaiting observation"
    latest_observation = observations[-1] if observations else None
    latest_observation_time = latest_observation["timestamp"].strftime("%Y-%m-%d %H:%M") if latest_observation else "No observation yet"

    health_badge = "Healthy"
    health_tone = "success"
    health_lower = str(health_category).lower()
    if any(k in health_lower for k in ["critical", "risk", "severe", "diseased"]):
        health_badge = "Critical"
        health_tone = "danger"
    elif any(k in health_lower for k in ["warning", "medium", "high"]):
        health_badge = "Warning"
        health_tone = "warning"

    cow_name = cow_dict.get("name") or selected_cow_id
    breed = cow_dict.get("breed") or "Unknown"
    age_months = cow_dict.get("age_months") or 24

    # ==============================================================================
    # HEADER & QUICK ACTIONS
    # ==============================================================================
    st.markdown(
        f"""
        <div class="cow-header-card">
            <div class="cow-header-inner">
                <div class="cow-profile-main">
                    <div class="cow-avatar-box">🐄</div>
                    <div>
                        <h1 class="cow-profile-title">{escape(cow_name)}</h1>
                        <div class="cow-profile-sub">
                            Cow ID: <strong>#{escape(selected_cow_id)}</strong> · Breed: <strong>{escape(breed)}</strong> · Age: <strong>{age_months} months</strong>
                        </div>
                        <div class="cow-badges-row">
                            <span class="status-badge {health_tone}">Health: {health_badge}</span>
                            <span class="status-badge neutral">Twin: {current_status}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_cols = st.columns(3, gap="small")
    with action_cols[0]:
        if st.button("✏️ Edit Profile", key="btn_prof_edit", use_container_width=True, type="secondary"):
            st.session_state.editing_cow_id = selected_cow_id
            st.session_state.active_section = "my_herd"
            st.rerun()

    with action_cols[1]:
        if st.button("📝 Record Observation", key="btn_prof_record_obs", use_container_width=True, type="primary"):
            st.session_state.selected_cow_id = selected_cow_id
            st.session_state.daily_ops_cow = selected_cow_id
            st.session_state.active_section = "daily_operations"
            st.rerun()

    with action_cols[2]:
        if st.button("💻 Open Digital Twin", key="btn_prof_open_dtwin", use_container_width=True, type="secondary"):
            st.session_state.selected_cow_id = selected_cow_id
            st.session_state.active_section = "digital_twin"
            st.rerun()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # ==============================================================================
    # 6 PROFESSIONAL TABS (Overview, Health, Production, History, Digital Twin, Recommendations)
    # ==============================================================================
    tab_overview, tab_health, tab_production, tab_history, tab_twin, tab_recs = st.tabs(
        ["Overview", "Health", "Production", "History", "Digital Twin", "Recommendations"]
    )

    # 1. OVERVIEW TAB
    with tab_overview:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("📌 Cow Overview", f"Core attributes and latest parameters for Cow #{selected_cow_id}")

        st.markdown(
            f"""
            <div class="cow-metric-grid">
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Age</div>
                    <div class="cow-metric-val">{age_months} months</div>
                    <div class="cow-metric-desc">Lifecycle stage</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Breed</div>
                    <div class="cow-metric-val">{escape(breed)}</div>
                    <div class="cow-metric-desc">Genetic line</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Weight</div>
                    <div class="cow-metric-val">{cow_dict.get('weight', defaults.get('weight', 450.0))} kg</div>
                    <div class="cow-metric-desc">Current body weight</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Health</div>
                    <div class="cow-metric-val"><span class="status-badge {health_tone}">{health_badge}</span></div>
                    <div class="cow-metric-desc">Alert status band</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Today's Prediction</div>
                    <div class="cow-metric-val">{current_prediction:.1f} L/day</div>
                    <div class="cow-metric-desc">Milk yield forecast</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Last Observation</div>
                    <div class="cow-metric-val">{latest_observation_time}</div>
                    <div class="cow-metric-desc">Latest recorded entry</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        latest_note = latest_observation["notes"] if latest_observation else "No observation notes logged yet."
        st.markdown(
            f"""
            <div style="background:var(--dv-surface-alt); border:1px solid var(--dv-border); border-radius:var(--dv-radius-sm); padding:0.9rem 1rem; margin-top:0.75rem;">
                <div style="font-weight:700; font-size:0.88rem; color:var(--dv-text); margin-bottom:0.25rem;">📝 Latest Observation Note</div>
                <div style="font-size:0.83rem; color:var(--dv-muted);">{escape(latest_note)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. HEALTH TAB
    with tab_health:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("🏥 Health Summary & Alerts", "Historical health logs and active alerts")

        col_h1, col_h2 = st.columns([1.2, 1], gap="medium")
        with col_h1:
            st.markdown("<div style='font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;'>Health Alerts & Stress Status</div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:var(--dv-surface-alt); border:1px solid var(--dv-border); border-left:4px solid var(--dv-{health_tone}); border-radius:var(--dv-radius-sm); padding:0.9rem 1rem;">
                    <div style="font-weight:700; color:var(--dv-text);">{escape(health_category)}</div>
                    <div style="font-size:0.83rem; color:var(--dv-muted); margin-top:0.25rem;">
                        {escape(health.get('recommendation', 'No active critical health alerts detected for this cow.'))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='margin-top:1rem; font-weight:700; font-size:0.9rem;'>Treatment & Vaccination Records</div>", unsafe_allow_html=True)
            st.info("No explicit vaccination or medical treatment logs are recorded for this cow in current dataset.", icon="ℹ️")

        with col_h2:
            st.markdown("<div style='font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;'>Observation History Summary</div>", unsafe_allow_html=True)
            if observations:
                for item in observations[-4:][::-1]:
                    st.markdown(
                        f"""
                        <div style="background:var(--dv-surface-alt); border:1px solid var(--dv-border); border-radius:var(--dv-radius-sm); padding:0.65rem 0.85rem; margin-bottom:0.45rem; font-size:0.82rem;">
                            <div style="font-weight:700; color:var(--dv-text);">📅 {item['timestamp'].strftime('%Y-%m-%d %H:%M')}</div>
                            <div style="color:var(--dv-muted); margin-top:0.15rem;">{escape(item['notes'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No past observations logged for this cow.", icon="ℹ️")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. PRODUCTION TAB
    with tab_production:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("🥛 Milk Production Analytics", "Forecasted daily yield and historical trends")

        col_p1, col_p2 = st.columns([1, 2], gap="medium")
        with col_p1:
            st.markdown(
                f"""
                <div class="cow-metric-card" style="margin-bottom:0.85rem;">
                    <div class="cow-metric-lbl">Milk Prediction</div>
                    <div class="cow-metric-val">{current_prediction:.1f} L/day</div>
                    <div class="cow-metric-desc">Forecasted daily yield</div>
                </div>
                <div class="cow-metric-card">
                    <div class="cow-metric-lbl">Model Confidence</div>
                    <div class="cow-metric-val">{float(prediction.get('confidence', 0.95)) * 100:.0f}%</div>
                    <div class="cow-metric-desc">Trained XGBoost Regressor</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_p2:
            st.markdown("<div style='font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;'>Production Trend Chart</div>", unsafe_allow_html=True)
            if twin.state.predictions:
                prediction_df = pd.DataFrame(twin.state.predictions)
                if not prediction_df.empty:
                    if "timestamp" in prediction_df.columns:
                        st.line_chart(prediction_df.set_index("timestamp")["prediction"])
                    else:
                        st.line_chart(prediction_df["prediction"])
            else:
                st.info("Line chart history will accumulate as daily observations are recorded for this cow.", icon="ℹ️")
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. HISTORY TAB (Vertical Timeline)
    with tab_history:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("📈 Operational History", "Vertical timeline of all recorded events (newest first)")

        timeline_events = []
        for obs in reversed(observations):
            timeline_events.append((obs["timestamp"], "Observation Recorded", obs["notes"]))

        if twin.latest_prediction:
            timeline_events.append((datetime.utcnow(), "Prediction Generated", f"Forecast output: {float(twin.latest_prediction.get('prediction', current_prediction) or 0.0):.1f} L/day"))
        if twin.latest_health:
            timeline_events.append((datetime.utcnow(), "Health Alert", str(twin.latest_health.get("alert_category", health_category))))
        if twin.latest_observation:
            timeline_events.append((datetime.utcnow(), "Twin Updated", "Digital twin memory refreshed with new parameters"))

        timeline_events.append((datetime.utcnow(), "Cow Registered", f"Cow {cow_name} (#{selected_cow_id}) initialized in farm workspace"))

        sorted_events = sorted(timeline_events, key=lambda x: x[0], reverse=True)[:10]

        st.markdown('<div class="cow-timeline">', unsafe_allow_html=True)
        for ts, title, details in sorted_events:
            ts_str = ts.strftime('%Y-%m-%d %H:%M') if isinstance(ts, datetime) else str(ts)
            st.markdown(
                f"""
                <div class="cow-timeline-item">
                    <div class="cow-timeline-dot"></div>
                    <div class="cow-timeline-evt">{escape(title)}</div>
                    <div class="cow-timeline-dt">🕒 {escape(ts_str)}</div>
                    <div class="cow-timeline-desc">{escape(details)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div></div>', unsafe_allow_html=True)

    # 5. DIGITAL TWIN TAB
    with tab_twin:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("💻 Digital Twin Summary", "Live memory state and sync status")

        col_t1, col_t2 = st.columns([1.5, 1], gap="medium")
        with col_t1:
            st.markdown(
                f"""
                <div class="cow-metric-grid">
                    <div class="cow-metric-card">
                        <div class="cow-metric-lbl">Twin Status</div>
                        <div class="cow-metric-val">{current_status}</div>
                        <div class="cow-metric-desc">Synchronization state</div>
                    </div>
                    <div class="cow-metric-card">
                        <div class="cow-metric-lbl">Latest Prediction</div>
                        <div class="cow-metric-val">{current_prediction:.1f} L/day</div>
                        <div class="cow-metric-desc">Milk yield output</div>
                    </div>
                    <div class="cow-metric-card">
                        <div class="cow-metric-lbl">Last Sync</div>
                        <div class="cow-metric-val">{latest_observation_time}</div>
                        <div class="cow-metric-desc">Timestamp of last memory sync</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
            if st.button("💻 Open Full Digital Twin", key="btn_open_full_dtwin", type="primary", use_container_width=True):
                st.session_state.selected_cow_id = selected_cow_id
                st.session_state.active_section = "digital_twin"
                st.rerun()

        with col_t2:
            st.markdown("<div style='font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;'>Recommendation Summary</div>", unsafe_allow_html=True)
            if twin.recommendations:
                for rec in twin.recommendations[:3]:
                    r_text = rec.get("message") if isinstance(rec, dict) else str(rec)
                    st.markdown(
                        f"""
                        <div style="background:var(--dv-surface-alt); border:1px solid var(--dv-border); border-left:4px solid var(--dv-accent); border-radius:var(--dv-radius-sm); padding:0.65rem 0.85rem; margin-bottom:0.45rem; font-size:0.82rem;">
                            {escape(r_text)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No digital twin recommendations compiled yet.", icon="ℹ️")
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. RECOMMENDATIONS TAB
    with tab_recs:
        st.markdown('<div class="cow-tab-panel">', unsafe_allow_html=True)
        render_section_title("💡 Recommendations", "Actionable guidance generated for this cow")

        all_recs = list(twin.recommendations)
        if health.get("recommendation"):
            all_recs.append({"message": health["recommendation"], "priority": "high"})

        if all_recs:
            for idx, rec in enumerate(all_recs[:5]):
                if isinstance(rec, dict):
                    msg = rec.get("message") or str(rec)
                    prio = str(rec.get("priority") or "medium").lower()
                else:
                    msg = str(rec)
                    prio = "medium"

                tone_cls = "danger" if prio in {"high", "critical"} else "warning" if prio in {"medium", "warning"} else "info"

                st.markdown(
                    f"""
                    <div style="background:var(--dv-surface-alt); border:1px solid var(--dv-border); border-left:4px solid var(--dv-{tone_cls}); border-radius:var(--dv-radius-sm); padding:0.85rem 1rem; margin-bottom:0.65rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                            <div style="font-weight:700; font-size:0.9rem; color:var(--dv-text);">💡 Action Item #{idx + 1}</div>
                            <span class="status-badge {tone_cls}">{prio.upper()} PRIORITY</span>
                        </div>
                        <div style="font-size:0.83rem; color:var(--dv-muted); line-height:1.45;">{escape(msg)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            render_empty_state(
                title="No active recommendations for this cow",
                message="This cow's parameters are healthy and operating smoothly.",
                icon="✨",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Secondary Navigation Footer
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    sec_cols = st.columns([1, 1], gap="small")
    with sec_cols[0]:
        if st.button("⬅️ Back to My Herd", key="btn_prof_back_herd", use_container_width=True, type="secondary"):
            st.session_state.selected_cow_id = None
            st.session_state.active_section = "my_herd"
            st.rerun()

    with sec_cols[1]:
        if st.button("🏠 Open Dashboard", key="btn_prof_open_dash", use_container_width=True, type="secondary"):
            st.session_state.active_section = "dashboard"
            st.rerun()
