# Crop Recommendation Model Training Report

This report summarizes the training metrics, classification accuracy, and confusion matrix for the RandomForestClassifier model used in the crop recommendation engine.

## Model Summary
- **Model Type**: RandomForestClassifier
- **Number of Estimators**: 150
- **Max Depth**: 12
- **Training Accuracy**: 99.68%
- **Test Accuracy**: 77.00%

## Features Utilized
### Categorical Fields (Label Encoded):
- `soil_type`
- `state`
- `district`
- `season`
- `water_availability`
- `previous_crop`

### Numeric Fields (Standardized):
- `rainfall`
- `temperature`
- `humidity`
- `farm_size`

## Evaluation Metrics

### Classification Report
```
              precision    recall  f1-score   support

      cotton       0.50      0.24      0.32        21
       maize       0.75      0.92      0.83       173
     mustard       0.54      0.29      0.38        75
      potato       0.67      0.15      0.25        26
        rice       1.00      0.17      0.29         6
     soybean       0.00      0.00      0.00        20
   sugarcane       0.50      0.26      0.34        23
      tomato       0.88      0.96      0.92       276
       wheat       0.68      0.94      0.79        80

    accuracy                           0.77       700
   macro avg       0.61      0.44      0.46       700
weighted avg       0.73      0.77      0.73       700

```

### Confusion Matrix
```
True \ Pred | cotton | maize | mustard | potato | rice | soybean | sugarcane | tomato | wheat
------------------------------------------------------------------------------------------------------------------------------------------------------
cotton      | 5    | 16   | 0    | 0    | 0    | 0    | 0    | 0    | 0   
maize       | 2    | 160  | 2    | 0    | 0    | 0    | 3    | 6    | 0   
mustard     | 0    | 4    | 22   | 1    | 0    | 0    | 0    | 13   | 35  
potato      | 0    | 0    | 3    | 4    | 0    | 0    | 0    | 19   | 0   
rice        | 0    | 3    | 0    | 0    | 1    | 0    | 2    | 0    | 0   
soybean     | 3    | 16   | 0    | 0    | 0    | 0    | 1    | 0    | 0   
sugarcane   | 0    | 15   | 0    | 0    | 0    | 2    | 6    | 0    | 0   
tomato      | 0    | 0    | 9    | 1    | 0    | 0    | 0    | 266  | 0   
wheat       | 0    | 0    | 5    | 0    | 0    | 0    | 0    | 0    | 75  
```

---
Report generated automatically on 2026-06-16 21:06:27
