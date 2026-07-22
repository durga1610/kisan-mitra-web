import unittest
import os
from advisory_engine import (
    _load_crop_recommendation_model,
    extract_prediction_features,
    predict_crop_recommendations,
)


class TestMLRecommendationIntegration(unittest.TestCase):

    def test_01_model_and_encoder_loading(self):
        model, encoder = _load_crop_recommendation_model()
        self.assertIsNotNone(model, "Random Forest model failed to load")
        self.assertIsNotNone(encoder, "LabelEncoder failed to load")
        self.assertEqual(len(encoder.classes_), 22, "LabelEncoder should contain 22 crop classes")

    def test_02_feature_extraction_and_ml_prediction(self):
        farm_ctx = {
            "id": "farm_test_123",
            "name": "Test Rice Plot",
            "soilType": "Black Soil",
            "waterAvailability": "High",
            "landArea": 5.0,
        }
        weather_ctx = {
            "temperature": 24.5,
            "humidity": 82.0,
            "season": "Kharif",
        }

        # 1. Feature Extraction
        features = extract_prediction_features(farm_ctx, weather_ctx)
        self.assertEqual(features["N"], 50)
        self.assertEqual(features["P"], 55)
        self.assertEqual(features["K"], 50)
        self.assertEqual(features["ph"], 7.5)
        self.assertEqual(features["temperature"], 24.5)

        # 2. ML Model Prediction Execution
        recommendations = predict_crop_recommendations(features)
        self.assertTrue(len(recommendations) > 0, "ML model should return top recommendations")
        self.assertLessEqual(len(recommendations), 4, "Should return top 4 recommendations")

        top_rec = recommendations[0]

        # 3. JSON Response Schema Compatibility Verification
        required_keys = [
            "cropName",
            "crop",
            "suitabilityScore",
            "score",
            "marketDemand",
            "demandScore",
            "expectedProfit",
            "growthPeriod",
            "matchReason",
            "source",
        ]
        for key in required_keys:
            self.assertIn(key, top_rec, f"Missing key '{key}' in ML recommendation output")

        self.assertEqual(top_rec["source"], "ML_MODEL")
        self.assertIsInstance(top_rec["suitabilityScore"], float)
        self.assertGreaterEqual(top_rec["suitabilityScore"], 0.0)
        self.assertLessEqual(top_rec["suitabilityScore"], 1.0)
        self.assertIsInstance(top_rec["matchReason"], str)

    def test_03_rice_optimal_conditions_prediction(self):
        # Rice optimal: High rainfall (~200mm), high humidity (~80%), high N (~90)
        features = {
            "N": 90,
            "P": 42,
            "K": 43,
            "temperature": 22.0,
            "humidity": 82.0,
            "ph": 6.5,
            "rainfall": 200.0,
            "soil_type": "Alluvial",
        }

        recs = predict_crop_recommendations(features)
        self.assertTrue(len(recs) > 0)
        top_crop = recs[0]["cropName"].lower()
        self.assertEqual(top_crop, "rice", f"Expected 'Rice' as top prediction for rice climate features, got '{top_crop}'")

    def test_04_cotton_optimal_conditions_prediction(self):
        # Cotton optimal: N=120, P=40, K=20, temp=24°C, humidity=80%, rainfall=80mm
        features = {
            "N": 120,
            "P": 40,
            "K": 20,
            "temperature": 24.0,
            "humidity": 80.0,
            "ph": 6.9,
            "rainfall": 80.0,
            "soil_type": "Black Soil",
        }

        recs = predict_crop_recommendations(features)
        self.assertTrue(len(recs) > 0)
        top_crop = recs[0]["cropName"].lower()
        self.assertEqual(top_crop, "cotton", f"Expected 'Cotton' as top prediction, got '{top_crop}'")


if __name__ == "__main__":
    unittest.main()
