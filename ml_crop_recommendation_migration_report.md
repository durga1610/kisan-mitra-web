# Kisan Mitra: ML Crop Recommendation Migration Report

This report documents the successful replacement of the rule-based crop recommendation engine in Kisan Mitra with a trained **Random Forest Machine Learning Model** (`crop_recommendation_model.pkl` and `label_encoder.pkl`).

---

## 1. Code Changes Summary

### Code Removed
- **Hardcoded Heuristic Rules**: Removed `recommend_crops_rule_based()` call inside `predict_crop_recommendations()` in [backend/advisory_engine.py](file:///c:/Users/durga/kisan_mitra/backend/advisory_engine.py#L2670).
- **Pickle Bypass Flag**: Removed `bypass_ml = True` override.
- **Un-sanitized Pickle Preprocessors**: Removed legacy `crop_recommendation_preprocessors.pkl` requirement.

### Code Replaced
- **Prediction Engine**: `predict_crop_recommendations(features)` inside `backend/advisory_engine.py` was replaced with **Random Forest ML Inference** executing `predict_proba()` against a 7-feature input vector (`N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`).

### Code Remaining Unchanged
- **Flutter UI Screens**: Zero changes to [crop_recommendation_screen.dart](file:///c:/Users/durga/kisan_mitra/lib/features/crop_recommendation/presentation/screens/crop_recommendation_screen.dart).
- **Flutter Repositories**: Zero changes to [recommendation_repository.dart](file:///c:/Users/durga/kisan_mitra/lib/core/repositories/recommendation_repository.dart).
- **Firebase Services & Firestore Schemas**: Zero database structure modifications.
- **API Endpoints**: `/api/v1/recommendations` and `/api/v1/crop-recommendation/predict` routes, rate limiters, and URL parameters remain 100% identical.
- **Other AI Modules**: AI Assistant, AI Advisory, Fertilizer Engine, Weather, and Market price services remain untouched.

---

## 2. Model Integration Architecture

### Singleton / Lazy Loading Pattern
Model artifacts are loaded **only once** into memory during backend initialization and cached across requests:

```python
_crop_recommendation_model = joblib.load("models/crop_recommendation_model.pkl")
_crop_label_encoder = joblib.load("models/label_encoder.pkl")
```
* **Performance Gain**: Inference executes in **< 2 milliseconds** per request without disk I/O latency.

### Feature Vector Format
Features are extracted in the exact order expected by the trained Random Forest model:
```python
input_df = pd.DataFrame(
    [[N, P, K, temperature, humidity, ph, rainfall]],
    columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
)
```

### Prediction Logging
Every recommendation request writes structured inference telemetry to logs:
```
[Prediction ML] Input Features: N=50.0, P=55.0, K=50.0, temp=24.5°C, hum=82.0%, ph=7.50, rain=150.0mm | Predicted Crop: 'Cotton' | Confidence: 99.55% | Inference Time: 1.42ms | Model Version: RF_Crop_Rec_v1.0
```

---

## 3. End-to-End Prediction Workflow

```
1. Flutter Client (CropRecommendationScreen)
   └── Farmer selects farm plot & opens screen.
2. WeatherService Query
   └── Fetches live temperature, humidity, and rainfall for farm GPS location.
3. RecommendationRepository Dispatch
   └── Sends HTTP POST request to /api/v1/recommendations with farm & weather context.
4. FastAPI Endpoint Layer (main.py)
   └── Receives payload and calls extract_prediction_features(farm, weather).
5. Soil Mapping Layer (advisory_engine.py)
   └── get_soil_default_values(soilType) maps farm soil to baseline [N, P, K, pH].
6. ML Inference Engine (advisory_engine.py)
   └── predict_crop_recommendations() executes Random Forest predict_proba().
7. Result Formatting & Backward Compatibility
   └── Formats top predictions into JSON schema (cropName, suitabilityScore, expectedProfit, matchReason, source="ML_MODEL").
8. Flutter UI Render
   └── Renders interactive crop recommendation cards with confidence scores.
```

---

## 4. Verification & Testing Summary

* **Unit Tests**: Executed `backend/test_soil_mapping.py` — **8/8 Passed**.
* **Integration Tests**: Executed `backend/test_ml_recommendation_integration.py` — **4/4 Passed**.
* **API Schema Contract**: Verified `RecommendationModel` compatibility in Flutter.
