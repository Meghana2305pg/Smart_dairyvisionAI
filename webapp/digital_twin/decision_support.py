"""Small decision-support helpers for the digital twin layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cow_twin import CowTwin


@dataclass(slots=True)
class Recommendation:
    """A conceptual recommendation derived from twin state."""

    message: str
    priority: str = "medium"


def build_recommendations(cow: "CowTwin") -> list[Recommendation]:
    """Create simple recommendations from the current cow state."""
    if cow.latest_health is None:
        return [Recommendation("Collect a fresh observation to update the twin.", "low")]

    severity = str(cow.latest_health.get("severity", "Low")).lower()
    if severity in {"critical", "high"}:
        return [
            Recommendation("Escalate the cow review and inspect feed and heat stress exposure.", "high"),
            Recommendation("Check recent health observations and intervene promptly.", "high"),
        ]
    if severity == "medium":
        return [Recommendation("Increase monitoring and review environmental conditions.", "medium")]
    return [Recommendation("Maintain the current management plan and continue monitoring.", "low")]
