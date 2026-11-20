# Health Alert Summary

Actionable health alerts for dairy farmers based on THI and predicted yield decline.

## Alert counts
- Health Risk Alert: 1299
- Heat Stress Alert: 1444
- Productivity Alert: 0
- No Alert: 257

## Severity summary
- Critical: 1299
- High: 908
- Medium: 536
- Low: 257

## THI stress category distribution
- No Stress: 0
- Mild: 257
- Moderate: 536
- Severe: 908
- Emergency: 1299

## Recommendation examples
- COW00000: Heat Stress Alert (High) — High heat stress detected. Consider active cooling, shading, and improved hydration measures.
- COW00001: Health Risk Alert (Critical) — Critical heat stress or productivity decline detected. Consider emergency cooling, veterinary assessment, and hydration.
- COW00002: Heat Stress Alert (Medium) — Moderate heat stress detected. Monitor cattle closely and provide ventilation and water access.
- COW00004: Health Risk Alert (Critical) — Critical heat stress or productivity decline detected. Consider emergency cooling, veterinary assessment, and hydration.
- COW00005: Health Risk Alert (Critical) — Critical heat stress or productivity decline detected. Consider emergency cooling, veterinary assessment, and hydration.

## Alert rules
- THI >= 70: Heat Stress Alert
- THI >= 79: Heat Stress Alert (High)
- THI >= 90: Health Risk Alert (Critical)
- Predicted yield decline > 10%: Productivity Alert
- Predicted yield decline > 20%: Health Risk Alert / Critical
