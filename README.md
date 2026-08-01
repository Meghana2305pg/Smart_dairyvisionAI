# Smart Dairy Farm Digital Twin

A research-grade machine learning pipeline for predicting milk yield under real-time ambient conditions, with a digital twin workspace and operational monitoring experience.

## What changed in the hardening pass

- Session persistence now keeps authentication, farm context, selected cows, and navigation state consistent.
- Login, registration, farm setup, cow registration, and daily operations now use validation helpers and user-friendly error messaging.
- Major workflows emit structured logs and expose loading states for long-running operations.
- Deployment preparation now includes environment variables, dependency checks, and Docker support scaffolding.

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy [.env.example](.env.example) to .env and set the required values.

### 3. Run the app locally

```bash
streamlit run webapp/app.py
```

### 4. Optional Docker run

```bash
docker build -t dairyvision-ai .
docker run -p 8501:8501 --env-file .env dairyvision-ai
```

## Project structure

- [webapp/app.py](webapp/app.py) – application entry point and session flow
- [webapp/screens](webapp/screens) – dashboard, herd, daily operations, analytics, explainability, and command centre workspaces
- [webapp/services](webapp/services) – auth, farm, cow, observation, and dashboard services
- [webapp/digital_twin](webapp/digital_twin) – twin state and twin intelligence logic
- [tests](tests) – regression and workflow coverage

## Verification

Run the following before deployment:

```bash
python -m compileall webapp tests
python -m unittest discover -s tests
```

## Additional docs

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [CHANGELOG.md](CHANGELOG.md)
