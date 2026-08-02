# Phase 7 — Digital Twin 2.0 Architecture Plan

## Goal

Prepare a scalable Digital Twin 2.0 architecture for DairyVision AI without rewriting the existing application. The design preserves the current Streamlit screens, service layer, repositories, and session-state flow while introducing a more extensible twin model for snapshots, history, playback, and future scenario simulation.

## Scope guardrails

- Do not redesign the application shell.
- Do not change existing routing behavior.
- Do not change session-state keys unless strictly required for a backward-compatible extension.
- Do not replace the current prediction, health, or explainability services.
- Keep the current UI stable and additive.

---

## 1. Existing architecture

### 1.1 Current digital twin package

The current digital-twin layer lives in the package [webapp/digital_twin](../webapp/digital_twin):

- CowTwin
  - Represents one cow.
  - Owns observation history, latest observation, latest AI outputs, recommendations, and an in-memory snapshot store.
  - Updates are driven by `record_observation()` and `refresh_from_ai()`.

- HerdTwin
  - Aggregates multiple cows into a herd-level twin.
  - Maintains herd-level state and simple aggregate summaries.

- FarmTwin
  - Represents the farm as a higher-level digital-twin context.
  - Aggregates herd-level information and exposes a coarse farm snapshot.

- TwinState
  - Stores evolving twin state: status, timestamps, context, observations, predictions, health assessments, explanations, recommendations, and simulations.
  - Supports serialization for future persistence.

- TwinIntelligence
  - Coordinates the existing AI services:
    - prediction service
    - health service
    - explainability service
    - weather service
  - Produces a structured `TwinIntelligenceResult` for each observation.

- Observation
  - Lightweight data container used when creating a new observation.

- TwinSnapshot
  - Immutable value object storing a single captured twin state.

- InMemorySnapshotStore
  - Stores ordered snapshot history per cow in memory.

### 1.2 Current twin state class

The current `TwinState` is intentionally simple and additive. It stores the latest status and grouped histories, but it does not yet model:

- event timelines as first-class entities
- versioned snapshots over time
- playback state
- what-if simulation state
- explicit temporal relationships between observations and AI outputs

### 1.3 Current twin engine

The current “engine” is effectively the combination of:

- `CowTwin.refresh_from_ai()`
- `TwinIntelligence.analyze_observation()`
- `build_recommendations()`
- `InMemorySnapshotStore.save_snapshot()`

This means a twin update is currently composed of:

1. A new observation is recorded.
2. The observation is passed through the intelligence layer.
3. Prediction, health, explainability, and optional simulation results are merged.
4. Recommendations are derived.
5. A snapshot is stored.

### 1.4 Current data flow

The current data flow is:

1. Daily Operations or other entry points create an `Observation`.
2. `ObservationService.record_observation()` persists the observation and triggers twin updates.
3. `CowTwin.record_observation()` stores the observation in the cow twin.
4. `CowTwin.refresh_from_ai()` calls `TwinIntelligence.analyze_observation()`.
5. Existing AI services generate prediction, health, explanation, and optional weather data.
6. Recommendations are created.
7. A `TwinSnapshot` is persisted to the in-memory snapshot store.
8. Dashboards, Digital Twin, Cow Profile, and Prediction screens read from the twin object and/or snapshot history.

### 1.5 Current update mechanism

The current update mechanism is event-driven but local and in-memory:

- A new observation triggers a fresh twin recomputation.
- The local `CowTwin` object is updated in memory.
- Snapshot history accumulates in `InMemorySnapshotStore`.
- Screens read from the same in-memory twin objects.

This is good for stability, but it lacks a formal timeline/history engine.

---

## 2. Proposed Digital Twin 2.0 architecture

### 2.1 Design principle

Digital Twin 2.0 should be an additive extension of the current model, not a replacement.

The existing public behavior should remain intact:

- `CowTwin` still exists.
- `FarmTwin` and `HerdTwin` still exist.
- `TwinIntelligence` still orchestrates the same services.
- Current screens still work through the same service flow.

The extension introduces a richer internal architecture for time-aware twin behavior while keeping the existing UI and business flow stable.

### 2.2 Proposed layers

Digital Twin 2.0 will introduce four layered capabilities on top of the current model:

1. Snapshot Engine
   - Captures immutable states over time.
   - Reuses the existing `TwinSnapshot` concept, but expands it into a richer, versioned timeline record.

2. Timeline and History Layer
   - Stores ordered events, observations, AI outputs, and recommendation changes.
   - Provides event-based access for UI history views and future playback.

3. Playback Controller
   - Replays twin state across time for review.
   - Supports “jump to previous state” and “replay recent changes” without re-running the current application logic.

4. What-If Simulator (future-ready)
   - Adds a placeholder extension point for scenario simulation.
   - Does not affect current screens until explicitly activated.

### 2.3 Compatibility strategy

To avoid breaking the app:

