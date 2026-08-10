import joblib
import os
from pathlib import Path

import matplotlib.pyplot as plt
from xgboost import XGBRegressor

from config import MODEL_PATH, OUTPUT_DIR

ROOT = Path(__file__).resolve().parent
output_path = ROOT / "outputs" / "xgboost_training_validation_rmse_curve.png"
os.makedirs(output_path.parent, exist_ok=True)

print("Loading tuned XGBoost model from:", MODEL_PATH)
model = joblib.load(MODEL_PATH)

history = None
if hasattr(model, "evals_result_"):
    history = model.evals_result_
    print("Found model.evals_result_")
else:
    try:
        booster = model.get_booster()
        if hasattr(booster, "evals_result"):
            if callable(booster.evals_result):
                history = booster.evals_result()
            else:
                history = booster.evals_result
            print("Found booster.evals_result")
    except Exception as exc:
        print("Booster inspect error:", exc)

if not history:
    raise RuntimeError(
        "Tuned XGBoost per-round eval history is unavailable in the current model. "
        "Cannot generate the requested training/validation RMSE curve."
    )

print("Eval history keys:", list(history.keys()))

def find_curve_keys(history_dict):
    train_key = None
    valid_key = None
    for key in history_dict:
        lower = key.lower()
        if "train" in lower and train_key is None:
            train_key = key
        if ("valid" in lower or "validation" in lower) and valid_key is None:
            valid_key = key
    if not train_key and len(history_dict) == 2:
        keys = list(history_dict.keys())
        train_key, valid_key = keys[0], keys[1]
    if not valid_key and train_key:
        for key in history_dict:
            if key != train_key:
                valid_key = key
                break
    return train_key, valid_key

train_key, valid_key = find_curve_keys(history)
if train_key is None or valid_key is None:
    raise RuntimeError(
        "Unable to identify both training and validation eval sets in XGBoost history. "
        "Found history keys: {}".format(list(history.keys()))
    )

print('Training history key:', train_key)
print('Validation history key:', valid_key)

train_metrics = history[train_key]
valid_metrics = history[valid_key]

if isinstance(train_metrics, dict):
    if "rmse" in train_metrics:
        train_rmse = train_metrics["rmse"]
    else:
        train_rmse = next((v for k, v in train_metrics.items() if isinstance(v, list)), None)
else:
    train_rmse = train_metrics

if isinstance(valid_metrics, dict):
    if "rmse" in valid_metrics:
        valid_rmse = valid_metrics["rmse"]
    else:
        valid_rmse = next((v for k, v in valid_metrics.items() if isinstance(v, list)), None)
else:
    valid_rmse = valid_metrics

if train_rmse is None or valid_rmse is None:
    raise RuntimeError(
        "Unable to extract RMSE lists from eval history."
    )

n_rounds = min(len(train_rmse), len(valid_rmse))
if len(train_rmse) != len(valid_rmse):
    print(
        f"Warning: training and validation RMSE lengths differ ({len(train_rmse)} vs {len(valid_rmse)}). "
        f"Using first {n_rounds} rounds."
    )

rounds = list(range(1, n_rounds + 1))
train_rmse = train_rmse[:n_rounds]
valid_rmse = valid_rmse[:n_rounds]

fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=300)
ax.plot(rounds, train_rmse, label="Training RMSE", color="#4C78A8", linewidth=2.2, marker="o", markersize=4)
ax.plot(rounds, valid_rmse, label="Validation RMSE", color="#F58518", linewidth=2.2, marker="o", markersize=4)

ax.set_title("XGBoost Training vs Validation RMSE", fontsize=14, fontweight="bold", pad=10)
ax.set_xlabel("Boosting Round", fontsize=11)
ax.set_ylabel("RMSE (L/day)", fontsize=11)
ax.set_xlim(1, n_rounds)
ax.set_axisbelow(True)
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.tick_params(axis="x", labelsize=10)
ax.tick_params(axis="y", labelsize=10)
ax.legend(frameon=False, fontsize=10, loc="best")
fig.tight_layout(pad=0.8)
fig.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close(fig)
print("Saved line graph to:", output_path)
