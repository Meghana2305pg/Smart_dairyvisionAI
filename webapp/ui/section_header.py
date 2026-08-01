from __future__ import annotations

from html import escape

from plotly import graph_objects as go
import streamlit as st


def apply_app_theme() -> None:
    """Apply the shared enterprise dashboard theme."""
    st.markdown(
        """
        <style>
        :root {
            --dv-bg: #f5f7fb;
            --dv-surface: #ffffff;
            --dv-surface-2: #f8fafc;
            --dv-border: rgba(15, 23, 42, 0.08);
            --dv-border-strong: rgba(15, 23, 42, 0.14);
            --dv-text: #0f172a;
            --dv-muted: #64748b;
            --dv-muted-2: #94a3b8;
            --dv-accent: #2563eb;
            --dv-accent-strong: #1d4ed8;
            --dv-success: #15803d;
            --dv-warning: #b45309;
            --dv-danger: #b91c1c;
            --dv-radius-xl: 24px;
            --dv-radius-lg: 18px;
            --dv-radius-md: 14px;
            --dv-radius-sm: 10px;
            --dv-shadow-lg: 0 18px 50px rgba(15, 23, 42, 0.08);
            --dv-shadow-md: 0 12px 28px rgba(15, 23, 42, 0.06);
            --dv-shadow-sm: 0 4px 16px rgba(15, 23, 42, 0.04);
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 28%),
                radial-gradient(circle at top right, rgba(21, 128, 61, 0.08), transparent 22%),
                linear-gradient(180deg, #f8fafc 0%, #f5f7fb 48%, #eef2f7 100%);
            color: var(--dv-text);
            font-family: "Avenir Next", "Segoe UI Variable", "SF Pro Text", "Helvetica Neue", sans-serif;
        }

        .stApp {
            background: transparent;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none !important;
        }

        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] {
            background: transparent !important;
            min-width: 0 !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        section[data-testid="stSidebar"]:empty,
        section[data-testid="stSidebar"] > div:empty {
            display: none !important;
            width: 0 !important;
            min-width: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        section[data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border-right: 1px solid rgba(16, 185, 129, 0.12);
        }

        .block-container {
            width: 100% !important;
            max-width: 100% !important;
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: clamp(1rem, 1.8vw, 1.6rem) !important;
            padding-right: clamp(1rem, 1.8vw, 1.6rem) !important;
        }

        .main .block-container {
            min-height: calc(100vh - 2rem);
        }

        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: var(--dv-text);
            letter-spacing: -0.02em;
            font-family: "Avenir Next", "Segoe UI Variable", "SF Pro Display", "Helvetica Neue", sans-serif;
        }

        p, li, label, span, div {
            color: var(--dv-text);
        }

        .hero-card,
        .section-card,
        .metric-card,
        .dashboard-card,
        .recommendation-card,
        .alert-card,
        .timeline-item,
        .app-topbar {
            background: var(--dv-surface);
            border: 1px solid var(--dv-border);
            box-shadow: var(--dv-shadow-sm);
        }

        .hero-card {
            border-radius: var(--dv-radius-xl);
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: var(--dv-shadow-md);
            background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.94) 100%);
        }

        .section-card {
            border-radius: var(--dv-radius-lg);
            padding: 1rem 1.05rem;
            margin-bottom: 0.9rem;
        }

        .metric-card {
            border-radius: var(--dv-radius-lg);
            padding: 1rem 1.05rem;
            min-height: 132px;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            box-shadow: var(--dv-shadow-sm);
        }

        .dashboard-card,
        .recommendation-card,
        .alert-card {
            border-radius: var(--dv-radius-md);
            padding: 0.95rem 1rem;
            margin-bottom: 0.75rem;
        }

        .dashboard-card:hover,
        .recommendation-card:hover,
        .alert-card:hover,
        .metric-card:hover,
        .section-card:hover {
            border-color: var(--dv-border-strong);
            box-shadow: var(--dv-shadow-md);
        }

        .card-title,
        .metric-title,
        .section-heading,
        .app-section-label {
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--dv-muted);
            margin-bottom: 0.3rem;
        }

        .card-value,
        .metric-value {
            font-size: clamp(1.15rem, 1.6vw, 1.45rem);
            line-height: 1.1;
            font-weight: 750;
            color: var(--dv-text);
        }

        .card-caption,
        .metric-subtitle,
        .timeline-detail,
        .timeline-stamp,
        .hero-subtitle,
        .hero-caption {
            color: var(--dv-muted);
            font-size: 0.94rem;
            line-height: 1.45;
        }

        .section-heading {
            color: var(--dv-text);
            font-size: 0.92rem;
            margin: 0.65rem 0 0.55rem;
        }

        .timeline-item {
            border-radius: 16px;
            border-left: 4px solid rgba(37, 99, 235, 0.45);
            padding: 0.8rem 0.95rem;
            margin-bottom: 0.65rem;
        }

        .timeline-title {
            font-weight: 700;
            color: var(--dv-text);
            margin-bottom: 0.15rem;
        }

        .timeline-detail {
            margin-top: 0;
        }

        .timeline-stamp {
            margin-top: 0.2rem;
            font-size: 0.82rem;
        }

        .app-topbar {
            border-radius: var(--dv-radius-xl);
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--dv-shadow-md);
            position: sticky;
            top: 0.65rem;
            z-index: 30;
            backdrop-filter: blur(16px);
            background: rgba(255, 255, 255, 0.9);
        }

        .topbar-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .brand-mark {
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--dv-accent) 0%, #22c55e 100%);
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.25);
        }

        .brand-title {
            font-size: 1.02rem;
            font-weight: 750;
            color: var(--dv-text);
        }

        .brand-subtitle {
            font-size: 0.82rem;
            color: var(--dv-muted);
        }

        .topbar-actions {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .stSidebar .stButton > button,
        section[data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
        }

        .stSidebar .option-menu,
        section[data-testid="stSidebar"] .option-menu {
            width: 100% !important;
        }

        .topbar-pill,
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.84rem;
            font-weight: 650;
            line-height: 1;
            white-space: nowrap;
        }

        .topbar-pill {
            background: var(--dv-surface-2);
            color: var(--dv-text);
            border: 1px solid var(--dv-border);
        }

        .app-nav-card {
            background: rgba(15, 23, 42, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--dv-radius-xl);
            padding: 0.9rem;
            box-shadow: none;
        }

        .nav-action {
            border: 1px solid transparent;
            background: transparent;
            color: rgba(255, 255, 255, 0.82);
            border-radius: 12px;
            margin-bottom: 0.35rem;
            text-align: left;
            padding: 0.62rem 0.75rem;
        }

        .nav-action.active {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.12);
        }

        .metric-title {
            margin-bottom: 0.2rem;
        }

        .metric-subtitle {
            margin-top: 0;
        }

        .status-badge.success { background: rgba(21, 128, 61, 0.12); color: var(--dv-success); }
        .status-badge.warning { background: rgba(180, 83, 9, 0.12); color: var(--dv-warning); }
        .status-badge.danger { background: rgba(185, 28, 28, 0.12); color: var(--dv-danger); }

        .recommendation-card {
            border-left: 4px solid rgba(21, 128, 61, 0.55);
        }

        .alert-card {
            border-left: 4px solid rgba(185, 28, 28, 0.72);
        }

        .alert-card.alert-warning {
            border-left-color: rgba(180, 83, 9, 0.72);
        }

        .alert-card.alert-info {
            border-left-color: rgba(37, 99, 235, 0.72);
        }

        .app-shell-grid {
            display: grid;
            grid-template-columns: minmax(260px, 300px) minmax(0, 1fr);
            gap: 1rem;
            align-items: start;
        }

        .shell-sidebar {
            position: sticky;
            top: 5.4rem;
            align-self: start;
        }

        .shell-main {
            min-width: 0;
        }

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            border-radius: 12px !important;
            border: 1px solid rgba(37, 99, 235, 0.18) !important;
            background: linear-gradient(180deg, var(--dv-accent) 0%, var(--dv-accent-strong) 100%) !important;
            color: white !important;
            font-weight: 650 !important;
            padding: 0.6rem 0.95rem !important;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.15);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: rgba(37, 99, 235, 0.28) !important;
            filter: brightness(0.97);
        }

        .stButton > button:focus-visible,
        .stDownloadButton > button:focus-visible,
        .stFormSubmitButton > button:focus-visible,
        input:focus-visible,
        textarea:focus-visible,
        div[data-baseweb="select"] *:focus-visible {
            outline: 2px solid rgba(37, 99, 235, 0.3) !important;
            outline-offset: 2px;
        }

        .stForm {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid var(--dv-border);
            border-radius: var(--dv-radius-lg);
            padding: 1rem;
            box-shadow: var(--dv-shadow-sm);
        }

        .stForm label,
        .stTextInput label,
        .stNumberInput label,
        .stTextArea label,
        .stSelectbox label,
        .stMultiSelect label,
        .stDateInput label,
        .stRadio label,
        .stCheckbox label {
            color: #111827 !important;
            font-weight: 600 !important;
        }

        input,
        textarea,
        [contenteditable="true"],
        div[data-baseweb="select"] input {
            color: #111827 !important;
            caret-color: #111827 !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }

        input,
        textarea,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"],
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            color: #111827 !important;
            border-color: #d1d5db !important;
        }

        input:focus,
        textarea:focus,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="base-input"]:focus-within,
        div[data-baseweb="input"]:focus-within {
            border-color: var(--dv-accent) !important;
            box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.14) !important;
        }

        input:invalid,
        textarea:invalid {
            border-color: #dc2626 !important;
        }

        input:valid,
        textarea:valid {
            border-color: #16a34a !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        div[data-baseweb="select"] input {
            color: #111827 !important;
        }

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stDateInput input {
            border-radius: 12px !important;
            border-color: #d1d5db !important;
            background: #ffffff !important;
            color: #111827 !important;
            min-height: 2.7rem;
        }

        .stTextInput input::placeholder,
        .stNumberInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #6b7280 !important;
        }

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stDateInput input {
            border-radius: 12px !important;
            border-color: var(--dv-border-strong) !important;
            background: rgba(255, 255, 255, 0.92) !important;
            color: #111827 !important;
            min-height: 2.7rem;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"],
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDeckGlJsonChart"] {
            border-radius: var(--dv-radius-md);
            overflow: hidden;
        }

        div[data-testid="stDataFrame"] table {
            border-collapse: separate !important;
            border-spacing: 0;
        }

        .stAlert {
            border-radius: var(--dv-radius-md) !important;
            border: 1px solid var(--dv-border) !important;
            box-shadow: var(--dv-shadow-sm);
        }

        hr {
            border-color: rgba(148, 163, 184, 0.2);
            margin: 1.1rem 0;
        }

        @media (max-width: 900px) {
            .app-shell-grid {
                grid-template-columns: 1fr;
            }

            .shell-sidebar {
                position: static;
            }

            .app-topbar {
                top: 0.35rem;
            }

            .block-container {
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
            }
        }

        @media (max-width: 640px) {
            .topbar-actions {
                justify-content: flex-start;
            }

            .hero-card,
            .section-card,
            .metric-card,
            .dashboard-card,
            .recommendation-card,
            .alert-card {
                padding: 0.9rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, badge: str | None = None, caption: str | None = None) -> None:
    """Render a polished reusable page header."""
    badge_html = (
        f"<div class='status-badge success' style='margin-bottom:0.6rem;'>{escape(badge)}</div>"
        if badge
        else ""
    )
    caption_html = f"<div class='hero-caption' style='margin-top:0.35rem;'>{escape(caption)}</div>" if caption else ""
    st.markdown(
        f"""
        <div class="hero-card">
          <div>{badge_html}</div>
          <h2 style="margin:0 0 0.25rem 0;">{escape(title)}</h2>
          <div class="hero-subtitle">{escape(subtitle)}</div>
          {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    """Render a standardized header for longer content sections."""
    st.markdown(f"<div class='section-heading'>{escape(title)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card-caption'>{escape(subtitle)}</div>", unsafe_allow_html=True)


def metric_card(title: str, value: str, subtitle: str, status: str | None = None) -> None:
    """Render a compact KPI card with a clear value and supporting context."""
    status_html = f"<div class='status-badge success'>{escape(status)}</div>" if status else ""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-title">{escape(title)}</div>
          <div class="metric-value">{escape(value)}</div>
          <div class="metric-subtitle">{escape(subtitle)}</div>
          {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, tone: str = "success") -> None:
    """Render a small status indicator."""
    safe_tone = tone if tone in {"success", "warning", "danger"} else "success"
    st.markdown(f"<span class='status-badge {safe_tone}'>{escape(label)}</span>", unsafe_allow_html=True)


def recommendation_panel(title: str, recommendation: str, improvement: str | None = None) -> None:
    """Render a concise recommendation block for operational pages."""
    gain_html = f"<div style='margin-top:0.45rem;color:var(--dv-text);'><strong>Expected improvement</strong> {escape(improvement)}</div>" if improvement else ""
    st.markdown(
        f"""
        <div class="recommendation-card">
          <div class="metric-title" style="color:var(--dv-success);">{escape(title)}</div>
          <div style="margin-top:0.35rem;color:var(--dv-text);font-weight:650;">{escape(recommendation)}</div>
          {gain_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def warning_banner(text: str) -> None:
    """Render a modest informational banner."""
    st.markdown(
        f"""
                <div class="section-card" style="border-color:rgba(148, 163, 184, 0.24);background:rgba(248, 250, 252, 0.92);">
                    <div style="color:var(--dv-text);">{escape(text)}</div>
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
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="#ffffff")
    return fig