- Keep the current `CowTwin` methods and fields intact.
- Add optional, non-breaking extension methods such as:
  - `capture_snapshot()`
  - `get_history()`
  - `get_timeline()`
  - `playback_state()`
  - `simulate_scenario()`
- Preserve the current `latest_prediction`, `latest_health`, `latest_explanation`, and `recommendations` fields.
- Route phase-7 UI enhancements through read-only adapters instead of replacing existing screens.

---

## 3. Snapshot Engine

### 3.1 Purpose

The Snapshot Engine will make twin updates explicit and durable over time.

Instead of only storing the latest AI output, Digital Twin 2.0 will capture:

- observation payload
- prediction output
- health result
- explanation output
- recommendation state
- timestamp
- twin status
- metadata

### 3.2 Proposed behavior

Each update should create a structured snapshot with:

- a stable snapshot identifier
- the cow identifier
- a timestamp
- the latest observation context
- the AI result payload
- the derived recommendation set
- the resulting twin status
- metadata for tracing and playback

### 3.3 Compatibility with current code

The existing `TwinSnapshot` can remain as the core record type. The Snapshot Engine will simply enrich how snapshots are created and consumed.

The current `InMemorySnapshotStore` can evolve to support:

- ordered per-cow histories
- latest-state lookup
- range-based history lookup
- timeline export helpers

### 3.4 Planned responsibilities

- `CowTwin` creates snapshots after each refresh.
- `SnapshotEngine` standardizes snapshot creation.
- `InMemorySnapshotStore` persists and retrieves snapshots.
- Screens continue to consume the latest snapshot, while future features can query richer history.

---

## 4. Timeline

### 4.1 Purpose

The timeline layer will provide a chronological view of the cow’s twin evolution.

This is different from the current simple observation list because it will represent:

- observation events
- prediction updates
- health assessments
- recommendation changes
- user-facing state transitions

### 4.2 Proposed timeline model

A timeline entry should contain:

- event type
- timestamp
- entity id
- summary text
- payload reference
- associated snapshot id

### 4.3 Integration points

- `CowTwin` will emit timeline events after each update.
- `TwinState` will store timeline entries or reference them.
- Future UI surfaces can query timeline entries without adding new backend logic paths.

### 4.4 Benefit

The timeline enables:

- richer history views on Cow Profile and Digital Twin
- easier playback
- better auditing of recommendations and risk changes

---

## 5. Playback

### 5.1 Purpose

Playback will let the user review the twin’s evolution over time without re-running the data pipeline.

### 5.2 Proposed approach

Playback should reuse previously captured snapshots and timeline events:

- select a snapshot or timeline range
- reconstruct the twin state from that moment
- render the state in a read-only view

### 5.3 Compatibility plan

Playback should not affect the live twin update path.

Instead of replacing current logic, playback becomes a read-only view over historical data:

- current live twin remains active for normal app use
- playback view renders historical snapshots from the store
- no user session or routing logic needs to change

### 5.4 Expected interaction model

- A user opens the Digital Twin or Cow Profile.
- The app shows the latest live state.
- A future playback control can move backward through history and render prior states.

---

## 6. Twin History

### 6.1 Purpose

Twin History provides a structured, queryable history of the cow’s digital-twin evolution.

### 6.2 What it should include

- observation history
- prediction history
- health history
- explanation history
- recommendation history
- snapshot history
- timeline history

### 6.3 Proposed storage concept

The current in-memory store should evolve into a history-oriented store that can answer questions like:

- What was the twin state at 10:00?
- What changed after the latest observation?
- Which recommendations were present at the prior snapshot?

### 6.4 Why it matters

Twin History is the foundation for both playback and future simulation.

---

## 7. Future What-If Simulator

### 7.1 Purpose

The What-If Simulator is a future-facing extension that will let the user test hypothetical conditions without changing live data.

Examples:

- simulate higher heat stress
- simulate reduced feed intake
- simulate different weather conditions
- simulate a change in health status or management action

### 7.2 Proposed architecture

The simulator should not be wired into the current live workflow yet. Instead, it should be introduced as an optional extension point:

- `TwinIntelligence` already has a `simulation_adapter` extension point.
- That can later be expanded into a richer simulation engine.
- The simulator should write to a separate simulation branch or preview state rather than mutate the live twin.

### 7.3 Compatibility plan

The current application remains stable because the simulator will be read-only and optional. It will not replace the existing prediction logic or current data flow.

---

## 8. How all components will interact

### 8.1 Runtime flow for the proposed architecture

1. A user records an observation through Daily Operations.
2. `ObservationService` persists the observation.
3. `CowTwin` records the observation and asks the intelligence layer to analyze it.
4. `TwinIntelligence` runs existing prediction, health, and explainability services.
5. The twin produces updated recommendations and status.
6. The Snapshot Engine captures a new snapshot.
7. The Timeline and History layer record the event.
8. Current UI screens continue to read the latest live state.
9. Optional playback and what-if features read the saved snapshots/history instead of recomputing from the live runtime.

