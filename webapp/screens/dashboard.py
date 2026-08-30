"""Phase 9.2 - Redesigned Dashboard Screen Using Design System Tokens & Components."""

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
from webapp.services.dashboard_service import DashboardService
from webapp.ui.design_system import (
    render_alert_card,
    render_empty_state,
    render_metric_card,
    render_recommendation_card,
    render_section_title,
    render_timeline_item,
)
from webapp.utils.logging import log_event


def _get_latest_twin_snapshot(cow_service: Any, cow_id: str | None) -> Any | None:
    """Return the latest snapshot from the selected cow twin when available."""
    if not cow_id:
        return None
    twin = getattr(cow_service, "_cow_twins", {}).get(cow_id)
    if twin is None:
        return None
    memory_store = getattr(twin, "memory_store", None)
    if memory_store is None:
        return None
    return memory_store.get_latest_snapshot(cow_id)


def _get_greeting_and_icon() -> tuple[str, str]:
    """Return a farm-friendly greeting and matching icon based on current time."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning", "👋"
    if hour < 18:
        return "Good Afternoon", "☀️"
    return "Good Evening", "🌙"


def _categorize_health_alerts(health_items: list[dict[str, Any]]) -> tuple[int, int, int, list[dict[str, Any]]]:
    """Categorize health alerts using dataset severity fields."""
    critical_alerts = []
    healthy_count = 0
    warning_count = 0

    for item in health_items:
        sev = str(item.get("severity") or "").lower()
        if sev in {"critical", "high", "danger", "warning", "medium"}:
            critical_alerts.append(item)
            if sev in {"critical", "high", "danger"}:
                pass
            else:
                warning_count += 1
        else:
            healthy_count += 1

    return healthy_count, warning_count, len(critical_alerts), critical_alerts


def render_dashboard() -> None:
    """Render the dashboard using Design System tokens and reusable UI components."""
    st.markdown(
        """
        <style>
        .dash-layout-container {
            padding: 0.1rem 0;
        }
        .dash-page-header {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.94) 100%);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-lg);
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--dv-shadow-sm);
        }
        .dash-page-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .dash-title {
            font-size: clamp(1.5rem, 2.2vw, 2rem);
            font-weight: 800;
            color: var(--dv-text);
            margin: 0.1rem 0;
            letter-spacing: -0.03em;
        }
        .dash-subtitle {
            color: var(--dv-muted);
            font-size: 0.92rem;
        }
        .dash-top-metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1.4rem;
        }
        .dash-quick-actions-card {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-md);
            padding: 1.1rem;
            box-shadow: var(--dv-shadow-sm);
        }
        @media (max-width: 1024px) {
            .dash-top-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 576px) {
            .dash-top-metrics { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading dashboard..."):
        dashboard_service: DashboardService = st.session_state.dashboard_service
        dashboard = dashboard_service.build_dashboard()
        base_temp, base_hum = get_current_weather()
        submitted_cow_id = st.session_state.get("submitted_cow_id") or st.session_state.get("selected_cow_id")
        cow_service = st.session_state.get("cow_service")
        latest_snapshot = _get_latest_twin_snapshot(cow_service, submitted_cow_id)

    if latest_snapshot is not None:
        input_row = {
            "age": float(getattr(latest_snapshot.observation, "age", None) or 36.0),
            "weight": float(getattr(latest_snapshot.observation, "weight", None) or 450.0),
            "feed": float(getattr(latest_snapshot.observation, "feed", None) or 20.0),
            "temperature": float(getattr(latest_snapshot.observation, "temperature", None) or base_temp),
            "humidity": float(getattr(latest_snapshot.observation, "humidity", None) or base_hum),
            "health_status": int(getattr(latest_snapshot.observation, "health_status", 0) or 0),
        }
        prediction = latest_snapshot.prediction or predict_milk_yield(input_row, base_temp=base_temp, base_hum=base_hum)
        health = latest_snapshot.health or get_health_alerts_for_input(input_row, base_temp=base_temp, base_hum=base_hum)
    else:
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

    cow_service = st.session_state.get("cow_service")

    live_cows = []
    if cow_service is not None:
        try:
            live_cows = cow_service.get_cows() or []
        except Exception:
            live_cows = []

    cow_count = int(dashboard.herd.get("cow_count", 0) or 0)
    if cow_count == 0 and live_cows:
        cow_count = len(live_cows)

    log_event("debug_dashboard_render", cow_count=cow_count, live_cow_count=len(live_cows), branch="empty" if cow_count == 0 else "normal")

    observation_count = int(dashboard.herd.get("observation_count", 0))
    recommendation_items = list(dashboard.recommendations or [])
    alert_entries = list(dashboard.health or [])

    healthy_count, warning_count, active_alert_count, active_alerts = _categorize_health_alerts(alert_entries)
    if healthy_count == 0 and cow_count:
        healthy_count = max(cow_count - active_alert_count, 0)

    milk_prediction = float(prediction.get("prediction", 0.0) or 0.0)
    farm_name = (dashboard.farm or {}).get("name") or st.session_state.get("farm_name") or "Green Pastures Farm"
    greeting, greeting_icon = _get_greeting_and_icon()
    today_label = datetime.now().strftime("%A, %d %b %Y")

    # ==============================================================================
    # PAGE HEADER
    # ==============================================================================
    col_hdr_left, col_hdr_right = st.columns([3, 1.2], gap="small")
    with col_hdr_left:
        st.markdown(
            f"""
            <div class="dash-page-header">
                <div class="dash-page-header-row">
                    <div>
                        <div style="font-size:0.8rem; font-weight:700; color:var(--dv-accent); text-transform:uppercase; letter-spacing:0.06em;">
                            {greeting} {greeting_icon} · {escape(farm_name)}
                        </div>
                        <h1 class="dash-title">Dashboard</h1>
                        <div class="dash-subtitle">
                            Monitor herd performance, AI predictions and operational health.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_hdr_right:
        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
        btn_cols = st.columns(2, gap="small")
        with btn_cols[0]:
            if st.button("🔄 Refresh", key="btn_dash_refresh", use_container_width=True, type="secondary"):
                st.rerun()

        with btn_cols[1]:
            # Generate Report CSV Download Button
            report_df = pd.DataFrame([
                {
                    "Farm": farm_name,
                    "Total Cows": cow_count,
                    "Predicted Milk Output (L)": f"{milk_prediction:.1f}",
                    "Healthy Cows": healthy_count,
                    "Active Health Alerts": active_alert_count,
                    "Date": today_label,
                }
            ])
            report_csv = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📊 Report",
                data=report_csv,
                file_name=f"farm_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary",
                key="btn_dash_report",
            )

    # Empty State check when no cows exist in workspace
    if cow_count == 0:
        render_empty_state(
            title="No cows registered in farm workspace yet",
            message="Register your first cow to begin monitoring herd metrics, milk yield predictions, and health alerts.",
            icon="🐄",
            action_label="Register First Cow",
            action_key="btn_dash_register_first",
        )
        if st.session_state.get("btn_dash_register_first"):
            st.session_state.show_herd_form = True
            st.session_state.active_section = "my_herd"
            st.rerun()
        return

    # ==============================================================================
    # TOP METRIC ROW (4 Metric Cards using render_metric_card component)
    # ==============================================================================
    col_m1, col_m2, col_m3, col_m4 = st.columns(4, gap="small")

    with col_m1:
        render_metric_card(
            title="Total Cows",
            value=str(cow_count),
            subtitle="Tracked herd size",
            icon="🐄",
            status="Stable",
            tone="success",
        )

    with col_m2:
        render_metric_card(
            title="Today's Predicted Milk",
            value=f"{milk_prediction:.1f} L",
            subtitle="Forecasted daily yield",
            icon="💧",
            status="Model forecast",
            tone="info",
        )

    with col_m3:
        render_metric_card(
            title="Healthy Cows",
            value=str(healthy_count),
            subtitle="Operating normally",
            icon="✅",
            status="Low risk",
            tone="success",
        )

    with col_m4:
        alert_status = "Needs review" if active_alert_count else "All clear"
        alert_tone = "danger" if active_alert_count else "success"
        render_metric_card(
            title="Active Alerts",
            value=str(active_alert_count),
            subtitle="Requires attention" if active_alert_count else "Zero warnings",
            icon="🚨",
            status=alert_status,
            tone=alert_tone,
        )

    st.markdown("<div style='margin-bottom: 1.4rem;'></div>", unsafe_allow_html=True)

    # ==============================================================================
    # SECOND ROW: Left = AI Recommendations, Right = Active Alerts
    # ==============================================================================
    col_r2_left, col_r2_right = st.columns([1.3, 1], gap="medium")

    # LEFT: AI RECOMMENDATIONS
    with col_r2_left:
        render_section_title("💡 AI Recommendations", "Actionable guidance generated from herd parameters")

        if recommendation_items:
            for idx, rec in enumerate(recommendation_items[:4]):
                if isinstance(rec, dict):
                    msg = rec.get("message") or rec.get("action") or str(rec)
                    title = rec.get("title") or f"Actionable Insight #{idx + 1}"
                    prio = str(rec.get("priority") or "medium").lower()
                elif hasattr(rec, "message"):
                    msg = getattr(rec, "message", str(rec))
                    title = getattr(rec, "title", f"Actionable Insight #{idx + 1}")
                    prio = str(getattr(rec, "priority", "medium")).lower()
                else:
                    msg = str(rec)
                    title = "Recommendation"
                    prio = "medium"

                render_recommendation_card(
                    title=title,
                    description=msg,
                    icon="💡",
                    priority=prio,
                )
        else:
            render_empty_state(
                title="No active AI recommendations",
                message="Your herd is operating within optimal baseline parameters. Recommendations will appear here automatically when health or feed events are detected.",
                icon="✨",
            )

    # RIGHT: ACTIVE ALERTS
    with col_r2_right:
        render_section_title("🚨 Active Alerts", "Priority health warnings requiring review")

        if alert_entries:
            for item in alert_entries[:4]:
                sev = str(item.get("severity") or "warning").lower()
                title = str(item.get("category") or item.get("alert_type") or "Health Warning")
                msg = str(item.get("message") or item.get("description") or "Check cow health parameters.")
                now_str = datetime.now().strftime("%I:%M %p")

                render_alert_card(
                    title=title,
                    message=msg,
                    severity=sev,
                    timestamp=f"Logged Today at {now_str}",
                )
        else:
            render_empty_state(
                title="No active health alerts",
                message="All monitored cows are operating in optimal health with zero active warnings.",
                icon="✅",
            )

    st.markdown("<div style='margin-bottom: 1.4rem;'></div>", unsafe_allow_html=True)

    # ==============================================================================
    # THIRD ROW: Left = Recent Activity Timeline, Right = Quick Actions
    # ==============================================================================
    col_r3_left, col_r3_right = st.columns([1.3, 1], gap="medium")

    # LEFT: RECENT ACTIVITY TIMELINE
    with col_r3_left:
        render_section_title("📈 Recent Activity Timeline", "Latest operational events across farm workspace")

        now_time = datetime.now().strftime("%I:%M %p")
        timeline_events = []

        if observation_count > 0:
            timeline_events.append(("Observation Recorded", f"Today, {now_time}", f"{observation_count} observation(s) logged in workspace.", "📝"))
        if dashboard.snapshots:
            timeline_events.append(("Twin Updated", f"Today, {now_time}", "Digital twin state refreshed with live parameters.", "💻"))
        if prediction:
            timeline_events.append(("Prediction Generated", f"Today, {now_time}", f"Yield forecast updated ({milk_prediction:.1f} L/day).", "💧"))
        if alert_entries:
            timeline_events.append(("Health Alert", f"Today, {now_time}", f"{len(alert_entries)} health item(s) active.", "🚨"))
        timeline_events.append(("Cow Registered", "Initial setup", f"{cow_count} cow(s) registered in herd database.", "🐄"))

        for title, ts, desc, icon in timeline_events[:5]:
            render_timeline_item(
                title=title,
                timestamp=ts,
                description=desc,
                icon=icon,
            )

    # RIGHT: QUICK ACTIONS
    with col_r3_right:
        render_section_title("⚡ Quick Actions", "Direct shortcuts to key operational workflows")

        st.markdown(
            """
            <div class="dashboard-card" style="padding:1rem; margin-bottom:0.85rem;">
                <div style="font-weight:700; margin-bottom:0.9rem;">Quick Actions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("➕ Add Cow", key="qa_btn_add_cow", type="primary", use_container_width=True):
            st.session_state.show_herd_form = True
            st.session_state.active_section = "my_herd"
            st.rerun()

        st.markdown("<div style='margin-top:0.45rem;'></div>", unsafe_allow_html=True)

        if st.button("📝 Record Observation", key="qa_btn_record_obs", type="primary", use_container_width=True):
            st.session_state.active_section = "daily_operations"
            st.rerun()

        st.markdown("<div style='margin-top:0.45rem;'></div>", unsafe_allow_html=True)

        if st.button("💻 Open Digital Twin", key="qa_btn_open_dtwin", type="secondary", use_container_width=True):
            st.session_state.active_section = "digital_twin"
            st.rerun()

        st.markdown("<div style='margin-top:0.45rem;'></div>", unsafe_allow_html=True)

        if st.button("📊 View Analytics", key="qa_btn_view_analytics", type="secondary", use_container_width=True):
            st.session_state.active_section = "analytics"
            st.rerun()

        st.markdown("<div style='margin-top:0.45rem;'></div>", unsafe_allow_html=True)

        if st.button("📄 Generate Report", key="qa_btn_gen_report", type="secondary", use_container_width=True):
            st.toast("Farm summary report generated successfully!", icon="✅")

    if st.session_state.get("dashboard_needs_refresh"):
        st.session_state["dashboard_needs_refresh"] = False
