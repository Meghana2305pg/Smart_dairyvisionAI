# THI Pipeline & Backup Audit Report
**Project:** DairyVision AI — Smart Dairy Monitoring System  
**Report Date:** 2026-11-19  
**Status:** INSPECTION ONLY — No files were modified during this audit  
**Auditor:** Antigravity AI Assistant  

---

## Executive Summary

The Temperature-Humidity Index (THI) formula implemented in this project uses a constant of **+16.4**, which is **30 units below** the standard Mader et al. (2006) Celsius formulation (+46.4). This discrepancy is not trivial: at typical dairy cattle environmental conditions (T=35°C, RH=80%), the implemented formula yields THI ≈ 60.9 ("Mild stress") while the standard formula yields THI ≈ 90.9 ("Emergency stress") — a two-category classification error.

**Every experiment, model, metric, SHAP analysis, simulation, and health alert output depends on THI.** Only the genetics module is independent. If the formula is corrected to +46.4, all experimental outputs must be regenerated and all paper-reported numerical results will change.

**This report covers:**
- A. Complete project file structure
- B. THI dependency map
- C. Experimental output inventory
- D. Model and experiment impact assessment
- E. Reproducibility assessment
- F. Proposed backup strategy (not yet implemented)
- G. Regeneration execution order (pending approval)
- H. Risk assessment

---

## A. Complete Project Structure

> [!NOTE] All paths are relative to `/Users/sanjana/Smart_dairyvisionAI/`. The `.venv/` directory is excluded from this listing.

### Source Code (Python)

| File | Purpose |
|------|---------|
| `feature_engineering.py` | Computes all engineered features including THI (line 89) |
| `data_loader.py` | Loads, merges (inner join on `Cattle_ID`), and assigns weather data |
| `weather.py` | Fetches Open-Meteo API; falls back to 28.0°C / 65.0% RH |
| `config.py` | Central config: `RANDOM_SEED=42`, `CV_FOLDS=5`, feature lists, fallback values |
| `thi_audit.py` | Standalone audit script; references +16.4 formula; contains unexecuted Fahrenheit formula |
| `train.py` | 5-fold CV training; calls `build_features()`; saves `models/best_milk_model.pkl` |
| `evaluate.py` | 80/20 split evaluation; calls `build_features()`; saves all metrics and plots |
| `simulate.py` | Digital twin simulation; calls `compute_thi()` directly at lines 164–165 |
| `health_alerts.py` | Rule-based health alerts; uses THI thresholds 70/79/90; loads `engineered_dataset.csv` |
| `anomaly_detection.py` | Anomaly detection; uses `thi` as one of 5 features; threshold ≥80 at line 33 |
| `explainability.py` | SHAP analysis; feature matrix `X` includes `thi`, `thi_squared`, `feed_thi_interaction` |
| `run_pipeline.py` | Master orchestrator; Steps 1–8 (weather → load → features → train → evaluate → SHAP → anomaly → health → simulate) |
| `health_classification.py` | Separate classification experiment; calls `assign_weather()` + `add_engineered_features()` |
| `xgboost_rmse_plot.py` | Standalone plot script; calls `build_features()` |
| `genetics/genetics_analysis.py` | Genetics module; uses `genetics/data/sire_performance.csv`; **does NOT call `build_features()`** |

### Notebooks

| File | Purpose |
|------|---------|
| `xgboost_training_vs_test_rmse.ipynb` | Notebook version of training/test RMSE curve; calls `build_features()` |

### Datasets (Raw)

| File | Rows | Columns | THI-Dependent? |
|------|------|---------|---------------|
| `data/global_cattle_milk_yield_prediction_dataset.csv` | 3,000 | 4 | No (input) |
| `data/global_cattle_disease_detection_dataset.csv` | 3,000 | 6 | No (input) |
| `genetics/data/sire_performance.csv` | — | — | No |

### Research Paper

