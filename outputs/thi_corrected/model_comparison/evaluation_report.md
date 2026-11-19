# DairyVision AI — Model Training & Evaluation Report
## THI-Corrected Dataset (+46.4)

**Generated:** 2026-11-19 15:17 IST  
**Dataset:** `outputs/thi_corrected/engineered_dataset.csv`  
**Dataset SHA-256:** `052cd89667b4cf9e37abd3f3c1df3a8dccb4869fe94c7d1eeaffc82a150485a6`  
**Features (12):** `age, weight, health_status, feed, temperature, humidity, thi, feed_weight_ratio, temp_humidity, thi_squared, feed_thi_interaction, age_weight_ratio`  
**Target:** `milk_output`  
**Train/Test split:** 80/20 (random_state=42)  
**Cross-validation:** 5-fold KFold (shuffle=True, random_state=42)  

---

## MAPE Computation Note
MAPE computed as mean(|y_true - y_pred| / max(|y_true|, 1e-6)) × 100. Epsilon guard of 1e-6 applied to avoid division by near-zero actuals. Actual target minimum is 11.5100 L — no near-zero values present in this dataset, so the guard has no practical effect.

---

## Cross-Validation Results (Training Set — 2,400 rows, 5 folds)

| Model | MAE mean±std | RMSE mean±std | R² mean±std | MAPE mean±std |
|-------|-------------|--------------|------------|--------------|
| Linear Regression | 2.0134±0.0512 | 2.5411±0.0816 | 0.1520±0.0190 | 9.7983%±0.2748% |
| Decision Tree | 2.2339±0.0346 | 2.8226±0.0308 | -0.0485±0.0661 | 10.8170%±0.2282% |
| Random Forest | 2.0287±0.0376 | 2.5713±0.0645 | 0.1310±0.0350 | 9.8666%±0.2054% |
| SVR | 2.0885±0.0295 | 2.6265±0.0543 | 0.0927±0.0506 | 10.1250%±0.1422% |
| XGBoost | 2.0758±0.0315 | 2.6236±0.0499 | 0.0950±0.0423 | 10.0830%±0.1955% |

---

## Test Set Results (held-out 600 rows, ranked by MAE)

| Rank | Model | MAE | RMSE | R² | MAPE |
|------|-------|-----|------|-----|------|
| 1 | Linear Regression | 2.0379 | 2.5809 | 0.1840 | 9.8757% |
| 2 | SVR | 2.0544 | 2.6054 | 0.1685 | 9.9316% |
| 3 | Random Forest | 2.0911 | 2.6264 | 0.1550 | 10.1369% |
| 4 | XGBoost | 2.0929 | 2.6410 | 0.1456 | 10.1481% |
| 5 | Decision Tree | 2.3186 | 2.8862 | -0.0204 | 11.2594% |

---

## Best Model: Linear Regression
- Test MAE  : 2.0379 L
- Test RMSE : 2.5809 L
- Test R²   : 0.1840
- Test MAPE : 9.8757%

---

## Hyperparameters

```json
{
  "Linear Regression": {
    "pipeline": "StandardScaler + LinearRegression",
    "fit_intercept": true
  },
  "Decision Tree": {
    "max_depth": 8,
    "min_samples_leaf": 4,
    "random_state": 42
  },
  "Random Forest": {
    "n_estimators": 300,
    "max_features": "sqrt",
    "max_depth": null,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1
  },
  "SVR": {
    "pipeline": "StandardScaler + SVR",
    "kernel": "rbf",
    "C": 10,
    "epsilon": 0.1,
    "gamma": "scale"
  },
  "XGBoost": {
    "n_estimators": 300,
    "learning_rate": 0.05,
    "max_depth": 4,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "n_jobs": -1
  }
}
```

---

## Library Versions

| Library | Version |
|---------|---------|
| scikit-learn | 1.9.0 |
| xgboost | 3.4.0 |
| numpy | 2.5.1 |
| pandas | 3.0.5 |

---

## Reproducibility

- Dataset SHA-256: `052cd89667b4cf9e37abd3f3c1df3a8dccb4869fe94c7d1eeaffc82a150485a6`
- RANDOM_SEED: 42
- Train/test split: `train_test_split(test_size=0.20, random_state=42)`
- KFold: `KFold(n_splits=5, shuffle=True, random_state=42)`
- LR and SVR wrapped in `sklearn.pipeline.Pipeline` with `StandardScaler`
  to prevent data leakage across CV folds.
- Tree-based models (DT, RF, XGBoost): no scaling required.
- Weather API not called; fallback values used (28.0°C, 65.0%).

## Output Files

| File | Description |
|------|-------------|
| `model_comparison.csv` | All metrics ranked by test MAE |
| `cv_fold_scores.csv` | Per-fold scores for all models (for Wilcoxon tests) |
| `test_predictions.csv` | y_true + predictions from all 5 models |
| `model_*.pkl` | Trained model objects |
| `hyperparameters.json` | All model configurations |
| `evaluation_report.md` | This report |
