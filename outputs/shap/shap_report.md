# SHAP Explainability Report

This report explains model predictions for milk yield using SHAP values computed on the final trained model.

## Top features (by mean absolute SHAP)

1. **weight** — mean |SHAP|=0.7201, mean SHAP=0.0111 (positive)

2. **age** — mean |SHAP|=0.3043, mean SHAP=0.0031 (positive)

3. **age_weight_ratio** — mean |SHAP|=0.1488, mean SHAP=-0.0120 (negative)

4. **feed_weight_ratio** — mean |SHAP|=0.0563, mean SHAP=0.0002 (positive)

5. **feed** — mean |SHAP|=0.0539, mean SHAP=-0.0038 (negative)

6. **feed_thi_interaction** — mean |SHAP|=0.0311, mean SHAP=-0.0005 (negative)

7. **feed_per_weight** — mean |SHAP|=0.0151, mean SHAP=0.0008 (positive)

8. **temp_humidity** — mean |SHAP|=0.0104, mean SHAP=-0.0005 (negative)

9. **thi** — mean |SHAP|=0.0102, mean SHAP=0.0004 (positive)

10. **temperature** — mean |SHAP|=0.0098, mean SHAP=-0.0001 (negative)

11. **humidity** — mean |SHAP|=0.0096, mean SHAP=0.0009 (positive)

12. **thi_squared** — mean |SHAP|=0.0033, mean SHAP=0.0003 (positive)

13. **health_status** — mean |SHAP|=0.0014, mean SHAP=-0.0000 (negative)

## Focused feature explanations

### thi
- Importance (mean |SHAP|): 0.0102
- Average contribution: 0.0004 (positive)
- Explanation: Temperature-Humidity Index captures combined heat stress — higher THI typically reduces milk yield; SHAP shows how THI shifts predictions for individual cows.

### age
- Importance (mean |SHAP|): 0.3043
- Average contribution: 0.0031 (positive)
- Explanation: Age affects production lifecycle; depending on parity/lactation stage, age can increase or decrease yield.

### weight
- Importance (mean |SHAP|): 0.7201
- Average contribution: 0.0111 (positive)
- Explanation: Body weight correlates with metabolic capacity and milk production; heavier cows often produce more, reflected in a positive SHAP sign when present.

### feed
- Importance (mean |SHAP|): 0.0539
- Average contribution: -0.0038 (negative)
- Explanation: Feed intake is a direct input; more feed generally supports higher yield, so SHAP often shows positive contributions for higher feed values.

## Engineered features

- **age_weight_ratio** — mean |SHAP|=0.1488, mean SHAP=-0.0120
- **feed_weight_ratio** — mean |SHAP|=0.0563, mean SHAP=0.0002
- **feed_thi_interaction** — mean |SHAP|=0.0311, mean SHAP=-0.0005
- **feed_per_weight** — mean |SHAP|=0.0151, mean SHAP=0.0008
- **thi** — mean |SHAP|=0.0102, mean SHAP=0.0004
- **thi_squared** — mean |SHAP|=0.0033, mean SHAP=0.0003

## How to read these results
- Mean |SHAP| indicates feature importance averaged across the dataset.
- Mean SHAP (signed) indicates whether a feature tends to push predictions up (positive) or down (negative).

Generated files:
- shap\shap_summary.png
- shap\shap_bar.png
- shap\shap_feature_importance.csv
