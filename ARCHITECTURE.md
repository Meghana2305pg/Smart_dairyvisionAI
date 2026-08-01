# Architecture Overview

## Runtime layers

- Streamlit frontend renders the application shell and routes users across the onboarding, dashboard, analytics, and twin workspaces.
- Service layer coordinates authentication, farm, cow, and observation workflows while keeping the UI thin.
- Digital twin layer owns per-cow state, recommendations, and snapshots without altering prediction logic.
- Repository layer persists app data and can be backed by local in-memory storage or Supabase-compatible services.

## Data flow

1. The user authenticates and creates or joins a farm.
2. The app stores farm, cow, and observation state in session state for continuity across navigation.
3. Daily operations and digital twin workspaces consume the same services to keep behavior consistent.
4. Dashboards assemble summaries from those services without changing the underlying ML or twin behavior.

## Deployment considerations

- Keep environment variables in .env or deployment secrets.
- The web app can run with `streamlit run webapp/app.py`.
- Optional containers can wrap the same entrypoint for production deployment.
