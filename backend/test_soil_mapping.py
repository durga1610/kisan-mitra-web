import unittest
from advisory_engine import get_soil_default_values, extract_prediction_features


class TestSoilTypeMapping(unittest.TestCase):

    def test_black_soil_mapping(self):
        result = get_soil_default_values("Black Soil")
        self.assertEqual(result["N"], 50)
        self.assertEqual(result["P"], 55)
        self.assertEqual(result["K"], 50)
        self.assertEqual(result["ph"], 7.5)

    def test_red_soil_mapping(self):
        result = get_soil_default_values("Red Soil")
        self.assertEqual(result["N"], 35)
        self.assertEqual(result["P"], 30)
        self.assertEqual(result["K"], 35)
        self.assertEqual(result["ph"], 5.8)

    def test_alluvial_soil_mapping(self):
        result = get_soil_default_values("Alluvial Soil")
        self.assertEqual(result["N"], 80)
        self.assertEqual(result["P"], 50)
        self.assertEqual(result["K"], 45)
        self.assertEqual(result["ph"], 6.8)

    def test_clay_soil_mapping(self):
        result = get_soil_default_values("Clay Soil")
        self.assertEqual(result["N"], 60)
        self.assertEqual(result["P"], 45)
        self.assertEqual(result["K"], 55)
        self.assertEqual(result["ph"], 7.2)

    def test_loamy_soil_mapping(self):
        result = get_soil_default_values("Loamy Soil")
        self.assertEqual(result["N"], 70)
        self.assertEqual(result["P"], 45)
        self.assertEqual(result["K"], 40)
        self.assertEqual(result["ph"], 6.5)

    def test_sandy_soil_mapping(self):
        result = get_soil_default_values("Sandy Soil")
        self.assertEqual(result["N"], 25)
        self.assertEqual(result["P"], 20)
        self.assertEqual(result["K"], 20)
        self.assertEqual(result["ph"], 6.0)

    def test_unknown_soil_mapping_defaults(self):
        result = get_soil_default_values("Marshy Volcanic Soil")
        self.assertEqual(result["N"], 50)
        self.assertEqual(result["P"], 40)
        self.assertEqual(result["K"], 40)
        self.assertEqual(result["ph"], 6.5)

    def test_extract_prediction_features_seven_inputs(self):
        farm_ctx = {"soilType": "Black Soil", "landArea": 4.5}
        weather_ctx = {"temperature": 28.5, "humidity": 75.0, "season": "Kharif"}
        
        features = extract_prediction_features(farm_ctx, weather_ctx)
        
        # Verify all 7 ML features exist
        required_features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        for feat in required_features:
            self.assertIn(feat, features, f"Missing feature: {feat}")
            
        self.assertEqual(features["N"], 50)
        self.assertEqual(features["P"], 55)
        self.assertEqual(features["K"], 50)
        self.assertEqual(features["ph"], 7.5)
        self.assertEqual(features["temperature"], 28.5)


if __name__ == "__main__":
    unittest.main()
