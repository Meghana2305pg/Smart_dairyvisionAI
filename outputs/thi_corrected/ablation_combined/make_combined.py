"""
Combined ablation analysis and chart generation.
Reads existing CSVs only — does NOT rerun experiments.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import os

OUT_DIR = '/Users/sanjana/Smart_dairyvisionAI/outputs/thi_corrected/ablation_combined'
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────────────────────
lr  = pd.read_csv('/Users/sanjana/Smart_dairyvisionAI/outputs/thi_corrected/ablation_study/ablation_results.csv')
xgb = pd.read_csv('/Users/sanjana/Smart_dairyvisionAI/outputs/thi_corrected/ablation_study_xgboost/xgboost_ablation_results.csv')
lr_cv  = pd.read_csv('/Users/sanjana/Smart_dairyvisionAI/outputs/thi_corrected/ablation_study/ablation_cv_scores.csv')
xgb_cv = pd.read_csv('/Users/sanjana/Smart_dairyvisionAI/outputs/thi_corrected/ablation_study_xgboost/xgboost_ablation_cv_scores.csv')

lr['model']  = 'Linear Regression'
xgb['model'] = 'XGBoost'

combined = pd.concat([lr, xgb], ignore_index=True)
combined = combined[['model','experiment','n_features',
                      'test_mae','test_rmse','test_r2','test_mape',
                      'cv_mae_mean','cv_mae_std','cv_r2_mean','cv_r2_std']]

combined.to_csv(os.path.join(OUT_DIR, 'combined_ablation_results.csv'), index=False)
print("Saved combined_ablation_results.csv")
print(combined.to_string(index=False))

# ── 2. Chart ──────────────────────────────────────────────────────────────────
exp_labels = {
    'A_Bio_Only':        'A: Bio Only\n(6 feat)',
    'B_Bio_Weather':     'B: Bio+Weather\n(9 feat)',
    'C_Bio_Weather_THI': 'C: Bio+Weather\n+THI (12 feat)',
}
exps  = ['A_Bio_Only','B_Bio_Weather','C_Bio_Weather_THI']
x_pos = np.arange(len(exps))
bar_w = 0.35

lr_row  = combined[combined['model']=='Linear Regression'].set_index('experiment')
xgb_row = combined[combined['model']=='XGBoost'].set_index('experiment')

lr_mae  = [lr_row.loc[e,'test_mae']  for e in exps]
xgb_mae = [xgb_row.loc[e,'test_mae'] for e in exps]
lr_r2   = [lr_row.loc[e,'test_r2']   for e in exps]
xgb_r2  = [xgb_row.loc[e,'test_r2']  for e in exps]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Combined Ablation Study: Linear Regression vs XGBoost', fontsize=13, fontweight='bold')

# Colours + hatches
lr_col  = '#2196F3'   # blue
xgb_col = '#FF9800'   # orange
lr_hatch  = '//'
xgb_hatch = 'xx'

def add_value_labels(ax, bars, fmt='{:.4f}', size=8.5):
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.001,
                fmt.format(h), ha='center', va='bottom', fontsize=size, fontweight='bold')

# — MAE subplot —
b1 = ax1.bar(x_pos - bar_w/2, lr_mae,  bar_w, label='Linear Regression',
             color=lr_col,  hatch=lr_hatch,  edgecolor='black', linewidth=0.8, alpha=0.85)
b2 = ax1.bar(x_pos + bar_w/2, xgb_mae, bar_w, label='XGBoost',
             color=xgb_col, hatch=xgb_hatch, edgecolor='black', linewidth=0.8, alpha=0.85)
add_value_labels(ax1, b1)
add_value_labels(ax1, b2)
ax1.set_title('Test MAE (lower is better)', fontsize=11)
ax1.set_ylabel('Mean Absolute Error (kg/day)', fontsize=10)
ax1.set_xticks(x_pos)
ax1.set_xticklabels([exp_labels[e] for e in exps], fontsize=9)
ax1.set_ylim(1.95, 2.20)
ax1.legend(fontsize=9)
ax1.grid(axis='y', alpha=0.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# — R² subplot —
b3 = ax2.bar(x_pos - bar_w/2, lr_r2,  bar_w, label='Linear Regression',
             color=lr_col,  hatch=lr_hatch,  edgecolor='black', linewidth=0.8, alpha=0.85)
b4 = ax2.bar(x_pos + bar_w/2, xgb_r2, bar_w, label='XGBoost',
             color=xgb_col, hatch=xgb_hatch, edgecolor='black', linewidth=0.8, alpha=0.85)
add_value_labels(ax2, b3)
add_value_labels(ax2, b4)
ax2.set_title('Test R² (higher is better)', fontsize=11)
ax2.set_ylabel('R² Score', fontsize=10)
ax2.set_xticks(x_pos)
ax2.set_xticklabels([exp_labels[e] for e in exps], fontsize=9)
ax2.set_ylim(0.08, 0.25)
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.3)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
chart_path = os.path.join(OUT_DIR, 'combined_ablation_comparison.png')
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved {chart_path}")
