# Deployment Guide

## Prerequisites

- Python 3.11+
- pip
- Optional: Docker

## Environment configuration

1. Copy [.env.example](.env.example) to .env.
2. Fill in Supabase values if you want to use the hosted repository layer.
3. Set `APP_ENV` and `LOG_LEVEL` for the runtime environment.

## Local startup

```bash
pip install -r requirements.txt
streamlit run webapp/app.py
```

## Optional Docker

```bash
docker build -t dairyvision-ai .
docker run -p 8501:8501 --env-file .env dairyvision-ai
```

## Production notes

- Use a managed secret store for environment variables.
- Enable persistent storage for logs and uploaded artifacts.
- Run the app behind a reverse proxy or container platform with health checks.