### 8.2 Interaction map

- Daily Operations
  - entry point for new observations
  - feeds the live twin update path

- Herd Management
  - selects cows and exposes cow-level context
  - remains compatible with the current twin lookup model

- Cow Profile
  - reads the current twin state plus history for richer displays

- Digital Twin screen
  - consumes live state and can later consume historical snapshot/playback views

- Prediction Service
  - remains the existing prediction engine
  - used by TwinIntelligence without modification

- Health Service
  - remains the current health engine
  - becomes one input into the richer twin state model

- Recommendation Engine
  - remains grounded in the current recommendation logic
  - will be extended to work from richer timeline and snapshot context

- Supabase repositories
  - continue to provide persistence for observations, cows, and farm data
  - remain separate from the twin runtime model

- Dashboard
  - continues to aggregate from services and twin objects
  - can later include snapshot and history summaries

- Session State
  - continues to store current workspace selection and navigation state
  - will only receive additive keys if required for playback or simulator features

---

## 9. Files expected to be modified during Phase 7

The following files are the Phase 7 implementation touchpoints for the architecture work described above:

### Core digital twin package

- [webapp/digital_twin/twin_state.py](../webapp/digital_twin/twin_state.py)
- [webapp/digital_twin/cow_twin.py](../webapp/digital_twin/cow_twin.py)
- [webapp/digital_twin/herd_twin.py](../webapp/digital_twin/herd_twin.py)
- [webapp/digital_twin/farm_twin.py](../webapp/digital_twin/farm_twin.py)
- [webapp/digital_twin/twin_intelligence.py](../webapp/digital_twin/twin_intelligence.py)
- [webapp/digital_twin/observation.py](../webapp/digital_twin/observation.py)
- [webapp/digital_twin/decision_support.py](../webapp/digital_twin/decision_support.py)

### Memory and snapshot layer

- [webapp/digital_twin/memory/snapshot.py](../webapp/digital_twin/memory/snapshot.py)
- [webapp/digital_twin/memory/memory_store.py](../webapp/digital_twin/memory/memory_store.py)
- [webapp/digital_twin/memory/health_history.py](../webapp/digital_twin/memory/health_history.py)
- [webapp/digital_twin/memory/observation_history.py](../webapp/digital_twin/memory/observation_history.py)
- [webapp/digital_twin/memory/prediction_history.py](../webapp/digital_twin/memory/prediction_history.py)
- [webapp/digital_twin/memory/recommendation_history.py](../webapp/digital_twin/memory/recommendation_history.py)
- [webapp/digital_twin/memory/weather_history.py](../webapp/digital_twin/memory/weather_history.py)

### Services and repositories

- [webapp/services/cow_service.py](../webapp/services/cow_service.py)
- [webapp/services/observation_service.py](../webapp/services/observation_service.py)
- [webapp/services/dashboard_service.py](../webapp/services/dashboard_service.py)
- [webapp/repositories/supabase_client.py](../webapp/repositories/supabase_client.py)
- [webapp/repositories/observation_repository.py](../webapp/repositories/observation_repository.py)
- [webapp/repositories/cow_repository.py](../webapp/repositories/cow_repository.py)
- [webapp/repositories/farm_repository.py](../webapp/repositories/farm_repository.py)

### Screens and UI surfaces

- [webapp/screens/digital_twin.py](../webapp/screens/digital_twin.py)
- [webapp/screens/cow_profile.py](../webapp/screens/cow_profile.py)
- [webapp/screens/prediction.py](../webapp/screens/prediction.py)
- [webapp/screens/dashboard.py](../webapp/screens/dashboard.py)
- [webapp/screens/command_centre.py](../webapp/screens/command_centre.py)
- [webapp/screens/herd.py](../webapp/screens/herd.py)

### Session and app shell

- [webapp/app.py](../webapp/app.py)
- [webapp/state/session_state.py](../webapp/state/session_state.py)

> Note: The above list reflects the files most likely to need changes once the Phase 7 architecture is implemented. The initial planning step does not introduce code changes yet.

---

## 10. Recommended implementation order for Phase 7

1. Extend `TwinState` and snapshot structures without removing current fields.
2. Add snapshot creation and history collection to `CowTwin`.
3. Introduce a history/timeline capability in the memory layer.
4. Add read-only playback support as a non-breaking enhancement.
5. Expose richer history in the Digital Twin and Cow Profile views.
6. Prepare the simulation extension point for future What-If functionality.

---

## 11. Architectural conclusion

Digital Twin 2.0 should be implemented as a layered, backward-compatible evolution of the current architecture.

The key idea is:

- keep the current twin and service model intact
- add a richer event, snapshot, history, and playback layer underneath it
- expose new capabilities through read-only and additive interfaces
- preserve the existing app stability while preparing for future simulation features
