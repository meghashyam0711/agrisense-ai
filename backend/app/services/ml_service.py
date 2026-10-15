"""
AgriSense-AI: Machine Learning Service Layer.
Manages model lifecycle, loads artifacts once, and provides thread-safe inference.
"""

import logging
from typing import Dict, Any, Optional
from ..core.config import settings
from ..schemas.prediction import PredictionRequest, PredictionResponse, ConfidenceInterval
from ..schemas.model_info import ModelInfoResponse

logger = logging.getLogger("agrisense.ml_service")

class PaddyMLService:
    """
    Singleton-style ML service to load and execute Scikit-learn Random Forest model.
    """

    def __init__(self):
        self.predictor = None
        self.is_loaded = False
        self.load_error: Optional[str] = None

    def load_model(self) -> None:
        """
        Loads the saved Random Forest model, preprocessor, and metadata from disk.
        Reports failures clearly without crashing the service.
        """
        try:
            from ml.src.inference import load_paddy_yield_predictor
            
            logger.info(f"Loading ML model from: {settings.MODEL_PATH}")
            self.predictor = load_paddy_yield_predictor(
                model_path=settings.MODEL_PATH,
                metadata_path=settings.FEATURE_COLUMNS_PATH
            )
            self.is_loaded = True
            self.load_error = None
            logger.info("ML model and preprocessor loaded successfully.")
        except Exception as e:
            self.predictor = None
            self.is_loaded = False
            self.load_error = f"Failed to load model artifacts: {str(e)}"
            logger.error(self.load_error)

    def is_healthy(self) -> bool:
        """Checks if the model is ready for inference."""
        return self.is_loaded and self.predictor is not None and self.predictor.model is not None

    def get_model_info(self) -> ModelInfoResponse:
        """
        Returns model metadata, evaluation metrics, and disclaimer.
        Sanitizes internal paths.
        """
        if not self.is_healthy():
            raise RuntimeError(f"Model service is not healthy. Error: {self.load_error}")

        meta = self.predictor.metadata
        return ModelInfoResponse(
            model_name=meta.get("model_name", "Random Forest Regressor"),
            version=meta.get("version", "1.0.0"),
            target_variable=meta.get("target_variable", "yield_tonnes_per_hectare"),
            target_unit=meta.get("target_unit", "tonnes_per_hectare"),
            created_at=meta.get("created_at", "N/A"),
            features_count=len(meta.get("feature_columns", [])),
            feature_columns=meta.get("feature_columns", []),
            top_10_feature_importances=meta.get("top_10_feature_importances", {}),
            evaluation_metrics=meta.get("evaluation_metrics", {}),
            disclaimer=meta.get("disclaimer", "Demonstration model only.")
        )

    def predict_yield(self, request: PredictionRequest) -> PredictionResponse:
        """
        Executes prediction on validated farmer payload.
        """
        if not self.is_healthy():
            raise RuntimeError(f"Prediction model is unavailable: {self.load_error}")

        payload = {
            "district": request.district,
            "season": request.season,
            "soil_type": request.soil_type,
            "rainfall_mm": request.rainfall_mm,
            "temperature_c": request.temperature_c,
            "humidity_pct": request.humidity_pct,
            "soil_ph": request.soil_ph,
            "soil_moisture_pct": request.soil_moisture_pct,
            "nitrogen_kg_ha": request.nitrogen_kg_ha,
            "phosphorus_kg_ha": request.phosphorus_kg_ha,
            "potassium_kg_ha": request.potassium_kg_ha,
            "previous_yield_tonnes_per_hectare": request.previous_yield_tonnes_per_hectare
        }

        # Run inference through PaddyYieldPredictor
        raw_res = self.predictor.predict(payload)

        # Plot total calculations
        area = request.area_hectares or 1.0
        total_tonnes = round(raw_res["predicted_yield_tonnes_per_hectare"] * area, 2)
        total_quintals = round(raw_res["predicted_yield_quintals_per_hectare"] * area, 1)

        conf = raw_res["confidence_interval_90"]
        conf_interval = ConfidenceInterval(
            lower_tonnes_ha=conf["lower_tonnes_ha"],
            upper_tonnes_ha=conf["upper_tonnes_ha"],
            lower_quintals_ha=conf["lower_quintals_ha"],
            upper_quintals_ha=conf["upper_quintals_ha"]
        )

        return PredictionResponse(
            success=True,
            crop="Paddy (Oryza sativa)",
            district=request.district,
            season=request.season,
            soil_type=request.soil_type,
            predicted_yield_tonnes_per_hectare=raw_res["predicted_yield_tonnes_per_hectare"],
            predicted_yield_quintals_per_hectare=raw_res["predicted_yield_quintals_per_hectare"],
            predicted_yield_kg_per_hectare=raw_res["predicted_yield_kg_per_hectare"],
            confidence_interval_90=conf_interval,
            total_estimated_production_tonnes=total_tonnes,
            total_estimated_production_quintals=total_quintals,
            tnau_potential_realization_pct=raw_res["tnau_potential_realization_pct"],
            model_version=raw_res["model_version"],
            disclaimer=raw_res["disclaimer"]
        )

# Module singleton instance
ml_service = PaddyMLService()
