"""Reusable card components for the dashboard."""
from __future__ import annotations

from html import escape

import streamlit as st


def metric_card(
    icon: str,
    title: str,
    value: str,
    subtitle: str = "",
    status: str | None = None,
) -> None:
    """Render a professional metric card."""
    status_html = f"<div class='status-badge success' style='margin-top:0.45rem;'>{escape(status)}</div>" if status else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:0.75rem;margin-bottom:0.15rem;'>
                <div style='font-size:1.5rem;line-height:1;'>{escape(icon)}</div>
            </div>
            <div class="metric-title">{escape(title)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-subtitle">{escape(subtitle)}</div>
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(
    title: str,
    content: str,
    footer: str = "",
) -> None:
    """Render an info card with title and content."""
    footer_html = f"<div class='card-caption' style='margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid rgba(148, 163, 184, 0.16);'>{escape(footer)}</div>" if footer else ""

    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="card-title">{escape(title)}</div>
            <div style='font-size:0.96rem;color:var(--dv-text);line-height:1.55;'>{escape(content)}</div>
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(
    title: str,
    message: str,
    severity: str = "warning",
    timestamp: str = "",
) -> None:
    """Render an alert card."""
    severity_colors = {
        "info": ("#0ea5e9", "#eff8ff"),
        "warning": ("#f59e0b", "#fff8ea"),
        "danger": ("#ef4444", "#fff1f2"),
    }
    color, bg_color = severity_colors.get(severity, severity_colors["info"])
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "danger": "🚨",
    }
    icon = icons.get(severity, "ℹ️")

    timestamp_html = f"<div class='timeline-stamp' style='margin-top:0.45rem;'>{escape(timestamp)}</div>" if timestamp else ""

    st.markdown(
        f"""
        <div class="alert-card alert-{severity}" style='border-left-color:{color};background:{bg_color};'>
            <div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem;'>
                <span style='font-size:1rem;line-height:1;'>{escape(icon)}</span>
                <div class='card-title' style='margin-bottom:0;'>{escape(title)}</div>
            </div>
            <div class='card-caption' style='color:var(--dv-text);'>{escape(message)}</div>
            {timestamp_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_card(
    title: str,
    description: str,
    icon: str = "💡",
) -> None:
    """Render a recommendation card."""
    st.markdown(
        f"""
        <div class="recommendation-card">
            <div style='display:flex;align-items:flex-start;gap:0.8rem;'>
                <div style='font-size:1.1rem;line-height:1;'>{escape(icon)}</div>
                <div style='flex:1;min-width:0;'>
                    <div class='card-title' style='margin-bottom:0.3rem;color:var(--dv-success);'>{escape(title)}</div>
                    <div class='card-caption' style='line-height:1.45;'>{escape(description)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