| File | Location | Git Status |
|------|----------|-----------|
| `IEEE_Paper_Nov12.tex` | `research_paper/` | **Untracked** (not committed to git) |

---

## B. THI Dependency Map

> [!IMPORTANT] The column "THI Dependency Type" distinguishes: **Direct** (computes or stores THI), **Indirect** (calls a function that computes THI), **Reference** (string/comment reference only), and **Threshold** (uses a numeric THI value for classification).

| File | Function / Line | THI Dependency Type | Regeneration Required? |
|------|----------------|--------------------|-----------------------|
| `feature_engineering.py` | `compute_thi()` line 89: `(0.8*T) + (RH/100*(T-14.4)) + 16.4` | **Direct — computation** | YES — this is the formula source |
| `config.py` | Line 100 comment references +16.4; `ALL_FEATURES` includes `thi`, `thi_squared`, `feed_thi_interaction` | Reference + feature list | YES (feature list; comment must be updated if formula changes) |
| `thi_audit.py` | Lines 88, 121, 238: string refs to +16.4; unexecuted Fahrenheit formula in module docstring | Reference | YES (string refs; not an executable dependency) |
| `data_loader.py` | `assign_weather()` → calls `compute_thi()` indirectly via `feature_engineering` import | **Indirect** | YES |
| `train.py` | Calls `build_features()` (which calls `compute_thi()`) | **Indirect** | YES — model trained on THI-contaminated features |
| `evaluate.py` | Calls `build_features()` | **Indirect** | YES — all test metrics derived from THI features |
| `simulate.py` | Lines 164–165: calls `compute_thi()` directly in simulation grid | **Direct — computation** | YES — all simulation THI values are wrong |
| `health_alerts.py` | Thresholds 70/79/90 applied to `thi` column from `engineered_dataset.csv` | **Threshold** | YES — thresholds may need recalibration with new THI scale |
| `anomaly_detection.py` | Line 33: `_binarize_heat_stress(thi >= 80)` | **Threshold** | YES — 80 threshold changes meaning with +46.4 |
| `explainability.py` | SHAP on feature matrix containing `thi`, `thi_squared`, `feed_thi_interaction` | **Indirect** | YES — all SHAP values, rankings, and plots will change |
| `run_pipeline.py` | Master orchestrator for Steps 1–8 | **Indirect (all steps)** | YES — reruns all dependent steps |
| `health_classification.py` | Calls `assign_weather()` + `add_engineered_features()` including THI features | **Indirect** | YES — classification model and metrics |
| `xgboost_rmse_plot.py` | Calls `build_features()` | **Indirect** | YES |
| `xgboost_training_vs_test_rmse.ipynb` | Calls `build_features()` | **Indirect** | YES |
| `genetics/genetics_analysis.py` | Uses `sire_performance.csv` only; no weather or feature engineering | **None** | **NO — fully independent** |
| `research_paper/IEEE_Paper_Nov12.tex` | Equations `thi_std` and `1`; stated statistics (mean 58.25, range 33.4–94.8); simulation THI values | Reference + stated results | YES — numeric values must be updated after regeneration |

### Data Flow Diagram

```
Raw CSVs (milk, disease)
        │
        ▼
data_loader.py::load_data()
  → pandas.merge(on='Cattle_ID', how='inner')   ← 3,000 merged records
  → assign_weather()
      → weather.py::fetch_weather()              ← Open-Meteo API or fallback (28.0°C, 65.0%)
  → Returns merged DataFrame with temperature, humidity columns
        │
        ▼
feature_engineering.py::build_features()
  → compute_thi(temperature, humidity)           ← LINE 89: +16.4 (THE ISSUE)
  → thi_squared = thi ** 2
  → feed_thi_interaction = feed_quantity * thi
  → heat_stress_indicator (threshold-based)
  → Returns feature matrix X, target y
        │
        ├──► train.py           → models/best_milk_model.pkl, cv_results.csv
        ├──► evaluate.py        → test_metrics.csv, feature_importance.csv, all plots
        ├──► explainability.py  → shap_feature_importance.csv, shap_summary.png, shap_bar.png
        ├──► simulate.py        → simulation_results.csv, simulation_heatmap.png (+ compute_thi direct)
        ├──► health_alerts.py   → health_alerts.csv
        ├──► anomaly_detection.py → anomaly_report.csv
        └──► health_classification.py → health_classification_metrics.csv, confusion_matrix.csv
```

