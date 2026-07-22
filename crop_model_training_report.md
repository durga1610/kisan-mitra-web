# Kisan Mitra: Crop Recommendation ML Model Training & Evaluation Report

This report documents the machine learning training pipeline, dataset analysis, model benchmarking, feature importance ranking, and artifact generation for the **Crop Recommendation** feature in Kisan Mitra.

---

## Step 1 – Dataset Analysis & Summary

* **Dataset Path**: `backend/dataset/Crop_recommendation.csv`
* **Dataset Dimensions**: **2,200 rows × 8 columns** (7 feature columns + 1 target column)
* **Data Types**:
  - `N` (Nitrogen): `int64` (Range: 0 – 140, Mean: 50.55, Median: 37.0)
  - `P` (Phosphorus): `int64` (Range: 5 – 145, Mean: 53.36, Median: 51.0)
  - `K` (Potassium): `int64` (Range: 5 – 205, Mean: 48.15, Median: 32.0)
  - `temperature`: `float64` (°C, Range: 8.83 – 43.68, Mean: 25.62, Median: 25.60)
  - `humidity`: `float64` (%, Range: 14.26 – 99.98, Mean: 71.48, Median: 80.47)
  - `ph`: `float64` (pH scale, Range: 3.50 – 9.94, Mean: 6.47, Median: 6.43)
  - `rainfall`: `float64` (mm, Range: 20.21 – 298.56, Mean: 103.46, Median: 94.87)
  - `label` (Target): `object` (Crop String Name)

### Data Quality Audit
* **Missing / Null Values**: **0 missing values** across all columns.
* **Duplicate Records**: **0 duplicate rows**.
* **Class Balance**: Perfectly balanced dataset with **22 unique crop categories** (exactly 100 samples per class):
  - *Crops included*: `apple`, `banana`, `blackgram`, `chickpea`, `coconut`, `coffee`, `cotton`, `grapes`, `jute`, `kidneybeans`, `lentil`, `maize`, `mango`, `mothbeans`, `mungbean`, `muskmelon`, `orange`, `papaya`, `pigeonpeas`, `pomegranate`, `rice`, `watermelon`.

---

## Step 2 – Preprocessing & Dataset Splitting

1. **Feature-Label Separation**:
   - `X` = `['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']`
   - `y` = `['label']`
2. **Target Label Encoding**:
   - Applied `sklearn.preprocessing.LabelEncoder` mapping 22 crop label strings to integer IDs `[0..21]`.
3. **Train-Test Partitioning**:
   - **Split Ratio**: 80% Training (1,760 samples) / 20% Testing (440 samples).
   - **Random Seed**: `random_state = 42` for strict reproducibility.
   - **Stratification**: `stratify=y` ensuring 20 test samples per crop class.

---

## Step 3 – Model Training & Benchmarking

Four classification models were trained and benchmarked using 5-Fold Stratified Cross-Validation:

| Model Name | Accuracy | Precision (Weighted) | Recall (Weighted) | F1 Score (Weighted) | 5-Fold Cross-Val Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Classifier** *(Selected)* | **99.55%** | **99.57%** | **99.55%** | **99.55%** | **99.32% (±0.43%)** |
| **XGBoost Classifier** | **99.32%** | **99.35%** | **99.32%** | **99.31%** | **98.86% (±0.65%)** |
| **Decision Tree Classifier** | **97.95%** | **98.06%** | **97.95%** | **97.94%** | **98.52% (±0.75%)** |
| **K-Nearest Neighbors (k=5)** | **97.73%** | **97.85%** | **97.73%** | **97.72%** | **97.73% (±0.48%)** |

> [!NOTE]  
> **Best Model Selection**: **Random Forest Classifier** achieved the highest overall test accuracy (**99.55%**) and F1-score (**99.55%**), demonstrating excellent generalization with low cross-validation variance.

---

## Step 4 – Feature Importance Ranking

The Random Forest model identified the relative contribution of each environmental and soil parameter to crop suitability predictions:

```
  Rainfall     :  ██████████████████████ (23.02%)
  Humidity     :  █████████████████████ (22.42%)
  Potassium (K):  ████████████████ (17.54%)
  Phosphorus (P): ██████████████ (15.08%)
  Nitrogen (N) :  ███████ (9.64%)
  Temperature  :  ██████ (7.24%)
  pH           :  ████ (5.06%)
```

* **Primary Drivers**: `rainfall` (23.02%) and `humidity` (22.42%) account for over **45%** of the decision boundary, as water availability heavily constrains crops like rice vs. pulses.
* **Secondary Drivers**: Soil nutrients (`K` at 17.54%, `P` at 15.08%, `N` at 9.64%) account for **42.26%** of model decisions.

---

## Step 5 – Classification Report (Best Model)

```
              precision    recall  f1-score   support

       apple       1.00      1.00      1.00        20
      banana       1.00      1.00      1.00        20
   blackgram       1.00      0.95      0.97        20
    chickpea       1.00      1.00      1.00        20
     coconut       1.00      1.00      1.00        20
      coffee       1.00      1.00      1.00        20
      cotton       1.00      1.00      1.00        20
      grapes       1.00      1.00      1.00        20
        jute       0.95      1.00      0.98        20
 kidneybeans       1.00      1.00      1.00        20
      lentil       1.00      1.00      1.00        20
       maize       0.95      1.00      0.98        20
       mango       1.00      1.00      1.00        20
   mothbeans       1.00      1.00      1.00        20
    mungbean       1.00      1.00      1.00        20
   muskmelon       1.00      1.00      1.00        20
      orange       1.00      1.00      1.00        20
      papaya       1.00      1.00      1.00        20
  pigeonpeas       1.00      1.00      1.00        20
 pomegranate       1.00      1.00      1.00        20
        rice       1.00      0.95      0.97        20
  watermelon       1.00      1.00      1.00        20

    accuracy                           1.00       440
   macro avg       1.00      1.00      1.00       440
weighted avg       1.00      1.00      1.00       440
```

---

## Step 6 – Generated Artifacts & Files

1. **Reusable Training Script**:
   - Location: [backend/training/train_crop_model.py](file:///c:/Users/durga/kisan_mitra/backend/training/train_crop_model.py)
   - Function: Reusable automated pipeline script. Retraining on updated datasets only requires running `python backend/training/train_crop_model.py`.

2. **Saved Model Binary**:
   - Location: [backend/models/crop_recommendation_model.pkl](file:///c:/Users/durga/kisan_mitra/backend/models/crop_recommendation_model.pkl)
   - Size: 3,492 KB
   - Format: `joblib` serialized `RandomForestClassifier`

3. **Saved Label Encoder Binary**:
   - Location: [backend/models/label_encoder.pkl](file:///c:/Users/durga/kisan_mitra/backend/models/label_encoder.pkl)
   - Size: 0.68 KB
   - Format: `joblib` serialized `LabelEncoder`

---

## Compliance Verification
- ✅ **Flutter UI**: 0 files modified.
- ✅ **Firebase Integration**: 0 files modified.
- ✅ **Backend Routes & Advisory Engine**: 0 existing files modified (`advisory_engine.py` untouched).
- ✅ **Standalone Execution**: Model trained, evaluated, and saved for future backend integration.
