"""Health alerts screen."""
from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from webapp.ui.section_header import render_page_header, render_section_header


def _normalise_severity(value: Any) -> str:
    if value is None:
        return "Healthy"
    text = str(value).strip().lower()
    if text in {"critical", "alert risk", "danger"}:
        return "Critical"
    if text in {"warning", "high", "medium", "alert"}:
        return "Warning"
    return "Healthy"


def _severity_badge_class(value: Any) -> str:
    severity = _normalise_severity(value)
    if severity == "Critical":
        return "critical"
    if severity == "Warning":
        return "warning"
    return "healthy"


def _normalise_cow_records(cow_records: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not cow_records:
        return []
    normalised: list[dict[str, Any]] = []
    for item in cow_records:
        if not isinstance(item, dict):
            continue
        payload = item.get("cow", item) if isinstance(item.get("cow"), dict) else item
        normalised.append(payload)
    return normalised


def _build_alert_rows() -> list[dict[str, Any]]:
    if "cow_service" not in st.session_state:
        return []

    cow_service = st.session_state.cow_service
    dashboard_service = st.session_state.get("dashboard_service")
    cow_records = _normalise_cow_records(cow_service.get_cows())
    dashboard = dashboard_service.build_dashboard() if dashboard_service else None
    health_rows = dashboard.health if dashboard else []

    cow_map: dict[str, dict[str, Any]] = {}
    for cow in cow_records:
        cow_id = str(cow.get("cow_id") or "").strip()
        if cow_id:
            cow_map[cow_id] = cow

    rows: list[dict[str, Any]] = []
    for alert in health_rows:
        cow_id = str(alert.get("cow_id") or "").strip()
        cow = cow_map.get(cow_id, {})
        severity = _normalise_severity(alert.get("severity") or alert.get("alert_category"))
        alert_type = str(alert.get("alert_category") or alert.get("stress_category") or "Health Alert")
        description = str(alert.get("recommendation") or "Review herd conditions and monitor the cow closely.")
        timestamp_raw = alert.get("timestamp")
        if timestamp_raw is None:
            timestamp_raw = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        timestamp = pd.to_datetime(timestamp_raw, errors="coerce")
        rows.append({
            "cow_id": cow_id,
            "cow_name": cow.get("name") or f"Cow {cow_id}",
            "severity": severity,
            "alert_type": alert_type,
            "timestamp": timestamp if pd.notna(timestamp) else pd.Timestamp.utcnow(),
            "description": description,
            "status": "Reviewed" if cow_id in st.session_state.get("reviewed_health_alerts", set()) else "Open",
        })
    return rows


def render_health() -> None:
    """Render the health alerts screen based on the project’s live dashboard data."""
    st.markdown(
        """
        <style>
        .health-toolbar {
            background: rgba(255,255,255,0.95);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 22px rgba(15,23,42,0.04);
            margin: 1rem 0 1.2rem;
        }
        .health-overview-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-bottom: 1.25rem;
        }
        .health-alert-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 20px rgba(15,23,42,0.04);
            margin-bottom: 0.9rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .health-alert-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 28px rgba(15,23,42,0.08);
        }
        .health-alert-card.critical { border-left: 5px solid #dc2626; }
        .health-alert-card.warning { border-left: 5px solid #f59e0b; }
        .health-alert-card.healthy { border-left: 5px solid #16a34a; }
        .health-alert-head {
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 0.55rem;
        }
        .severity-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .severity-pill.critical { background: rgba(220,38,38,0.1); color: #b91c1c; }
        .severity-pill.warning { background: rgba(245,158,11,0.12); color: #b45309; }
        .severity-pill.healthy { background: rgba(22,163,74,0.12); color: #15803d; }
        .health-alert-name {
            font-size: 1.1rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
        }
        .health-alert-meta {
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 0.2rem;
        }
        .health-alert-desc {
            color: #334155;
            line-height: 1.5;
            margin: 0.8rem 0;
        }
        .health-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.65rem;
        }
        .health-empty {
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 18px;
            padding: 1.2rem;
            box-shadow: 0 10px 20px rgba(15,23,42,0.04);
            text-align: center;
            color: #475569;
        }
        @media (max-width: 980px) {
            .health-overview-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 620px) {
            .health-overview-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_page_header(
        "Health Alerts",
        "Monitor the health status of your herd and respond to critical events.",
        badge="Monitoring",
    )

    alerts = _build_alert_rows()
    total_alerts = len(alerts)
    critical_alerts = sum(1 for alert in alerts if alert["severity"] == "Critical")
    warning_alerts = sum(1 for alert in alerts if alert["severity"] == "Warning")
    healthy_cows = sum(1 for alert in alerts if alert["severity"] == "Healthy")

    st.markdown('<div class="health-overview-grid">', unsafe_allow_html=True)
    summary_cards = [
        ("Total Alerts", total_alerts),
        ("Critical Alerts", critical_alerts),
        ("Warning Alerts", warning_alerts),
        ("Healthy Cows", healthy_cows),
    ]
    for label, value in summary_cards:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="card-title">{label}</div>
                <div style="font-size: clamp(1.5rem, 2vw, 2rem); font-weight: 800; letter-spacing: -0.05em; color: #0f172a;">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="health-toolbar">', unsafe_allow_html=True)
    with st.container():
        filter_cols = st.columns([1.2, 1.2, 1.1, 1.1, 2.2])
        with filter_cols[0]:
            severity_filter = st.selectbox("Severity", ["All", "Critical", "Warning", "Healthy"], index=0)
        with filter_cols[1]:
            cow_options = ["All", *sorted({alert["cow_name"] for alert in alerts})]
            selected_cow = st.selectbox("Cow", cow_options, index=0)
        with filter_cols[2]:
            selected_date = st.date_input("Date", value=None)
        with filter_cols[3]:
            status_filter = st.selectbox("Status", ["All", "Open", "Reviewed"], index=0)
        with filter_cols[4]:
            search_text = st.text_input("Search", placeholder="Cow or alert type")
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_alerts = []
    for alert in alerts:
        severity_match = severity_filter == "All" or alert["severity"] == severity_filter
        cow_match = selected_cow == "All" or alert["cow_name"] == selected_cow
        date_match = selected_date is None or pd.Timestamp(alert["timestamp"]).date() == pd.Timestamp(selected_date).date()
        status_match = status_filter == "All" or alert["status"] == status_filter
        search_match = not search_text or search_text.lower() in alert["cow_name"].lower() or search_text.lower() in alert["alert_type"].lower() or search_text.lower() in alert["description"].lower()
        if severity_match and cow_match and date_match and status_match and search_match:
            filtered_alerts.append(alert)

    render_section_header("Recent Alerts", "The latest health alerts requiring attention.")

    if not filtered_alerts:
        st.markdown(
            """
            <div class="health-empty">
                <div style="font-size: 2.4rem; margin-bottom: 0.5rem;">📋</div>
                <h4 style="margin: 0 0 0.4rem; color: #0f172a;">No alerts match the current filters</h4>
                <div>Use a different filter combination, or record a fresh observation to refresh the health workspace.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for idx, alert in enumerate(filtered_alerts):
        severity_class = _severity_badge_class(alert["severity"])
        st.markdown(
            f"""
            <div class="health-alert-card {severity_class}">
                <div class="health-alert-head">
                    <div>
                        <p class="health-alert-name">{escape(alert['cow_name'])}</p>
                        <div class="health-alert-meta">Cow ID: {escape(alert['cow_id'])}</div>
                    </div>
                    <div class="severity-pill {severity_class}">{escape(alert['severity'])}</div>
                </div>
                <div class="health-alert-meta">Alert Type: {escape(alert['alert_type'])} • {escape(alert['timestamp'].strftime('%Y-%m-%d %H:%M'))}</div>
                <div class="health-alert-desc">{escape(alert['description'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_cols = st.columns([1, 1, 1, 1.1], gap="small")
        with action_cols[0]:
            if st.button("View Cow Profile", key=f"view_profile_{idx}", use_container_width=True):
                st.session_state.selected_cow_id = alert["cow_id"]
                st.session_state.active_section = "cow_profile"
                st.rerun()
        with action_cols[1]:
            if st.button("Record Observation", key=f"record_obs_{idx}", use_container_width=True):
                st.session_state.selected_cow_id = alert["cow_id"]
                st.session_state.daily_ops_cow = alert["cow_id"]
                st.session_state.active_section = "daily_operations"
                st.rerun()
        with action_cols[2]:
            if st.button("Open Digital Twin", key=f"open_twin_{idx}", use_container_width=True):
                st.session_state.selected_cow_id = alert["cow_id"]
                st.session_state.active_section = "digital_twin"
                st.rerun()
        with action_cols[3]:
            reviewed_id = f"alert_{alert['cow_id']}_{idx}"
            if st.button("Reviewed" if alert["status"] == "Reviewed" else "Mark as Reviewed", key=f"toggle_review_{reviewed_id}", use_container_width=True):
                reviewed = set(st.session_state.get("reviewed_health_alerts", set()))
                if reviewed_id in reviewed:
                    reviewed.remove(reviewed_id)
                else:
                    reviewed.add(reviewed_id)
                st.session_state.reviewed_health_alerts = reviewed
                st.rerun()
