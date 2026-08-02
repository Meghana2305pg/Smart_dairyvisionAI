"""Legacy UI header primitives delegating to the centralized design system."""

from __future__ import annotations

from html import escape

from plotly import graph_objects as go
import streamlit as st

from webapp.ui.design_system import (
    apply_global_theme as _apply_global_theme,
    render_metric_card as _ds_render_metric_card,
    render_page_header as _ds_render_page_header,
    render_section_title as _ds_render_section_title,
    render_status_badge as _ds_render_status_badge,
)


def apply_app_theme() -> None:
    """Apply the shared enterprise dashboard theme."""
    _apply_global_theme()


def render_page_header(title: str, subtitle: str, badge: str | None = None, caption: str | None = None) -> None:
    """Render a polished reusable page header using the centralized design system."""
    _ds_render_page_header(title=title, subtitle=subtitle, badge=badge or caption or "")


def render_section_header(title: str, subtitle: str) -> None:
    """Render a standardized header for longer content sections using the centralized design system."""
    _ds_render_section_title(title=title, subtitle=subtitle)


def metric_card(title: str, value: str, subtitle: str, status: str | None = None) -> None:
    """Render a compact KPI card using the centralized design system."""
    _ds_render_metric_card(title=title, value=value, subtitle=subtitle, status=status)


def status_badge(label: str, tone: str = "success") -> None:
    """Render a small status indicator using the centralized design system."""
    _ds_render_status_badge(label=label, status_type=tone)


def recommendation_panel(title: str, recommendation: str, improvement: str | None = None) -> None:
    """Render a concise recommendation block for operational pages."""
    gain_html = f"<div style='margin-top:0.45rem;color:var(--dv-text);'><strong>Expected improvement</strong> {escape(improvement)}</div>" if improvement else ""
    st.markdown(
        f"""
        <div class="recommendation-card" style="padding:1rem;margin-bottom:0.75rem;">
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
        <div class="section-card" style="border-color:var(--dv-border-strong);background:var(--dv-surface-alt);padding:1rem;">
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
                "bar": {"color": "#15803d"},
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
