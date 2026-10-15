"""
AgriSense-AI: Machine Learning Engine & Model Training Pipeline.
Trains a Scikit-Learn Random Forest Regressor to predict paddy crop yield (tonnes/ha),
evaluates against baseline, and serializes model bundle and feature metadata using Joblib.
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from .interface import CropYieldModelInterface, EvaluationMetrics
from .preprocessing import PaddyDataPreprocessor
from .dataset_schema import FEATURE_BOUNDS

class PaddyYieldModelTrainer(CropYieldModelInterface):
    """
    Implements model training, evaluation, cross-validation, and Joblib serialization.
    """

    def __init__(
        self,
        target_column: str = "yield_tonnes_per_hectare",
        random_state: int = 42
    ):
        self.target_column = target_column
        self.random_state = random_state
        self.preprocessor = PaddyDataPreprocessor(target_column=target_column)
        self.model: Optional[RandomForestRegressor] = None
        self.baseline_model: Optional[DummyRegressor] = None
        self.feature_columns: List[str] = []
        self.metrics: Optional[Dict[str, Any]] = None
        self.feature_importances: Dict[str, float] = {}

    def train(self, raw_data: pd.DataFrame) -> EvaluationMetrics:
        """
        Executes end-to-end preprocessing, train/test split, model training,
        cross-validation, and metrics evaluation.
        """
        print("[1/5] Preprocessing raw dataset...")
        processed_df = self.preprocessor.process_pipeline(raw_data, is_train=True)
        
        # Leakage-free separation of feature matrix and target
        X, y = self.preprocessor.split_features_and_target(processed_df)
        self.feature_columns = list(X.columns)

        print(f"[+] Total samples: {len(X)}, Feature dimensions: {len(self.feature_columns)}")

        # 80/20 Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=self.random_state
        )

        print(f"[2/5] Training data: {len(X_train)} samples, Test data: {len(X_test)} samples")

        # 1. Baseline Model (Mean Predictor)
        print("[3/5] Training Dummy Regressor baseline...")
        self.baseline_model = DummyRegressor(strategy="mean")
        self.baseline_model.fit(X_train, y_train)
        baseline_preds = self.baseline_model.predict(X_test)
        
        base_mae = float(mean_absolute_error(y_test, baseline_preds))
        base_rmse = float(root_mean_squared_error(y_test, baseline_preds))
        base_r2 = float(r2_score(y_test, baseline_preds))

        # 2. Random Forest Regressor
        print("[4/5] Training Random Forest Regressor...")
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features=0.8,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        rf_preds = self.model.predict(X_test)

        rf_mae = float(mean_absolute_error(y_test, rf_preds))
        rf_rmse = float(root_mean_squared_error(y_test, rf_preds))
        rf_r2 = float(r2_score(y_test, rf_preds))

        # 5-Fold Cross Validation
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(self.model, X, y, cv=kfold, scoring="r2", n_jobs=-1)
        cv_r2_mean = float(np.mean(cv_scores))
        cv_r2_std = float(np.std(cv_scores))

        # Calculate Feature Importances
        importances = self.model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        self.feature_importances = {
            self.feature_columns[i]: round(float(importances[i]), 4)
            for i in sorted_idx
        }

        # Store comprehensive metrics
        self.metrics = {
            "random_forest": {
                "test_mae": round(rf_mae, 4),
                "test_rmse": round(rf_rmse, 4),
                "test_r2": round(rf_r2, 4),
                "cv_5fold_r2_mean": round(cv_r2_mean, 4),
                "cv_5fold_r2_std": round(cv_r2_std, 4),
            },
            "baseline_mean": {
                "test_mae": round(base_mae, 4),
                "test_rmse": round(base_rmse, 4),
                "test_r2": round(base_r2, 4),
            },
            "sample_counts": {
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "total_samples": len(X)
            }
        }

        print("[5/5] Model evaluation completed successfully.")
        return EvaluationMetrics(
            mae=round(rf_mae, 4),
            rmse=round(rf_rmse, 4),
            r2_score=round(rf_r2, 4),
            samples_count=len(y_test)
        )

    def predict(self, feature_payload: Dict[str, Any]) -> float:
        """
        Generates yield prediction in tonnes/hectare for a single input record.
        """
        if self.model is None or not self.preprocessor.is_fitted:
            raise RuntimeError("Model and preprocessor must be trained or loaded before prediction.")

        df_input = pd.DataFrame([feature_payload])
        processed_input = self.preprocessor.process_pipeline(df_input, is_train=False)

        # Align with training columns
        X_input = processed_input.reindex(columns=self.feature_columns, fill_value=0.0)
        prediction = float(self.model.predict(X_input)[0])
        return round(prediction, 3)

    def save(
        self,
        model_path: str = "ml/saved_models/rf_paddy_yield_model.joblib",
        metadata_path: str = "ml/saved_models/feature_metadata.json"
    ) -> None:
        """
        Serializes trained Random Forest model, fitted preprocessor, and JSON metadata.
        """
        if self.model is None:
            raise RuntimeError("Cannot save an untrained model.")

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

        preprocessor_path = model_path.replace("rf_paddy_yield_model.joblib", "preprocessor.joblib")

        # 1. Save Scikit-Learn Model
        joblib.dump(self.model, model_path, compress=3)
        print(f"[+] Model saved to: {model_path}")

        # 2. Save Fitted Preprocessor
        joblib.dump(self.preprocessor, preprocessor_path, compress=3)
        print(f"[+] Preprocessor saved to: {preprocessor_path}")

        # 3. Save Metadata JSON
        metadata = {
            "model_name": "AgriSense Random Forest Paddy Yield Regressor",
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "target_variable": self.target_column,
            "target_unit": "tonnes_per_hectare",
            "evaluation_metrics": self.metrics,
            "feature_columns": self.feature_columns,
            "top_10_feature_importances": dict(list(self.feature_importances.items())[:10]),
            "hyperparameters": self.model.get_params(),
            "disclaimer": (
                "DEMONSTRATION MODEL ONLY: Trained on synthetic proxy data informed by TNAU guidelines. "
                "Not validated for commercial agricultural investment decisions."
            )
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"[+] Metadata saved to: {metadata_path}")

    def load(
        self,
        model_path: str = "ml/saved_models/rf_paddy_yield_model.joblib",
        metadata_path: str = "ml/saved_models/feature_metadata.json"
    ) -> None:
        """
        Deserializes model, preprocessor, and feature metadata into memory.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at: {metadata_path}")

        preprocessor_path = model_path.replace("rf_paddy_yield_model.joblib", "preprocessor.joblib")
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor file not found at: {preprocessor_path}")

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        self.feature_columns = metadata.get("feature_columns", [])
        self.metrics = metadata.get("evaluation_metrics", {})
        self.feature_importances = metadata.get("top_10_feature_importances", {})
        print(f"[+] Model and preprocessor loaded successfully from {model_path}")


