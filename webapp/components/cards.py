"""Reusable card components backed by the centralized design system."""

from __future__ import annotations

from webapp.ui.design_system import (
    render_alert_card as _render_alert_card,
    render_info_card as _render_info_card,
    render_metric_card as _render_metric_card,
    render_recommendation_card as _render_recommendation_card,
)


def metric_card(
    icon: str,
    title: str,
    value: str,
    subtitle: str = "",
    status: str | None = None,
) -> None:
    """Render a metric card using the centralized design system."""
    _render_metric_card(
        title=title,
        value=value,
        subtitle=subtitle,
        icon=icon,
        status=status,
    )


def info_card(
    title: str,
    content: str,
    footer: str = "",
) -> None:
    """Render an info card using the centralized design system."""
    _render_info_card(
        title=title,
        content=content,
        footer=footer,
    )


def alert_card(
    title: str,
    message: str,
    severity: str = "warning",
    timestamp: str = "",
) -> None:
    """Render an alert card using the centralized design system."""
    _render_alert_card(
        title=title,
        message=message,
        severity=severity,
        timestamp=timestamp,
    )


def recommendation_card(
    title: str,
    description: str,
    icon: str = "💡",
) -> None:
    """Render a recommendation card using the centralized design system."""
    _render_recommendation_card(
        title=title,
        description=description,
        icon=icon,
    )
