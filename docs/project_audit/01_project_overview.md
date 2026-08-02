# DairyVision AI — Complete Project Audit

> **Audit date:** 2026-08-02  
> **Repository:** `Smart_dairyvisionAI` · **Version:** v2.3.1  
> **Mode:** Read-only analysis — NO code was changed.

---

## Table of Contents

1. [Overall Architecture](#1-overall-architecture)
2. [Folder Structure](#2-folder-structure)
3. [Application Flow](#3-application-flow)
4. [Screen Hierarchy](#4-screen-hierarchy)
5. [Backend Hierarchy](#5-backend-hierarchy)
6. [Service Hierarchy](#6-service-hierarchy)
7. [Repository Layer](#7-repository-layer)
8. [Data Flow](#8-data-flow)
9. [Streamlit Execution Flow](#9-streamlit-execution-flow)
10. [Module Deep-Dives](#10-module-deep-dives)
11. [Current Strengths](#11-current-strengths)
12. [Current Weaknesses](#12-current-weaknesses)

---

## 1. Overall Architecture

DairyVision AI is a **single-process, Streamlit-hosted** web application implementing a full-stack dairy farm intelligence platform. The system is architecturally divided into five clear tiers:

```
+----------------------------------------------------------+
|                    Browser / User                        |
+-----------------------------+----------------------------+
                              |  HTTP (Streamlit WebSocket)
+-----------------------------v----------------------------+
|              Streamlit UI Layer (webapp/)                |
|  Layout Shell -> Screens -> UI Components                |
+-----------------------------+----------------------------+
                              |  Python function calls
+-----------------------------v----------------------------+
|         Application Services (webapp/services/)         |
|  AuthService  FarmService  CowService                   |
|  ObservationService  DashboardService                   |
+-----------------------------+----------------------------+
                              |
          +-------------------+------------------+
          |                                      |
+---------v-----------+          +--------------v-----------+
|  Digital Twin Layer |          |  Backend AI Services     |
|  (webapp/digital_   |          |  (webapp/backend_        |
|   twin/)            |          |   services/)             |
|  CowTwin HerdTwin   |          |  prediction_service      |
|  FarmTwin           |          |  health_service          |
|  TwinIntelligence   |          |  explainability_service  |
|  InMemoryStore      |          |  feature_service         |
+---------------------+          |  simulation_service      |
                                 |  weather_service         |
                                 +--------------------------+
                              |  Wraps root-level modules
+-----------------------------v----------------------------+
|           Root-Level ML Pipeline (project root)         |
|  data_loader.py  feature_engineering.py  train.py      |
|  simulate.py  explainability.py  health_alerts.py      |
|  anomaly_detection.py  evaluate.py  weather.py         |
+-----------------------------+----------------------------+
                              |
+-----------------------------v----------------------------+
|         Repository Layer (webapp/repositories/)         |
|  SupabaseClient (singleton) -> in-memory fallback       |
|  CowRepository  FarmRepository  ObservationRepository  |
|  DashboardRepository                                    |
+-----------------------------+----------------------------+
                              |
+-----------------------------v----------------------------+
|       External Services & Storage                       |
|  Supabase (Auth + PostgreSQL)  Open-Meteo API          |
|  datasets/ (CSV files)  models/ (PKL file)             |
|  outputs/ (pre-computed artifacts)                     |
+----------------------------------------------------------+
```

**Key architectural decisions:**

- The system is **entirely server-side** — there is no separate frontend/backend process split. Streamlit handles both the UI rendering and the Python execution in the same process.
- All runtime state lives in `st.session_state` — there is **no database session persistence** for the app state (though Supabase Auth tokens survive).
- The `SupabaseClient` is used primarily for **authentication** via the official Supabase Python SDK. All entity storage (cows, farms, observations) currently uses an **in-memory dict** within the `SupabaseClient` wrapper — it does NOT write to Supabase tables.
- The root-level Python scripts (`train.py`, `simulate.py`, etc.) are a **separate research/ML pipeline** that are wrapped by `backend_services/` so the Streamlit app can call them.

---

## 2. Folder Structure

```
Smart_dairyvisionAI/
|
+-- webapp/                         # Main Streamlit application
|   +-- app.py                      # Entry point: page config, session init, routing
|   +-- app_old.py                  # Legacy version (preserved, unused)
|   |
|   +-- layout/                     # Global shell, topbar, sidebar
|   |   +-- shell.py                # Composes topbar + sidebar + screen
|   |   +-- sidebar.py              # Navigation menu (streamlit-option-menu)
|   |   +-- topbar.py               # Top header bar
|   |
|   +-- screens/                    # Full-page screen renderers (24 files)
|   |   +-- dashboard.py            # Main KPI dashboard
|   |   +-- herd.py                 # Herd management (list + add cow)
|   |   +-- cow_profile.py          # Individual cow profile
|   |   +-- operations.py           # Daily observation workflow
|   |   +-- prediction.py           # AI prediction center
|   |   +-- digital_twin.py         # Digital twin workspace
|   |   +-- health.py               # Health alerts
|   |   +-- analytics.py            # Analytics & charts
|   |   +-- explainability.py       # SHAP / feature importance
|   |   +-- command_centre.py       # Live ops command center
|   |   +-- settings.py             # App settings
|   |   +-- [sub-components]        # charts.py, filter_panel.py, etc.
|   |
|   +-- services/                   # Application service layer
|   |   +-- auth_service.py         # Supabase Auth wrapper
|   |   +-- farm_service.py         # Farm CRUD + FarmTwin init
|   |   +-- cow_service.py          # Cow CRUD + CowTwin init
|   |   +-- observation_service.py  # Observation creation + twin update
|   |   +-- dashboard_service.py    # Dashboard aggregate builder
|   |
|   +-- repositories/               # Data access layer
|   |   +-- supabase_client.py      # Singleton Supabase client (in-memory fallback)
|   |   +-- cow_repository.py       # CRUD for "cows" table
|   |   +-- farm_repository.py      # CRUD for "farms" table
|   |   +-- observation_repository.py # CRUD for "observations"
|   |   +-- dashboard_repository.py # Read-only aggregation queries
|   |
|   +-- digital_twin/               # Domain model for digital twins
|   |   +-- __init__.py             # Public exports
|   |   +-- cow_twin.py             # CowTwin dataclass (per-cow AI state)
|   |   +-- herd_twin.py            # HerdTwin (aggregate of CowTwins)
|   |   +-- farm_twin.py            # FarmTwin (aggregate of HerdTwins)
|   |   +-- twin_state.py           # TwinState (status, history lists)
|   |   +-- twin_intelligence.py    # TwinIntelligence (AI orchestrator)
|   |   +-- observation.py          # Observation dataclass
|   |   +-- decision_support.py     # Rule-based recommendation engine
|   |   +-- memory/
|   |       +-- memory_store.py     # InMemorySnapshotStore
|   |       +-- snapshot.py         # TwinSnapshot (immutable record)
|   |       +-- health_history.py   # Per-cow health history log
|   |       +-- prediction_history.py
|   |       +-- observation_history.py
|   |       +-- recommendation_history.py
|   |       +-- weather_history.py
|   |
|   +-- backend_services/           # Wrappers around root ML modules
|   |   +-- _bootstrap.py           # Adds project root to sys.path
|   |   +-- model_loader.py         # @st.cache_resource model loader
|   |   +-- feature_service.py      # @st.cache_data feature pipeline
|   |   +-- prediction_service.py   # predict_milk_yield()
|   |   +-- health_service.py       # get_health_alerts_for_input()
|   |   +-- explainability_service.py # SHAP / feature importance
|   |   +-- simulation_service.py   # What-if scenario simulation
|   |   +-- analytics_service.py    # Evaluation artifact paths
|   |   +-- weather_service.py      # @st.cache_data(ttl=300) weather
|   |
|   +-- state/
|   |   +-- session_state.py        # APP_STATE constants + bootstrap helpers
|   |
|   +-- config/
|   |   +-- settings.py             # Path constants + env overrides
|   |
|   +-- ui/                         # Shared UI primitives
|   |   +-- section_header.py       # apply_app_theme(), render_page_header()
|   |   +-- navigation.py           # Navigation helper
|   |   +-- analytics_views.py      # Analytics sub-views
|   |   +-- daily_operations.py     # Ops UI helpers
|   |   +-- herd_management.py      # Herd UI helpers
|   |   +-- cow_profile.py          # Profile UI helpers
|   |   +-- dashboard_cards.py      # Dashboard card components
|   |   +-- recommendation_panel.py
|   |   +-- twin_status_card.py
|   |
|   +-- components/                 # Reusable Streamlit components
|   |   +-- cards.py                # info_card(), recommendation_card()
|   |   +-- timeline.py             # Activity timeline
|   |
|   +-- utils/                      # Cross-cutting utilities
|   |   +-- validation.py           # Form validation helpers
|   |   +-- logging.py              # log_event(), log_error()
|   |   +-- requirements_check.py   # Dep verification at startup
|   |
|   +-- pages/                      # Streamlit multi-page stubs
|   |   +-- 00_Login.py             # Redirect stub
|   |   +-- 01_Prediction.py        # Standalone prediction page
|   |   +-- 02_Digital_Twin.py      # Standalone twin page
|   |   +-- 03_Health_Alerts.py     # Standalone alerts page
|   |   +-- 04_Explainability.py    # Standalone explainability page
|   |   +-- 05_Command_Centre.py    # Standalone command centre
|   |
|   +-- research_pages/             # Research/model analysis pages
|       +-- 05_Model_Performance.py
|       +-- 06_Model_Comparison.py
|       +-- 07_Dataset_Overview.py
|       +-- 08_About_Project.py
|
+-- datasets/                       # Raw input CSVs
|   +-- global_cattle_disease_detection_dataset.csv
|   +-- global_cattle_milk_yield_prediction_dataset.csv
|
+-- models/                         # Trained model artifacts
|   +-- best_milk_model.pkl
|
+-- outputs/                        # Generated analysis artifacts
|   +-- engineered_dataset.csv
|   +-- cv_results.csv
|   +-- health_alerts.csv
|   +-- anomaly_report.csv
|   +-- shap/                       # SHAP explainability outputs
|   +-- [various PNGs + CSVs]
|
+-- genetics/                       # Genetic analysis module (standalone)
|   +-- train_models.py
|   +-- evaluate_models.py
|   +-- genetics_dashboard.py
|   +-- genetics_report.py
|   +-- genetics_visualization.py
|   +-- sire_ranking.py
|   +-- load_data.py
|
+-- tests/                          # Unit + integration tests (11 files)
|
+-- config.py                       # Root ML pipeline config
+-- data_loader.py                  # Dataset loading + merging
+-- feature_engineering.py          # THI + feature computation
+-- train.py                        # Model training pipeline
+-- evaluate.py                     # Model evaluation
+-- simulate.py                     # What-if simulation engine
+-- explainability.py               # SHAP report generation
+-- health_alerts.py                # Batch health alert generation
+-- anomaly_detection.py            # Anomaly detection (Isolation Forest)
+-- thi_audit.py                    # THI distribution analysis
+-- run_pipeline.py                 # Full pipeline orchestrator
+-- weather.py                      # Open-Meteo API wrapper
+-- requirements.txt
+-- Dockerfile
+-- .env / .env.example
```

---

## 3. Application Flow

The application has **three distinct lifecycle phases** per user:

### Phase 1: Pre-Authentication
```
User visits app
     |
     v
APP_STATE_NOT_AUTHENTICATED
     |
     +-- active_view == "login"    ->  render_login_screen()
     +-- active_view == "register" -> render_register_screen()
           | (on success)
           v
     set authenticated=True, set pending_farm_setup=True
     APP_STATE_AUTHENTICATED_NO_FARM
```

### Phase 2: Farm Onboarding
```
APP_STATE_AUTHENTICATED_NO_FARM
     |
     v
render_farm_setup_screen()
     | (on success)
     v
FarmService.create_farm()
     -> creates FarmRepository record (in-memory)
     -> instantiates FarmTwin
set farm=..., pending_farm_setup=False
APP_STATE_AUTHENTICATED_WITH_FARM
```

### Phase 3: Main Application
```
APP_STATE_AUTHENTICATED_WITH_FARM / _WITH_COWS
     |
     v
render_app_shell()
     |
     +-- render_topbar()
     +-- render_sidebar() -> returns selected section key
     +-- render_screen(section) -> dispatches to screen renderer
```

### State Machine
```
NOT_AUTHENTICATED
    |  login() or register()
    v
AUTHENTICATED_NO_FARM
    |  create_farm()
    v
AUTHENTICATED_WITH_FARM
    |  register_cow()
    v
AUTHENTICATED_WITH_COWS
```

---

## 4. Screen Hierarchy

All screens dispatched by `webapp/app.py -> render_screen()`:

```
Main Application Shell
+-- render_app_shell()
    +-- render_topbar()         [layout/topbar.py]
    +-- render_sidebar()        [layout/sidebar.py]
    +-- render_screen(section)
        |
        +-- "dashboard"          -> render_dashboard()        [screens/dashboard.py]
        |     KPIs, AI recs, alerts, quick actions
        |
        +-- "my_herd"            -> render_herd()             [screens/herd.py]
        |     Herd list, add-cow form, search/filter
        |     +-- navigates to -> render_cow_profile()       [screens/cow_profile.py]
        |           Overview, History, Twin, Prediction tabs
        |
        +-- "daily_operations"   -> render_daily_operations() [screens/operations.py]
        |     5-step guided workflow:
        |     Select Cow -> Observation -> Review -> Generate -> Results
        |
        +-- "digital_twin"       -> render_digital_twin()     [screens/digital_twin.py]
        |     Twin status, observation history, simulation
        |
        +-- "health_alerts"      -> render_health()           [screens/health.py]
        |     Herd-level alert table, severity filters
        |
        +-- "analytics"          -> render_analytics()        [screens/analytics.py]
        |     Charts, export, filter panels
        |
        +-- "explainability"     -> render_explainability()   [screens/explainability.py]
        |     SHAP values, feature importance, comparison
        |
        +-- "command_centre"     -> render_command_centre()   [screens/command_centre.py]
        |     Live feed, system health, weather monitor
        |
        +-- "settings"           -> render_settings()         [screens/settings.py]
              User profile, farm info, system status

Pre-Auth Screens (no sidebar, no topbar):
+-- render_login_screen()         [in app.py]
+-- render_register_screen()      [in app.py]
+-- render_farm_setup_screen()    [in app.py]
```

---

## 5. Backend Hierarchy

### Tier A: Root-Level ML Research Pipeline

Standalone Python CLI programs run offline to produce model artifacts.

```
Root ML Pipeline
+-- run_pipeline.py           # Orchestrates all steps in order
|   +-- Step 1: data_loader.py        -> loads + merges CSVs
|   +-- Step 2: feature_engineering.py -> adds THI, feed ratios, etc.
|   +-- Step 3: train.py              -> cross-validation + model selection
|   +-- Step 4: evaluate.py           -> test set evaluation + plots
|   +-- Step 5: simulate.py           -> what-if grid simulation
|   +-- Step 6: explainability.py     -> SHAP report generation
|   +-- Step 7: health_alerts.py      -> batch alert generation
|   +-- Step 8: anomaly_detection.py  -> Isolation Forest anomaly scan
|
+-- thi_audit.py              # Standalone THI analysis
+-- test_weather.py           # Weather API connectivity test
+-- genetics/                 # Separate genetic analysis pipeline (isolated)
```

### Tier B: Backend Services (webapp/backend_services/)

Thin wrapper functions bridging Streamlit to root-level ML modules.

```
backend_services/
+-- _bootstrap.py             # sys.path patcher (adds project root)
+-- model_loader.py           # @st.cache_resource: loads best_milk_model.pkl
+-- feature_service.py        # @st.cache_data: prepare_feature_frame(), build_feature_row()
+-- prediction_service.py     # predict_milk_yield(input_row, temp, hum)
+-- health_service.py         # get_health_alerts_for_input(input_row, ...)
+-- explainability_service.py # get_explanation_for_input(input_row, ...)
+-- simulation_service.py     # run_dynamic_simulation(input_row, feed_range, temp_range)
+-- analytics_service.py      # Reads evaluation artifact CSV/PNG paths
+-- weather_service.py        # @st.cache_data(ttl=300): fetch_weather()
```

---

## 6. Service Hierarchy

```
webapp/services/
|
+-- AuthService
|   +-- Dependencies: SupabaseClient (Supabase SDK Auth)
|   +-- Methods: register_user(), login(), logout(), current_user()
|   +-- Holds: _current_user dict in memory
|
+-- FarmService
|   +-- Dependencies: FarmRepository, FarmTwin
|   +-- Methods: create_farm(), get_farm(), update_farm(), delete_farm()
|   +-- Holds: _farm_twins dict (farm_id -> FarmTwin)
|
+-- CowService
|   +-- Dependencies: CowRepository, CowTwin
|   +-- Methods: register_cow(), update_cow(), delete_cow(), get_cows()
|   +-- Holds: _cow_twins dict (cow_id -> CowTwin)  <-- KEY state store
|
+-- ObservationService
|   +-- Dependencies: ObservationRepository, CowService
|   +-- Methods: record_observation()
|   +-- Side effects: calls twin.record_observation() + twin.refresh_from_ai()
|
+-- DashboardService
    +-- Dependencies: DashboardRepository, FarmService, CowService, ObservationService
    +-- Methods: build_dashboard() -> DashboardView
    +-- Returns: DashboardView (farm, herd, predictions, health, recs, snapshots)
```

---

## 7. Repository Layer

```
webapp/repositories/
|
+-- SupabaseClient (Singleton via from_env())
|   +-- _client: official Supabase Python SDK client (Auth only)
|   +-- _tables: dict[table_name, list[dict]]  <-- IN-MEMORY STORE
|   +-- Methods: insert(), update(), delete(), list(), get()
|   +-- CRITICAL: All entity writes go to _tables (in-memory), NOT to Supabase DB
|       Only Auth operations use the real Supabase SDK client
|
+-- CowRepository          -> wraps SupabaseClient("cows")
+-- FarmRepository         -> wraps SupabaseClient("farms")
+-- ObservationRepository  -> wraps SupabaseClient("observations")
+-- DashboardRepository    -> read-only: list farms/cows/observations/snapshots
```

> **Critical Finding:** `SupabaseClient._tables` is the actual runtime store. The `supabase.create_client()` is only initialized for Auth. All CRUD operations use the in-memory dict. **Data does not survive a server restart or new session.**

---

## 8. Data Flow

### 8.1 Observation -> Prediction -> Health -> Explainability

```
User submits daily observation form
     |
     v
ObservationService.record_observation(cow_id, age, weight, feed, temp, hum, health_status, notes)
     |
     +-- Creates Observation dataclass
     +-- Writes to ObservationRepository (in-memory)
     +-- Gets or creates CowTwin for cow_id
     +-- CowTwin.record_observation(observation)        <- updates state
     +-- CowTwin.refresh_from_ai(base_temp, base_hum)  <- triggers AI pipeline
              |
              v
      TwinIntelligence.analyze_observation(observation)
              |
              +-- predict_milk_yield(input_row, temp, hum)
              |     +-- build_feature_row() -> model.predict()
              |         -> returns {prediction: float, feature_names, feature_values}
              |
              +-- get_health_alerts_for_input(input_row, temp, hum, predicted_yield)
              |     +-- compare baseline (20C, 50% humidity) vs current
              |         -> compute decline_pct, THI, stress_category
              |         -> _classify_alert(thi, decline_pct)
              |         -> returns {severity, alert_category, recommendation, ...}
              |
              +-- get_explanation_for_input(input_row, temp, hum)
                    +-- SHAP TreeExplainer -> shap_values
                        -> ranked [{feature, contribution, abs_contribution}]
              |
              v
      TwinIntelligenceResult stored on CowTwin
      build_recommendations(cow_twin) -> Recommendation list
      TwinSnapshot created -> saved to InMemorySnapshotStore
```

### 8.2 Weather Data Flow

```
get_current_weather()  [@st.cache_data(ttl=300)]
     |
     v
weather.fetch_weather(lat=12.97, lon=77.59)
     |
     +-- GET https://api.open-meteo.com/v1/forecast
     |     ?latitude=12.97&longitude=77.59
     |     &current=temperature_2m,relative_humidity_2m
     |
     +-- On success: return (temperature_C, humidity_pct)
     +-- On failure: return (FALLBACK_TEMP=28.0, FALLBACK_HUM=65.0)
```

### 8.3 Dashboard Data Flow

```
DashboardService.build_dashboard()
     |
     +-- DashboardRepository.get_farms()       -> SupabaseClient._tables["farms"]
     +-- DashboardRepository.get_cows()        -> SupabaseClient._tables["cows"]
     +-- DashboardRepository.get_observations() -> in-memory
     +-- DashboardRepository.get_snapshots()   -> in-memory
     |
     +-- For each cow_id in CowService._cow_twins:
     |     twin.latest_prediction  -> predictions[]
     |     twin.latest_health      -> health[]
     |     twin.recommendations    -> recommendations[]
     |     twin.memory_store.get_latest_snapshot() -> snapshots[]
     |
     +-- Returns DashboardView(farm, herd, predictions, health, recs, snapshots)
```

### 8.4 ML Training Pipeline (Offline)

```
run_pipeline.py
     |
     v
data_loader.load_and_prepare()
     |  inner-join disease CSV + yield CSV on Cattle_ID
     v
feature_engineering.build_features(df_clean, base_temp, base_hum)
     |  adds: temperature, humidity (synthetic with Gaussian noise)
     |  computes: thi, feed_weight_ratio, feed_per_weight,
     |            temp_humidity, thi_squared, feed_thi_interaction, age_weight_ratio
     v
train.py -> KFold CV (5 folds)
     |  candidates: XGBoost, Random Forest, Decision Tree, Linear, Dummy
     |  selection: Wilcoxon signed-rank test on R2 scores
     v
models/best_milk_model.pkl  (saved with joblib)
     v
evaluate.py -> test set metrics, plots
     v
simulate.py -> feed x temperature grid -> prediction intervals
     v
explainability.py -> SHAP TreeExplainer -> shap_summary.png, shap_feature_importance.csv
     v
health_alerts.py -> THI + yield decline -> health_alerts.csv
     v
anomaly_detection.py -> Isolation Forest -> anomaly_report.csv
```

---

## 9. Streamlit Execution Flow

Every browser interaction triggers a **full re-run** of `webapp/app.py`:

```
Browser event (click, input, form submit)
     |
     v
streamlit run webapp/app.py  (entry point)
     |
     v
main()
 1. st.set_page_config(page_title="DairyVision AI", layout="wide")
 2. apply_app_theme()              <- injects global CSS via st.markdown()
 3. initialize_app_state()
    +-- bootstrap_session_state()  <- sets defaults ONLY on first run
        +-- instantiates: AuthService, FarmService, CowService,
                          ObservationService, DashboardService
 4. _prepare_workspace_state()
    +-- _restore_workspace_state() <- re-reads user/farm from session_state
    +-- update_app_state()         <- recomputes APP_STATE from current session
    +-- _sync_query_params_from_session() <- clears URL params
 5. app_state = st.session_state.get("app_state")
 6. Branch on app_state:
    +-- NOT_AUTHENTICATED  -> render login or register (no sidebar)
    +-- AUTHENTICATED_NO_FARM -> render farm setup (no sidebar)
    +-- AUTHENTICATED_WITH_FARM/_WITH_COWS
          +-- render_app_shell(lambda: render_screen(section))
                +-- apply_app_theme()     <- re-applied (idempotent CSS)
                +-- render_topbar()
                +-- with st.sidebar: render_sidebar() -> selected_key
                +-- render_screen(section) -> [screen-specific renderer]
```

**Important Streamlit behaviors:**
- `@st.cache_resource` (model loader): persists **across all sessions**, shared between users
- `@st.cache_data` (feature frame, weather): per-session with TTL for weather (5 min)
- `st.session_state` is per-user per-browser-tab — NOT shared between users
- Every `st.rerun()` triggers a full re-execution from `main()`

---

## 10. Module Deep-Dives

---

### 10.1 Authentication

| Item | Detail |
|------|--------|
| **File** | `webapp/services/auth_service.py` |
| **Purpose** | Wraps Supabase Auth SDK for user registration and login |
| **Dependencies** | `supabase` Python SDK, `SupabaseClient` |
| **Data flow** | Form -> validate_login_form() -> AuthService.login() -> Supabase.sign_in_with_password() -> session_state |
| **State stored** | `user`, `user_id`, `user_email`, `user_name`, `authenticated` in session_state |

**Authentication mechanism:**
- Uses **Supabase Auth** (email + password) — the ONLY place where the real Supabase client is used
- On login success: stores `_current_user` dict within `AuthService` instance (stored in session_state)
- Logout: calls `auth.sign_out()`, clears in-memory user
- No JWT refresh logic — relies on Supabase session TTL

**Weaknesses:**
- `_current_user` lives on the `AuthService` Python object. Since service is in session_state, it survives navigation but NOT a server restart
- No role-based access control (no admin vs. farmer distinction)
- Email normalization (`strip().lower()`) only done on login, not on register
- No "forgot password" / reset flow
- The user `full_name` is NOT fetched on login (Supabase returns minimal user data via `sign_in_with_password`)

---

### 10.2 Farm Onboarding

| Item | Detail |
|------|--------|
| **File** | `webapp/app.py` (render_farm_setup_screen), `webapp/services/farm_service.py` |
| **Purpose** | First-run farm creation after authentication |
| **Dependencies** | `FarmService`, `FarmRepository`, `FarmTwin` |
| **Data flow** | Form -> validate_farm_setup_form() -> FarmService.create_farm() -> in-memory record + FarmTwin |

**Farm ID generation (fragile):**
```python
farm_id = f"farm-{farm_name.lower().replace(' ', '-')}"
```
No uniqueness check, special chars not sanitized, two farms with same name would clash.

**Weaknesses:**
- Farm ID derived from name without sanitization (unicode, double-spaces not handled)
- No uniqueness constraint — duplicate farms silently allowed
- Farm data goes to in-memory only, NOT to Supabase DB
- No farm update UI after initial creation
- `farm_size` stored as a string, not a numeric type

---

### 10.3 Herd Management

| Item | Detail |
|------|--------|
| **File** | `webapp/screens/herd.py` (697 lines) |
| **Purpose** | View, filter, and add cows; navigate to individual cow profiles |
| **Dependencies** | `CowService`, `CowTwin`, validation utils |
| **State** | `herd_search_term`, `herd_status_filter`, `herd_breed_filter` in session_state |

**Cow registration flow:**
1. User fills cow ID + name + optional metadata
2. `validate_cow_registration_form()` runs
3. `CowService.register_cow()` -> `CowRepository.create()` + `CowTwin(cow_id, name)` instantiated
4. `st.session_state.cows` refreshed via `cow_service.get_cows()`

**Filtering:** Client-side search/filter on in-memory cow list — no server-side filtering.

**Weaknesses:**
- Cow twins created lazily via `_get_or_create_twin()` inside screen — bypasses service layer in some paths
- 697-line file; should be decomposed into sub-modules
- No bulk operations (no multi-cow select/action)
- No cow deletion confirmation modal
- Breed, lactation stage, age entered as free text — no biological plausibility validation

---

### 10.4 Daily Operations & Observation Workflow

| Item | Detail |
|------|--------|
| **File** | `webapp/screens/operations.py` (432 lines) |
| **Purpose** | Guided 5-step form to record observations and trigger AI analysis |
| **Dependencies** | `ObservationService`, `CowService`, backend AI services, weather service |
| **State** | `daily_ops_*` keys in session_state, `daily_ops_phase` ("form" or "results") |

**Workflow steps:**
1. **Select Cow** — dropdown from registered cows
2. **Observation** — age, weight, feed, temperature, humidity, health status, notes
3. **Review** — summary before submission
4. **Generate** — calls `ObservationService.record_observation()` -> triggers full AI pipeline
5. **Results** — displays prediction, health alert, SHAP explanation, recommendations

**Weaknesses:**
- Observation data is fully in-memory — no persistence to Supabase DB
- `daily_ops_*` session state keys are flat top-level keys — difficult to reset atomically
- Workflow phase tracked via `daily_ops_phase` string — not a proper state machine
- Temperature and humidity are manually entered (not auto-populated from weather service)
- Notes field max length 200 chars enforced by validation only (no DB constraint)

---

### 10.5 Digital Twin Implementation

| Item | Detail |
|------|--------|
| **Files** | `webapp/digital_twin/` (entire directory) |
| **Purpose** | Per-cow stateful AI context with observation history, predictions, health, snapshots |
| **Dependencies** | `TwinIntelligence` -> backend_services (prediction, health, explainability, weather) |

**Architecture:**
```
FarmTwin (farm_id)
  +-- herds: dict[str, HerdTwin]     [NEVER ACTUALLY LINKED IN PRACTICE]
        +-- cows: dict[str, CowTwin] [NEVER ACTUALLY LINKED IN PRACTICE]
              +-- state: TwinState
              |     status, observations[], predictions[], health[], recommendations[]
              +-- intelligence: TwinIntelligence
              |     -> calls predict, health, explain, weather services
              +-- memory_store: InMemorySnapshotStore
              |     -> _snapshots: dict[snapshot_id, TwinSnapshot]
              |     -> _history: dict[cow_id, list[TwinSnapshot]]
              +-- latest_prediction / latest_health / latest_explanation / recommendations
```

**TwinIntelligence pipeline:**
```
analyze_observation(observation, base_temp, base_hum)
  1. predict_milk_yield(input_row)   -> {prediction, feature_names, feature_values}
  2. get_health_alerts_for_input()   -> {severity, alert_category, recommendation, ...}
  3. get_explanation_for_input()     -> [{feature, contribution, abs_contribution}...]
  4. _resolve_weather()              -> {temperature, humidity} from Open-Meteo
  5. _resolve_simulation()           -> None (adapter not yet connected)
  -> returns TwinIntelligenceResult
```

**Snapshot lifecycle:**
1. After every `refresh_from_ai()`, a `TwinSnapshot` is created
2. Snapshot saved to `InMemorySnapshotStore` (per-cow history list)
3. Latest snapshot accessible via `memory_store.get_latest_snapshot(cow_id)`
4. Dashboard and screens retrieve snapshots from `CowService._cow_twins`

**Strengths:**
- `PersistencePort` Protocol defined for future database backing
- Immutable `TwinSnapshot` records (dataclasses with timestamps)
- `TwinState.to_persistence_payload()` ready for serialization

**Weaknesses:**
- `FarmTwin` and `HerdTwin` exist but are **never actually linked** — CowTwins are created directly by `CowService` without being registered into a `HerdTwin`
- The `simulation_adapter` on `TwinIntelligence` is always `None` — simulation only available through separate `simulation_service.py`
- All twin state is in-memory — server restart loses everything
- `HerdTwin.aggregate_snapshot_summary()` has a **bug**: `average_thi` loop body is `sum([value.get("temperature", 0.0) for value in []])` — always returns None
- Screen files directly access `cow_service._cow_twins` private dict (tight coupling)

---

### 10.6 Prediction Workflow

| Item | Detail |
|------|--------|
| **File** | `webapp/backend_services/prediction_service.py`, `webapp/screens/prediction.py` |
| **Purpose** | Real-time milk yield prediction from user-supplied or twin-stored observations |
| **Model** | `models/best_milk_model.pkl` — best model from CV |
| **Dependencies** | `model_loader`, `feature_service`, `config.ALL_FEATURES` |

**Feature vector (ALL_FEATURES — 13 features):**
- Base: `age, weight, health_status, feed, temperature, humidity`
- Engineered: `thi, feed_weight_ratio, feed_per_weight, temp_humidity, thi_squared, feed_thi_interaction, age_weight_ratio`

**THI formula (NRC 2001):**
`THI = T_db - (0.31 - 0.31 x RH/100) x (T_db - 14.4) - 32`

**THI stress thresholds (config.py):**
| THI Range | Category |
|-----------|----------|
| < 60 | No stress (thermoneutral) |
| 60–70 | Mild stress |
| 70–79 | Moderate stress (milk yield -10%) |
| 79–90 | Severe stress (milk yield -20%+) |
| >= 90 | Emergency (life-threatening) |

**Weaknesses:**
- No real-time confidence interval (only available via batch simulation)
- Model version hardcoded (`best_milk_model.pkl`) — no versioning or A/B testing
- `@st.cache_resource` means all users share the same model instance
- Cold start loads entire training dataset via `prepare_feature_frame()`

---

### 10.7 Health Alerts

| Item | Detail |
|------|--------|
| **Files** | `webapp/backend_services/health_service.py`, root `health_alerts.py` |
| **Purpose** | Real-time per-cow health classification based on THI and yield decline |
| **Algorithm** | Rule-based threshold classification |

**Classification thresholds:**

| Condition | Severity | Alert |
|-----------|----------|-------|
| THI >= 90 OR decline > 20% | Critical | Health Risk Alert |
| THI >= 79 | High | Heat Stress Alert |
| Decline > 20% | Critical | Productivity Alert |
| Decline > 10% | High | Productivity Alert |
| THI >= 70 | Medium | Heat Stress Alert |
| Otherwise | Low | No Alert |

**Decline calculation:**
```
baseline: temp=20C, hum=50%
decline_pct = 100 x (baseline_yield - current_yield) / baseline_yield
```

**Weaknesses:**
- Thresholds are hardcoded — not configurable per farm or breed
- USDA THI thresholds designed for North American Holstein cattle — may not apply to Indian breeds (Sahiwal, Gir) which are more heat-tolerant
- Batch `health_alerts.py` and interactive `health_service.py` have overlapping but inconsistent logic
- Root-level `_prepare_health_df()` ignores the `df_full` parameter (dead parameter)
- No alert deduplication — same alert generated every form submission

---

### 10.8 Explainability (SHAP)

| Item | Detail |
|------|--------|
| **Files** | `webapp/backend_services/explainability_service.py`, root `explainability.py` |
| **Purpose** | Feature-level explanation of milk yield predictions |
| **Method** | SHAP TreeExplainer for tree-based models |

**3-level fallback chain:**
1. Try `shap.TreeExplainer` on live model -> SHAP values per feature
2. If SHAP unavailable: read `outputs/shap/shap_feature_importance.csv`
3. If CSV unavailable: use `model.feature_importances_`
4. If nothing: zeros

**Weaknesses:**
- `shap` is optional — if missing, silently falls back to feature importances (different semantics than SHAP values)
- No baseline/expected value shown (required to correctly interpret SHAP)
- SHAP computation is synchronous and blocking — no async execution
- No user-facing explanation of what SHAP values mean

---

### 10.9 Analytics

| Item | Detail |
|------|--------|
| **File** | `webapp/screens/analytics.py` (308 lines), `webapp/screens/charts.py` |
| **Purpose** | Time-series charts, herd trends, weather correlation, export |

**Charts implemented:**
- Milk production trend
- Health trend
- Prediction history
- Weather vs. milk correlation (Plotly)

**Weaknesses:**
- All chart data from in-memory session state (cow twins) — no historical database
- With no persistent observations, charts show only current session data
- Filter panel (date range, cow, breed, health) operates on small in-memory lists
- Export panel limited to current session data only

---

### 10.10 Command Centre

| Item | Detail |
|------|--------|
| **File** | `webapp/screens/command_centre.py` (298 lines) |
| **Purpose** | Real-time operational overview with activity feed, system health, weather |
| **Sub-modules** | `activity_feed.py`, `live_alerts.py`, `system_health.py`, `weather_monitor.py` |

**Panels:**
- Activity feed (recent observations, twin syncs, recommendations)
- Live alert groups (severity-bucketed health alerts)
- System health (model status, Supabase connectivity)
- Weather monitor (current temp, humidity, THI)

**Weaknesses:**
- "Live" is a misnomer — data refreshes only on page reload, no streaming
- No auto-refresh / polling mechanism
- Activity feed assembled from session state, not a persistent event log

---

### 10.11 Session Management

| Item | Detail |
|------|--------|
| **File** | `webapp/state/session_state.py` |
| **Purpose** | Initialize and read/write Streamlit session state safely |
| **Constants** | `APP_STATE_NOT_AUTHENTICATED`, `_NO_FARM`, `_WITH_FARM`, `_WITH_COWS` |

**Bootstrap pattern (idempotent — runs once per session):**
```python
def bootstrap_session_state(defaults):
    if st.session_state.get("_session_bootstrapped"):
        return  # only runs once
    init_session_defaults(defaults)
    st.session_state["_session_bootstrapped"] = True
```

**Weaknesses:**
- ~25+ flat top-level session state keys — no namespacing or grouping
- Services stored as Python objects in session_state (works but unconventional)
- No serialization of session state — cannot resume sessions after tab close
- Multiple `_restore_workspace_state` fallback paths create complex initialization logic

---

### 10.12 ML Pipeline (Root-Level Backend)

| Item | Detail |
|------|--------|
| **Purpose** | Full offline research pipeline from raw data to trained model + analysis artifacts |
| **Entry point** | `run_pipeline.py` |
| **Target** | Milk yield prediction (regression, continuous) |

**Datasets:**
| Dataset | Key Columns |
|---------|-------------|
| `global_cattle_disease_detection_dataset.csv` | Cattle_ID, disease indicators |
| `global_cattle_milk_yield_prediction_dataset.csv` | Cattle_ID, Age_Months, Weight_kg, Feed_Quantity_kg, Milk_Yield_L |

**Models trained:** XGBoost, Random Forest, Decision Tree, Linear Regression, Dummy

**Model selection:** Wilcoxon signed-rank test on 5-fold CV R2 scores

**Weaknesses:**
- Only one model saved — no versioning or rollback capability
- Anomaly detection results (Isolation Forest) not integrated into webapp alerts
- Genetics module entirely disconnected from webapp
- Training THI uses synthetic noise; production THI uses real API — distribution mismatch
- Inner join on Cattle_ID may drop significant data if datasets grow independently

---

### 10.13 Genetics Module

| Item | Detail |
|------|--------|
| **Directory** | `genetics/` |
| **Purpose** | Breeding/genetics analysis including sire ranking and genetic evaluation |
| **Status** | **Completely standalone** — zero integration with main Streamlit webapp |

The genetics module has its own `data/` and `outputs/` subdirectories. It is not accessible through any navigation item or screen. No `__init__.py` exports are registered in the webapp package.

---

## 11. Current Strengths

| # | Category | Strength |
|---|----------|----------|
| S1 | Architecture | Clear 5-tier layering (UI -> Services -> Twin -> AI Backend -> Repository) with well-defined responsibilities |
| S2 | Digital Twin | Conceptually sound twin hierarchy (CowTwin -> HerdTwin -> FarmTwin) with clean domain separation |
| S3 | ML Pipeline | Rigorous training with Wilcoxon-validated model selection and 5-fold CV |
| S4 | Feature Engineering | THI computed without target manipulation — biologically correct (NRC 2001 citation) |
| S5 | Explainability | 3-level SHAP fallback chain ensures some explanation always returned |
| S6 | Caching | Correct use of `@st.cache_resource` (model) and `@st.cache_data` (features, weather) |
| S7 | Validation | Centralized form validation (`utils/validation.py`) with clear user-facing errors |
| S8 | Logging | Structured `log_event()` / `log_error()` throughout key workflows |
| S9 | Testing | 11 test files covering services, twin logic, memory, and workspace screens |
| S10 | Session | Idempotent `bootstrap_session_state()` prevents double-initialization |
| S11 | Auth | Real Supabase Auth integration (email/password, sign_up, sign_in) |
| S12 | UI Design | Consistent design system via CSS variables (`--dv-*`), responsive grids, hover transitions |
| S13 | Robustness | Weather service graceful fallback; explainability multi-level fallback; all AI calls in try/except |
| S14 | Extensibility | `PersistencePort` Protocol and `simulation_adapter`/`weather_adapter` extension points on TwinIntelligence |
| S15 | Documentation | Module-level docstrings, config comments, THI formula attribution with citation |

---

## 12. Current Weaknesses

### Critical / Data Integrity

| # | Issue | Impact |
|---|-------|--------|
| W1 | **All entity data is in-memory only** — `SupabaseClient._tables` is a Python dict. A server restart or new session loses all cows, farms, observations, and twin snapshots | Data loss on every restart |
| W2 | **FarmTwin and HerdTwin are never connected** — cows managed directly via `CowService._cow_twins` dict without being registered into `HerdTwin.cows` | Herd-level twin aggregation entirely broken |
| W3 | **`HerdTwin.aggregate_snapshot_summary()` bug** — `average_thi` computation loop body is `sum([value.get(...) for value in []])` which always evaluates to 0 | THI aggregation always returns None |
| W4 | **Farm ID is collision-prone** — `f"farm-{name.lower().replace(' ', '-')}"` — no uniqueness check or sanitization | Silent data corruption for duplicate farm names |

### Architecture / Design

| # | Issue | Impact |
|---|-------|--------|
| W5 | **Direct access to private service internals** — screens access `cow_service._cow_twins` directly, bypassing service API | Tight coupling; hard to refactor |
| W6 | **Dual routing systems** — both `pages/` (Streamlit multi-page) and `app.py` (manual section routing) coexist | Navigation confusion |
| W7 | **Services stored as Python objects in `st.session_state`** — mutable internal state can silently drift | Hard-to-debug state corruption |
| W8 | **No real Supabase DB writes** — all CRUD writes to in-memory dict; SDK client used for auth only | No actual backend persistence |
| W9 | **`_normalize_observation()` duplicated 4x across screens** — identical code in digital_twin.py, prediction.py, explainability.py, cow_profile.py | DRY violation; bug fixes must be applied 4x |

### Performance / Scalability

| # | Issue | Impact |
|---|-------|--------|
| W10 | **`prepare_feature_frame()` loads entire CSV on cold start** — first user of session loads full dataset | Cold-start latency |
| W11 | **SHAP computation is synchronous and blocking** — no async; blocks Streamlit thread during observation submission | UI freezes during heavy computation |
| W12 | **No pagination in herd list** — all cows loaded into memory and rendered at once | Performance degrades with large herds |

### UX / Completeness

| # | Issue | Impact |
|---|-------|--------|
| W13 | **Weather coordinates hardcoded** to Bangalore (lat=12.97, lon=77.59) | Wrong weather data for non-Bangalore farms |
| W14 | **No "forgot password" or email verification flow** | Cannot recover locked accounts |
| W15 | **No auto-populate temperature/humidity from weather** in daily operations form | Inaccurate observations; UX friction |
| W16 | **Genetics module not integrated** — no way to view genetics results in UI | Feature gap |
| W17 | **Health thresholds assume Holstein cattle** — USDA/NRC 2001 THI thresholds may not apply to Indian breeds (Sahiwal, Gir) | Incorrect health alerts for local breeds |
| W18 | **No cow deletion confirmation modal** — cows deletable without warning | Accidental data loss |
| W19 | **`app_old.py` committed to repo** — 16KB of dead code in main webapp directory | Maintenance confusion |
| W20 | **Research pages and production pages share `pages/` directory** — model-performance pages visible to end users | Unprofessional UX |

### Testing / Quality

| # | Issue | Impact |
|---|-------|--------|
| W21 | **Tests are mostly unit-level** — no end-to-end tests covering observation -> twin -> dashboard pipeline | Regressions may pass unit tests |
| W22 | **`test_webapp_ui.py` is only 607 bytes** — likely a placeholder | Low UI test confidence |

---

*End of Audit — `docs/project_audit/01_project_overview.md`*

*Generated by architectural analysis of all source files. No code was modified.*
