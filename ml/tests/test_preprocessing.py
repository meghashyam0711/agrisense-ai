"""
Unit Tests for AgriSense-AI Agricultural Preprocessing Module.
Tests schema validation, missing value imputation, outlier handling,
feature engineering, and target leakage prevention.
"""

import unittest
import numpy as np
import pandas as pd

from ml.src.preprocessing import PaddyDataPreprocessor
from ml.src.dataset_schema import FEATURE_BOUNDS

class TestPaddyDataPreprocessor(unittest.TestCase):

    def setUp(self):
        self.preprocessor = PaddyDataPreprocessor(target_column="yield_tonnes_per_hectare")
        # Sample mini-dataset
        self.sample_data = pd.DataFrame({
            "district": ["Thanjavur", "Tiruvarur", "Madurai", "Thanjavur"],
            "season": ["Samba", "Kuruvai", "Navarai", "Samba"],
            "soil_type": ["Alluvial", "Clayey", "Red Loam", "Alluvial"],
            "rainfall_mm": [1150.0, 650.0, np.nan, 1150.0],  # Includes NaN and duplicate
            "temperature_c": [29.5, 33.0, 35.0, 29.5],
            "humidity_pct": [82.0, 75.0, 64.0, 82.0],
            "soil_ph": [6.8, 7.2, 14.5, 6.8],  # Includes outlier pH 14.5
            "soil_moisture_pct": [75.0, 80.0, 65.0, 75.0],
            "nitrogen_kg_ha": [135.0, 120.0, 110.0, 135.0],
            "phosphorus_kg_ha": [45.0, 40.0, 35.0, 45.0],
            "potassium_kg_ha": [42.0, 40.0, 38.0, 42.0],
            "previous_yield_tonnes_per_hectare": [4.5, 4.2, 3.8, 4.5],
            "yield_tonnes_per_hectare": [5.1, 4.6, 3.9, 5.1]
        })

    def test_schema_validation(self):
        validation = self.preprocessor.validate_schema(self.sample_data)
        self.assertTrue(validation["is_valid"])
        self.assertEqual(validation["duplicate_count"], 1)
        self.assertIn("rainfall_mm", validation["null_counts"])
        self.assertEqual(validation["null_counts"]["rainfall_mm"], 1)

    def test_clean_data_deduplication_and_imputation(self):
        cleaned = self.preprocessor.clean_data(self.sample_data, is_train=True)
        
        # Duplicates must be removed (4 rows -> 3 rows)
        self.assertEqual(len(cleaned), 3)
        
        # Missing rainfall must be imputed with median of non-null values (1150 + 650) / 2 = 900.0
        self.assertFalse(cleaned["rainfall_mm"].isnull().any())
        self.assertEqual(cleaned.loc[2, "rainfall_mm"], 900.0)
        
        # Outlier pH (14.5) must be replaced and imputed within bounds
        self.assertTrue(cleaned["soil_ph"].max() <= FEATURE_BOUNDS["soil_ph"]["max"])

    def test_feature_engineering(self):
        cleaned = self.preprocessor.clean_data(self.sample_data, is_train=True)
        engineered = self.preprocessor.engineer_features(cleaned)
        
        # Check derived columns
        self.assertIn("npk_total_kg_ha", engineered.columns)
        self.assertIn("n_p_ratio", engineered.columns)
        self.assertIn("n_k_ratio", engineered.columns)
        self.assertIn("rainfall_temp_ratio", engineered.columns)
        self.assertIn("ph_optimality_deviation", engineered.columns)
        
        # Check calculation correctness
        expected_npk = engineered.loc[0, "nitrogen_kg_ha"] + engineered.loc[0, "phosphorus_kg_ha"] + engineered.loc[0, "potassium_kg_ha"]
        self.assertAlmostEqual(engineered.loc[0, "npk_total_kg_ha"], expected_npk)

    def test_leakage_free_target_split(self):
        cleaned = self.preprocessor.clean_data(self.sample_data, is_train=True)
        X, y = self.preprocessor.split_features_and_target(cleaned)
        
        # Target must not be in feature matrix X
        self.assertNotIn("yield_tonnes_per_hectare", X.columns)
        self.assertEqual(len(y), len(X))
        self.assertEqual(y.name, "yield_tonnes_per_hectare")

    def test_categorical_encoding(self):
        cleaned = self.preprocessor.clean_data(self.sample_data, is_train=True)
        encoded = self.preprocessor.encode_categorical_features(cleaned, is_train=True)
        
        # Categorical columns must be replaced with one-hot encoded dummies
        for cat in self.preprocessor.CATEGORICAL_COLUMNS:
            self.assertNotIn(cat, encoded.columns)
            
        # Target must be preserved in encoded output
        self.assertIn("yield_tonnes_per_hectare", encoded.columns)

if __name__ == "__main__":
    unittest.main()
