# Statistical Validation Summary — DairyVision AI Model Comparison

**Date:** 2026-11-19  
**Test:** Wilcoxon Signed-Rank Test (pairwise, fold-level MAE)  
**CV:** 5-fold, same split across all models  
**Correction:** Holm (step-down) multiple comparison correction

---

## 1. Complete Pairwise Wilcoxon Results

| Model A | Model B | MAE A | MAE B | Diff (A−B) | W stat | p (raw) | p (Holm) | Sig? |
|---|---|---|---|---|---|---|---|---|
| Linear Regression | Decision Tree | 2.0134 | 2.2339 | −0.2205 | 0.0 | 0.0625 | 0.0625 | ❌ |
| Linear Regression | Random Forest | 2.0134 | 2.0287 | −0.0154 | 2.0 | 0.1875 | 1.0000 | ❌ |
| Linear Regression | SVR | 2.0134 | 2.0885 | −0.0751 | 0.0 | 0.0625 | 0.1250 | ❌ |
| Linear Regression | XGBoost | 2.0134 | 2.0758 | −0.0624 | 0.0 | 0.0625 | 0.1875 | ❌ |
| Decision Tree | Random Forest | 2.2339 | 2.0287 | +0.2051 | 0.0 | 0.0625 | 0.2500 | ❌ |
| Decision Tree | SVR | 2.2339 | 2.0885 | +0.1454 | 0.0 | 0.0625 | 0.3125 | ❌ |
| Decision Tree | XGBoost | 2.2339 | 2.0758 | +0.1581 | 0.0 | 0.0625 | 0.3750 | ❌ |
| Random Forest | SVR | 2.0287 | 2.0885 | −0.0598 | 0.0 | 0.0625 | 0.4375 | ❌ |
| Random Forest | XGBoost | 2.0287 | 2.0758 | −0.0471 | 0.0 | 0.0625 | 0.5000 | ❌ |
| SVR | XGBoost | 2.0885 | 2.0758 | +0.0127 | 3.0 | 0.3125 | 1.0000 | ❌ |

**Result: 0 of 10 pairs statistically significant at α = 0.05 (before or after Holm correction).**

---

## 2. Holm Correction Procedure

Holm's step-down method:
1. Sort raw p-values in ascending order: [0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.1875, 0.3125]
2. Multiply the smallest p by m=10, next by m−1=9, etc.
3. Apply cumulative max to preserve monotonicity.

After correction, minimum adjusted p = 0.0625 × 10 = 0.625 — well above α = 0.05.

---

## 3. Critical Limitation: Minimum Achievable p-Value with n=5 Folds

With only **5 paired observations**, the Wilcoxon signed-rank test has a theoretical minimum two-sided p-value of **0.0625** (achieved when all 5 differences have the same sign, W=0). This means:

> **It is mathematically impossible to achieve p < 0.05 with n=5 paired folds using the Wilcoxon signed-rank test.**

This is a methodological constraint, not an indicator that all models perform identically. The fold-level MAE differences are consistent in direction (e.g., Decision Tree is worse than all other models in every fold), but the sample size is insufficient to achieve conventional statistical significance.

---

## 4. Implications for the Paper

The paper's earlier claim of "statistically significant improvements for XGBoost" is **incorrect** and must be retracted. The correct statement is:

> *"Model selection was evaluated using the Wilcoxon signed-rank test on fold-level MAE scores. With five cross-validation folds, the minimum attainable two-sided p-value is 0.0625; consequently, no pairwise difference reached statistical significance at α = 0.05 after Holm correction. While XGBoost achieved the numerically lowest CV MAE, the performance differences between the top-four models (Linear Regression, Random Forest, SVR, XGBoost) are not statistically distinguishable under the current evaluation design."*

---

## 5. Recommendation

For future work: use repeated k-fold cross-validation (e.g., 10-fold repeated 5 times = 50 paired observations), which would provide sufficient power to detect the observed effect sizes.
