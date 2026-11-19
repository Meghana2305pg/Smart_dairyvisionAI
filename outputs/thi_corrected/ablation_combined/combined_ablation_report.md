# Combined Ablation Study Report — Linear Regression vs XGBoost

**Date:** 2026-11-19  
**Dataset:** `outputs/thi_corrected/engineered_dataset.csv`  
**Split:** 80/20 (2,400 train / 600 test), `random_state=42`  
**CV:** 5-fold KFold, `shuffle=True`, `random_state=42`

---

## 1. Feature Sets

| Experiment | Features | n |
|---|---|---|
| **A — Bio Only** | age, weight, health_status, feed, feed_weight_ratio, age_weight_ratio | 6 |
| **B — Bio+Weather** | A + temperature, humidity, temp_humidity | 9 |
| **C — Bio+Weather+THI** | B + thi, thi_squared, feed_thi_interaction | 12 |

---

## 2. Full Metrics Table — Both Models, All Experiments

| Model | Experiment | n | Test MAE | Test RMSE | Test R² | Test MAPE | CV MAE Mean | CV MAE Std |
|---|---|---|---|---|---|---|---|---|
| Linear Regression | A — Bio Only | 6 | 2.0394 | 2.5831 | 0.1826 | 9.88% | 2.0107 | 0.0455 |
| Linear Regression | B — Bio+Weather | 9 | 2.0389 | 2.5822 | 0.1833 | 9.88% | 2.0131 | 0.0469 |
| Linear Regression | C — Bio+Weather+THI | 12 | **2.0379** | **2.5809** | **0.1840** | **9.88%** | 2.0134 | 0.0458 |
| XGBoost | A — Bio Only | 6 | 2.0877 | 2.6450 | 0.1430 | 10.13% | 2.0519 | 0.0338 |
| XGBoost | B — Bio+Weather | 9 | 2.1061 | 2.6471 | 0.1417 | 10.22% | 2.0637 | 0.0168 |
| XGBoost | C — Bio+Weather+THI | 12 | 2.0944 | 2.6484 | 0.1408 | 10.16% | 2.0699 | 0.0309 |

> **Best overall (ablation test set):** Linear Regression — Experiment C (MAE 2.0379, R² 0.1840)

---

## 3. Per-Fold CV MAE — Linear Regression

| Fold | A — Bio Only | B — Bio+Weather | C — Bio+Weather+THI |
|---|---|---|---|
| 1 | 2.0304 | 2.0308 | 2.0328 |
| 2 | 2.0163 | 2.0239 | 2.0238 |
| 3 | 1.9392 | 1.9383 | 1.9411 |
| 4 | 1.9904 | 1.9923 | 1.9904 |
| 5 | 2.0770 | 2.0804 | 2.0786 |

## Per-Fold CV MAE — XGBoost

| Fold | A — Bio Only | B — Bio+Weather | C — Bio+Weather+THI |
|---|---|---|---|
| 1 | 2.0240 | 2.0762 | 2.0738 |
| 2 | 2.0492 | 2.0484 | 2.0421 |
| 3 | 2.0279 | 2.0420 | 2.0322 |
| 4 | 2.0414 | 2.0647 | 2.0824 |
| 5 | 2.1171 | 2.0872 | 2.1191 |

---

## 4. Does Adding Weather Features Improve Prediction?

### For Linear Regression
**Marginally yes — but not meaningfully.** Adding basic weather (B) reduces MAE by 0.0005 L over bio-only (A). Adding THI features (C) gives the best test-set result. Total improvement A→C: **−0.0015 L MAE, +0.0014 R²**. This is smaller than the CV fold standard deviation (~0.045 L) and not statistically distinguishable with 5 folds.

### For XGBoost
**No — adding weather features degrades performance.** Bio-only (A) gives the best XGBoost result (MAE 2.0877, R² 0.1430). Adding weather (B) increases MAE by +0.018 L (+0.9%). Adding THI (C) partially recovers but remains above bio-only. This reversal reflects XGBoost's vulnerability to low-signal synthetic features: its expressive tree splits overfit to noise that OLS naturally regularises through near-zero coefficient assignment.

### Why Linear Regression Outperforms XGBoost in the Ablation
OLS assigns near-zero coefficients to uninformative features, implicitly regularising their contribution. XGBoost lacks this implicit property when features are noisy. This does **not** contradict the five-model comparison result — on the full 12-feature dataset, the CV MAE ordering was different due to partition differences (see audit report).

---

## 5. Limitations

- **Statistical power:** Differences between experiments (< 0.003 L MAE) are smaller than within-fold standard deviations (0.03–0.05 L). No formal significance test was run between ablation experiments.
- **Synthetic weather:** All weather variables are synthetically generated. Real field data with matched observations would be expected to show clearer environmental-feature contributions.
- **Fixed hyperparameters:** XGBoost hyperparameters were not retuned per feature subset.
