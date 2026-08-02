"""Reusable Polaris dashboard UI components for the executive dashboard."""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def render_dashboard_panel(title: str, subtitle: str = "", icon: str = "", badge: str | None = None, tone: str = "neutral") -> None:
    """Render a polished card shell for dashboard sections."""
    badge_html = f"<span class='status-badge {tone}' style='margin-left:0.5rem;'>{escape(badge)}</span>" if badge else ""
    icon_html = f"<span style='font-size:1rem;margin-right:0.4rem;'>{escape(icon)}</span>" if icon else ""
    subtitle_html = f"<div style='margin-top:0.25rem;font-size:0.9rem;color:var(--dv-muted);'>{escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:0.9rem; background:linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:0.75rem;flex-wrap:wrap;">
                <div style="display:flex;align-items:center;gap:0.45rem;">
                    {icon_html}
                    <div style="font-size:1rem;font-weight:700;color:var(--dv-text);">{escape(title)}</div>
                </div>
                {badge_html}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_polaris_metric_card(title: str, value: str, subtitle: str = "", icon: str = "", tone: str = "neutral") -> None:
    """Render a premium KPI card aligned with Polaris styling."""
    tone_class = tone if tone in {"success", "warning", "danger", "info", "neutral"} else "neutral"
    st.markdown(
        f"""
        <div class="metric-card" style="padding:1rem 1.05rem; min-height: 138px; background:linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.96));">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                <div style="font-size:0.78rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(title)}</div>
                <div style="font-size:1.15rem;line-height:1;">{escape(icon)}</div>
            </div>
            <div style="margin-top:0.25rem;">
                <div style="font-size:clamp(1.35rem, 1.8vw, 1.8rem);font-weight:800;letter-spacing:-0.03em;color:var(--dv-text);">{escape(value)}</div>
                <div style="margin-top:0.35rem;font-size:0.88rem;color:var(--dv-muted);">{escape(subtitle)}</div>
            </div>
            <span class='status-badge {tone_class}' style='margin-top:0.25rem;'>{tone_class.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_polaris_weather_card(temperature: Any, humidity: Any, condition: str = "Stable", risk: str = "Low") -> None:
    """Render a weather and environment snapshot card."""
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; background:linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(240,249,255,0.95) 100%);">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.8rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-accent);">Weather & Environment</div>
                    <div style="margin-top:0.3rem;font-size:1.25rem;font-weight:800;color:var(--dv-text);">{escape(str(temperature))}°C / {escape(str(humidity))}%</div>
                </div>
                <span class='status-badge info'>{escape(condition)}</span>
            </div>
            <div style="margin-top:0.75rem;padding:0.8rem 0.9rem;border-radius:14px;background:rgba(255,255,255,0.9);border:1px solid var(--dv-border);">
                <div style="font-size:0.88rem;color:var(--dv-muted);">Operational risk outlook</div>
                <div style="margin-top:0.3rem;font-size:1rem;font-weight:700;color:var(--dv-text);">{escape(risk)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_polaris_bar_chart(title: str, subtitle: str, items: list[dict[str, Any]], accent: str = "#2563eb") -> None:
    """Render a compact performance bar chart using existing metric values."""
    if not items:
        return
    max_value = max(float(item.get("value", 0)) for item in items)
    bars = []
    for item in items:
        value = float(item.get("value", 0))
        height = max(8, int((value / max_value) * 100)) if max_value else 0
        bars.append(
            f"""
            <div style="flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;gap:0.35rem;">
                <div style="width:100%;height:84px;border-radius:12px;background:linear-gradient(180deg, rgba(226,232,240,0.35), rgba(226,232,240,0.8));display:flex;align-items:flex-end;padding:0.28rem;box-sizing:border-box;">
                    <div style="width:100%;height:{height}%;border-radius:10px;background:linear-gradient(180deg, {accent}, rgba(37,99,235,0.7));"></div>
                </div>
                <div style="font-size:0.74rem;color:var(--dv-muted);text-align:center;">{escape(str(item.get('label','')))}</div>
            </div>
            """
        )
    bars_html = "".join(bars)
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:0.9rem; background:linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));">
            <div style="font-size:0.8rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-accent);">{escape(title)}</div>
            <div style="margin-top:0.2rem;font-size:0.88rem;color:var(--dv-muted);">{escape(subtitle)}</div>
            <div style="margin-top:0.85rem;display:flex;align-items:flex-end;gap:0.65rem;">
                {bars_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
