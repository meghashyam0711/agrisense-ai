"""
Pydantic schemas for API root status, health check, and model metadata.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RootResponse(BaseModel):
    name: str
    status: str
    version: str
    description: str
    docs_url: Optional[str]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: Optional[str]
    environment: str
    timestamp: str

class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    target_variable: str
    target_unit: str
    created_at: str
    features_count: int
    feature_columns: List[str]
    top_10_feature_importances: Dict[str, float]
    evaluation_metrics: Dict[str, Any]
    disclaimer: str
