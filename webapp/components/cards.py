"""Reusable card components for the dashboard."""
from __future__ import annotations

import streamlit as st


def metric_card(
    icon: str,
    title: str,
    value: str,
    subtitle: str = "",
    status: str | None = None,
) -> None:
    """
    Render a professional metric card.

    Args:
        icon: Emoji icon for the card
        title: Card title
        value: Main metric value
        subtitle: Secondary text
        status: Optional status indicator (e.g., "↑ 8.6% vs yesterday")
    """
    status_html = f"<div style='color: #64748b; font-size: 12px; margin-top: 6px;'>{status}</div>" if status else ""

    st.markdown(
        f"""
        <div style='
            background: white;
            border: 1px solid #e5ebf2;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            min-height: 140px;
            display: flex;
            flex-direction: column;
        '>
            <div style='
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            '>
                <div style='font-size: 28px;'>{icon}</div>
            </div>
            <div style='
                font-size: 12px;
                color: #64748b;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 8px;
            '>{title}</div>
            <div style='
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 4px;
            '>{value}</div>
            <div style='
                font-size: 13px;
                color: #475569;
                margin-bottom: 8px;
            '>{subtitle}</div>
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
    """
    Render an info card with title and content.

    Args:
        title: Card title
        content: Main content
        footer: Optional footer text
    """
    footer_html = f"<div style='font-size: 12px; color: #64748b; margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5ebf2;'>{footer}</div>" if footer else ""

    st.markdown(
        f"""
        <div style='
            background: white;
            border: 1px solid #e5ebf2;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        '>
            <div style='
                font-size: 12px;
                color: #64748b;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 12px;
            '>{title}</div>
            <div style='
                font-size: 14px;
                color: #0f172a;
                line-height: 1.5;
            '>{content}</div>
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
    """
    Render an alert card.

    Args:
        title: Alert title
        message: Alert message
        severity: "info", "warning", or "danger"
        timestamp: Optional timestamp
    """
    severity_colors = {
        "info": ("#0ea5e9", "#164e63"),
        "warning": ("#f59e0b", "#78350f"),
        "danger": ("#ef4444", "#7c2d12"),
    }
    color, bg_color = severity_colors.get(severity, severity_colors["info"])
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "danger": "🚨",
    }
    icon = icons.get(severity, "ℹ️")

    timestamp_html = f"<div style='font-size: 12px; color: #64748b; margin-top: 8px;'>{timestamp}</div>" if timestamp else ""

    st.markdown(
        f"""
        <div style='
            background: white;
            border-left: 4px solid {color};
            border: 1px solid #e5ebf2;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        '>
            <div style='
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 6px;
            '>
                <span style='font-size: 18px;'>{icon}</span>
                <div style='
                    font-size: 14px;
                    font-weight: 600;
                    color: #0f172a;
                '>{title}</div>
            </div>
            <div style='
                font-size: 13px;
                color: #475569;
                margin-left: 26px;
            '>{message}</div>
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
    """
    Render a recommendation card.

    Args:
        title: Recommendation title
        description: Detailed description
        icon: Emoji icon
    """
    st.markdown(
        f"""
        <div style='
            background: white;
            border: 1px solid #e5ebf2;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            border-left: 4px solid #2f7d32;
        '>
            <div style='
                display: flex;
                align-items: flex-start;
                gap: 12px;
            '>
                <div style='font-size: 20px;'>{icon}</div>
                <div style='flex: 1;'>
                    <div style='
                        font-size: 14px;
                        font-weight: 600;
                        color: #0f172a;
                        margin-bottom: 4px;
                    '>{title}</div>
                    <div style='
                        font-size: 13px;
                        color: #475569;
                        line-height: 1.4;
                    '>{description}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
