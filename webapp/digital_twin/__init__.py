"""Conceptual digital-twin domain layer for DairyVision AI."""

from .cow_twin import CowTwin
from .decision_support import Recommendation, build_recommendations
from .farm_twin import FarmTwin
from .herd_twin import HerdTwin
from .observation import Observation
from .twin_intelligence import TwinIntelligence, TwinIntelligenceResult
from .twin_state import PersistencePort, TwinState

__all__ = [
    "CowTwin",
    "FarmTwin",
    "HerdTwin",
    "Observation",
    "PersistencePort",
    "Recommendation",
    "TwinIntelligence",
    "TwinIntelligenceResult",
    "TwinState",
    "build_recommendations",
]
