from __future__ import annotations

import streamlit as st
from plotly import graph_objects as go


def apply_app_theme() -> None:
    """Apply a minimal enterprise-style theme to the Streamlit experience."""
    st.markdown(
        """
        <style>
        /* CRITICAL: Completely hide Streamlit's native sidebar and multipage navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stSidebarContent"] {
            display: none !important;
        }
        .st-emotion-cache-uf99v0 {
            display: none !important;
        }
        /* Hide the pages sidebar area entirely */
        .stApp > div:nth-child(1) > div:nth-child(1) {
            display: none !important;
        }
        /* Adjust main content to use full width without sidebar */
        .stApp {
            background: #f4f7fb;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 100% !important;
            width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .hero-card {
            background: linear-gradient(135deg, #ffffff 0%, #f5f9ff 100%);
            border: 1px solid #dfe8f3;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }
        .section-card {
            background: #fbfcfe;
            border: 1px solid #e6edf5;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid #e7ece6;
            border-radius: 10px;
            padding: 0.85rem 0.95rem;
            min-height: 118px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .dashboard-card {
            background: #ffffff;
            border: 1px solid #e5ebf2;
            border-radius: 12px;
            padding: 0.9rem 0.95rem;
            margin-bottom: 0.7rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.03);
        }
        .card-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.3rem;
        }
        .card-value {
            font-size: 1.16rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .card-caption {
            font-size: 0.92rem;
            color: #475569;
        }
        .section-heading {
            font-size: 0.96rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0.8rem 0 0.5rem 0;
        }
        .timeline-item {
            border-left: 2px solid #dbeafe;
            padding: 0.45rem 0 0.45rem 0.8rem;
            margin-bottom: 0.55rem;
        }
        .timeline-title {
            font-weight: 700;
            color: #0f172a;
        }
        .timeline-detail {
            color: #475569;
            font-size: 0.94rem;
            margin-top: 0.18rem;
        }
        .timeline-stamp {
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 0.18rem;
        }
        .app-topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.65rem 0.9rem;
            background: #ffffff;
            border: 1px solid #e5ebf2;
            border-radius: 14px;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }
        .topbar-brand {
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }
        .brand-mark {
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #2f7d32, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1rem;
        }
        .brand-title {
            font-size: 1rem;
            font-weight: 700;
            color: #0f172a;
        }
        .brand-subtitle {
            font-size: 0.8rem;
            color: #64748b;
        }
        .topbar-actions {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
        }
        .topbar-pill {
            background: #f8fafc;
            border: 1px solid #e5ebf2;
            border-radius: 999px;
            padding: 0.35rem 0.6rem;
            color: #334155;
            font-size: 0.84rem;
        }
        .app-nav-card {
            background: #ffffff;
            border: 1px solid #e5ebf2;
            border-radius: 16px;
            padding: 0.7rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }
        .nav-action {
            border: 1px solid transparent;
            background: transparent;
            color: #334155;
            border-radius: 10px;
            margin-bottom: 0.35rem;
            text-align: left;
            padding: 0.55rem 0.65rem;
        }
        .nav-action.active {
            background: #eff6ff;
            color: #1d4ed8;
            border-color: #bfdbfe;
        }
        .metric-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.28rem;
        }
        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .metric-subtitle {
            font-size: 0.9rem;
            color: #475569;
        }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            margin-top: 0.45rem;
        }
        .sidebar .block-container {
            padding-top: 0.7rem;
        }
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #2f7d32;
            background: #2f7d32;
            color: white;
        }
        .stButton > button:hover {
            border-color: #1b5e20;
            background: #27682b;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, badge: str | None = None, caption: str | None = None) -> None:
    """Render a polished reusable page header."""
    badge_html = (
        f"<div style='display:inline-block;padding:0.26rem 0.7rem;border-radius:999px;background:#2f7d32;color:white;font-size:0.78rem;font-weight:700;margin-bottom:0.6rem;'>{badge}</div>"
        if badge
        else ""
    )
    caption_html = f"<div style='color:#475569; margin-top:0.3rem;'>{caption}</div>" if caption else ""
    st.markdown(
        f"""
        <div class="hero-card">
          <div>{badge_html}</div>
          <h2 style="margin:0 0 0.25rem 0; color:#0f172a;">{title}</h2>
          <div style="color:#475569; font-size:1rem;">{subtitle}</div>
          {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    """Render a standardized header for longer content sections."""
    st.subheader(title)
    st.caption(subtitle)


def metric_card(title: str, value: str, subtitle: str, status: str | None = None) -> None:
    """Render a compact KPI card with a clear value and supporting context."""
    status_html = f"<div class='status-badge' style='background:#ecfdf3;color:#166534;'>{status}</div>" if status else ""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-title">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-subtitle">{subtitle}</div>
          {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, tone: str = "success") -> None:
    """Render a small status indicator."""
    colors = {
        "success": ("#ecfdf3", "#166534"),
        "warning": ("#fffbeb", "#92400e"),
        "danger": ("#fef2f2", "#991b1b"),
    }
    bg, color = colors.get(tone, colors["success"])
    st.markdown(f"<span class='status-badge' style='background:{bg};color:{color};'>{label}</span>", unsafe_allow_html=True)


def recommendation_panel(title: str, recommendation: str, improvement: str | None = None) -> None:
    """Render a concise recommendation block for operational pages."""
    gain_html = f"<div style='margin-top:0.45rem;color:#0f172a;'><strong>Expected improvement</strong> {improvement}</div>" if improvement else ""
    st.markdown(
        f"""
        <div class="section-card">
          <div style="font-size:0.82rem;font-weight:700;color:#2f7d32;text-transform:uppercase;letter-spacing:0.04em;">{title}</div>
          <div style="margin-top:0.35rem;color:#0f172a;font-weight:600;">{recommendation}</div>
          {gain_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def warning_banner(text: str) -> None:
    """Render a modest informational banner."""
    st.markdown(
        f"""
        <div class="section-card" style="border-color:#cbd5e1;background:#f8fafc;">
          <div style="color:#334155;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Keep the legacy helper as a no-op so the custom shell remains the only navigation surface."""
    return


def gauge_chart(value: float, title: str, target: float | None = None) -> go.Figure:
    """Create a compact gauge figure for key operational values."""
    max_value = target if target is not None else max(100.0, value * 1.35)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            gauge={
                "axis": {"range": [None, max_value]},
                "bar": {"color": "#2f7d32"},
                "steps": [
                    {"range": [0, max_value * 0.6], "color": "#f1f5f9"},
                    {"range": [max_value * 0.6, max_value * 0.85], "color": "#e2e8f0"},
                    {"range": [max_value * 0.85, max_value], "color": "#cbd5e1"},
                ],
            },
        )
    )
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig
