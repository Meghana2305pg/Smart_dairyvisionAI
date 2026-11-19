# DairyVision AI — Statistical Comparison Report
## Pairwise Wilcoxon Signed-Rank Tests on 5-Fold CV MAE

**Generated:** 2026-11-19 15:21 IST  
**CV scores source:** `outputs/thi_corrected/model_comparison/cv_fold_scores.csv`  
**Number of models:** 5  
**Number of pairs tested:** 10  
**Number of CV folds (paired observations):** 5  
**Primary metric:** Fold-level MAE  
**Significance level:** α = 0.05  
**Multiple-comparison correction:** Holm step-down  

---

## ⚠️ Statistical Power Warning

The Wilcoxon signed-rank test requires a minimum of **6 non-zero differences** to
achieve any p-value ≤ 0.05 with the exact method (n=5 pairs yields a minimum
achievable p-value of 0.0625 with the two-sided exact test). This means:

- **No pair can be declared statistically significant at α=0.05** using only 5 folds,
  regardless of how large the observed MAE differences are.
- Results should be interpreted as **descriptive** (direction and magnitude of
  difference) rather than inferential.
- Conclusions about model superiority should be treated as **preliminary** and
  would require more folds or repeated experiments to confirm.

---

## Per-Model Mean CV MAE

| Model | Fold MAEs | Mean MAE |
|-------|-----------|----------|
| Linear Regression | [2.0328, 2.0238, 1.9411, 1.9904, 2.0786] | 2.0134 |
| Decision Tree | [2.2044, 2.1937, 2.2362, 2.2713, 2.2637] | 2.2339 |
| Random Forest | [2.0225, 2.0412, 1.9863, 2.008, 2.0855] | 2.0287 |
| SVR | [2.1049, 2.0899, 2.0722, 2.0493, 2.1261] | 2.0885 |
| XGBoost | [2.0997, 2.0582, 2.0368, 2.0694, 2.1148] | 2.0758 |

---

## Pairwise Wilcoxon Results

| Model A | Model B | Mean MAE A | Mean MAE B | Diff (A−B) | W | p_raw | p_holm | Sig (raw) | Sig (Holm) |
|---------|---------|-----------|-----------|-----------|---|-------|--------|-----------|------------|
| Linear Regression | Decision Tree | 2.0134 | 2.2339 | -0.2205 | 0.0 | 0.0625 | 0.0625 | ✗ | ✗ |
| Linear Regression | Random Forest | 2.0134 | 2.0287 | -0.0154 | 2.0 | 0.1875 | 1.0000 | ✗ | ✗ |
| Linear Regression | SVR | 2.0134 | 2.0885 | -0.0751 | 0.0 | 0.0625 | 0.1250 | ✗ | ✗ |
| Linear Regression | XGBoost | 2.0134 | 2.0758 | -0.0624 | 0.0 | 0.0625 | 0.1875 | ✗ | ✗ |
| Decision Tree | Random Forest | 2.2339 | 2.0287 | +0.2051 | 0.0 | 0.0625 | 0.2500 | ✗ | ✗ |
| Decision Tree | SVR | 2.2339 | 2.0885 | +0.1454 | 0.0 | 0.0625 | 0.3125 | ✗ | ✗ |
| Decision Tree | XGBoost | 2.2339 | 2.0758 | +0.1581 | 0.0 | 0.0625 | 0.3750 | ✗ | ✗ |
| Random Forest | SVR | 2.0287 | 2.0885 | -0.0598 | 0.0 | 0.0625 | 0.4375 | ✗ | ✗ |
| Random Forest | XGBoost | 2.0287 | 2.0758 | -0.0471 | 0.0 | 0.0625 | 0.5000 | ✗ | ✗ |
| SVR | XGBoost | 2.0885 | 2.0758 | +0.0127 | 3.0 | 0.3125 | 1.0000 | ✗ | ✗ |

---

## Interpretation

- **Pairs significant at raw α=0.05:** 0 out of 10
- **Pairs significant after Holm correction:** 0 out of 10

As explained in the power warning above, **the minimum achievable two-sided
exact p-value with n=5 paired observations is 0.0625**, which exceeds α=0.05.
Therefore, no pair can be declared statistically significant in this analysis,
and no Holm-corrected p-value can reach significance.

The rank ordering by mean CV MAE is:

| Rank | Model | Mean CV MAE |
|------|-------|------------|
| 1 | Linear Regression | 2.0134 |
| 2 | Random Forest | 2.0287 |
| 3 | XGBoost | 2.0758 |
| 4 | SVR | 2.0885 |
| 5 | Decision Tree | 2.2339 |

**Linear Regression achieves the lowest mean CV MAE (2.0134 L)**,
followed closely by Random Forest (2.0287 L). The differences between
the top four models are small (< 0.08 L MAE). Decision Tree is the clear
underperformer with a negative mean R² across folds.

These rankings are consistent with the test-set results but cannot be confirmed
as statistically significant with n=5 folds. A 10-fold or repeated k-fold
cross-validation design would provide more statistical power for future work.

---

## Method Notes

- **Test:** Wilcoxon signed-rank test, two-sided, exact method (scipy `method='exact'`)
- **Input:** Paired fold-level MAE scores (5 values per model)
- **Correction:** Holm step-down procedure applied to all 10 raw p-values
- **Test predictions:** Not used as inputs — test-set rows are not independent
  paired observations and must not be treated as such for signed-rank tests
