"""Application-level settings for the new Streamlit frontend."""

from __future__ import annotations

from pathlib import Path

WEBAPP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = WEBAPP_ROOT.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"
LOG_DIR = PROJECT_ROOT / "logs"
DATASETS_DIR = PROJECT_ROOT / "datasets"

MODEL_PATH = MODELS_DIR / "best_milk_model.pkl"
ENGINEERED_DATASET_PATH = OUTPUT_DIR / "engineered_dataset.csv"

DEFAULT_BASE_TEMP = 28.0
DEFAULT_BASE_HUM = 65.0
