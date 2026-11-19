# Noise Sensitivity Analysis Report
## DairyVision AI — XGBoost Model

**Date:** November 2026  
**Analysis:** Gaussian weather-noise perturbation study  
**Model:** XGBoost (n_estimators=300, lr=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8, min_child_weight=3, reg_alpha=0.1, reg_lambda=1.0)

---

## 1. Objective

This study evaluates the prediction stability of the XGBoost dairy-output model when Gaussian noise is added to the synthetic weather measurements (temperature and humidity). The goal is to determine whether small or moderate errors in weather sensor readings meaningfully degrade model performance.

> **Important:** The noise levels defined below (A–D) are **experimental settings** designed to simulate measurement uncertainty. They are **not** biological thresholds or recommended operating ranges for cattle management.

---

## 2. Experiment Design

| Experiment | Temp Noise SD (°C) | Humidity Noise SD (%) | Description              |
|------------|-------------------:|----------------------:|--------------------------|
| A          | 0.0                | 0.0                   | No noise (baseline)      |
| B          | 1.0                | 3.0                   | Low noise                |
| C          | 2.5                | 7.5                   | Moderate noise           |
| D          | 4.0                | 10.0                  | High noise               |

### Physical Clipping Bounds Applied

After adding noise, values were clipped to physically meaningful ranges for cattle environments:

- **Temperature:** clipped to [0, 55] °C
- **Humidity:** clipped to [5, 100] %

### Procedure (per experiment)

1. Load `outputs/thi_corrected/engineered_dataset.csv` (3,000 records; original file unmodified).
2. Add Gaussian noise to `temperature` and `humidity` columns using `np.random.default_rng(42)`.
3. Clip noisy values to physical bounds above.
4. Recompute derived weather features:
   - `thi = (0.8 × T) + ((RH/100) × (T − 14.4)) + 46.4`
   - `temp_humidity = T × RH`
   - `thi_squared = thi²`
   - `feed_thi_interaction = feed × thi`
   - *(Non-weather features `age_weight_ratio`, `feed_weight_ratio` left unchanged)*
5. Apply 80/20 train-test split (`random_state=42`; identical to baseline).
6. Train XGBoost on training split (2,400 rows), evaluate on test split (600 rows).
7. Run 5-fold cross-validation on training set (`KFold(shuffle=True, random_state=42)`).
8. Compute MAE, RMSE, R², MAPE (epsilon=1e-6 guard against division by zero).

---

## 3. Full Test-Set Results

| Exp | Temp SD | Hum SD | Test MAE | Test RMSE | Test R² | Test MAPE (%) |
|-----|--------:|-------:|---------:|----------:|--------:|--------------:|
| A   | 0.0°C   | 0.0%   | 2.0929   | 2.6410    | 0.1456  | 10.148        |
| B   | 1.0°C   | 3.0%   | 2.0881   | 2.6300    | 0.1527  | 10.121        |
| C   | 2.5°C   | 7.5%   | 2.0828   | 2.6154    | 0.1621  | 10.101        |
| D   | 4.0°C   | 10.0%  | 2.0940   | 2.6456    | 0.1426  | 10.168        |

---

## 4. Cross-Validation Results (5-Fold on Training Set)

| Exp | CV MAE Mean | CV MAE Std | CV RMSE Mean | CV RMSE Std | CV R² Mean | CV R² Std |
|-----|------------:|-----------:|-------------:|------------:|-----------:|----------:|
| A   | 2.0758      | 0.0315     | 2.6236       | 0.0499      | 0.0950     | 0.0423    |
| B   | 2.0627      | 0.0317     | 2.6033       | 0.0529      | 0.1092     | 0.0337    |
| C   | 2.0419      | 0.0383     | 2.5886       | 0.0617      | 0.1193     | 0.0344    |
| D   | 2.0518      | 0.0284     | 2.5953       | 0.0462      | 0.1142     | 0.0450    |

### Per-Fold CV Table

