"""
evaluate_all_models.py
======================
Evaluate all candidate regression models on the same held-out test split,
then save a comparison table and graphs for report use.

Usage:
    python evaluate_all_models.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error, mean_absolute_percentage_error,
    mean_squared_error, r2_score
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

sys.path.insert(0, os.path.dirname(__file__))
from config import OUTPUT_DIR, MODEL_PARAMS, RANDOM_SEED
from data_loader import load_and_prepare
from feature_engineering import build_features
from weather import fetch_weather


def compute_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    return {
        "R2": r2,
        "MAE": mae,
        "RMSE": rmse,
        "MAPE_pct": mape,
    }


def load_tuned_xgboost_params():
    tuning_path = os.path.join(OUTPUT_DIR, "tuning_results.json")
    if os.path.exists(tuning_path):
        with open(tuning_path, "r") as f:
            tuning = json.load(f)
        xgb_params = tuning.get("XGBoost", {})
        if xgb_params:
            return xgb_params
    return MODEL_PARAMS["XGBoost"]


def build_models():
    xgb_params = load_tuned_xgboost_params()
    return {
        "Naive Baseline": DummyRegressor(strategy="mean"),
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(**MODEL_PARAMS["Decision Tree"]),
        "Random Forest": RandomForestRegressor(**MODEL_PARAMS["Random Forest"]),
        "XGBoost": XGBRegressor(**xgb_params, verbosity=0),
    }


def highlight_best(df, metric="R2"):
    best = df[metric].idxmax()
    df["Best"] = df.index == best
    return best


def plot_r2_comparison(df, path):
    df_plot = df.copy()
    df_plot["Color"] = np.where(df_plot["Best"], "Best model", "Other models")
    fig = px.bar(
        df_plot,
        x="Model",
        y="R2",
        color="Color",
        color_discrete_map={"Best model": "#1D9E75", "Other models": "#7F7F7F"},
        title="Model Comparison — R² on Held-Out Test Set",
        text=df_plot["R2"].round(4),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="R²", xaxis_title="Model", width=900, height=520)
    fig.write_image(path)
    return fig


def plot_error_comparison(df, path):
    df_long = df.melt(
        id_vars=["Model", "Best"],
        value_vars=["MAE", "RMSE", "MAPE_pct"],
        var_name="Metric",
        value_name="Value",
    )
    df_long["Metric Label"] = df_long["Metric"].replace({
        "MAPE_pct": "MAPE (%)",
    })
    fig = px.bar(
        df_long,
        x="Model",
        y="Value",
        color="Metric Label",
        barmode="group",
        text_auto='.2f',
        title="Model Comparison — Test-set Error Metrics",
        labels={"Value": "Metric value", "Model": "Model"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(width=1000, height=560, uniformtext_minsize=8, uniformtext_mode='hide')
    fig.write_image(path)
    return fig


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_clean = load_and_prepare()
    base_temp, base_hum = fetch_weather()
    _, X, y = build_features(df_clean, base_temp, base_hum)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, shuffle=True
    )

    models = build_models()
    records = []

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = compute_metrics(y_test, y_pred)
        records.append({"Model": name, **metrics})

    df_metrics = pd.DataFrame(records)
    df_metrics = df_metrics.set_index("Model")
    best_model = highlight_best(df_metrics, metric="R2")

    summary_path = os.path.join(OUTPUT_DIR, "model_comparison_test_metrics.csv")
    df_metrics.to_csv(summary_path)

    plot_r2_comparison(df_metrics.reset_index(), os.path.join(OUTPUT_DIR, "model_comparison_r2.png"))
    plot_error_comparison(df_metrics.reset_index(), os.path.join(OUTPUT_DIR, "model_comparison_error_metrics.png"))

    print("Saved model comparison metrics and graphs to outputs/")
    print(f"Best model by R²: {best_model}")
    print(df_metrics)


if __name__ == "__main__":
    main()