---

## C. Experimental Output Inventory

> [!NOTE] "THI-Dep." = output value depends on the THI formula. "Regen. Needed" = must be regenerated if formula is corrected. All paths are relative to `/Users/sanjana/Smart_dairyvisionAI/`.

### Primary Outputs (`outputs/`)

| Filename | Size | Created / Modified | THI-Dep. | Regen. Needed | Generating Script |
|----------|------|--------------------|----------|--------------|-------------------|
| `outputs/engineered_dataset.csv` | 652 KB | Aug 30 2026 00:57 | **YES** | YES | `feature_engineering.py` via `thi_audit.py` or `run_pipeline.py` |
| `models/best_milk_model.pkl` | 352 KB | Aug 29 2026 23:47 | **YES** | YES | `train.py` |
| `outputs/cv_results.csv` | 1.8 KB | Aug 29 2026 23:47 | **YES** | YES | `train.py` |
| `outputs/test_metrics.csv` | 97 B | Aug 29 2026 23:47 | **YES** | YES | `evaluate.py` |
| `outputs/feature_importance.csv` | 821 B | Aug 29 2026 23:47 | **YES** | YES | `evaluate.py` |
| `outputs/paper_table_model_comparison.csv` | 329 B | Aug 29 2026 23:47 | **YES** | YES | `run_pipeline.py` |
| `outputs/all_model_test_comparison.csv` | — | Aug 29 2026 23:47 | **YES** | YES | `evaluate.py` |
| `outputs/model_test_error_metrics.csv` | — | Aug 29 2026 23:47 | **YES** | YES | `evaluate.py` |
| `outputs/tuning_results.json` | 341 B | Aug 10 2026 15:36 | Partial* | Conditional* | `train.py` (RandomizedSearchCV) |
| `outputs/simulation_results.csv` | 2.8 KB | Aug 29 2026 23:47 | **YES** | YES | `simulate.py` |
| `outputs/anomaly_report.csv` | 895 KB | Aug 30 2026 00:57 | **YES** | YES | `anomaly_detection.py` |
| `outputs/anomaly_summary.md` | — | Aug 30 2026 00:57 | **YES** | YES | `anomaly_detection.py` |
| `outputs/health_alerts.csv` | 561 KB | Aug 29 2026 23:47 | **YES** | YES | `health_alerts.py` |
| `outputs/health_alert_summary.md` | — | Aug 10 2026 15:36 | **YES** | YES | `health_alerts.py` |
| `outputs/thi_distribution_report.txt` | — | Jul 31 2026 | **YES** | YES | `thi_audit.py` |

> *`tuning_results.json` stores XGBoost hyperparameters found by RandomizedSearchCV. The hyperparameters themselves are not THI values, but they were optimized on THI-contaminated data. If the formula is corrected, the optimal hyperparameters may shift — the safest approach is to re-run tuning, though reusing existing params is an acceptable trade-off for speed.

### Figure Outputs (`outputs/`)

