"""Twin Intelligence orchestrates AI services for the digital-twin layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from webapp.backend_services.explainability_service import get_explanation_for_input
from webapp.backend_services.health_service import get_health_alerts_for_input
from webapp.backend_services.prediction_service import predict_milk_yield
from webapp.backend_services.weather_service import get_current_weather

from .observation import Observation


@dataclass(slots=True)
class TwinIntelligenceResult:
    """Structured AI output produced for a single observation."""

    observation: Observation
    prediction: dict[str, Any] | None = None
    health: dict[str, Any] | None = None
    explanation: list[dict[str, Any]] | None = None
    weather: dict[str, Any] | None = None
    simulation: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TwinIntelligence:
    """Coordinate the existing backend services from one place for all digital twins.

    The class is intentionally thin and additive. It reuses the existing
    prediction, health, explainability, and weather services without changing
    their implementation.
    """

    simulation_adapter: Callable[[Observation, TwinIntelligenceResult], dict[str, Any] | None] | None = None
    weather_adapter: Callable[[Observation], dict[str, Any] | None] | None = None

    def analyze_observation(
        self,
        observation: Observation,
        base_temp: float | None = None,
        base_hum: float | None = None,
    ) -> TwinIntelligenceResult:
        """Run the existing AI services for a single observation and merge results."""
        resolved_temp = base_temp if base_temp is not None else observation.temperature or 28.0
        resolved_hum = base_hum if base_hum is not None else observation.humidity or 65.0

        input_row = observation.to_input_row()
        errors: dict[str, str] = {}

        prediction = None
        health = None
        explanation = None

        try:
            prediction = predict_milk_yield(input_row, base_temp=resolved_temp, base_hum=resolved_hum)
        except Exception as exc:  # pragma: no cover - defensive guard
            errors["prediction"] = str(exc)

        try:
            health = get_health_alerts_for_input(
                input_row,
                base_temp=resolved_temp,
                base_hum=resolved_hum,
                predicted_yield=prediction.get("prediction") if prediction else None,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            errors["health"] = str(exc)

        try:
            explanation = get_explanation_for_input(input_row, base_temp=resolved_temp, base_hum=resolved_hum)
        except Exception as exc:  # pragma: no cover - defensive guard
            errors["explanation"] = str(exc)

        weather_result = self._resolve_weather(observation)
        simulation_result = self._resolve_simulation(observation, prediction, health, explanation)

        metadata = {
            "base_temp": resolved_temp,
            "base_hum": resolved_hum,
            "weather_source": "adapter" if weather_result is not None else "none",
            "simulation_source": "adapter" if simulation_result is not None else "none",
            "service_errors": errors,
        }

        return TwinIntelligenceResult(
            observation=observation,
            prediction=prediction,
            health=health,
            explanation=explanation,
            weather=weather_result,
            simulation=simulation_result,
            metadata=metadata,
        )

    def _resolve_weather(self, observation: Observation) -> dict[str, Any] | None:
        """Resolve weather information through a future adapter if provided."""
        if self.weather_adapter is not None:
            return self.weather_adapter(observation)

        try:
            temp, humidity = get_current_weather()
        except Exception:
            return None

        return {"temperature": temp, "humidity": humidity}

    def _resolve_simulation(
        self,
        observation: Observation,
        prediction: dict[str, Any],
        health: dict[str, Any],
        explanation: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Provide an extension point for future simulation modules."""
        if self.simulation_adapter is None:
            return None
        return self.simulation_adapter(observation, TwinIntelligenceResult(observation, prediction, health, explanation))
