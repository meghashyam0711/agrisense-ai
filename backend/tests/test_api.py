"""
AgriSense-AI: Automated FastAPI Endpoint Tests.
Tests root status, health checks, prediction inference, input validations,
error handling, model-info, and model-loading failure states.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend and project root are importable
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import app
from app.services.ml_service import ml_service

class TestAgriSenseAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize TestClient within lifespan context
        cls.client = TestClient(app)
        # Ensure model is loaded for standard tests
        ml_service.load_model()

        cls.valid_payload = {
            "district": "Thanjavur",
            "season": "Samba",
            "soil_type": "Alluvial",
            "rainfall_mm": 1150.0,
            "temperature_c": 29.5,
            "humidity_pct": 82.0,
            "soil_ph": 6.8,
            "soil_moisture_pct": 76.0,
            "nitrogen_kg_ha": 140.0,
            "phosphorus_kg_ha": 48.0,
            "potassium_kg_ha": 45.0,
            "previous_yield_tonnes_per_hectare": 4.5,
            "area_hectares": 2.5
        }

    def test_root_endpoint(self):
        """Tests GET / returns 200 and operational status."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "operational")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("AgriSense", data["name"])

    def test_health_endpoint(self):
        """Tests GET /health returns 200 and model readiness."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])
        self.assertIn("timestamp", data)

    def test_predict_endpoint_valid_payload(self):
        """Tests POST /predict with complete farm inputs."""
        response = self.client.post("/predict", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["crop"], "Paddy (Oryza sativa)")
        self.assertEqual(data["district"], "Thanjavur")
        self.assertEqual(data["season"], "Samba")

        # Yield checks
        yield_t = data["predicted_yield_tonnes_per_hectare"]
        self.assertGreaterEqual(yield_t, 2.0)
        self.assertLessEqual(yield_t, 7.5)

        # Conversions check
        self.assertAlmostEqual(data["predicted_yield_quintals_per_hectare"], round(yield_t * 10, 1), places=1)
        self.assertAlmostEqual(data["predicted_yield_kg_per_hectare"], round(yield_t * 1000, 0), delta=10)

        # Plot total calculations (2.5 ha)
        expected_total_tonnes = round(yield_t * 2.5, 2)
        self.assertAlmostEqual(data["total_estimated_production_tonnes"], expected_total_tonnes, places=2)

        # Confidence interval check
        conf = data["confidence_interval_90"]
        self.assertLess(conf["lower_tonnes_ha"], conf["upper_tonnes_ha"])

    def test_predict_endpoint_legacy_aliases(self):
        """Tests POST /predict supports field aliases (nitrogen, ph, moisture)."""
        aliased_payload = {
            "district": "Tiruvarur",
            "season": "Kuruvai",
            "soil_type": "Clayey",
            "rainfall_mm": 650.0,
            "temperature_c": 33.0,
            "humidity_pct": 72.0,
            "ph": 7.0,                 # Alias for soil_ph
            "moisture": 75.0,           # Alias for soil_moisture_pct
            "nitrogen": 120.0,          # Alias for nitrogen_kg_ha
            "phosphorus": 40.0,        # Alias for phosphorus_kg_ha
            "potassium": 40.0,         # Alias for potassium_kg_ha
            "previous_yield": 4.2       # Alias for previous_yield_tonnes_per_hectare
        }
        response = self.client.post("/predict", json=aliased_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["predicted_yield_tonnes_per_hectare"], 0.0)

    def test_predict_endpoint_missing_fields(self):
        """Tests POST /predict with missing required fields returns 422."""
        incomplete_payload = self.valid_payload.copy()
        del incomplete_payload["rainfall_mm"]
        response = self.client.post("/predict", json=incomplete_payload)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Validation Error")

    def test_predict_endpoint_invalid_range(self):
        """Tests POST /predict with physically impossible inputs returns 422."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["soil_ph"] = 14.5  # Max allowed is 9.5
        response = self.client.post("/predict", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_predict_endpoint_invalid_district(self):
        """Tests POST /predict with non-Tamil Nadu district returns 422."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["district"] = "London"
        response = self.client.post("/predict", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_model_info_endpoint(self):
        """Tests GET /model-info returns complete metadata."""
        response = self.client.get("/model-info")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("Random Forest", data["model_name"])
        self.assertEqual(data["target_unit"], "tonnes_per_hectare")
        self.assertGreater(data["features_count"], 15)
        self.assertIn("evaluation_metrics", data)
        self.assertIn("disclaimer", data)
        self.assertIn("top_10_feature_importances", data)

    def test_model_unloaded_failure_handling(self):
        """Tests 503 error handling when model is deliberately marked unloaded."""
        # Temporarily simulate unloaded model
        original_loaded = ml_service.is_loaded
        original_predictor = ml_service.predictor
        try:
            ml_service.is_loaded = False
            ml_service.predictor = None

            # Health check should report degraded
            health_res = self.client.get("/health")
            self.assertEqual(health_res.status_code, 200)
            self.assertEqual(health_res.json()["status"], "degraded")
            self.assertFalse(health_res.json()["model_loaded"])

            # Predict should return 503 Service Unavailable
            pred_res = self.client.post("/predict", json=self.valid_payload)
            self.assertEqual(pred_res.status_code, 503)

            # Model info should return 503 Service Unavailable
            info_res = self.client.get("/model-info")
            self.assertEqual(info_res.status_code, 503)
        finally:
            # Restore model state
            ml_service.is_loaded = original_loaded
            ml_service.predictor = original_predictor

    def test_cors_headers(self):
        """Tests CORS headers for allowed frontend origin."""
        headers = {"Origin": "http://localhost:3000"}
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3000")

if __name__ == "__main__":
    unittest.main()
