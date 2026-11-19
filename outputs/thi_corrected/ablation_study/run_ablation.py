"""
Ablation Study — Contribution of Weather Features
===================================================
Three experiments using Linear Regression:
  A: Biological/Production features only
  B: Bio + Basic Weather
  C: Bio + Weather + THI features

Dataset  : outputs/thi_corrected/engineered_dataset.csv
Split    : 80/20, random_state=42 (identical to five-model stage)
CV       : 5-fold KFold, shuffle=True, random_state=42
Pipeline : StandardScaler → LinearRegression (fitted inside each fold)
Outputs  : ablation_results.csv, ablation_cv_scores.csv,
           ablation_comparison.png, ablation_report.md
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = "/Users/sanjana/Smart_dairyvisionAI"
DATASET_PATH = os.path.join(PROJECT_ROOT, "outputs/thi_corrected/engineered_dataset.csv")
OUT_DIR      = os.path.join(PROJECT_ROOT, "outputs/thi_corrected/ablation_study")

# ── Feature sets ─────────────────────────────────────────────────────────────
EXP_A = ["age", "weight", "health_status", "feed", "feed_weight_ratio", "age_weight_ratio"]
EXP_B = EXP_A + ["temperature", "humidity", "temp_humidity"]
EXP_C = EXP_B + ["thi", "thi_squared", "feed_thi_interaction"]

EXPERIMENTS = {
    "A_Bio_Only":        EXP_A,
    "B_Bio_Weather":     EXP_B,
    "C_Bio_Weather_THI": EXP_C,
}

TARGET = "milk_output"
RANDOM_SEED = 42
CV_FOLDS    = 5
EPSILON     = 1e-6   # MAPE guard

# ── Load dataset ─────────────────────────────────────────────────────────────
print(f"Loading dataset: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")

# Verify features exist
all_required = set(EXP_C + [TARGET])
missing = all_required - set(df.columns)
if missing:
    print(f"\nERROR: Missing columns in dataset: {missing}")
    sys.exit(1)
print("  All required features confirmed present in dataset.\n")

# ── Split (identical parameters to five-model stage) ─────────────────────────
X_full = df[EXP_C]  # widest superset; we'll slice per experiment
y      = df[TARGET]

X_train_full, X_test_full, y_train, y_test = train_test_split(
    X_full, y, test_size=0.20, random_state=RANDOM_SEED
)
print(f"Split: {len(y_train)} train / {len(y_test)} test  (random_state={RANDOM_SEED})")

# ── Helpers ──────────────────────────────────────────────────────────────────
def mape(y_true, y_pred, eps=EPSILON):
    return np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps))) * 100

def compute_metrics(y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mp   = mape(np.array(y_true), np.array(y_pred))
    return mae, rmse, r2, mp

# ── Run experiments ───────────────────────────────────────────────────────────
kf = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)

results_rows   = []
cv_scores_rows = []

for exp_name, features in EXPERIMENTS.items():
    print(f"\n{'='*60}")
    print(f"Experiment: {exp_name}  ({len(features)} features)")
    print(f"  Features: {features}")

    X_train = X_train_full[features]
    X_test  = X_test_full[features]

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  LinearRegression()),
    ])

    # 5-fold CV on training set
    fold_mae, fold_rmse, fold_r2, fold_mape_ = [], [], [], []

    for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_train), start=1):
        X_tr, X_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

        pipe.fit(X_tr, y_tr)
        y_val_pred = pipe.predict(X_val)
        m, r, r2_, mp = compute_metrics(y_val.values, y_val_pred)

        fold_mae.append(m);  fold_rmse.append(r)
        fold_r2.append(r2_); fold_mape_.append(mp)

        cv_scores_rows.append({
            "experiment": exp_name,
            "fold":       fold_idx,
            "mae":        round(m,  4),
            "rmse":       round(r,  4),
            "r2":         round(r2_, 4),
            "mape":       round(mp, 4),
        })
        print(f"    Fold {fold_idx}: MAE={m:.4f}  RMSE={r:.4f}  R²={r2_:.4f}  MAPE={mp:.4f}%")

    # Refit on full training set → evaluate test set
    pipe.fit(X_train, y_train)
    y_test_pred = pipe.predict(X_test)
    t_mae, t_rmse, t_r2, t_mape = compute_metrics(y_test.values, y_test_pred)

    print(f"  TEST  : MAE={t_mae:.4f}  RMSE={t_rmse:.4f}  R²={t_r2:.4f}  MAPE={t_mape:.4f}%")
    print(f"  CV    : MAE={np.mean(fold_mae):.4f}±{np.std(fold_mae):.4f}")

    results_rows.append({
        "experiment":    exp_name,
        "n_features":    len(features),
        "test_mae":      round(t_mae,  4),
        "test_rmse":     round(t_rmse, 4),
        "test_r2":       round(t_r2,   4),
        "test_mape":     round(t_mape, 4),
        "cv_mae_mean":   round(np.mean(fold_mae),  4),
        "cv_mae_std":    round(np.std(fold_mae),   4),
        "cv_rmse_mean":  round(np.mean(fold_rmse), 4),
        "cv_rmse_std":   round(np.std(fold_rmse),  4),
        "cv_r2_mean":    round(np.mean(fold_r2),   4),
        "cv_r2_std":     round(np.std(fold_r2),    4),
        "cv_mape_mean":  round(np.mean(fold_mape_),4),
        "cv_mape_std":   round(np.std(fold_mape_), 4),
    })

# ── Save CSVs ─────────────────────────────────────────────────────────────────
results_df   = pd.DataFrame(results_rows)
cv_scores_df = pd.DataFrame(cv_scores_rows)

results_path   = os.path.join(OUT_DIR, "ablation_results.csv")
cv_scores_path = os.path.join(OUT_DIR, "ablation_cv_scores.csv")

results_df.to_csv(results_path,   index=False)
cv_scores_df.to_csv(cv_scores_path, index=False)
print(f"\nSaved: {results_path}")
print(f"Saved: {cv_scores_path}")

# ── Comparison chart ──────────────────────────────────────────────────────────
exp_labels = ["A: Bio Only", "B: Bio+Weather", "C: Bio+Weather+THI"]
mae_vals   = results_df["test_mae"].tolist()
r2_vals    = results_df["test_r2"].tolist()

x = np.arange(len(exp_labels))
width = 0.35

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Ablation Study — Linear Regression\n(Effect of Weather and THI Features on Milk Yield Prediction)",
             fontsize=12, fontweight="bold")

# MAE bar chart
ax1 = axes[0]
bars1 = ax1.bar(x, mae_vals, width=0.5, color=["#4c72b0", "#55a868", "#c44e52"], edgecolor="black")
ax1.set_xticks(x); ax1.set_xticklabels(exp_labels, fontsize=9)
ax1.set_ylabel("Test MAE (Litres)"); ax1.set_title("Test MAE (lower is better)")
for bar, val in zip(bars1, mae_vals):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             f"{val:.4f}", ha="center", va="bottom", fontsize=9)
ymin1 = max(0, min(mae_vals) - 0.05)
ax1.set_ylim(ymin1, max(mae_vals) + 0.1)

# R² bar chart
ax2 = axes[1]
bars2 = ax2.bar(x, r2_vals, width=0.5, color=["#4c72b0", "#55a868", "#c44e52"], edgecolor="black")
ax2.set_xticks(x); ax2.set_xticklabels(exp_labels, fontsize=9)
ax2.set_ylabel("Test R²"); ax2.set_title("Test R² (higher is better)")
for bar, val in zip(bars2, r2_vals):
    offset = 0.003 if val >= 0 else -0.015
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + offset,
             f"{val:.4f}", ha="center", va="bottom", fontsize=9)
ymin2 = min(0, min(r2_vals)) - 0.05
ax2.set_ylim(ymin2, max(r2_vals) + 0.08)
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")

plt.tight_layout()
chart_path = os.path.join(OUT_DIR, "ablation_comparison.png")
plt.savefig(chart_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {chart_path}")

# ── Print final table ─────────────────────────────────────────────────────────
print("\n" + "="*70)
print("ABLATION RESULTS SUMMARY")
print("="*70)
print(results_df.to_string(index=False))

# Return data for report writing
print("\n__ABLATION_DATA_START__")
import json
print(json.dumps({
    "results": results_rows,
    "exp_a_features": EXP_A,
    "exp_b_features": EXP_B,
    "exp_c_features": EXP_C,
}))
print("__ABLATION_DATA_END__")
