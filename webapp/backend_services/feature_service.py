"""Wrapper service for preparing features using the existing feature engineering pipeline."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from webapp.backend_services._bootstrap import ensure_project_on_path
from webapp.config.settings import DEFAULT_BASE_HUM, DEFAULT_BASE_TEMP

ensure_project_on_path()


@st.cache_data(show_spinner=False)
def prepare_feature_frame(base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> tuple[Any, Any, Any]:
    """Reuse the existing data loading and feature engineering pipeline with caching."""
    try:
        from data_loader import load_and_prepare
        from feature_engineering import build_features
    except ImportError as exc:
        raise RuntimeError("The existing data-loading and feature-engineering backend could not be imported.") from exc

    df_clean = load_and_prepare()
    df_full, X, y = build_features(df_clean, base_temp=base_temp, base_hum=base_hum)
    return df_full, X, y


@st.cache_data(show_spinner=False)
def get_feature_defaults(base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> dict[str, Any]:
    """Return sensible default values for the interactive UI from the existing training data."""
    _, X, _ = prepare_feature_frame(base_temp=base_temp, base_hum=base_hum)
    defaults: dict[str, Any] = {}
    for column in X.columns:
        series = X[column]
        if pd.api.types.is_numeric_dtype(series):
            defaults[column] = float(series.mean())
        else:
            defaults[column] = series.mode().iloc[0] if not series.mode().empty else 0

    defaults.update({
        "age": defaults.get("age", 36.0),
        "weight": defaults.get("weight", 450.0),
        "feed": defaults.get("feed", 20.0),
        "health_status": int(round(defaults.get("health_status", 0))),
        "temperature": base_temp,
        "humidity": base_hum,
    })
    return defaults


def build_feature_row(input_row: dict[str, Any], base_temp: float = DEFAULT_BASE_TEMP, base_hum: float = DEFAULT_BASE_HUM) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Build a one-row feature matrix from current user input values using the existing engineering logic."""
    print("STEP 7 build_feature_row")
    try:
        from config import ALL_FEATURES, TARGET
        from feature_engineering import add_engineered_features
    except ImportError as exc:
        raise RuntimeError("The existing feature-engineering backend could not be imported.") from exc

    defaults = get_feature_defaults(base_temp=base_temp, base_hum=base_hum)
    print("STEP 7a get_feature_defaults")
    row_data = {
        "age": float(input_row.get("age", defaults.get("age", 36.0))),
        "weight": float(input_row.get("weight", defaults.get("weight", 450.0))),
        "health_status": int(input_row.get("health_status", defaults.get("health_status", 0))),
        "feed": float(input_row.get("feed", defaults.get("feed", 20.0))),
        "temperature": float(input_row.get("temperature", base_temp)),
        "humidity": float(input_row.get("humidity", base_hum)),
        TARGET: 0.0,
    }

    row_df = pd.DataFrame([row_data])
    row_df = add_engineered_features(row_df)
    row_df = row_df.dropna(subset=ALL_FEATURES + [TARGET]).reset_index(drop=True)
    X_row = row_df[ALL_FEATURES]
    y_row = row_df[TARGET]
    return row_df, X_row, y_row
