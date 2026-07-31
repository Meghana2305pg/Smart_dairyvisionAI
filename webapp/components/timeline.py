"""Activity timeline component."""
from __future__ import annotations

import streamlit as st


def render_activity_timeline(items: list[tuple[str, str, str]]) -> None:
    """
    Render an activity timeline.

    Args:
        items: List of (time, title, description) tuples
    """
    timeline_html = ""
    for time, title, description in items:
        timeline_html += f"""
        <div style='
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            align-items: flex-start;
        '>
            <div style='
                width: 8px;
                height: 8px;
                border-radius: 999px;
                background: #2f7d32;
                margin-top: 6px;
                flex-shrink: 0;
            '></div>
            <div style='flex: 1;'>
                <div style='
                    font-size: 13px;
                    font-weight: 600;
                    color: #0f172a;
                    margin-bottom: 2px;
                '>{title}</div>
                <div style='
                    font-size: 12px;
                    color: #475569;
                    margin-bottom: 4px;
                '>{description}</div>
                <div style='
                    font-size: 11px;
                    color: #94a3b8;
                '>{time}</div>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div style='
            background: white;
            border: 1px solid #e5ebf2;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        '>
            {timeline_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def quick_action_button(
    icon: str,
    label: str,
    on_click: Callable | None = None,
) -> None:
    """
    Render a quick action button.

    Args:
        icon: Emoji icon
        label: Button label
        on_click: Optional callback
    """
    from typing import Callable

    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.markdown(f"<div style='font-size: 24px;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        if st.button(label, use_container_width=True, key=f"quick_action_{label}"):
            if on_click:
                on_click()
