"""
Model Interface and ML Pipeline Contracts.
Defines abstract specifications and interfaces for training, serialization,
prediction, and evaluation without implementing the training logic (Phase 1).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
from pydantic import BaseModel

class EvaluationMetrics(BaseModel):
    """Evaluation metrics for Scikit-Learn Random Forest Regressor."""
    mae: float
    rmse: float
    r2_score: float
    samples_count: int

class CropYieldModelInterface(ABC):
    """
    Standard interface contract for the Scikit-learn Random Forest regression model.
    Implementations in Phase 2 must adhere strictly to these method signatures.
    """

    @abstractmethod
    def train(self, data: pd.DataFrame) -> EvaluationMetrics:
        """
        Train Random Forest Regressor on preprocessed dataset.
        
        Args:
            data: DataFrame containing input features and target yield (kg/ha).
            
        Returns:
            EvaluationMetrics: Calculated validation metrics (MAE, RMSE, R²).
        """
        pass

    @abstractmethod
    def predict(self, feature_payload: Dict[str, Any]) -> float:
        """
        Generate yield prediction in kg/hectare.
        
        Args:
            feature_payload: Dictionary of validated agronomic and weather inputs.
            
        Returns:
            float: Predicted yield in kg/hectare.
        """
        pass

    @abstractmethod
    def save(self, model_path: str, metadata_path: str) -> None:
        """
        Serialize model and associated pipeline feature encoders.
        
        Args:
            model_path: Filepath for the .joblib model bundle.
            metadata_path: Filepath for feature column names and scaler params.
        """
        pass

    @abstractmethod
    def load(self, model_path: str, metadata_path: str) -> None:
        """
        Deserialize and load model bundle into memory.
        
        Args:
            model_path: Filepath to saved .joblib model.
            metadata_path: Filepath to feature metadata.
        """
        pass
