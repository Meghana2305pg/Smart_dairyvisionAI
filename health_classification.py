"""
health_classification.py
=======================
Separate cattle health-status classification experiment.

This module is intentionally isolated from the milk-yield regression pipeline.
It uses the same merged cattle dataset and the existing binary health label
(`health_status`) to build a proper held-out test evaluation for the health
classification objective.

It does NOT modify the regression model, tuning logic, or digital-twin
simulation pipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from data_loader import load_and_prepare
from feature_engineering import add_engineered_features, assign_weather

logger = logging.getLogger(__name__)

CLASSIFICATION_FEATURES = [
    "age",
    "weight",
    "feed",
    "temperature",
    "humidity",
    "thi",
    "feed_weight_ratio",
    "feed_per_weight",
    "temp_humidity",
    "thi_squared",
    "feed_thi_interaction",
    "age_weight_ratio",
]


def prepare_classification_dataset() -> pd.DataFrame:
    """Build the feature matrix for the health classification objective.

    We intentionally reuse the same dataset-cleaning and feature-engineering
    workflow as the milk-yield pipeline, but we do not save or modify the
    regression outputs. This keeps the classification experiment separate and
    faithful to the current data.
    """
    df = load_and_prepare()
    df = assign_weather(df, base_temp=28.0, base_hum=65.0)
    df = add_engineered_features(df)

    required = [*CLASSIFICATION_FEATURES, "health_status"]
    df = df.dropna(subset=required).reset_index(drop=True)
    return df


def plot_confusion_matrix(cm: np.ndarray, output_path: str | Path) -> str:
    """Save a publication-ready confusion matrix figure."""
    labels = ["Healthy", "Diseased"]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title("Health-status confusion matrix")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


def compute_classification_metrics(y_true: pd.Series | np.ndarray,
                                  y_pred: pd.Series | np.ndarray) -> dict[str, float]:
    """Compute classification metrics on a held-out test set."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def plot_training_validation_loss(history: dict, output_path: str | Path) -> str:
    """Save the XGBoost training/validation log-loss curve for the tuned model."""
    fig, ax = plt.subplots(figsize=(7, 4.5))

    valid_keys = [k for k in history if "validation" in k]
    if not valid_keys:
        raise ValueError("Training history does not contain validation logloss data.")

    train_key = next((k for k in history if "validation_0" in k), None)
    valid_key = next((k for k in history if "validation_1" in k), None)
    if train_key is None or valid_key is None:
        train_key = list(history.keys())[0]
        valid_key = list(history.keys())[-1]

    train_vals = history[train_key]["logloss"]
    valid_vals = history[valid_key]["logloss"]
    x = np.arange(1, len(train_vals) + 1)

    ax.plot(x, train_vals, label="Training loss", linewidth=2)
    ax.plot(x, valid_vals, label="Validation loss", linewidth=2)
    ax.set_xlabel("Boosting round")
    ax.set_ylabel("Log loss")
    ax.set_title("Health-status classification: training vs validation loss")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(output_path)


def build_health_classification_outputs(output_root: str | Path | None = None) -> tuple[dict[str, float], list[str], list[str]]:
    """Train a tuned XGBoost classifier and compare it with the current baseline.

    The same train/validation/test split is used for both models. The validation
    set is used to select the tuned hyperparameters and the hold-out test set is
    kept untouched for the final paper-ready metrics.
    """
    output_root = Path(output_root) if output_root is not None else Path("research_outputs")
    figures_dir = output_root / "figures"
    tables_dir = output_root / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    df = prepare_classification_dataset()
    X = df[CLASSIFICATION_FEATURES].copy()
    y = df["health_status"].astype(int)

    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full,
        y_train_full,
        test_size=0.20,
        random_state=42,
        stratify=y_train_full,
    )

    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    scale_pos_weight = (n_neg / n_pos) if n_pos else 1.0

    baseline_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        learning_rate=0.05,
        max_depth=4,
        n_estimators=300,
        subsample=0.9,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )
    baseline_model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=False,
    )
    baseline_pred = baseline_model.predict(X_test)
    baseline_metrics = compute_classification_metrics(y_test, baseline_pred)
    baseline_cm = confusion_matrix(y_test, baseline_pred, labels=[0, 1])

    tuned_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        learning_rate=0.03,
        max_depth=3,
        n_estimators=600,
        subsample=0.8,
        colsample_bytree=0.9,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
    )
    tuned_model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=False,
    )
    tuned_pred = tuned_model.predict(X_test)
    tuned_metrics = compute_classification_metrics(y_test, tuned_pred)
    tuned_cm = confusion_matrix(y_test, tuned_pred, labels=[0, 1])

    metrics_csv_path = tables_dir / "health_classification_metrics.csv"
    confusion_csv_path = tables_dir / "health_classification_confusion_matrix.csv"
    confusion_plot_path = figures_dir / "health_classification_confusion_matrix.png"
    loss_plot_path = figures_dir / "health_classification_loss_curve.png"

    comparison_df = pd.DataFrame([
        {"model": "baseline", **baseline_metrics},
        {"model": "tuned_xgb", **tuned_metrics},
    ])
    comparison_df.to_csv(metrics_csv_path, index=False)

    tuned_confusion_df = pd.DataFrame(
        tuned_cm,
        index=["Actual Healthy", "Actual Diseased"],
        columns=["Predicted Healthy", "Predicted Diseased"],
    )
    tuned_confusion_df.to_csv(confusion_csv_path)

    plot_confusion_matrix(tuned_cm, confusion_plot_path)
    plot_training_validation_loss(tuned_model.evals_result(), loss_plot_path)

    print("\n=== FINAL HEALTH-STATUS CLASSIFICATION TEST SET METRICS ===")
    print(f"Baseline: {baseline_metrics}")
    print(f"Tuned XGB: {tuned_metrics}")
    print("Confusion matrix (tuned XGB):")
    print(tuned_confusion_df)

    logger.info("Health classification baseline metrics: %s", baseline_metrics)
    logger.info("Health classification tuned metrics: %s", tuned_metrics)
    logger.info("Saved classification figures: %s", [str(confusion_plot_path), str(loss_plot_path)])
    logger.info("Saved classification tables: %s", [str(metrics_csv_path), str(confusion_csv_path)])

    return tuned_metrics, [str(confusion_plot_path), str(loss_plot_path)], [str(metrics_csv_path), str(confusion_csv_path)]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
    metrics, figure_paths, csv_paths = build_health_classification_outputs()
    print("\nFinal tuned model metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    logger.info("Health classification final metrics: %s", metrics)
    logger.info("Saved classification figures: %s", figure_paths)
    logger.info("Saved classification tables: %s", csv_paths)
