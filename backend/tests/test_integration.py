"""
AgriSense-AI: End-to-End API Integration & User Workflow Tests (Phase 9).
Verifies the complete farmer workflow:
1. Health check
2. Live weather query
3. Farm profile creation
4. Machine Learning yield prediction
5. TNAU agronomic recommendation engine
6. SQLite prediction history persistence
7. Ground-truth harvest outcome recording with variance
8. Bilingual localization retrieval
9. Invalid inputs & failure handling
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure backend and project root are importable
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import app
from app.db.init_db import init_db
from app.services.ml_service import ml_service


class TestEndToEndFarmerWorkflow(unittest.TestCase):
    """End-to-end integration test exercising all connected API features."""

    @classmethod
    def setUpClass(cls):
        init_db()
        ml_service.load_model()
        cls.client = TestClient(app)

    def test_step1_health_check(self):
        """Verifies backend and ML model readiness."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])

    def test_step2_weather_query(self):
        """Verifies weather retrieval for Cauvery Delta district."""
        res = self.client.get("/api/v1/weather/current?district=Thanjavur")
        self.assertIn(res.status_code, [200, 502, 504])  # 200 if online, 502/504 handled gracefully
        if res.status_code == 200:
            data = res.json()
            self.assertEqual(data["location"], "Thanjavur")
            self.assertIsInstance(data["temperature_c"], float)

    def test_step3_farm_profile_creation(self):
        """Verifies farmer holding registration."""
        farm_payload = {
            "farmer_name": "S. Ramasamy",
            "contact_phone": "+91 94421 88990",
            "district": "Thanjavur",
            "taluk": "Orathanadu",
            "village": "Pudukkottai",
            "total_area_hectares": 3.0,
            "fields": [
                {
                    "field_name": "Main Delta Plot",
                    "area_hectares": 3.0,
                    "soil_type": "Alluvial",
                    "soil_ph": 6.8,
                    "irrigation_source": "Canal"
                }
            ]
        }
        res = self.client.post("/api/v1/farms/", json=farm_payload)
        self.assertEqual(res.status_code, 201)
        farm_data = res.json()
        self.assertIsNotNone(farm_data["id"])
        self.assertEqual(farm_data["farmer_name"], "S. Ramasamy")


    def test_step4_ml_yield_prediction(self):
        """Verifies Random Forest model inference."""
        pred_payload = {
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
            "area_hectares": 3.0
        }
        # Test v1 endpoint
        res = self.client.post("/api/v1/crop/predict", json=pred_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["predicted_yield_tonnes_per_hectare"], 0.0)
        self.assertGreater(data["predicted_yield_quintals_per_hectare"], 0.0)
        self.assertIsNotNone(data["confidence_interval_90"])

        # Test root endpoint
        res_root = self.client.post("/predict", json=pred_payload)
        self.assertEqual(res_root.status_code, 200)

    def test_step5_recommendations_engine(self):
        """Verifies TNAU smart recommendation engine."""
        rec_payload = {
            "district": "Thanjavur",
            "season": "Samba",
            "growth_stage": "vegetative_tillering",
            "soil_type": "Alluvial",
            "soil_ph": 6.8,
            "soil_moisture_pct": 74.0,
            "nitrogen_kg_ha": 135.0,
            "phosphorus_kg_ha": 45.0,
            "potassium_kg_ha": 42.0,
            "temperature_c": 29.5,
            "humidity_pct": 82.0,
            "forecast_rain_expected_mm": 5.0,
            "forecast_rain_prob_pct": 20
        }
        res = self.client.post("/recommendations", json=rec_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["rule_type"], "agronomic_expert_system")
        self.assertIsInstance(data["irrigation_advisory"], list)
        self.assertIsInstance(data["fertilizer_advisory"], list)
        self.assertIsInstance(data["soil_health_advisory"], list)
        self.assertIsInstance(data["pest_monitoring_alerts"], list)

    def test_step6_persist_and_query_history(self):
        """Verifies saving prediction to SQLite and querying logs."""
        save_payload = {
            "district": "Thanjavur",
            "season": "Samba",
            "soil_type": "Alluvial",
            "area_hectares": 2.5,
            "rainfall_mm": 1100.0,
            "temperature_c": 30.0,
            "humidity_pct": 80.0,
            "soil_ph": 6.8,
            "soil_moisture_pct": 74.0,
            "nitrogen_kg_ha": 135.0,
            "phosphorus_kg_ha": 45.0,
            "potassium_kg_ha": 42.0,
            "previous_yield_tonnes_per_hectare": 4.2,
            "predicted_yield_tonnes_per_hectare": 4.60,
            "predicted_yield_quintals_per_hectare": 46.0,
            "predicted_yield_kg_per_hectare": 4600.0,
            "model_name": "RandomForestRegressor",
            "model_version": "1.0.0"
        }
        res_save = self.client.post("/api/v1/history/predictions", json=save_payload)
        self.assertEqual(res_save.status_code, 201)
        pred_id = res_save.json()["id"]

        # Query history
        res_logs = self.client.get(f"/api/v1/history/logs?district=Thanjavur")
        self.assertEqual(res_logs.status_code, 200)
        logs = res_logs.json()
        self.assertTrue(any(item["id"] == pred_id for item in logs))

        # Record actual harvest outcome and check variance
        harvest_payload = {
            "prediction_id": pred_id,
            "harvest_date": "2026-10-15",
            "actual_yield_tonnes_per_hectare": 4.85,
            "notes": "Harvested successfully under favorable weather."
        }
        res_h = self.client.post("/api/v1/history/harvest", json=harvest_payload)
        self.assertEqual(res_h.status_code, 201)
        h_data = res_h.json()
        self.assertEqual(h_data["actual_yield_quintals_per_hectare"], 48.5)
        self.assertAlmostEqual(h_data["variance_tonnes"], 0.25, places=2)

    def test_step7_bilingual_localization(self):
        """Verifies localization endpoint delivers complete Tamil and English dictionaries."""
        res_en = self.client.get("/api/v1/i18n/en")
        self.assertEqual(res_en.status_code, 200)
        self.assertEqual(res_en.json()["brand_title"], "AgriSense-AI")

        res_ta = self.client.get("/api/v1/i18n/ta")
        self.assertEqual(res_ta.status_code, 200)
        self.assertEqual(res_ta.json()["brand_title"], "அக்ரிசென்ஸ்-AI")

    def test_step8_failure_handling_and_validation(self):
        """Verifies graceful handling of invalid inputs and edge cases."""
        # Invalid district
        bad_pred = {
            "district": "UnknownCity",
            "season": "Samba",
            "soil_type": "Alluvial",
            "rainfall_mm": 1000.0,
            "temperature_c": 30.0,
            "humidity_pct": 80.0,
            "soil_ph": 6.8,
            "soil_moisture_pct": 70.0,
            "nitrogen_kg_ha": 120.0,
            "phosphorus_kg_ha": 40.0,
            "potassium_kg_ha": 40.0,
            "previous_yield_tonnes_per_hectare": 4.0
        }
        res = self.client.post("/api/v1/crop/predict", json=bad_pred)
        self.assertEqual(res.status_code, 422)

        # Invalid pH
        bad_ph = dict(bad_pred)
        bad_ph["district"] = "Thanjavur"
        bad_ph["soil_ph"] = 15.0  # Out of range
        res_ph = self.client.post("/api/v1/crop/predict", json=bad_ph)
        self.assertEqual(res_ph.status_code, 422)


if __name__ == "__main__":
    unittest.main()