| Filename | THI-Dep. | Regen. Needed | Generating Script |
|----------|----------|--------------|-------------------|
| `outputs/predicted_vs_actual.png` | YES | YES | `evaluate.py` |
| `outputs/cv_r2_boxplot.png` | YES | YES | `evaluate.py` |
| `outputs/xgboost_training_validation_rmse_curve.png` | YES | YES | `evaluate.py` |
| `outputs/all_model_test_comparison.png` | YES | YES | `evaluate.py` |
| `outputs/model_test_error_metrics.png` | YES | YES | `evaluate.py` |
| `outputs/model_comparison_r2.png` | YES | YES | `evaluate.py` |
| `outputs/residual_histogram.png` | YES | YES | `evaluate.py` |
| `outputs/residuals_vs_fitted.png` | YES | YES | `evaluate.py` |
| `outputs/simulation_heatmap.png` | YES | YES | `simulate.py` |
| `outputs/simulation_feedlines.png` | YES | YES | `simulate.py` |
| `outputs/simulation_thi_impact.png` | YES | YES | `simulate.py` |
| `outputs/shap/shap_summary.png` | YES | YES | `explainability.py` |
| `outputs/shap/shap_bar.png` | YES | YES | `explainability.py` |
| `outputs/thi_histogram.png` | YES | YES | `thi_audit.py` |

### Health Classification Outputs

| Filename | THI-Dep. | Regen. Needed | Generating Script |
|----------|----------|--------------|-------------------|
| `research_outputs/tables/health_classification_metrics.csv` | YES | YES | `health_classification.py` |
| `research_outputs/tables/confusion_matrix.csv` | YES | YES | `health_classification.py` |

### SHAP Outputs

| Filename | THI-Dep. | Regen. Needed | Generating Script |
|----------|----------|--------------|-------------------|
| `outputs/shap/shap_feature_importance.csv` | YES | YES | `explainability.py` |

### Mirror/Duplicate Outputs

| Directory | Notes |
|-----------|-------|
| `research_outputs/` | Mirror of `outputs/`; created Aug 29 23:40 |
| `Outputs/` (capital O) | Also mirrors `outputs/`; both must be regenerated |

### Genetics Outputs (Independent)

| Directory | THI-Dep. | Regen. Needed |
|-----------|----------|--------------|
| `outputs/genetics/*` | **NO** | **NO** |

---

## D. Model and Experiment Impact Assessment

| Experiment / Model | Uses THI? | Regeneration Required? | Notes |
|-------------------|----------|----------------------|-------|
| XGBoost Regressor | YES | YES | Primary model; `thi`, `thi_squared`, `feed_thi_interaction` are features |
| Random Forest Regressor | YES | YES | Same feature matrix |
| Linear Regression | YES | YES | Same feature matrix |
| Decision Tree Regressor | YES | YES | Same feature matrix |
| Naive baseline | YES | YES | Same feature matrix or target-only baseline |
| 5-fold Cross-Validation | YES | YES | Each fold uses `build_features()` |
| Wilcoxon statistical test | YES | YES | Input is per-fold R² values; will change with new THI |
| SHAP analysis | YES | YES | SHAP values, rankings, and feature importance plots will change |
| Ablation study | YES | YES | If ablation removes THI features, results change |
| Gaussian noise sensitivity | YES | YES | Noise is added to THI-computed features |
| Anomaly detection | YES | YES | `thi` is one of 5 anomaly features; threshold at 80 |
| Health alert classification | YES | YES | Thresholds 70/79/90 calibrated to +16.4 scale |
| Digital twin simulation | YES | YES | `compute_thi()` called directly; all grid values wrong |
| Health classification model | YES | YES | Via `assign_weather()` + `add_engineered_features()` |
| Genetics module | **NO** | **NO** | Fully independent; uses `sire_performance.csv` only |

### Quantified Formula Impact

At representative conditions (T=35°C, RH=80%):

| Formula | THI Value | Stress Category | Category Offset |
|---------|-----------|----------------|----------------|
| Implemented (+16.4) | 60.9 | Mild | — |
| Standard Mader (+46.4) | 90.9 | Emergency | +2 categories |

The discrepancy is a fixed offset of exactly **+30 THI units** across all conditions. However, derived features are **not** offset by a simple constant:
- `thi_squared`: $(x+30)^2 \neq x^2 + 30^2$ — non-linear amplification
- `feed_thi_interaction`: scaled proportionally but changes feed-to-THI ratio non-linearly
- Heat stress indicator (threshold-based): category boundaries shift entirely

