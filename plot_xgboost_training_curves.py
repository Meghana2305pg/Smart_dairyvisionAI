"""
plot_xgboost_training_curves.py
================================
Train the tuned XGBoost model and generate evaluation curves for
loss metrics and R² on the same train/test split.

Usage:
    python plot_xgboost_training_curves.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

sys.path.insert(0, os.path.dirname(__file__))
from config import OUTPUT_DIR, MODEL_PARAMS, RANDOM_SEED
from data_loader import load_and_prepare
from feature_engineering import build_features
from weather import fetch_weather


def load_tuned_xgboost_params():
    tuning_path = os.path.join(OUTPUT_DIR, "tuning_results.json")
    if os.path.exists(tuning_path):
        with open(tuning_path, "r") as f:
            tuning = json.load(f)
        params = tuning.get("XGBoost")
        if params:
            return params
    return MODEL_PARAMS["XGBoost"]


def compute_curve_metrics(model, X, y):
    iteration_count = model.get_booster().best_iteration + 1 if hasattr(model.get_booster(), 'best_iteration') else model.n_estimators
    records = []
    for itr in range(1, model.n_estimators + 1):
        y_train_pred = model.predict(X[0], iteration_range=(0, itr)) if isinstance(X, tuple) else model.predict(X, iteration_range=(0, itr))
        r2 = r2_score(y, y_train_pred)
        rmse = np.sqrt(mean_squared_error(y, y_train_pred))
        mae = mean_absolute_error(y, y_train_pred)
        records.append({"iteration": itr, "R2": r2, "RMSE": rmse, "MAE": mae})
    return pd.DataFrame(records)


def build_plotly_curve(df, title, y_col, y_label, path):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["iteration"], y=df[f"train_{y_col}"], mode="lines", name="Train"))
    fig.add_trace(go.Scatter(x=df["iteration"], y=df[f"test_{y_col}"], mode="lines", name="Test"))
    fig.update_layout(
        title=title,
        xaxis_title="Boosting round",
        yaxis_title=y_label,
        width=900,
        height=520,
        legend_title="Dataset"
    )
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

    xgb_params = load_tuned_xgboost_params()
    xgb_params = {**xgb_params, "verbosity": 0, "n_jobs": -1, "eval_metric": ["rmse", "mae"]}
    print("Using XGBoost parameters:")
    print(json.dumps(xgb_params, indent=2))

    model = XGBRegressor(**xgb_params)
    eval_set = [(X_train, y_train), (X_test, y_test)]
    model.fit(
        X_train,
        y_train,
        eval_set=eval_set,
        verbose=False,
    )
    evals_result = model.evals_result()

    # Build loss curves from evals_result
    iters = list(range(1, len(evals_result["validation_0"]["rmse"]) + 1))
    df_loss = pd.DataFrame({
        "iteration": iters,
        "train_rmse": evals_result["validation_0"]["rmse"],
        "test_rmse": evals_result["validation_1"]["rmse"],
        "train_mae": evals_result["validation_0"]["mae"],
        "test_mae": evals_result["validation_1"]["mae"],
    })

    # Compute R² per iteration
    df_r2 = []
    for itr in iters:
        train_pred = model.predict(X_train, iteration_range=(0, itr))
        test_pred = model.predict(X_test, iteration_range=(0, itr))
        df_r2.append({
            "iteration": itr,
            "train_r2": r2_score(y_train, train_pred),
            "test_r2": r2_score(y_test, test_pred),
        })
    df_r2 = pd.DataFrame(df_r2).rename(columns={"train_r2": "train_R2", "test_r2": "test_R2"})

    # Save CSVs
    df_loss.to_csv(os.path.join(OUTPUT_DIR, "xgboost_loss_curve.csv"), index=False)
    df_r2.to_csv(os.path.join(OUTPUT_DIR, "xgboost_r2_curve.csv"), index=False)

    # Save plots
    build_plotly_curve(
        df_loss.rename(columns={"train_rmse": "train_RMSE", "test_rmse": "test_RMSE"}),
        "XGBoost Training vs Test RMSE",
        "RMSE",
        "RMSE",
        os.path.join(OUTPUT_DIR, "xgboost_rmse_curve.png"),
    )
    build_plotly_curve(
        df_loss.rename(columns={"train_mae": "train_MAE", "test_mae": "test_MAE"}),
        "XGBoost Training vs Test MAE",
        "MAE",
        "MAE",
        os.path.join(OUTPUT_DIR, "xgboost_mae_curve.png"),
    )
    build_plotly_curve(
        df_r2,
        "XGBoost Training vs Test R²",
        "R2",
        "R²",
        os.path.join(OUTPUT_DIR, "xgboost_r2_curve.png"),
    )

    final_metrics = {
        "train_R2": r2_score(y_train, model.predict(X_train)),
        "test_R2": r2_score(y_test, model.predict(X_test)),
        "train_RMSE": np.sqrt(mean_squared_error(y_train, model.predict(X_train))),
        "test_RMSE": np.sqrt(mean_squared_error(y_test, model.predict(X_test))),
        "train_MAE": mean_absolute_error(y_train, model.predict(X_train)),
        "test_MAE": mean_absolute_error(y_test, model.predict(X_test)),
    }
    pd.Series(final_metrics).to_csv(os.path.join(OUTPUT_DIR, "xgboost_final_metrics.csv"))

    print("Saved XGBoost training curves and metrics to outputs/")
    print(json.dumps(final_metrics, indent=2))


if __name__ == "__main__":
    main()
