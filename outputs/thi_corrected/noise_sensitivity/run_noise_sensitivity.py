"""
Gaussian Noise Sensitivity Analysis for DairyVision AI XGBoost model.
Tests prediction stability under varying levels of weather measurement noise.
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os, math

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = "/Users/sanjana/Smart_dairyvisionAI"
DATASET_PATH = os.path.join(PROJECT_ROOT, "outputs/thi_corrected/engineered_dataset.csv")
OUT_DIR      = os.path.join(PROJECT_ROOT, "outputs/thi_corrected/noise_sensitivity")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────
TARGET   = "milk_output"
ALL_FEATURES = [
    "age", "weight", "health_status", "feed",
    "temperature", "humidity", "thi",
    "feed_weight_ratio", "temp_humidity", "thi_squared",
    "feed_thi_interaction", "age_weight_ratio"
]

XGB_PARAMS = dict(
    n_estimators=300, learning_rate=0.05, max_depth=4,
    subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
    reg_alpha=0.1, reg_lambda=1.0, random_state=42, n_jobs=-1,
    verbosity=0
)

NOISE_EXPERIMENTS = [
    {"name": "A", "temp_sd": 0.0, "humidity_sd": 0.0},
    {"name": "B", "temp_sd": 1.0, "humidity_sd": 3.0},
    {"name": "C", "temp_sd": 2.5, "humidity_sd": 7.5},
    {"name": "D", "temp_sd": 4.0, "humidity_sd": 10.0},
]

# Physical clipping bounds
TEMP_CLIP   = (0.0, 55.0)   # °C for cattle environments
HUMID_CLIP  = (5.0, 100.0)  # %


# ── Metrics helper ─────────────────────────────────────────────────────────
def compute_metrics(y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    eps  = 1e-6
    mape = float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + eps)))) * 100.0
    return mae, rmse, r2, mape


# ── Load dataset ───────────────────────────────────────────────────────────
print("Loading dataset …")
df_orig = pd.read_csv(DATASET_PATH)
print(f"  Rows: {len(df_orig)}, Columns: {list(df_orig.columns)}")

results_rows = []
cv_rows      = []

# ── Run experiments ────────────────────────────────────────────────────────
for exp in NOISE_EXPERIMENTS:
    name        = exp["name"]
    temp_sd     = exp["temp_sd"]
    humidity_sd = exp["humidity_sd"]
    print(f"\n=== Experiment {name}: temp_sd={temp_sd}, humidity_sd={humidity_sd} ===")

    # Work on a copy so we never touch the original dataframe
    df = df_orig.copy()

    # Add Gaussian noise with fresh RNG (seed=42 each experiment for reproducibility)
    rng = np.random.default_rng(42)

    if temp_sd > 0.0:
        noise_t = rng.normal(0.0, temp_sd, size=len(df))
        df["temperature"] = df["temperature"] + noise_t
    if humidity_sd > 0.0:
        noise_h = rng.normal(0.0, humidity_sd, size=len(df))
        df["humidity"] = df["humidity"] + noise_h

    # Clip to physical bounds
    df["temperature"] = df["temperature"].clip(*TEMP_CLIP)
    df["humidity"]    = df["humidity"].clip(*HUMID_CLIP)

    # Recompute THI and dependent derived features
    T  = df["temperature"]
    RH = df["humidity"]
    df["thi"]               = (0.8 * T) + ((RH / 100.0) * (T - 14.4)) + 46.4
    df["temp_humidity"]     = T * RH
    df["thi_squared"]       = df["thi"] ** 2
    df["feed_thi_interaction"] = df["feed"] * df["thi"]
    # age_weight_ratio and feed_weight_ratio are NOT recomputed

    X = df[ALL_FEATURES]
    y = df[TARGET]

    # 80/20 train-test split (identical seed to baseline)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Train XGBoost
    model = XGBRegressor(**XGB_PARAMS)
    model.fit(X_train, y_train)

    # Test-set metrics
    y_pred_test = model.predict(X_test)
    test_mae, test_rmse, test_r2, test_mape = compute_metrics(
        np.array(y_test), y_pred_test
    )
    print(f"  Test → MAE={test_mae:.4f}, RMSE={test_rmse:.4f}, R²={test_r2:.4f}, MAPE={test_mape:.4f}%")

    # 5-fold CV on training set
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_maes, fold_rmses, fold_r2s = [], [], []

    for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_train), start=1):
        Xf_train, Xf_val = X_train.iloc[tr_idx], X_train.iloc[val_idx]
        yf_train, yf_val = y_train.iloc[tr_idx], y_train.iloc[val_idx]

        cv_model = XGBRegressor(**XGB_PARAMS)
        cv_model.fit(Xf_train, yf_train)
        yf_pred  = cv_model.predict(Xf_val)

        f_mae, f_rmse, f_r2, f_mape = compute_metrics(np.array(yf_val), yf_pred)
        fold_maes.append(f_mae)
        fold_rmses.append(f_rmse)
        fold_r2s.append(f_r2)
        print(f"    Fold {fold_idx}: MAE={f_mae:.4f}, RMSE={f_rmse:.4f}, R²={f_r2:.4f}, MAPE={f_mape:.4f}%")

        cv_rows.append({
            "experiment": name,
            "fold": fold_idx,
            "mae":  round(f_mae,  6),
            "rmse": round(f_rmse, 6),
            "r2":   round(f_r2,   6),
            "mape": round(f_mape, 6),
        })

    cv_mae_mean  = np.mean(fold_maes)
    cv_mae_std   = np.std(fold_maes,  ddof=1)
    cv_rmse_mean = np.mean(fold_rmses)
    cv_rmse_std  = np.std(fold_rmses, ddof=1)
    cv_r2_mean   = np.mean(fold_r2s)
    cv_r2_std    = np.std(fold_r2s,   ddof=1)
    print(f"  CV → MAE={cv_mae_mean:.4f}±{cv_mae_std:.4f}, "
          f"RMSE={cv_rmse_mean:.4f}±{cv_rmse_std:.4f}, "
          f"R²={cv_r2_mean:.4f}±{cv_r2_std:.4f}")

    results_rows.append({
        "experiment":   name,
        "temp_sd":      temp_sd,
        "humidity_sd":  humidity_sd,
        "test_mae":     round(test_mae,     6),
        "test_rmse":    round(test_rmse,    6),
        "test_r2":      round(test_r2,      6),
        "test_mape":    round(test_mape,    6),
        "cv_mae_mean":  round(cv_mae_mean,  6),
        "cv_mae_std":   round(cv_mae_std,   6),
        "cv_rmse_mean": round(cv_rmse_mean, 6),
        "cv_rmse_std":  round(cv_rmse_std,  6),
        "cv_r2_mean":   round(cv_r2_mean,   6),
        "cv_r2_std":    round(cv_r2_std,    6),
    })


# ── Save CSVs ──────────────────────────────────────────────────────────────
df_results = pd.DataFrame(results_rows)
df_cv      = pd.DataFrame(cv_rows)

results_path = os.path.join(OUT_DIR, "noise_sensitivity_results.csv")
cv_path      = os.path.join(OUT_DIR, "noise_sensitivity_cv.csv")
df_results.to_csv(results_path, index=False)
df_cv.to_csv(cv_path, index=False)
print(f"\nSaved: {results_path}")
print(f"Saved: {cv_path}")


# ── Plot ───────────────────────────────────────────────────────────────────
exp_labels = df_results["experiment"].tolist()
maes       = df_results["test_mae"].tolist()
r2s        = df_results["test_r2"].tolist()
noise_desc = [f"{row.temp_sd}°C / {row.humidity_sd}%" for row in df_results.itertuples()]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("XGBoost Prediction Stability Under Gaussian Weather Noise", fontsize=14, fontweight="bold")

ax1.plot(exp_labels, maes, marker="o", color="steelblue", linewidth=2, markersize=8, label="Test MAE")
for i, (lbl, v) in enumerate(zip(exp_labels, maes)):
    ax1.annotate(f"{v:.3f}", (lbl, v), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=10)
ax1.set_xlabel("Noise Level", fontsize=12)
ax1.set_ylabel("MAE (litres)", fontsize=12)
ax1.set_title("Mean Absolute Error vs Noise Level", fontsize=12)
ax1.grid(True, linestyle="--", alpha=0.6)
ax1.set_xticks(range(len(exp_labels)))
ax1.set_xticklabels([f"{lbl}\n({d})" for lbl, d in zip(exp_labels, noise_desc)], fontsize=9)

ax2.plot(exp_labels, r2s, marker="s", color="darkorange", linewidth=2, markersize=8, label="Test R²")
for i, (lbl, v) in enumerate(zip(exp_labels, r2s)):
    ax2.annotate(f"{v:.4f}", (lbl, v), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=10)
ax2.set_xlabel("Noise Level", fontsize=12)
ax2.set_ylabel("R²", fontsize=12)
ax2.set_title("R² Score vs Noise Level", fontsize=12)
ax2.grid(True, linestyle="--", alpha=0.6)
ax2.set_xticks(range(len(exp_labels)))
ax2.set_xticklabels([f"{lbl}\n({d})" for lbl, d in zip(exp_labels, noise_desc)], fontsize=9)

plt.tight_layout()
plot_path = os.path.join(OUT_DIR, "noise_sensitivity_comparison.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {plot_path}")


# ── Print final summary for report writing ─────────────────────────────────
print("\n=== FINAL RESULTS SUMMARY ===")
print(df_results.to_string(index=False))
print("\n=== CV RESULTS ===")
print(df_cv.to_string(index=False))