def run_training_pipeline(
    raw_data_path: str = "ml/data/raw/synthetic_paddy_yield_tn.csv",
    model_output_path: str = "ml/saved_models/rf_paddy_yield_model.joblib",
    metadata_output_path: str = "ml/saved_models/feature_metadata.json"
):
    print("=" * 70)
    print("AGRISENSE-AI: MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 70)

    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(
            f"Dataset not found at {raw_data_path}. Please run Phase 3 validation script first."
        )

    raw_df = pd.read_csv(raw_data_path)
    trainer = PaddyYieldModelTrainer()
    
    # Train & evaluate
    metrics = trainer.train(raw_df)

    print("\n" + "=" * 50)
    print("MODEL EVALUATION RESULTS (Test Set n=400)")
    print("=" * 50)
    print(f"{'Metric':<25} | {'Baseline (Mean)':<15} | {'Random Forest':<15}")
    print("-" * 60)
    print(f"{'MAE (tonnes/ha)':<25} | {trainer.metrics['baseline_mean']['test_mae']:<15.4f} | {trainer.metrics['random_forest']['test_mae']:<15.4f}")
    print(f"{'RMSE (tonnes/ha)':<25} | {trainer.metrics['baseline_mean']['test_rmse']:<15.4f} | {trainer.metrics['random_forest']['test_rmse']:<15.4f}")
    print(f"{'R² Score':<25} | {trainer.metrics['baseline_mean']['test_r2']:<15.4f} | {trainer.metrics['random_forest']['test_r2']:<15.4f}")
    print(f"{'5-Fold CV R²':<25} | {'N/A':<15} | {trainer.metrics['random_forest']['cv_5fold_r2_mean']:.4f} (±{trainer.metrics['random_forest']['cv_5fold_r2_std']:.4f})")
    print("=" * 60)

    print("\nTop 5 Most Important Features:")
    for rank, (feat, imp) in enumerate(list(trainer.feature_importances.items())[:5], 1):
        print(f"  {rank}. {feat:<32}: {imp * 100:.2f}%")

    # Save artifacts
    print("\n[*] Saving model artifacts...")
    trainer.save(model_output_path, metadata_output_path)

    # Verification sample prediction
    sample_payload = {
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
    sample_pred = trainer.predict(sample_payload)
    print(f"\n[Verification] Sample Prediction for Thanjavur (Samba):")
    print(f"  -> Predicted Yield: {sample_pred:.3f} tonnes/ha ({sample_pred * 10:.2f} Q/ha)")
    print("=" * 70)


if __name__ == "__main__":
    run_training_pipeline()
