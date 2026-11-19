# Synthetic Weather Generation Methodology
## DairyVision AI — Smart Dairy Farm Digital Twin

> **Important:** All temperature, humidity, and THI values used in the feature matrix are **synthetically generated**, not measured from a real farm or retrieved from archival meteorological records. The pipeline does not ship with or read any weather CSV file. The only real-world anchor is an optional run-time API call that provides a single baseline pair `(T_baseline, RH_baseline)`.

---

## 1. Overview

The source cattle datasets contain no timestamps and no geographic coordinates beyond a configured farm location. Because per-record date-matched weather retrieval is therefore infeasible, the pipeline generates realistic per-animal ambient conditions programmatically via a seasonal stochastic model seeded with `RANDOM_SEED = 42`.

Weather assignment is performed inside `feature_engineering.py → assign_weather()`. The function is deterministic given the fixed seed; re-running with the same seed produces identical temperature and humidity columns.

**Key property:** `milk_output` (the target variable `y`) is **never modified** during weather assignment or feature engineering. Temperature and humidity are added purely as input features; their statistical association with milk yield is learned entirely by the ML models from the training data.

---

## 2. Pipeline Entry Point — Open-Meteo API Call

`weather.py → fetch_weather()` is called once at pipeline startup.

| Property | Detail |
|---|---|
| API endpoint | `https://api.open-meteo.com/v1/forecast?...&current=temperature_2m,relative_humidity_2m` |
| Coordinates | Bangalore, India (lat 12.97°N, lon 77.59°E) — configurable via `WEATHER_LAT` / `WEATHER_LON` |
| Returns | A single `(temperature_C, humidity_pct)` pair representing current conditions |
| Timeout | 10 seconds |
| Fallback condition | Any of: `ConnectionError`, `Timeout`, `KeyError`, `TypeError`, `ValueError`, or any other exception |
| Fallback values | **`FALLBACK_TEMP = 28.0 °C`**, **`FALLBACK_HUM = 65.0 %`** (Bangalore annual average) |

> **Role of the API value:** This baseline pair `(T_baseline, RH_baseline)` is passed to `assign_weather()` as the function arguments `base_temp` / `base_hum`, **but the current implementation of `assign_weather()` does not actually use these arguments** — the seasonal generator uses its own hard-coded seasonal ranges. The API call therefore serves only as a live-data placeholder; in practice the synthetic seasonal model governs all final values.

---

## 3. Synthetic Seasonal Weather Model — `assign_weather()`

The function is in `feature_engineering.py` (lines 118–216). It operates on the full 3,000-record DataFrame.

### 3.1 Random Number Generator

```python
rng = np.random.default_rng(RANDOM_SEED)   # RANDOM_SEED = 42
```

NumPy's PCG64 generator seeded at **42** ensures reproducibility.

### 3.2 Seasonal Phase

```python
seasonal_phase = rng.uniform(0, 1, n)   # n = 3,000
```

Each record is assigned a random annual phase uniformly drawn from `[0, 1)`, representing its position within the year. This models the full seasonal cycle without actual calendar dates.

### 3.3 Temperature Generation

| Step | Formula / Value |
|---|---|
| Seasonal min | 18.0 °C |
| Seasonal max | 42.0 °C |
| Seasonal base | `18 + 24 × (0.55 + 0.45 × sin(2π × phase))` → peaks at summer phase ≈ 0.75 |
| Diurnal/micro perturbation | Gaussian noise, **σ = 3.0 °C** |
| After perturbation clip | `np.clip(..., 18.0, 42.0)` |

> Note: `config.py` also defines `TEMP_SIGMA = 2.5 °C` and `TEMP_CLIP = (5.0, 50.0)`, but `assign_weather()` uses its own inline values (σ = 3.0 °C, clip 18–42 °C). The config constants are legacy / reserved for a different code path.

### 3.4 Humidity Generation

| Step | Formula / Value |
|---|---|
| Seasonal min | 40.0 % |
| Seasonal max | 95.0 % |
| Seasonal base | `95 − 55 × (0.5 + 0.4 × sin(2π × phase))` — inversely correlated with temperature peak |
| Diurnal/micro perturbation | Gaussian noise, **σ = 6.0 %** |
| After perturbation clip | `np.clip(..., 40.0, 95.0)` |

> `config.py` defines `HUM_SIGMA = 7.5 %` and `HUM_CLIP = (10.0, 100.0)` but, as above, the actual function uses its own inline constants.

### 3.5 Hot-Humid Boost (~35 % of Records)

```python
hot_humid_mask = rng.uniform(0, 1, n) < 0.35
```

Records under this mask receive:
- Temperature: `+7.0 °C`, clipped to `[18.0, 50.0]`
- Humidity: `+18.0 %`, clipped to `[40.0, 95.0]`

This models moderate summer heat-wave and monsoon co-occurrence scenarios.

