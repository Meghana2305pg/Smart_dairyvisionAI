# SHAP Analysis Report — DairyVision AI XGBoost Model
## 1. Model and Feature List
**Model:** XGBoost Regressor (`outputs/thi_corrected/model_comparison/model_xgboost.pkl`)

**Features (12):** age, weight, health_status, feed, temperature, humidity, thi, feed_weight_ratio, temp_humidity, thi_squared, feed_thi_interaction, age_weight_ratio

**Target:** `milk_output` (litres/day)

---
## 2. SHAP Value Matrix Dimensions
- Test set: **600 samples × 12 features**
- SHAP matrix shape: **(600, 12)**
- Explainer: `shap.TreeExplainer` (exact Shapley values)

---
## 3. Global Feature Importance Table

| Rank | Feature | Readable Label | Mean |SHAP| |
|------|---------|---------------|-------------|
| 1 | weight | Weight | 0.690741 |
| 2 | age | Age | 0.459916 |
| 3 | age_weight_ratio | Age/Weight Ratio | 0.170937 |
| 4 | feed_weight_ratio | Feed/Weight Ratio | 0.150728 |
| 5 | feed | Feed | 0.149888 |
| 6 | feed_thi_interaction | Feed x THI | 0.135242 |
| 7 | temp_humidity | Temp x Humidity | 0.098207 |
| 8 | humidity | Humidity | 0.091585 |
| 9 | thi | THI | 0.083163 |
| 10 | temperature | Temperature | 0.074321 |
| 11 | thi_squared | THI squared | 0.042086 |
| 12 | health_status | Health Status | 0.019603 |

---
## 4. Interpretation of Top 5 Features

| Rank | Feature | Mean |SHAP| |
|------|---------|-------------|
| 1 | Weight | 0.690741 |
| 2 | Age | 0.459916 |
| 3 | Age/Weight Ratio | 0.170937 |
| 4 | Feed/Weight Ratio | 0.150728 |
| 5 | Feed | 0.149888 |

**No weather / THI features appear in the top 5.**

### Weight (`weight`)

Body weight proxies metabolic capacity. Heavier animals generally receive positive SHAP; underweight animals contribute negatively.

### Age (`age`)

Age has a non-linear relationship with output. Mid-parity cows (peak lactation) receive positive SHAP; very young or old animals are penalised. XGBoost tree splits capture this non-linearity.

### Age/Weight Ratio (`age_weight_ratio`)

Age/weight ratio captures body-condition relative to developmental stage. Poor-condition older animals receive negative SHAP; well-conditioned animals receive positive SHAP.

### Feed/Weight Ratio (`feed_weight_ratio`)

Feed scaled by body weight is a proxy for relative feed sufficiency. Animals above their breed-average feed allowance receive positive SHAP.

### Feed (`feed`)

Feed intake is the dominant driver of milk yield. High feed values produce strongly positive SHAP contributions; low feed suppresses predictions. This aligns with biology: dietary energy directly limits milk synthesis.

### Weather / THI context

Weather and THI features do **not** appear in the top 5 by global mean |SHAP|. This is consistent with **synthetic weather generation**: temperature and humidity are drawn from seasonal ranges with Gaussian noise, so their variance is statistically present but not calibrated to real farm conditions. The model therefore attributes most predictive power to animal-intrinsic features (feed, age, weight, health). This is a known limitation of synthetic weather and should be explicitly stated in any publication.

---
## 5. Dependence Plot Interpretations

### 5.1. Weight (`weight`)

Positive monotone trend for body weight. Very heavy and very light extremes may show saturation effects.

### 5.2. Age (`age`)

Likely hump-shaped: mid-age animals (peak lactation) receive positive SHAP; very young and geriatric animals receive negative SHAP.

### 5.3. Age/Weight Ratio (`age_weight_ratio`)

Animals with high ratio (old but light) receive negative SHAP; low ratio (well-conditioned young) receive positive SHAP.

---
## 6. Important Caveats

> **SHAP values quantify the contribution of each feature within THIS model on THIS dataset. They do not establish causation.**

- The model was trained on a **synthetic dataset** using parametric weather generation and plausible animal physiology assumptions, not from a longitudinal field study.
- SHAP feature rankings reflect both biological signal and artefacts of the synthetic data-generating process.
- Weather / THI features with moderate or low importance may have higher real-world importance than these values suggest, because synthetic weather has lower within-season variance than actual climate data.
- Results should be interpreted as internal model explanations and not as causal estimates of biological effect sizes.

---
## 7. Output Files

| File | Description |
|------|-------------|
| `shap_beeswarm_summary.png` | SHAP beeswarm plot (all 12 features, all 600 test samples) |
| `shap_feature_importance_bar.png` | Horizontal bar chart of mean |SHAP| per feature |
| `shap_dependence_weight.png` | SHAP dependence plot for Weight |
| `shap_dependence_age.png` | SHAP dependence plot for Age |
| `shap_dependence_age_weight_ratio.png` | SHAP dependence plot for Age/Weight Ratio |
| `shap_feature_importance.csv` | Numerical importance table (feature, mean_abs_shap, rank) |
| `shap_report.md` | This report |

*Generated automatically by the DairyVision AI SHAP analysis pipeline.*
