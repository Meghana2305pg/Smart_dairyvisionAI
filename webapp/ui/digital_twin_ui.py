"""Reusable Polaris-inspired UI components for the Digital Twin screen."""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st


def render_digital_twin_hero(cow_name: str, breed: str, age: str, farm: str, twin_status: str, last_updated: str, weather: str = "", weather_tone: str = "info") -> None:
    """Render a premium hero section for the Digital Twin workspace."""
    st.markdown(
        f"""
        <div class="hero-card" style="padding:1.2rem 1.25rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96)); border:1px solid var(--dv-border); border-radius:22px; box-shadow:var(--dv-shadow-md);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;">
                <div style="flex:1;min-width:240px;">
                    <div style="font-size:0.74rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">Digital Twin · Premium Operations View</div>
                    <h1 style="font-size:clamp(1.75rem, 2.3vw, 2.45rem);font-weight:800;letter-spacing:-0.03em;color:var(--dv-text);margin:0.2rem 0 0.35rem;">{escape(cow_name)}</h1>
                    <div style="font-size:0.94rem;color:var(--dv-muted);line-height:1.55;">{escape(breed)} · {escape(age)} · {escape(farm)}</div>
                </div>
                <div style="display:flex;flex-direction:column;gap:0.45rem;align-items:flex-start;min-width:220px;">
                    <span class='status-badge success' style='padding:0.35rem 0.7rem;'>{escape(twin_status)}</span>
                    <div style="font-size:0.82rem;color:var(--dv-muted);">Last updated · {escape(last_updated)}</div>
                    <span class='status-badge {weather_tone}' style='padding:0.32rem 0.65rem;'>{escape(weather)}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, subtitle: str = "", tone: str = "neutral", icon: str = "●") -> None:
    """Render a polished KPI card with icon, value, subtitle, and status chip."""
    st.markdown(
        f"""
        <div class="metric-card" style="padding:1rem 1.05rem; min-height:132px; background:linear-gradient(135deg, rgba(255,255,255,0.99), rgba(248,250,252,0.95));">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
                <div style="font-size:0.74rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(title)}</div>
                <div style="font-size:1rem;line-height:1;">{escape(icon)}</div>
            </div>
            <div style="margin-top:0.25rem;font-size:clamp(1.15rem, 1.7vw, 1.65rem);font-weight:800;letter-spacing:-0.03em;color:var(--dv-text);">{escape(value)}</div>
            <div style="margin-top:0.35rem;font-size:0.84rem;color:var(--dv-muted);">{escape(subtitle)}</div>
            <span class='status-badge {tone}' style='margin-top:0.3rem;'>{tone.upper()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(cards: list[dict[str, str]]) -> None:
    """Render a single responsive KPI row using the Polaris card pattern."""
    if not cards:
        return
    cards_html = "".join(
        f"""
        <div style="border:1px solid var(--dv-border); border-radius:16px; padding:0.95rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); box-shadow:var(--dv-shadow-sm); min-height:132px;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
                <div style="font-size:0.72rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(card.get('title', 'Metric'))}</div>
                <div style="font-size:1rem;line-height:1;">{escape(card.get('icon', '●'))}</div>
            </div>
            <div style="margin-top:0.3rem;font-size:clamp(1.15rem, 1.7vw, 1.65rem);font-weight:800;letter-spacing:-0.03em;color:var(--dv-text);">{escape(card.get('value', 'n/a'))}</div>
            <div style="margin-top:0.3rem;font-size:0.84rem;color:var(--dv-muted);">{escape(card.get('subtitle', ''))}</div>
            <span class='status-badge {card.get("tone", "neutral")}' style='margin-top:0.35rem;'>{str(card.get('tone', 'neutral')).upper()}</span>
        </div>
        """
        for card in cards
    )
    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;margin-bottom:1rem;">{cards_html}</div>
        """,
        unsafe_allow_html=True,
    )


def render_status_panel(title: str, items: list[tuple[str, str, str, str]]) -> None:
    """Render a current-status panel using compact metadata cards."""
    if not items:
        return
    items_html = "".join(
        f"""
        <div style="border:1px solid var(--dv-border); border-radius:14px; padding:0.8rem; background:rgba(255,255,255,0.96); box-shadow:var(--dv-shadow-sm);">
            <div style="display:flex;align-items:center;gap:0.45rem;">
                <div style="font-size:1rem;line-height:1;">{escape(icon)}</div>
                <div style="font-size:0.72rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(label)}</div>
            </div>
            <div style="margin-top:0.35rem;font-size:1rem;font-weight:700;color:var(--dv-text);">{escape(value)}</div>
            <div style="margin-top:0.2rem;font-size:0.8rem;color:var(--dv-muted);">{escape(description)}</div>
        </div>
        """
        for label, value, description, icon in items
    )
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);margin-bottom:0.8rem;">{escape(title)}</div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.7rem;">{items_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_horizontal_timeline(events: list[dict[str, Any]]) -> None:
    """Render a polished horizontal timeline component using the existing twin timeline items."""
    if not events:
        return
    cards = []
    for event in events[-5:]:
        cards.append(
            f"""
            <div style="border:1px solid var(--dv-border);border-radius:16px;padding:0.8rem;background:rgba(255,255,255,0.96);box-shadow:var(--dv-shadow-sm);">
                <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(str(event.get('timestamp', 'n/a')))}</div>
                <div style="margin-top:0.35rem;font-size:0.92rem;font-weight:700;color:var(--dv-text);">{escape(str(event.get('notes', 'Observation')))}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.8rem;">
                <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">Twin Timeline</div>
                <div style="font-size:0.8rem;color:var(--dv-muted);">Recent state changes</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.7rem;">{''.join(cards)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_snapshot_cards(events: list[dict[str, Any]]) -> None:
    """Render recent snapshots as premium explorer cards with health, prediction, and status."""
    if not events:
        return
    cards = []
    for event in events[-4:]:
        cards.append(
            f"""
            <div style="border:1px solid var(--dv-border);border-radius:16px;padding:0.9rem;background:rgba(255,255,255,0.96);box-shadow:var(--dv-shadow-sm);">
                <div style="font-size:0.7rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">{escape(str(event.get('timestamp','n/a')))}</div>
                <div style="margin-top:0.3rem;font-size:0.95rem;font-weight:700;color:var(--dv-text);">{escape(str(event.get('health','Stable')))}</div>
                <div style="margin-top:0.25rem;font-size:0.84rem;color:var(--dv-muted);">Prediction · {escape(str(event.get('prediction','n/a')))}</div>
                <div style="margin-top:0.35rem;font-size:0.8rem;color:var(--dv-accent);font-weight:700;">{escape(str(event.get('status','Live')))}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.8rem;">
                <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">Snapshot Explorer</div>
                <div style="font-size:0.8rem;color:var(--dv-muted);">Ready for future playback navigation</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0.7rem;">{''.join(cards)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_decision_center(recommendations: list[dict[str, Any]]) -> None:
    """Render a premium AI decision center and friendly empty state when no recommendations are present."""
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.8rem;">
                <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">AI Decision Center</div>
                <div style="font-size:0.8rem;color:var(--dv-muted);">Executive briefing</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not recommendations:
        st.markdown(
            """
            <div style="border:1px dashed var(--dv-border-strong); border-radius:16px; padding:1rem; background:rgba(255,255,255,0.95); text-align:center;">
                <div style="font-size:1.05rem;font-weight:700;color:var(--dv-text);">Everything looks healthy.</div>
                <div style="margin-top:0.35rem;font-size:0.9rem;color:var(--dv-muted);">AI recommendations will appear automatically whenever intervention becomes beneficial.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cards = []
    for idx, item in enumerate(recommendations[:4], start=1):
        priority = str(item.get("priority") or "Low")
        tone = "danger" if priority.lower() in {"critical", "high", "danger"} else "warning" if priority.lower() in {"medium", "warning"} else "info"
        cards.append(
            f"""
            <div style="border:1px solid var(--dv-border); border-radius:16px; padding:0.9rem; background:rgba(255,255,255,0.96); box-shadow:var(--dv-shadow-sm);">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
                    <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-muted);">Insight {idx}</div>
                    <span class='status-badge {tone}'>{escape(priority.upper())}</span>
                </div>
                <div style="margin-top:0.5rem;font-size:0.95rem;font-weight:700;color:var(--dv-text);">{escape(str(item.get('message', 'No guidance available')))}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.7rem;">{''.join(cards)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trend_chart_card(title: str, dataframe: pd.DataFrame, x_column: str, y_column: str, empty_message: str = "Historical data is still being collected.") -> None:
    """Render a premium trend card with either a chart or a professional empty-state fallback."""
    if dataframe.empty or len(dataframe) < 2:
        st.markdown(
            f"""
            <div class="section-card" style="padding:1rem 1.05rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
                <div style="font-size:0.76rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-accent);margin-bottom:0.45rem;">{escape(title)}</div>
                <div style="border:1px dashed var(--dv-border-strong); border-radius:14px; padding:0.9rem; text-align:center; background:rgba(255,255,255,0.95);">
                    <div style="font-size:0.95rem;font-weight:700;color:var(--dv-text);">No trend history yet</div>
                    <div style="margin-top:0.35rem;font-size:0.84rem;color:var(--dv-muted);">{escape(empty_message)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    chart_data = dataframe[[x_column, y_column]].copy()
    chart_data = chart_data.rename(columns={x_column: "step", y_column: "value"})
    st.markdown(
        f"""
        <div class="section-card" style="padding:1rem 1.05rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="font-size:0.76rem;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--dv-accent);margin-bottom:0.6rem;">{escape(title)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.line_chart(chart_data.set_index("step"), use_container_width=True)


def render_playback_controls() -> None:
    """Render refined placeholder playback controls for future interaction integration."""
    st.markdown(
        """
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.8rem;">
                <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">Playback Controls</div>
                <div style="font-size:0.8rem;color:var(--dv-muted);">Placeholder surface for future navigation</div>
            </div>
            <div style="border:1px solid var(--dv-border); border-radius:999px; height:0.38rem; background:linear-gradient(90deg, rgba(47,125,50,0.25), rgba(148,163,184,0.18)); margin-bottom:0.8rem;"></div>
            <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
                <button disabled style="padding:0.55rem 0.9rem;border-radius:999px;border:1px solid var(--dv-border);background:var(--dv-surface);color:var(--dv-muted);cursor:not-allowed;">◀ Previous</button>
                <button disabled style="padding:0.55rem 0.9rem;border-radius:999px;border:1px solid var(--dv-border);background:var(--dv-surface);color:var(--dv-muted);cursor:not-allowed;">▶ Play</button>
                <button disabled style="padding:0.55rem 0.9rem;border-radius:999px;border:1px solid var(--dv-border);background:var(--dv-surface);color:var(--dv-muted);cursor:not-allowed;">⏸ Pause</button>
                <button disabled style="padding:0.55rem 0.9rem;border-radius:999px;border:1px solid var(--dv-border);background:var(--dv-surface);color:var(--dv-muted);cursor:not-allowed;">Next ▶</button>
                <button disabled style="padding:0.55rem 0.9rem;border-radius:999px;border:1px solid var(--dv-border);background:var(--dv-surface);color:var(--dv-muted);cursor:not-allowed;">↺ Return to Live</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scenario_studio_card() -> None:
    """Render a polished scenario studio feature card with a primary CTA."""
    st.markdown(
        """
        <div class="section-card" style="padding:1rem 1.1rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,255,255,0.97), rgba(248,250,252,0.95)); border:1px solid var(--dv-border); border-radius:18px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.78rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:var(--dv-accent);">Scenario Studio</div>
                    <div style="margin-top:0.35rem;font-size:1rem;font-weight:700;color:var(--dv-text);">Run What-If simulations without affecting the live Digital Twin.</div>
                </div>
                <div style="font-size:0.84rem;color:var(--dv-muted);">Launch for safe planning</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
