"""
AgriSense-AI: Reusable Model Inference & Yield Prediction Module.
Provides robust input validation, model loading, confidence estimation,
and multi-unit yield outputs (tonnes/ha, quintals/ha, kg/ha).
"""

import os
import json
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib

from .dataset_schema import FEATURE_BOUNDS, TNAU_RECOMMENDED_NPK

class PaddyYieldPredictor:
    """
    Production inference engine for Tamil Nadu Paddy Yield Prediction.
    Loads trained Random Forest model and preprocessor to generate validated predictions.
    """

    def __init__(
        self,
        model_path: str = "ml/saved_models/rf_paddy_yield_model.joblib",
        metadata_path: str = "ml/saved_models/feature_metadata.json"
    ):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.preprocessor_path = model_path.replace("rf_paddy_yield_model.joblib", "preprocessor.joblib")
        
        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.feature_columns: List[str] = []
        self.rmse: float = 0.28  # Default residual fallback if metadata missing

        self.load()

    def load(self) -> None:
        """Loads model binary, preprocessor, and metadata from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at: {self.model_path}")
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(f"Preprocessor artifact not found at: {self.preprocessor_path}")
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file not found at: {self.metadata_path}")

        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.feature_columns = self.metadata.get("feature_columns", [])
        rf_metrics = self.metadata.get("evaluation_metrics", {}).get("random_forest", {})
        self.rmse = rf_metrics.get("test_rmse", 0.28)

    def validate_inputs(self, input_data: Dict[str, Any]) -> None:
        """
        Validates raw farmer inputs against physical and agronomic boundaries.
        Raises ValueError with clear guidance if inputs are invalid.
        """
        required_keys = [
            "district", "season", "soil_type", "rainfall_mm",
            "temperature_c", "humidity_pct", "soil_ph",
            "soil_moisture_pct", "nitrogen_kg_ha", "phosphorus_kg_ha",
            "potassium_kg_ha", "previous_yield_tonnes_per_hectare"
        ]

        missing = [k for k in required_keys if k not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        # Check bounds
        for key, bounds in FEATURE_BOUNDS.items():
            if key in input_data and input_data[key] is not None:
                val = float(input_data[key])
                if val < bounds["min"] or val > bounds["max"]:
                    raise ValueError(
                        f"Input parameter '{key}' value {val} is outside valid agronomic bounds "
                        f"[{bounds['min']} to {bounds['max']} {bounds['unit']}]."
                    )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates comprehensive prediction metrics for a farmer's plot.
        
        Args:
            input_data: Dictionary containing agronomic, soil, and weather values.
            
        Returns:
            Dict containing yield in tonnes/ha, quintals/ha, kg/ha, 90% confidence bounds,
            and comparison against TNAU baselines.
        """
        # 1. Validate inputs
        self.validate_inputs(input_data)

        # 2. Preprocess payload
        df_input = pd.DataFrame([input_data])
        processed = self.preprocessor.process_pipeline(df_input, is_train=False)

        # 3. Align features with model
        X_aligned = processed.reindex(columns=self.feature_columns, fill_value=0.0)

        # 4. Predict yield using Random Forest
        # Predict individual tree predictions to compute exact predictive standard deviation
        tree_predictions = np.array([tree.predict(X_aligned.values)[0] for tree in self.model.estimators_])
        mean_pred = float(np.mean(tree_predictions))
        tree_std = float(np.std(tree_predictions))

        # 90% Confidence Interval (Z=1.645) combining tree variance and model RMSE
        pred_uncertainty = max(tree_std * 1.645, self.rmse * 1.28)
        lower_bound = max(1.0, round(mean_pred - pred_uncertainty, 2))
        upper_bound = round(mean_pred + pred_uncertainty, 2)

        # Unit conversions
        yield_tonnes_ha = round(mean_pred, 2)
        yield_quintals_ha = round(mean_pred * 10.0, 1)
        yield_kg_ha = round(mean_pred * 1000.0, 0)

        # Comparison against TNAU season baseline
        season = input_data.get("season", "Samba")
        baseline_info = TNAU_RECOMMENDED_NPK.get(season, {"typical_yield_tonnes": 5.0})
        typical_yield = baseline_info.get("typical_yield_tonnes", 5.0)
        potential_pct = min(round((yield_tonnes_ha / typical_yield) * 100, 1), 120.0)

        return {
            "predicted_yield_tonnes_per_hectare": yield_tonnes_ha,
            "predicted_yield_quintals_per_hectare": yield_quintals_ha,
            "predicted_yield_kg_per_hectare": yield_kg_ha,
            "confidence_interval_90": {
                "lower_tonnes_ha": lower_bound,
                "upper_tonnes_ha": upper_bound,
                "lower_quintals_ha": round(lower_bound * 10, 1),
                "upper_quintals_ha": round(upper_bound * 10, 1),
            },
            "district": input_data.get("district"),
            "season": season,
            "tnau_potential_realization_pct": potential_pct,
            "model_version": self.metadata.get("version", "1.0.0"),
            "disclaimer": self.metadata.get("disclaimer", "Demonstration model only.")
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates predictions for a DataFrame batch.
        """
        results = []
        for _, row in df.iterrows():
            pred = self.predict(row.to_dict())
            results.append(pred["predicted_yield_tonnes_per_hectare"])
        output_df = df.copy()
        output_df["predicted_yield_tonnes_per_hectare"] = results
        return output_df


def load_paddy_yield_predictor(
    model_path: str = "ml/saved_models/rf_paddy_yield_model.joblib",
    metadata_path: str = "ml/saved_models/feature_metadata.json"
) -> PaddyYieldPredictor:
    """Convenience factory function to load the trained predictor."""
    return PaddyYieldPredictor(model_path=model_path, metadata_path=metadata_path)
