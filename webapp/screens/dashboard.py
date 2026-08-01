"""Dashboard screen for DairyVision AI."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from webapp.backend_services.feature_service import get_feature_defaults
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather
from webapp.services.dashboard_service import DashboardService


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


def _get_greeting() -> str:
    """Return a farm-friendly greeting based on the current time."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def _get_healthy_and_alert_counts(health_items: list[dict[str, Any]]) -> tuple[int, int]:
    """Summarize current health data using actual severity values already in the dataset."""
    if not health_items:
        return 0, 0

    active_alerts = 0
    healthy_count = 0
    for item in health_items:
        severity = str(item.get("severity") or "").lower()
        if severity in {"high", "critical", "warning"}:
            active_alerts += 1
        else:
            healthy_count += 1
    return healthy_count, active_alerts


def _render_empty_state(title: str, message: str, icon: str = "✨") -> None:
    """Render a compact empty state card with a clear explanation."""
    st.markdown(
        f"""
        <div class="dashboard-empty-state">
            <div class="empty-state-icon">{icon}</div>
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-copy">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    """Render the main dashboard screen with a compact operations overview."""
    st.markdown(
        """
        <style>
        .dashboard-shell {
            padding: 0.1rem 0;
        }
        .dashboard-hero {
            background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(248,250,252,0.95));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.06);
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .dashboard-hero-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .dashboard-hero-title {
            font-size: clamp(1.5rem, 2vw, 2rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.15;
            color: #0f172a;
            margin: 0;
        }
        .dashboard-hero-meta {
            color: #475569;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.4rem;
        }
        .dashboard-hero-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-top: 0.55rem;
            max-width: 620px;
        }
        .dashboard-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: rgba(37, 99, 235, 0.08);
            color: #1d4ed8;
            border: 1px solid rgba(37, 99, 235, 0.12);
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .dashboard-kpi-grid {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.85rem;
            margin-bottom: 1.1rem;
        }
        .dashboard-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
            min-height: 138px;
            transition: transform 180ms ease, box-shadow 180ms ease;
        }
        .dashboard-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }
        .dash-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .dash-card-icon {
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            background: rgba(37, 99, 235, 0.08);
            color: #1d4ed8;
        }
        .dash-card-icon.success { background: rgba(21, 128, 61, 0.08); color: #15803d; }
        .dash-card-icon.warning { background: rgba(245, 158, 11, 0.10); color: #b45309; }
        .dash-card-icon.danger { background: rgba(239, 68, 68, 0.10); color: #b91c1c; }
        .dash-card-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #64748b;
        }
        .dash-card-value {
            font-size: clamp(1.3rem, 1.9vw, 1.8rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.15;
            color: #0f172a;
            margin: 0.25rem 0 0.1rem;
        }
        .dash-card-subtitle {
            font-size: 0.82rem;
            color: #64748b;
        }
        .dash-card-status {
            display: inline-flex;
            align-items: center;
            margin-top: 0.65rem;
            font-size: 0.76rem;
            font-weight: 700;
            border-radius: 999px;
            padding: 0.38rem 0.62rem;
        }
        .dash-card-status.success { background: rgba(21, 128, 61, 0.10); color: #15803d; }
        .dash-card-status.warning { background: rgba(245, 158, 11, 0.12); color: #b45309; }
        .dash-card-status.danger { background: rgba(239, 68, 68, 0.10); color: #b91c1c; }
        .dash-card-status.neutral { background: rgba(148, 163, 184, 0.12); color: #475569; }
        .dashboard-layout {
            display: grid;
            grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.9fr);
            gap: 1rem;
            align-items: start;
        }
        .panel-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 20px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.04);
            padding: 1rem 1rem 0.5rem;
        }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.85rem;
        }
        .panel-title {
            font-size: 0.9rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #475569;
            margin: 0;
        }
        .panel-subtitle {
            color: #64748b;
            font-size: 0.85rem;
            margin: 0.15rem 0 0;
        }
        .recommendation-list, .alert-list, .timeline-list {
            display: grid;
            gap: 0.75rem;
        }
        .recommendation-item, .alert-item, .timeline-item {
            background: #f8fafc;
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
        }
        .recommendation-item {
            border-left: 4px solid rgba(21,128,61,0.7);
        }
        .alert-item {
            border-left: 4px solid rgba(239,68,68,0.7);
        }
        .alert-item.warning {
            border-left-color: rgba(245,158,11,0.7);
        }
        .alert-item.info {
            border-left-color: rgba(37,99,235,0.7);
        }
        .chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.28rem 0.55rem;
            font-size: 0.7rem;
            font-weight: 700;
            margin-top: 0.55rem;
        }
        .chip.success { background: rgba(21,128,61,0.10); color: #15803d; }
        .chip.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .chip.danger { background: rgba(239,68,68,0.10); color: #b91c1c; }
        .chip.neutral { background: rgba(148,163,184,0.12); color: #475569; }
        .dashboard-empty-state {
            background: linear-gradient(135deg, rgba(248,250,252,1), rgba(255,255,255,0.96));
            border: 1px dashed rgba(148,163,184,0.35);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            text-align: center;
        }
        .empty-state-icon {
            font-size: 1.6rem;
            margin-bottom: 0.35rem;
        }
        .empty-state-title {
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .empty-state-copy {
            color: #64748b;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .action-stack {
            display: grid;
            gap: 0.7rem;
        }
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 700 !important;
            height: 44px !important;
            box-shadow: none !important;
            transition: all 180ms ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: white !important;
            border: none !important;
        }
        .stButton > button[kind="secondary"] {
            background: white !important;
            color: #0f172a !important;
            border: 1px solid rgba(148,163,184,0.32) !important;
        }
        @media (max-width: 1100px) {
            .dashboard-kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .dashboard-layout { grid-template-columns: 1fr; }
        }
        @media (max-width: 720px) {
            .dashboard-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .dashboard-hero-row { align-items: flex-start; }
        }
        @media (max-width: 480px) {
            .dashboard-kpi-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading latest dashboard context..."):
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

    cow_count = int(dashboard.herd.get("cow_count", 0))
    observation_count = int(dashboard.herd.get("observation_count", 0))
    recommendation_items = list(dashboard.recommendations or [])
    alert_entries = list(dashboard.health or [])
    healthy_count, active_alert_count = _get_healthy_and_alert_counts(alert_entries)

    if healthy_count == 0 and cow_count:
        healthy_count = max(cow_count - active_alert_count, 0)

    milk_prediction = float(prediction.get("prediction", 0.0) or 0.0)
    farm_name = (dashboard.farm or {}).get("name") or "Current Farm"
    greeting = _get_greeting()
    today_label = datetime.now().strftime("%A, %d %b %Y")

    st.markdown(
        f"""
        <div class="dashboard-shell">
            <div class="dashboard-hero">
                <div class="dashboard-hero-row">
                    <div>
                        <div class="dashboard-badge">{greeting}</div>
                        <h1 class="dashboard-hero-title">{farm_name}</h1>
                        <div class="dashboard-hero-meta">{today_label}</div>
                    </div>
                    <div class="dashboard-badge">Operational overview</div>
                </div>
                <div class="dashboard-hero-subtitle">
                    Today’s farm summary: {cow_count} cows tracked, {milk_prediction:.1f} L predicted output, and {active_alert_count} active alert(s) requiring attention.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_items = [
        {
            "label": "Total Cows",
            "value": str(cow_count),
            "status": "Stable" if cow_count else "No cows yet",
            "tone": "neutral" if not cow_count else "success",
            "icon": "🐄",
            "icon_tone": "success",
        },
        {
            "label": "Predicted Milk Yield",
            "value": f"{milk_prediction:.1f} L",
            "status": "Current forecast" if milk_prediction else "Awaiting forecast",
            "tone": "neutral" if not milk_prediction else "success",
            "icon": "💧",
            "icon_tone": "success",
        },
        {
            "label": "Healthy Cows",
            "value": str(healthy_count),
            "status": "Low risk" if healthy_count else "No stable cows",
            "tone": "success" if healthy_count else "neutral",
            "icon": "✅",
            "icon_tone": "success",
        },
        {
            "label": "Active Alerts",
            "value": str(active_alert_count),
            "status": "Needs review" if active_alert_count else "No active alerts",
            "tone": "danger" if active_alert_count else "neutral",
            "icon": "🚨",
            "icon_tone": "danger" if active_alert_count else "success",
        },
        {
            "label": "Weather",
            "value": f"{base_temp:.0f}°C",
            "status": f"Humidity {base_hum:.0f}%",
            "tone": "neutral",
            "icon": "🌤️",
            "icon_tone": "success",
        },
        {
            "label": "Recent Observations",
            "value": str(observation_count),
            "status": "Logged today" if observation_count else "No observations yet",
            "tone": "neutral" if not observation_count else "success",
            "icon": "📝",
            "icon_tone": "success",
        },
    ]

    st.markdown('<div class="dashboard-kpi-grid">', unsafe_allow_html=True)
    for item in kpi_items:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dash-card-header">
                    <div class="dash-card-label">{item['label']}</div>
                    <div class="dash-card-icon {item['icon_tone']}">{item['icon']}</div>
                </div>
                <div class="dash-card-value">{item['value']}</div>
                <div class="dash-card-subtitle">{item['status']}</div>
                <div class="dash-card-status {item['tone']}">{item['status']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.5, 0.95], gap="medium")

    with left_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">AI Recommendations</div>
                        <p class="panel-subtitle">Operational guidance generated from the latest context.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if recommendation_items:
            for rec in recommendation_items[:3]:
                message = rec.get("message") if isinstance(rec, dict) else (rec.message if hasattr(rec, "message") else str(rec))
                st.markdown(
                    f"""
                    <div class="recommendation-item">
                        <div style='font-weight:700; color:#0f172a; margin-bottom:0.25rem;'>AI insight</div>
                        <div style='color:#475569; line-height:1.5;'>{message}</div>
                        <div class='chip success'>Recommended</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            _render_empty_state("No recommendations yet", "AI guidance will appear here once observations and alerts are available.", "🧠")

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Recent Activity</div>
                        <p class="panel-subtitle">Key events from the current farm workspace.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        timeline_items = []
        if observation_count:
            timeline_items.append(("Observations", f"{observation_count} recent observation(s) logged in the farm workspace.", "neutral"))
        if dashboard.snapshots:
            timeline_items.append(("Twin snapshot", "Latest digital twin snapshot synced and ready for review.", "success"))
        if recommendation_items:
            timeline_items.append(("AI guidance", "Recommendations refreshed from the current herd context.", "success"))
        if not timeline_items:
            timeline_items.append(("Workspace ready", "No recent operational events have been logged yet.", "neutral"))

        for title, detail, tone in timeline_items[:4]:
            st.markdown(
                f"""
                <div class="timeline-item">
                    <div style='font-weight:700; color:#0f172a; margin-bottom:0.15rem;'>{title}</div>
                    <div style='color:#475569; line-height:1.5;'>{detail}</div>
                    <div class='chip {tone}'>{tone.replace('neutral', 'info').replace('success', 'success').replace('warning', 'warning')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Critical Alerts</div>
                        <p class="panel-subtitle">Highest priority issues to review today.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if alert_entries:
            for item in alert_entries[:3]:
                severity = str(item.get("severity") or "warning").lower()
                tone = "warning" if severity in {"medium", "warning"} else "danger" if severity in {"high", "critical"} else "info"
                title = str(item.get("category") or item.get("alert_type") or "Health alert")
                message = str(item.get("message") or item.get("description") or "Alert details available in the health system.")
                st.markdown(
                    f"""
                    <div class="alert-item {tone}">
                        <div style='font-weight:700; color:#0f172a; margin-bottom:0.2rem;'>{title}</div>
                        <div style='color:#475569; line-height:1.5;'>{message}</div>
                        <div class='chip {tone}'>{severity.upper()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            _render_empty_state("No critical alerts", "Everything is currently stable for your tracked herd.", "✅")

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel-card">
                <div class="panel-header">
                    <div>
                        <div class="panel-title">Quick Actions</div>
                        <p class="panel-subtitle">Common farm operations in one place.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_items = [
            ("Add Cow", "my_herd", "primary", "➕"),
            ("Record Observation", "daily_operations", "primary", "📝"),
            ("View Digital Twin", "digital_twin", "secondary", "🧠"),
            ("Open Analytics", "analytics", "secondary", "📊"),
        ]

        for label, section_key, button_type, icon in action_items:
            if button_type == "primary":
                if st.button(f"{icon} {label}", key=f"dashboard_action_{section_key}", use_container_width=True, type="primary"):
                    st.session_state.active_section = section_key
                    st.rerun()
            else:
                if st.button(f"{icon} {label}", key=f"dashboard_action_{section_key}", use_container_width=True, type="secondary"):
                    st.session_state.active_section = section_key
                    st.rerun()

    if st.session_state.get("dashboard_needs_refresh"):
        st.session_state["dashboard_needs_refresh"] = False
