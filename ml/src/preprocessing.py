"""
AgriSense-AI: Reusable Agricultural Data Preprocessing Module.
Handles data loading, validation, missing value imputation, outlier handling,
feature engineering, categorical encoding, and leakage-free train/test splitting.
"""

import os
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd

from .dataset_schema import FEATURE_BOUNDS, TNDistrict, PaddySeason, SoilType

class PaddyDataPreprocessor:
    """
    Production-grade preprocessor for Tamil Nadu paddy crop yield prediction.
    Ensures zero data leakage between training and testing splits.
    """

    CATEGORICAL_COLUMNS = ["district", "season", "soil_type"]
    NUMERICAL_FEATURES = [
        "rainfall_mm",
        "temperature_c",
        "humidity_pct",
        "soil_ph",
        "soil_moisture_pct",
        "nitrogen_kg_ha",
        "phosphorus_kg_ha",
        "potassium_kg_ha",
        "previous_yield_tonnes_per_hectare"
    ]
    TARGET_COLUMN = "yield_tonnes_per_hectare"

    def __init__(self, target_column: str = "yield_tonnes_per_hectare"):
        self.target_column = target_column
        self.imputation_medians: Dict[str, float] = {}
        self.categorical_modes: Dict[str, str] = {}
        self.encoded_feature_columns: List[str] = []
        self.is_fitted: bool = False

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Safely loads a CSV dataset with preliminary validation.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset file not found at: {filepath}")
        df = pd.read_csv(filepath)
        if df.empty:
            raise ValueError(f"Loaded dataset at {filepath} is empty.")
        return df

    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Checks for expected column existence and data types.
        """
        all_required = self.CATEGORICAL_COLUMNS + self.NUMERICAL_FEATURES
        if self.target_column in df.columns:
            all_required.append(self.target_column)

        missing_columns = [col for col in all_required if col not in df.columns]
        null_counts = df.isnull().sum().to_dict()
        duplicate_count = int(df.duplicated().sum())

        is_valid = len(missing_columns) == 0
        return {
            "is_valid": is_valid,
            "total_rows": len(df),
            "missing_columns": missing_columns,
            "null_counts": null_counts,
            "duplicate_count": duplicate_count
        }

    def clean_data(self, df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
        """
        Removes duplicates, enforces valid agronomic ranges, and imputes missing values.
        In training mode, learns imputation parameters; in eval mode, applies fitted parameters.
        """
        cleaned_df = df.copy()

        # 1. Remove duplicate observations
        cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)

        # 2. Out-of-bounds sanitation: Replace anomalous physical values with NaN
        for col, bounds in FEATURE_BOUNDS.items():
            if col in cleaned_df.columns:
                invalid_mask = (cleaned_df[col] < bounds["min"]) | (cleaned_df[col] > bounds["max"])
                if invalid_mask.any():
                    cleaned_df.loc[invalid_mask, col] = np.nan

        # 3. Learn or apply numerical medians for imputation
        for col in self.NUMERICAL_FEATURES:
            if col in cleaned_df.columns:
                if is_train or col not in self.imputation_medians:
                    self.imputation_medians[col] = float(
                        cleaned_df[col].median()
                        if not cleaned_df[col].dropna().empty
                        else FEATURE_BOUNDS[col]["default_median"]
                    )
                cleaned_df[col] = cleaned_df[col].fillna(self.imputation_medians[col])

        # 4. Learn or apply categorical modes
        for col in self.CATEGORICAL_COLUMNS:
            if col in cleaned_df.columns:
                if is_train or col not in self.categorical_modes:
                    mode_series = cleaned_df[col].mode()
                    self.categorical_modes[col] = str(mode_series.iloc[0]) if not mode_series.empty else "Alluvial"
                cleaned_df[col] = cleaned_df[col].fillna(self.categorical_modes[col])

        # 5. Clean target column if present
        if self.target_column in cleaned_df.columns:
            # Target cannot be imputed; drop rows with NaN target
            cleaned_df = cleaned_df.dropna(subset=[self.target_column]).reset_index(drop=True)

        if is_train:
            self.is_fitted = True

        return cleaned_df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Derives agronomic interaction indicators based on soil science and crop physiology.
        """
        res = df.copy()

        # Macronutrient stoichiometry (NPK total & ratios)
        res["npk_total_kg_ha"] = res["nitrogen_kg_ha"] + res["phosphorus_kg_ha"] + res["potassium_kg_ha"]
        res["n_p_ratio"] = res["nitrogen_kg_ha"] / (res["phosphorus_kg_ha"] + 1e-4)
        res["n_k_ratio"] = res["nitrogen_kg_ha"] / (res["potassium_kg_ha"] + 1e-4)

        # Thermal-moisture index (heat-humidity discomfort indicator)
        res["heat_humidity_index"] = res["temperature_c"] * (res["humidity_pct"] / 100.0)

        # Rainfall to temperature moisture adequacy
        res["rainfall_temp_ratio"] = res["rainfall_mm"] / (res["temperature_c"] + 1e-4)

        # Soil pH optimality distance (Absolute deviation from optimal neutral 6.8)
        res["ph_optimality_deviation"] = np.abs(res["soil_ph"] - 6.8)

        return res

    def encode_categorical_features(self, df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
        """
        One-hot encodes district, season, and soil_type features.
        Preserves column structure across training and inference splits.
        """
        features_df = df.copy()
        
        # Isolate target if present
        target_series = None
        if self.target_column in features_df.columns:
            target_series = features_df[self.target_column]
            features_df = features_df.drop(columns=[self.target_column])

        # Perform one-hot encoding
        encoded_df = pd.get_dummies(features_df, columns=self.CATEGORICAL_COLUMNS, drop_first=False, dtype=float)

        if is_train:
            self.encoded_feature_columns = [c for c in encoded_df.columns]
        else:
            # Reindex to ensure identical feature columns as training
            encoded_df = encoded_df.reindex(columns=self.encoded_feature_columns, fill_value=0.0)

        # Re-attach target if it existed
        if target_series is not None:
            encoded_df[self.target_column] = target_series.values

        return encoded_df

    def split_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Splits dataset into feature matrix X and target vector y.
        Guarantees no target column in X (leakage prevention).
        """
        if self.target_column not in df.columns:
            raise KeyError(f"Target column '{self.target_column}' is missing from the dataset.")

        X = df.drop(columns=[self.target_column]).copy()
        y = df[self.target_column].copy()
        return X, y

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates numerical and categorical summary statistics.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        summary = {}

        for col in numeric_cols:
            series = df[col].dropna()
            summary[col] = {
                "count": int(series.count()),
                "mean": round(float(series.mean()), 3),
                "std": round(float(series.std()), 3),
                "min": round(float(series.min()), 3),
                "q25": round(float(series.quantile(0.25)), 3),
                "median": round(float(series.median()), 3),
                "q75": round(float(series.quantile(0.75)), 3),
                "max": round(float(series.max()), 3),
                "missing": int(df[col].isnull().sum())
            }

        return summary

    def process_pipeline(
        self,
        raw_df: pd.DataFrame,
        is_train: bool = True
    ) -> pd.DataFrame:
        """
        Full end-to-end preprocessing execution:
        Clean -> Feature Engineering -> Categorical Encoding
        """
        cleaned = self.clean_data(raw_df, is_train=is_train)
        engineered = self.engineer_features(cleaned)
        encoded = self.encode_categorical_features(engineered, is_train=is_train)
        return encoded
