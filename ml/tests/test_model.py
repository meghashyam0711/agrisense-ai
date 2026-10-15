"""
Unit & Integration Tests for AgriSense-AI Machine Learning Model & Inference Engine.
Tests model artifact loading, input validation boundaries, prediction outputs,
confidence interval calculation, and batch predictions.
"""

import unittest
import os
import pandas as pd
from ml.src.inference import PaddyYieldPredictor, load_paddy_yield_predictor

class TestPaddyYieldPredictor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_path = "ml/saved_models/rf_paddy_yield_model.joblib"
        cls.metadata_path = "ml/saved_models/feature_metadata.json"
        cls.predictor = load_paddy_yield_predictor(
            model_path=cls.model_path,
            metadata_path=cls.metadata_path
        )
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
            "previous_yield_tonnes_per_hectare": 4.5
        }

    def test_model_artifact_loading(self):
        """Verifies that model binary, preprocessor, and metadata load cleanly."""
        self.assertIsNotNone(self.predictor.model)
        self.assertIsNotNone(self.predictor.preprocessor)
        self.assertIsInstance(self.predictor.feature_columns, list)
        self.assertGreater(len(self.predictor.feature_columns), 15)
        self.assertEqual(self.predictor.metadata.get("target_variable"), "yield_tonnes_per_hectare")

    def test_valid_prediction_structure_and_bounds(self):
        """Tests that prediction returns correct units, valid range, and confidence interval."""
        res = self.predictor.predict(self.valid_payload)
        
        # Check keys
        self.assertIn("predicted_yield_tonnes_per_hectare", res)
        self.assertIn("predicted_yield_quintals_per_hectare", res)
        self.assertIn("predicted_yield_kg_per_hectare", res)
        self.assertIn("confidence_interval_90", res)
        
        # Check agronomic range (realistic paddy yield in TN is between 2.0 and 7.5 tonnes/ha)
        y_tonnes = res["predicted_yield_tonnes_per_hectare"]
        self.assertGreaterEqual(y_tonnes, 2.0)
        self.assertLessEqual(y_tonnes, 7.5)
        
        # Check unit consistency: 1 tonne = 10 quintals = 1,000 kg
        self.assertAlmostEqual(res["predicted_yield_quintals_per_hectare"], round(y_tonnes * 10, 1), places=1)
        self.assertAlmostEqual(res["predicted_yield_kg_per_hectare"], round(y_tonnes * 1000, 0), delta=10)

        # Check confidence bounds
        conf = res["confidence_interval_90"]
        self.assertLess(conf["lower_tonnes_ha"], conf["upper_tonnes_ha"])
        self.assertLessEqual(conf["lower_tonnes_ha"], y_tonnes)
        self.assertGreaterEqual(conf["upper_tonnes_ha"], y_tonnes)

    def test_missing_input_fields_validation(self):
        """Verifies that omitting a required field raises ValueError."""
        incomplete_payload = self.valid_payload.copy()
        del incomplete_payload["nitrogen_kg_ha"]
        
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict(incomplete_payload)
        self.assertIn("nitrogen_kg_ha", str(ctx.exception))

    def test_out_of_bounds_input_validation(self):
        """Verifies that physically impossible inputs are rejected."""
        # 1. Negative rainfall
        corrupt_rain = self.valid_payload.copy()
        corrupt_rain["rainfall_mm"] = -50.0
        with self.assertRaises(ValueError):
            self.predictor.predict(corrupt_rain)

        # 2. Impossible soil pH (> 14)
        corrupt_ph = self.valid_payload.copy()
        corrupt_ph["soil_ph"] = 15.0
        with self.assertRaises(ValueError):
            self.predictor.predict(corrupt_ph)

        # 3. Excessive N (> 300 kg/ha)
        corrupt_n = self.valid_payload.copy()
        corrupt_n["nitrogen_kg_ha"] = 650.0
        with self.assertRaises(ValueError):
            self.predictor.predict(corrupt_n)

    def test_batch_prediction(self):
        """Tests batch prediction capability on multiple farm plots."""
        batch_df = pd.DataFrame([
            self.valid_payload,
            {**self.valid_payload, "district": "Madurai", "season": "Kuruvai", "rainfall_mm": 600.0}
        ])
        results_df = self.predictor.predict_batch(batch_df)
        self.assertIn("predicted_yield_tonnes_per_hectare", results_df.columns)
        self.assertEqual(len(results_df), 2)
        for val in results_df["predicted_yield_tonnes_per_hectare"]:
            self.assertGreaterEqual(val, 2.0)
            self.assertLessEqual(val, 7.5)

    def test_metadata_evaluation_metrics(self):
        """Verifies that saved metadata contains valid evaluation metrics beating baseline."""
        metrics = self.predictor.metadata.get("evaluation_metrics", {})
        rf_metrics = metrics.get("random_forest", {})
        base_metrics = metrics.get("baseline_mean", {})

        # RF R² should be substantially higher than 0.80 and baseline R²
        self.assertGreater(rf_metrics.get("test_r2", 0), 0.80)
        self.assertGreater(rf_metrics.get("test_r2", 0), base_metrics.get("test_r2", 0))
        # RF MAE should be substantially lower than baseline MAE
        self.assertLess(rf_metrics.get("test_mae", 1), base_metrics.get("test_mae", 1))

if __name__ == "__main__":
    unittest.main()