### 3.6 Severe Boost (~8 % of Records)

```python
severe_mask = rng.uniform(0, 1, n) < 0.08
```

Records under this mask receive:
- Temperature: `+14.0 °C`, clipped to `[18.0, 52.0]`
- Humidity: `+25.0 %`, clipped to `[40.0, 98.0]`

This models extreme heat-wave and drought scenarios.

### 3.7 Final Temperature and Humidity Ranges

| Variable | Minimum | Maximum | Notes |
|---|---|---|---|
| Temperature | **18.0 °C** | **52.0 °C** | 52 °C only for severe-boost records |
| Humidity | **40.0 %** | **98.0 %** | 98 % only for severe-boost records |

Typical (non-extreme) records fall within 18–42 °C and 40–95 %.

---

## 4. Feature Engineering — `add_engineered_features()`

### 4.1 THI Formula

The **Temperature-Humidity Index** follows the standard Celsius formulation of Mader et al. (2006):

```
THI = (0.8 × T_db) + ((RH / 100) × (T_db − 14.4)) + 46.4
```

where:
- `T_db` = dry-bulb temperature in °C  
- `RH` = relative humidity in % (0–100)

Implemented exactly as:
```python
thi = (0.8 * temperature) + ((humidity / 100.0) * (temperature - 14.4)) + 46.4
```

| THI Range | Heat Stress Category |
|---|---|
| < 60 | No Stress (Thermoneutral) |
| 60–70 | Mild Stress |
| 70–79 | Moderate Stress (~10% yield decline) |
| 79–90 | Severe Stress (~20%+ yield decline) |
| ≥ 90 | Emergency (life-threatening) |

### 4.2 All Engineered Features

| Feature | Formula | Purpose |
|---|---|---|
| `thi` | See §4.1 | Primary heat-stress composite |
| `feed_weight_ratio` | `feed / weight` | Feeding efficiency proxy |
| `temp_humidity` | `temperature × humidity` | Temperature-humidity interaction |
| `thi_squared` | `thi²` | Non-linear heat stress effect |
| `feed_thi_interaction` | `feed × thi` | Heat stress effect on feeding |
| `age_weight_ratio` | `age / weight` | Body condition proxy |

### 4.3 ALL_FEATURES List (from config.py)

```python
BASE_FEATURES      = ["age", "weight", "health_status", "feed",
                       "temperature", "humidity"]
ENGINEERED_FEATURES = ["thi", "feed_weight_ratio",
                        "temp_humidity", "thi_squared",
                        "feed_thi_interaction", "age_weight_ratio"]
ALL_FEATURES        = BASE_FEATURES + ENGINEERED_FEATURES   # 12 features total
TARGET              = "milk_output"
```

### 4.4 Independence of Weather from Milk Yield

`milk_output` is **not read, modified, or consulted** anywhere inside `assign_weather()` or `add_engineered_features()`. The weather generation is a purely structural assignment; any observed correlation between THI features and milk yield in the fitted models is learned from co-occurrence patterns in the data, not encoded by design.

---

## 5. Workflow Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     WEATHER GENERATION PIPELINE                          │
└──────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────┐
  │  Open-Meteo API    │  fetch_weather() — weather.py
  │  GET /v1/forecast  │  lat=12.97, lon=77.59
  │  current endpoint  │  timeout=10s
  └────────┬───────────┘
           │  success
           ▼
  ┌────────────────────┐         ┌──────────────────────────────┐
  │  (T_baseline,      │         │  FALLBACK (any exception):   │
  │   RH_baseline)     │         │  T = 28.0 °C, RH = 65.0 %   │
  │  from API          │         └──────────────┬───────────────┘
  └────────┬───────────┘                        │
           └──────────────────┬─────────────────┘
                              │  base_temp, base_hum passed to
                              ▼  assign_weather() [not used by generator]

  ┌────────────────────────────────────────────────────────────────────┐
  │  SEASONAL PHASE — assign_weather()  — feature_engineering.py      │
  │                                                                    │
  │  rng = np.random.default_rng(42)                                  │
  │  seasonal_phase ~ Uniform(0, 1)  for each of n=3000 records       │
  └────────────────────────┬───────────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
  ┌─────────────────────┐       ┌──────────────────────────┐
  │  TEMPERATURE BASE   │       │  HUMIDITY BASE           │
  │  Sinusoidal model   │       │  Inverse-sinusoidal      │
  │  18 + 24×(0.55 +   │       │  95 − 55×(0.5 +         │
  │   0.45×sin(2π×φ))  │       │   0.4×sin(2π×φ))        │
  └────────┬────────────┘       └───────────┬──────────────┘
           │                               │
           ▼                               ▼
  ┌─────────────────────┐       ┌──────────────────────────┐
  │  GAUSSIAN PERTURBATION      │  GAUSSIAN PERTURBATION   │
  │  + N(0, σ=3.0 °C)   │       │  + N(0, σ=6.0 %)        │
  └────────┬────────────┘       └───────────┬──────────────┘
           │                               │
           ▼                               ▼
  ┌─────────────────────┐       ┌──────────────────────────┐
  │  CLIP [18, 42] °C   │       │  CLIP [40, 95] %         │
  └────────┬────────────┘       └───────────┬──────────────┘
           └───────────────┬───────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │  HOT-HUMID BOOST (~35%)       │
           │  Temp += 7°C → clip [18,50]   │
           │  Hum  += 18% → clip [40,95]   │
           └───────────────┬───────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │  SEVERE BOOST (~8%)           │
           │  Temp += 14°C → clip [18,52]  │
           │  Hum  += 25% → clip [40,98]   │
           └───────────────┬───────────────┘
                           │
                           ▼
           ┌───────────────────────────────────────────────────┐
           │  THI CALCULATION — compute_thi()                  │
           │                                                   │
           │  THI = (0.8×T) + ((RH/100)×(T−14.4)) + 46.4     │
           └───────────────────────────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────────────────────────┐
           │  FEATURE ENGINEERING — add_engineered_features()  │
           │                                                   │
           │  feed_weight_ratio = feed / weight                │
           │  temp_humidity     = temperature × humidity       │
           │  thi_squared       = thi²                         │
           │  feed_thi_interaction = feed × thi               │
           │  age_weight_ratio  = age / weight                 │
           └───────────────────────────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │  Feature matrix X (12 cols)   │
           │  Target y = milk_output       │
           │  (y is NEVER modified)        │
           └───────────────────────────────┘