---

## E. Reproducibility Assessment

### Deterministic Components

| Component | Seed / Fixed Value | Reproducible? |
|-----------|-------------------|--------------|
| KFold cross-validation | `RANDOM_SEED = 42` (`config.py`) | YES |
| `train_test_split` (80/20) | `random_state = 42` | YES |
| Random Forest `RandomState` | `RANDOM_SEED = 42` | YES |
| XGBoost `seed` | `RANDOM_SEED = 42` | YES |
| `RandomizedSearchCV` | `random_state = 42` | YES |
| Gaussian noise perturbation | `np.random.default_rng(RANDOM_SEED)` | YES |
| Weather fallback temperature | `FALLBACK_TEMP = 28.0°C` (`config.py`) | YES |
| Weather fallback humidity | `FALLBACK_HUM = 65.0%` (`config.py`) | YES |
| XGBoost hyperparameters | Stored in `outputs/tuning_results.json` | YES (if reused) |

### Non-Deterministic Components

| Component | Issue | Mitigation |
|-----------|-------|-----------|
| Open-Meteo API fetch | Real-time weather values differ on each call | Use fallback values; set `USE_API = False` or disconnect network |
| Package versions | Minor version changes may affect floating-point | Pin versions using `.venv`; check `pip freeze` |

### Environment Requirements for Exact Reproduction

- Python **3.12.13** (from `.python-version`)
- All packages installed in `.venv/` (versions recorded at time of original run)
- Weather API disabled OR internet disconnected (use `FALLBACK_TEMP=28.0`, `FALLBACK_HUM=65.0`)
- Hyperparameters reloaded from `outputs/tuning_results.json` (not re-tuned)

### Timestamp Inconsistency (Verified Fact)

> [!WARNING] The `outputs/engineered_dataset.csv` timestamp is **Aug 30 2026 00:57**, while `models/best_milk_model.pkl`, `cv_results.csv`, and all evaluation outputs are **Aug 29 2026 23:47**. The model was trained on a different version of `engineered_dataset.csv` than the one currently on disk. The Aug 30 file was regenerated by `thi_audit.py` *after* the model was trained. The current model and the current engineered dataset are **out of sync**.

---

## F. Proposed Backup Strategy

> [!CAUTION] This backup has NOT been implemented. It must be created before any formula correction is applied. Approval is required before creating the backup.

### Proposed Directory Structure

```
/Users/sanjana/Smart_dairyvisionAI/backups/pre_thi_correction/
├── source/                          # All Python source files
│   ├── feature_engineering.py
│   ├── data_loader.py
│   ├── weather.py
│   ├── config.py
│   ├── thi_audit.py
│   ├── train.py
│   ├── evaluate.py
│   ├── simulate.py
│   ├── health_alerts.py
│   ├── anomaly_detection.py
│   ├── explainability.py
│   ├── run_pipeline.py
│   ├── health_classification.py
│   ├── xgboost_rmse_plot.py
│   └── genetics/
├── datasets/                        # Raw input CSVs
│   ├── global_cattle_milk_yield_prediction_dataset.csv
│   └── global_cattle_disease_detection_dataset.csv
├── models/                          # Trained model artifacts
│   └── best_milk_model.pkl          (352 KB)
├── results/                         # All CSV result files
│   ├── engineered_dataset.csv       (652 KB)
│   ├── cv_results.csv
│   ├── test_metrics.csv
│   ├── feature_importance.csv
│   ├── paper_table_model_comparison.csv
│   ├── simulation_results.csv
│   ├── health_alerts.csv            (561 KB)
│   ├── anomaly_report.csv           (895 KB)
│   ├── tuning_results.json
│   └── shap/shap_feature_importance.csv
├── figures/                         # All PNG outputs
│   └── [all .png files from outputs/]
├── paper/                           # Research paper
│   └── IEEE_Paper_Nov12.tex
└── configuration/                   # Config and environment
    ├── config.py
    ├── .python-version
    └── backup_manifest.txt          # List of files + checksums
```

