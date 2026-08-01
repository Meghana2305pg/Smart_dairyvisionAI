"""Weather monitoring helpers for the command centre."""
from __future__ import annotations

from typing import Any


def build_weather_payload(weather: tuple[float, float] | None) -> dict[str, Any]:
    """Build a weather summary payload using the current weather tuple."""
    temperature, humidity = weather if weather else (0.0, 0.0)
    thi = round((0.8 * temperature) + ((humidity / 100.0) * (temperature - 14.4)) + 16.4, 1)
    heat_stress = "High" if thi >= 79 else "Moderate" if thi >= 70 else "Low"
    return {
        "temperature": temperature,
        "humidity": humidity,
        "thi": thi,
        "heat_stress": heat_stress,
    }