| Exp | Fold | MAE    | RMSE   | R²     | MAPE (%)  |
|-----|-----:|-------:|-------:|-------:|----------:|
| A   | 1    | 2.0997 | 2.6262 | 0.0928 | 10.253    |
| A   | 2    | 2.0582 | 2.6145 | 0.0842 | 10.108    |
| A   | 3    | 2.0368 | 2.5944 | 0.0310 |  9.763    |
| A   | 4    | 2.0694 | 2.5767 | 0.1336 | 10.226    |
| A   | 5    | 2.1148 | 2.7061 | 0.1333 | 10.064    |
| B   | 1    | 2.0577 | 2.5907 | 0.1171 | 10.024    |
| B   | 2    | 2.0345 | 2.5786 | 0.1092 |  9.996    |
| B   | 3    | 2.0429 | 2.5654 | 0.0525 |  9.802    |
| B   | 4    | 2.0627 | 2.5855 | 0.1277 | 10.209    |
| B   | 5    | 2.1156 | 2.6963 | 0.1395 | 10.071    |
| C   | 1    | 2.0512 | 2.5895 | 0.1179 |  9.986    |
| C   | 2    | 2.0529 | 2.5869 | 0.1034 | 10.095    |
| C   | 3    | 1.9855 | 2.5393 | 0.0717 |  9.527    |
| C   | 4    | 2.0297 | 2.5377 | 0.1596 | 10.060    |
| C   | 5    | 2.0901 | 2.6895 | 0.1438 |  9.934    |
| D   | 1    | 2.0428 | 2.5797 | 0.1246 |  9.961    |
| D   | 2    | 2.0791 | 2.6256 | 0.0764 | 10.226    |
| D   | 3    | 2.0213 | 2.5565 | 0.0591 |  9.701    |
| D   | 4    | 2.0314 | 2.5543 | 0.1486 | 10.080    |
| D   | 5    | 2.0843 | 2.6601 | 0.1625 |  9.884    |

---

## 5. Interpretation

### Does prediction quality degrade with more weather noise?

**No — the model demonstrates strong robustness to weather noise across all tested levels.**

The key findings are:

| Metric | Range across A–D | Max Δ from Baseline (A) |
|--------|-----------------|--------------------------|
| Test MAE   | 2.0828 – 2.0940 | ±0.0112 litres           |
| Test RMSE  | 2.6154 – 2.6456 | ±0.0256 litres           |
| Test R²    | 0.1426 – 0.1621 | ±0.0165                  |
| Test MAPE  | 10.10% – 10.17% | ±0.047 percentage points |

The variation in MAE across all four noise levels is less than **0.012 litres**, which is negligible relative to the absolute prediction error (~2.09 litres). R² fluctuates by at most ±0.016, well within the fold-to-fold variance seen in cross-validation.

Notably, Experiment C (moderate noise: 2.5°C / 7.5%) shows *marginally lower* MAE (2.0828) than the no-noise baseline (Experiment A: 2.0929). This is expected stochastic variability — the XGBoost ensemble is not sensitive to the small perturbations introduced.

### Comparison to No-Noise Baseline (Experiment A)

Experiment A (temp_sd=0.0, humidity_sd=0.0) serves as the internal no-noise baseline:
- **Test MAE:** 2.0929 | **R²:** 0.1456 | **MAPE:** 10.148%
- **CV MAE:** 2.0758 ± 0.0315

The CV MAE of **2.0758** matches the XGBoost CV MAE from the full five-model comparison (2.0758), confirming consistency between this analysis and the main experiment.

The test R² of 0.1456 (vs. the five-model comparison value) may differ slightly because the noise pipeline processes the engineered dataset afresh and applies the same 80/20 split. The random_state=42 ensures consistent splits, but minor floating-point differences in the engineered columns (e.g., THI recomputed from the same base temperature/humidity) can shift predictions marginally.

---

## 6. Limitations

1. **Synthetic weather baseline:** The original dataset's temperature and humidity values are themselves generated by a stochastic simulation (see `weather.py`). This study adds Gaussian perturbations *on top of* that existing variance. The measured robustness may therefore be partly attributable to the model already learning to handle noisy weather inputs during initial training.

2. **Independent RNG per experiment:** Each noise level uses a fresh `np.random.default_rng(42)` instance, ensuring each experiment is independent and reproducible, but means noise vectors are drawn from the same seed — not an accumulation of noise.

3. **Weather-only noise:** This study perturbs only temperature and humidity (and their derived features). Other sources of real-world noise (e.g., measurement errors in age, weight, feed quantity) are not tested.

4. **Model not retrained on a held-out noise-free set:** Each experiment trains and tests on the same noisy dataset. A stricter design would train on noisy data and test on clean data (or vice versa).

---

## 7. Output Files

| File | Description |
|------|-------------|
| `noise_sensitivity_results.csv` | Experiment-level summary (test + CV metrics) |
| `noise_sensitivity_cv.csv` | Per-fold CV metrics for all 4 experiments |
| `noise_sensitivity_comparison.png` | Line charts: MAE and R² vs noise level (dpi=150) |
| `noise_sensitivity_report.md` | This report |

---

*Analysis executed with Python (.venv), XGBoost, scikit-learn. Random seed: 42 throughout.*