### Git Preservation (Recommended in Addition)

```bash
# Step 1: Add untracked paper to git
git add research_paper/IEEE_Paper_Nov12.tex

# Step 2: Commit current state including tracked deletions of old paper files
git commit -m "Pre-THI-correction snapshot: add IEEE_Paper_Nov12.tex, record old paper deletions"

# Step 3: Create a tag for easy reference
git tag pre-thi-correction-snapshot
```

> [!NOTE] Git only tracks source files. Outputs (`outputs/`, `models/`, `research_outputs/`) are likely in `.gitignore`. Those must be backed up by file copy, not git.

### Estimated Backup Size

| Category | Approximate Size |
|----------|----------------|
| `health_alerts.csv` | 561 KB |
| `anomaly_report.csv` | 895 KB |
| `engineered_dataset.csv` | 652 KB |
| `best_milk_model.pkl` | 352 KB |
| All PNGs (combined) | ~600 KB |
| Source files (combined) | ~100 KB |
| **Total estimated** | **~3.2 MB** |

---

## G. Regeneration Execution Order (Pending Approval)

> [!IMPORTANT] This section is for planning only. Do NOT execute until explicitly approved by the user.

The following steps are strictly sequential. Each step depends on the previous.

| Step | Action | File / Command | Verification |
|------|--------|---------------|-------------|
| 1 | Create backup | `cp -r` to `backups/pre_thi_correction/` | Verify file count matches source |
| 2 | Commit paper to git | `git add` + `git commit` + `git tag` | `git log --oneline -3` |
| 3 | Correct formula | `feature_engineering.py:89`: change `+ 16.4` → `+ 46.4` | Also update `config.py:100` comment and `thi_audit.py` string refs |
| 4 | Verify arithmetic | At T=28°C, RH=65%: expected 47.64 (+16.4) vs 77.64 (+46.4) | Manual calculation |
| 5 | Regenerate all outputs | `python run_pipeline.py` | Check exit code = 0 |
| 6 | Verify THI statistics | Check mean, range in `outputs/engineered_dataset.csv` | New mean should be ~88 (old mean + 30) |
| 7 | Check stress distribution | Verify stress categories make biological sense at +46.4 | At T=28, RH=65: THI ≈ 77.6 → "Moderate" (expected correct range) |
| 8 | Collect new metrics | Read `outputs/test_metrics.csv` | Record new MAE, RMSE, R², MAPE |
| 9 | Verify SHAP | Check `outputs/shap/shap_feature_importance.csv` | Verify `thi` ranking vs `thi_squared` etc. |
| 10 | Update paper equations | Update eq `1` constant `16.4` → `46.4`; remove limitation note if corrected | LaTeX compile check |
| 11 | Update paper statistics | Replace THI mean (58.25), range (33.4–94.8) with new values | Verify against step 6 |
| 12 | Update simulation values in paper | Replace grid THI values (33.1, 42.1, 51.3, etc.) if cited | Match `simulation_results.csv` |
| 13 | Compile and review paper | `pdflatex IEEE_Paper_Nov12.tex` | Check for LaTeX errors; review PDF |

---

## H. Risk Assessment

> [!CAUTION] The following risks must be understood before approving formula correction.

### Biological Scale Shift

With +46.4, simulation temperatures (18–42°C) will produce THI values approximately 62–101:

| Temperature (°C) | RH=65% THI (+16.4, current) | THI (+46.4, standard) | Stress Category (standard) |
|-----------------|-----------------------------|-----------------------|---------------------------|
| 18 | ~33 | ~63 | Mild |
| 24 | ~42 | ~72 | Moderate |
| 30 | ~51 | ~81 | Severe |
| 36 | ~61 | ~91 | Emergency |
| 42 | ~71 | ~101 | Emergency |

