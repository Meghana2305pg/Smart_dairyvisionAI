"""Combined ablation analysis (LR + XGBoost) and Wilcoxon audit."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = "/Users/sanjana/Smart_dairyvisionAI"
OUT = os.path.join(PROJECT, "outputs/thi_corrected/ablation_combined")
os.makedirs(OUT, exist_ok=True)

# ── Load existing ablation CSVs ───────────────────────────────────────────────
lr  = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/ablation_study/ablation_results.csv"))
xgb = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/ablation_study_xgboost/xgboost_ablation_results.csv"))
lr_cv  = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/ablation_study/ablation_cv_scores.csv"))
xgb_cv = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/ablation_study_xgboost/xgboost_ablation_cv_scores.csv"))
wilcoxon = pd.read_csv(os.path.join(PROJECT,"outputs/thi_corrected/statistical_analysis/wilcoxon_results.csv"))

# Add model column
lr["model"]  = "Linear Regression"
xgb["model"] = "XGBoost"
lr_cv["model"]  = "Linear Regression"
xgb_cv["model"] = "XGBoost"

combined    = pd.concat([lr, xgb], ignore_index=True)
combined_cv = pd.concat([lr_cv, xgb_cv], ignore_index=True)

# Reorder columns
cols = ["model","experiment","n_features","test_mae","test_rmse","test_r2",
        "test_mape","cv_mae_mean","cv_mae_std","cv_r2_mean","cv_r2_std"]
combined[cols].to_csv(os.path.join(OUT,"combined_ablation_results.csv"), index=False)
combined_cv.to_csv(os.path.join(OUT,"combined_ablation_cv_scores.csv"), index=False)
print("Saved: combined_ablation_results.csv")

# ── Chart: grouped bar (3 exp groups, 2 models, 2 metrics) ───────────────────
exp_labels = ["A: Bio Only", "B: Bio+Weather", "C: Bio+Weather+THI"]
x = np.arange(3)
w = 0.35

lr_mae  = lr["test_mae"].tolist();  xgb_mae  = xgb["test_mae"].tolist()
lr_r2   = lr["test_r2"].tolist();   xgb_r2   = xgb["test_r2"].tolist()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Combined Ablation Study: Linear Regression vs XGBoost\n"
             "(Milk Yield Prediction — Effect of Weather and THI Features)",
             fontsize=12, fontweight="bold")

for ax, metric_lr, metric_xgb, ylabel, title, better in [
    (axes[0], lr_mae, xgb_mae, "Test MAE (Litres/day)", "Test MAE (lower is better)", "lower"),
    (axes[1], lr_r2,  xgb_r2,  "Test R²",               "Test R² (higher is better)", "higher"),
]:
    b1 = ax.bar(x - w/2, metric_lr,  w, label="Linear Regression",
                color="#4c72b0", edgecolor="black", alpha=0.85, hatch="")
    b2 = ax.bar(x + w/2, metric_xgb, w, label="XGBoost",
                color="#c44e52", edgecolor="black", alpha=0.85, hatch="//")
    ax.set_xticks(x); ax.set_xticklabels(exp_labels, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9); ax.set_title(title, fontsize=10)
    ax.legend(fontsize=9)
    if title.endswith("better)") and "lower" in title:
        ax.set_ylim(max(0, min(metric_lr+metric_xgb)-0.05), max(metric_lr+metric_xgb)+0.12)
    else:
        ax.axhline(0, color="black", lw=0.8, ls="--")
        ax.set_ylim(min(0, min(metric_lr+metric_xgb))-0.03, max(metric_lr+metric_xgb)+0.07)
    for bar, val in zip(list(b1)+list(b2), metric_lr+metric_xgb):
        offset = 0.003 if val >= 0 else -0.012
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+offset,
                f"{val:.4f}", ha="center", va="bottom", fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(OUT,"combined_ablation_comparison.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved: combined_ablation_comparison.png")

# ── Print summary ─────────────────────────────────────────────────────────────
print("\n=== COMBINED ABLATION SUMMARY ===")
for _, r in combined[cols].iterrows():
    print(f"  {r.model:<20s} | {r.experiment:<22s} | MAE={r.test_mae:.4f} | R²={r.test_r2:.4f} | MAPE={r.test_mape:.2f}%")

print("\n=== WILCOXON RESULTS ===")
print(wilcoxon.to_string(index=False))

print("\nDONE")
