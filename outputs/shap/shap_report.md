# SHAP Explainability Report

This report explains model predictions for milk yield using SHAP values computed on the final trained model.

## Top features (by mean absolute SHAP)

1. **weight** — mean |SHAP|=1.0249, mean SHAP=0.0442 (positive)

2. **age_weight_ratio** — mean |SHAP|=0.5952, mean SHAP=-0.0065 (negative)

3. **feed_thi_interaction** — mean |SHAP|=0.4717, mean SHAP=-0.0090 (negative)

4. **temp_humidity** — mean |SHAP|=0.4194, mean SHAP=0.0069 (positive)

5. **feed** — mean |SHAP|=0.3777, mean SHAP=-0.0009 (negative)

6. **humidity** — mean |SHAP|=0.2977, mean SHAP=-0.0114 (negative)

7. **age** — mean |SHAP|=0.2529, mean SHAP=-0.0129 (negative)

8. **thi_squared** — mean |SHAP|=0.0780, mean SHAP=0.0003 (positive)

9. **temperature** — mean |SHAP|=0.0461, mean SHAP=-0.0000 (negative)

10. **thi** — mean |SHAP|=0.0191, mean SHAP=0.0000 (positive)

11. **health_status** — mean |SHAP|=0.0059, mean SHAP=-0.0017 (negative)

12. **feed_weight_ratio** — mean |SHAP|=0.0014, mean SHAP=0.0003 (positive)

## Focused feature explanations

### thi
- Importance (mean |SHAP|): 0.0191
- Average contribution: 0.0000 (positive)
- Explanation: Temperature-Humidity Index captures combined heat stress — higher THI typically reduces milk yield; SHAP shows how THI shifts predictions for individual cows.

### age
- Importance (mean |SHAP|): 0.2529
- Average contribution: -0.0129 (negative)
- Explanation: Age affects production lifecycle; depending on parity/lactation stage, age can increase or decrease yield.

### weight
- Importance (mean |SHAP|): 1.0249
- Average contribution: 0.0442 (positive)
- Explanation: Body weight correlates with metabolic capacity and milk production; heavier cows often produce more, reflected in a positive SHAP sign when present.

### feed
- Importance (mean |SHAP|): 0.3777
- Average contribution: -0.0009 (negative)
- Explanation: Feed intake is a direct input; more feed generally supports higher yield, so SHAP often shows positive contributions for higher feed values.

## Engineered features

- **age_weight_ratio** — mean |SHAP|=0.5952, mean SHAP=-0.0065
- **feed_thi_interaction** — mean |SHAP|=0.4717, mean SHAP=-0.0090
- **thi_squared** — mean |SHAP|=0.0780, mean SHAP=0.0003
- **thi** — mean |SHAP|=0.0191, mean SHAP=0.0000
- **feed_weight_ratio** — mean |SHAP|=0.0014, mean SHAP=0.0003

## How to read these results
- Mean |SHAP| indicates feature importance averaged across the dataset.
- Mean SHAP (signed) indicates whether a feature tends to push predictions up (positive) or down (negative).

Generated files:
- shap\shap_summary.png
- shap\shap_bar.png
- shap\shap_feature_importance.csv
