# Crop Suitability Model Training Report

This report outlines the training and evaluation metrics for the **AI Crop Suitability Validation Model** in Kisan Mitra.

## 1. Model Comparisons

We compared multiple classification algorithms to determine the best model for validating custom crops before planting:

| Model Name | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| RandomForest | 0.9104 | 0.9110 | 0.8276 | 0.8673 |
| XGBoost | 0.9630 | 0.9610 | 0.9333 | 0.9469 |
| LightGBM | 0.9612 | 0.9586 | 0.9305 | 0.9443 |
| CatBoost | 0.9492 | 0.9407 | 0.9141 | 0.9272 |

**Selected Model:** `XGBoost`

---

## 2. Feature Importances

The feature importance contribution from the selected model `XGBoost`:

| Rank | Feature | Importance |
|---|---|---|
| 1 | season | 0.4558 |
| 2 | target_crop | 0.1529 |
| 3 | water_availability | 0.1365 |
| 4 | soil_type | 0.0724 |
| 5 | previous_crop | 0.0678 |
| 6 | rainfall | 0.0470 |
| 7 | temperature | 0.0320 |
| 8 | humidity | 0.0167 |
| 9 | farm_size | 0.0065 |
| 10 | state | 0.0064 |
| 11 | district | 0.0061 |

---

## 3. Confusion Matrix

The confusion matrix for the test partition is visualized below:

![Confusion Matrix](file:///C:/Users/durga/kisan_mitra/backend/confusion_matrix.png)
