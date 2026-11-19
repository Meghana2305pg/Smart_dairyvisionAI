"""SHAP analysis on trained XGBoost model."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib, shap

PROJECT = "/Users/sanjana/Smart_dairyvisionAI"
OUT = os.path.join(PROJECT, "outputs/thi_corrected/shap_analysis")
os.makedirs(OUT, exist_ok=True)

FEATURES = ["age","weight","health_status","feed","temperature","humidity",
            "thi","feed_weight_ratio","temp_humidity","thi_squared",
            "feed_thi_interaction","age_weight_ratio"]
LABELS = ["Age (months)","Weight (kg)","Health Status","Feed (kg/day)",
          "Temperature (°C)","Humidity (%)","THI","Feed/Weight Ratio",
          "Temp×Humidity","THI²","Feed×THI Interaction","Age/Weight Ratio"]
TARGET = "milk_output"

# Load
print("Loading model and data...")
model = joblib.load(os.path.join(PROJECT,"outputs/thi_corrected/model_comparison/model_xgboost.pkl"))
df = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/engineered_dataset.csv"))

from sklearn.model_selection import train_test_split
X = df[FEATURES]; y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
print(f"Test set shape: {X_test.shape}")

# SHAP
print("Computing SHAP values (TreeExplainer)...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
print(f"SHAP values shape: {shap_values.shape}")

# ── Figure 1: Beeswarm ────────────────────────────────────────────────────────
print("Generating beeswarm plot...")
fig, ax = plt.subplots(figsize=(9, 6))
shap.summary_plot(shap_values, X_test, feature_names=LABELS,
                  show=False, plot_size=None)
plt.title("SHAP Summary — XGBoost Milk Yield Prediction", fontsize=12, fontweight="bold", pad=10)
plt.xlabel("SHAP Value (impact on predicted milk yield, L/day)", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT,"shap_beeswarm_summary.png"), dpi=150, bbox_inches="tight")
plt.close("all")
print("  Saved: shap_beeswarm_summary.png")

# ── Figure 2: Global importance bar ──────────────────────────────────────────
print("Generating feature importance bar chart...")
mean_abs = np.abs(shap_values).mean(axis=0)
importance_df = pd.DataFrame({"feature": FEATURES, "label": LABELS, "mean_abs_shap": mean_abs})
importance_df = importance_df.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
importance_df["rank"] = importance_df.index + 1

fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#c44e52" if i < 3 else "#4c72b0" for i in range(len(importance_df))]
bars = ax.barh(importance_df["label"][::-1], importance_df["mean_abs_shap"][::-1],
               color=colors[::-1], edgecolor="black", alpha=0.85)
ax.set_xlabel("Mean |SHAP Value| (impact on milk yield L/day)", fontsize=10)
ax.set_title("Global XGBoost Feature Importance (SHAP)", fontsize=12, fontweight="bold")
for bar, val in zip(bars, importance_df["mean_abs_shap"][::-1]):
    ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
            f"{val:.4f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUT,"shap_feature_importance_bar.png"), dpi=150, bbox_inches="tight")
plt.close("all")
print("  Saved: shap_feature_importance_bar.png")

# ── Figure 3: Dependence plots (top 3) ───────────────────────────────────────
print("Generating dependence plots for top 3 features...")
for i in range(3):
    feat = importance_df["feature"].iloc[i]
    label = importance_df["label"].iloc[i]
    feat_idx = FEATURES.index(feat)
    fig, ax = plt.subplots(figsize=(7, 4))
    shap.dependence_plot(feat_idx, shap_values, X_test,
                         feature_names=LABELS, show=False, ax=ax)
    ax.set_title(f"SHAP Dependence — {label}", fontsize=11, fontweight="bold")
    ax.set_ylabel(f"SHAP Value for {label}", fontsize=9)
    plt.tight_layout()
    fname = f"shap_dependence_{feat}.png"
    plt.savefig(os.path.join(OUT, fname), dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: {fname}")

# ── Save numerical CSV ────────────────────────────────────────────────────────
importance_df[["rank","feature","label","mean_abs_shap"]].to_csv(
    os.path.join(OUT,"shap_feature_importance.csv"), index=False)
print("Saved: shap_feature_importance.csv")

# ── Print for report ──────────────────────────────────────────────────────────
print("\n=== SHAP Feature Importance (ranked) ===")
for _, row in importance_df.iterrows():
    print(f"  {int(row.rank):2d}. {row.label:<28s} {row.mean_abs_shap:.5f}")

print("\nDONE")