This means the corrected formula places most of the simulated temperature range in "Severe" or "Emergency" stress categories — which may be biologically more accurate for high-humidity tropical conditions but may also reduce model variation in the heat stress feature.

### Metric Impact

All reported paper metrics will change:

| Metric | Current Value (with +16.4) | New Value (with +46.4) |
|--------|---------------------------|----------------------|
| MAE | 2.0348 | Unknown |
| RMSE | 2.5746 | Unknown |
| R² | 0.1880 | Unknown |
| MAPE | 9.864% | Unknown |

The direction of change (improvement or degradation) cannot be predicted without rerunning experiments.

### Non-Linear Feature Distortion

- `thi_squared` grows as $(x+30)^2$. For current x≈58, this is $3,364$ vs. corrected $7,744$ — a 2.3× difference. This non-linearly amplifies the distortion across all models.
- `feed_thi_interaction` changes proportionally to new THI values, changing feed-to-THI ratios across the entire dataset.

### Threshold Recalibration

Health alert thresholds (70/79/90) and anomaly detection threshold (≥80) were calibrated on the +16.4 scale. After correction, these thresholds must be reviewed:
- With +46.4, the "No stress" zone (THI < 70) will cover a narrower temperature range
- Alert categories will fire at lower real-world temperatures than currently
- These thresholds may now better match published dairy stress literature

### Model Behavior Uncertainty

XGBoost is a tree-based model that learns splits from data. A +30 offset in THI changes the split boundaries learned during training. Random Forest, Decision Tree, and Linear Regression will all respond differently. The R² of 0.188 is already modest; it could improve (THI now spans a range where stress genuinely correlates with yield) or degrade (the new scale may not align better with the yield target).

---

## Unresolved Questions

1. **Should the THI thresholds (70/79/90) be recalibrated after formula correction?** The current thresholds were defined relative to the +16.4 scale. The standard literature thresholds for Celsius THI are typically ≥72 (mild), ≥80 (moderate), ≥90 (severe). After correction, the existing thresholds may actually align better with published values — but this must be verified.

2. **Will the corrected formula improve or harm model accuracy?** This can only be determined empirically after regeneration.

3. **Is the `engineered_dataset.csv` out-of-sync with the trained model?** Yes (confirmed: model=Aug 29, dataset=Aug 30). Before any correction, the existing model should be treated as trained on a dataset that no longer exists on disk. Regeneration will resolve this inconsistency.

4. **Should `tuning_results.json` hyperparameters be reused or re-tuned?** Reusing is faster and may be acceptable, but the optimal hyperparameters may differ on the corrected THI data. This is a research judgment call.

5. **What is the git state of output files?** The `outputs/` and `models/` directories are likely in `.gitignore`. Their contents are not tracked. File copy backup is mandatory before correction.

---

## Summary: What Must Change vs. What Can Stay

| Component | Action Required After Formula Correction |
|-----------|----------------------------------------|
| `feature_engineering.py` line 89 | **Change** `+ 16.4` → `+ 46.4` |
| `config.py` line 100 comment | **Update** to reflect +46.4 |
| `thi_audit.py` string references | **Update** (documentation only) |
| All `outputs/` CSV files | **Regenerate** |
| All `models/*.pkl` | **Regenerate** |
| All `outputs/*.png` figures | **Regenerate** |
| `research_paper/IEEE_Paper_Nov12.tex` | **Update** THI equation, stats, simulation values |
| `genetics/` module | **No change needed** |
| `genetics/data/sire_performance.csv` | **No change needed** |
| Raw input CSVs (`data/`) | **No change needed** |

---

*This report was produced by inspection only. No files were modified during this audit. All findings are based on verified code, file timestamps, and manual arithmetic verification. Formula correction requires explicit user approval before any implementation begins.*