```

---

## 6. Config.py — Relevant Constants

| Constant | Value | Used by |
|---|---|---|
| `RANDOM_SEED` | **42** | `assign_weather()`, all model `random_state` params |
| `FALLBACK_TEMP` | **28.0 °C** | `weather.py` fallback |
| `FALLBACK_HUM` | **65.0 %** | `weather.py` fallback |
| `WEATHER_LAT` | 12.97 | Open-Meteo API latitude |
| `WEATHER_LON` | 77.59 | Open-Meteo API longitude |
| `TEMP_SIGMA` | 2.5 °C | Defined in config; not used by `assign_weather()` |
| `HUM_SIGMA` | 7.5 % | Defined in config; not used by `assign_weather()` |
| `TEMP_CLIP` | (5.0, 50.0) | Defined in config; not used by `assign_weather()` |
| `HUM_CLIP` | (10.0, 100.0) | Defined in config; not used by `assign_weather()` |
| `THI_COMFORT` | 60 | Stress boundary |
| `THI_MILD` | 70 | Stress boundary |
| `THI_MODERATE` | 79 | Stress boundary |
| `THI_SEVERE` | 90 | Stress boundary |

---

## 7. Limitations and Caveats

### 7.1 Synthetic Nature
All weather values in the feature matrix are **synthetic**, generated by a parameterised stochastic model. They do not represent actual on-farm measurements, archival station data, or reanalysis products. Any association learned by the models between THI-derived features and milk yield reflects patterns constructed by the synthetic generation process, not biological field observations.

### 7.2 Independence from Milk Yield
Temperature and humidity are assigned **independently of each record's `milk_output` value**. The generator has no knowledge of individual yield levels and applies the same seasonal/stochastic model uniformly across all records. This means the data contain no guaranteed causal signal between heat stress and yield; any correlation is incidental.

### 7.3 Absence of Timestamps
The source datasets carry no observation dates. The seasonal phase variable is a **surrogate** for calendar position and is drawn at random from a uniform distribution. Records are not ordered temporally, so the generated weather does not correspond to any real seasonal sequence.

### 7.4 No Geolocation Matching
Although the API call uses Bangalore coordinates as a default, the actual per-record temperature and humidity values are generated by the stochastic seasonal model, not by interpolating real weather for any specific location. The coordinates only serve as an API query point for the single baseline pair.

### 7.5 Possible Artificial Correlations
The sinusoidal seasonal model creates a **structural inverse correlation** between temperature and humidity at the seasonal level (hot seasons are drier; cool seasons are more humid). The hot-humid and severe-boost masks then partially reverse this by simultaneously elevating both temperature and humidity for a subset of records. This results in a bimodal joint distribution of `(temperature, humidity)` that may not reflect any real local climate. Models trained on this data may exploit these distribution artefacts rather than genuine physiological relationships.

### 7.6 Generalisability
Because the weather inputs are synthetic and not geographically or temporally anchored, conclusions about the magnitude of THI effects on milk yield in this study cannot be directly generalised to real farm settings. The pipeline is intended as a proof-of-concept digital twin demonstrating the integration of heat-stress indices into ML-based yield prediction.
