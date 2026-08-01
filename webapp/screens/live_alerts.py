"""Alert grouping helpers for the command centre."""
from __future__ import annotations

from typing import Any


def build_alert_groups(health: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group health alerts into critical, warning, and info buckets."""
    grouped: dict[str, list[dict[str, Any]]] = {"critical": [], "warning": [], "info": []}
    for item in health:
        severity = str(item.get("severity") or "info").lower()
        if severity in {"critical", "high"}:
            grouped["critical"].append(item)
        elif severity in {"medium", "warning"}:
            grouped["warning"].append(item)
        else:
            grouped["info"].append(item)
    return grouped
