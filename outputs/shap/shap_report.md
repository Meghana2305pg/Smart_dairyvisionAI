# SHAP Explainability Report

This report explains model predictions for milk yield using SHAP values computed on the final trained model.

## Top features (by mean absolute SHAP)

1. **weight** — mean |SHAP|=0.8995, mean SHAP=0.0385 (positive)

2. **age_weight_ratio** — mean |SHAP|=0.6805, mean SHAP=-0.0078 (negative)

3. **temp_humidity** — mean |SHAP|=0.3992, mean SHAP=0.0062 (positive)

4. **feed_thi_interaction** — mean |SHAP|=0.3533, mean SHAP=-0.0089 (negative)

5. **age** — mean |SHAP|=0.3354, mean SHAP=-0.0176 (negative)

6. **humidity** — mean |SHAP|=0.2851, mean SHAP=-0.0113 (negative)

7. **feed_per_weight** — mean |SHAP|=0.1351, mean SHAP=0.0011 (positive)

8. **feed_weight_ratio** — mean |SHAP|=0.1348, mean SHAP=0.0013 (positive)

9. **thi_squared** — mean |SHAP|=0.0544, mean SHAP=0.0000 (positive)

10. **temperature** — mean |SHAP|=0.0517, mean SHAP=-0.0010 (negative)

11. **thi** — mean |SHAP|=0.0136, mean SHAP=0.0022 (positive)

12. **health_status** — mean |SHAP|=0.0029, mean SHAP=-0.0014 (negative)

13. **feed** — mean |SHAP|=0.0027, mean SHAP=0.0002 (positive)

## Focused feature explanations

### thi
- Importance (mean |SHAP|): 0.0136
- Average contribution: 0.0022 (positive)
- Explanation: Temperature-Humidity Index captures combined heat stress — higher THI typically reduces milk yield; SHAP shows how THI shifts predictions for individual cows.

### age
- Importance (mean |SHAP|): 0.3354
- Average contribution: -0.0176 (negative)
- Explanation: Age affects production lifecycle; depending on parity/lactation stage, age can increase or decrease yield.

### weight
- Importance (mean |SHAP|): 0.8995
- Average contribution: 0.0385 (positive)
- Explanation: Body weight correlates with metabolic capacity and milk production; heavier cows often produce more, reflected in a positive SHAP sign when present.

### feed
- Importance (mean |SHAP|): 0.0027
- Average contribution: 0.0002 (positive)
- Explanation: Feed intake is a direct input; more feed generally supports higher yield, so SHAP often shows positive contributions for higher feed values.

## Engineered features

- **age_weight_ratio** — mean |SHAP|=0.6805, mean SHAP=-0.0078
- **feed_thi_interaction** — mean |SHAP|=0.3533, mean SHAP=-0.0089
- **feed_per_weight** — mean |SHAP|=0.1351, mean SHAP=0.0011
- **feed_weight_ratio** — mean |SHAP|=0.1348, mean SHAP=0.0013
- **thi_squared** — mean |SHAP|=0.0544, mean SHAP=0.0000
- **thi** — mean |SHAP|=0.0136, mean SHAP=0.0022

## How to read these results
- Mean |SHAP| indicates feature importance averaged across the dataset.
- Mean SHAP (signed) indicates whether a feature tends to push predictions up (positive) or down (negative).

Generated files:
- shap/shap_summary.png
- shap/shap_bar.png
- shap/shap_feature_importance.csv
