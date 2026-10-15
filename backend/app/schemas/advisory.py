"""
Pydantic schemas for Crop Optimization and Agronomic Advisory.
"""

from typing import List, Dict
from pydantic import BaseModel, Field

class NutrientOptimizationRecommendation(BaseModel):
    """Specific nutrient balance recommendations."""
    nutrient: str  # Nitrogen, Phosphorus, Potassium
    current_kg_ha: float
    recommended_kg_ha: float
    difference_kg_ha: float
    action: str  # "Increase", "Maintain", "Reduce"
    guidance: str

class OptimizationAdvisoryResponse(BaseModel):
    """
    Contract for crop optimization guidance based on TNAU recommendations
    and predicted yield sensitivity.
    """
    district: str
    season: str
    target_potential_yield_kg_ha: float
    nutrient_recommendations: List[NutrientOptimizationRecommendation]
    irrigation_advisory: str
    soil_health_note: str
    tamil_advisory: Dict[str, str] = Field(
        ...,
        description="Localized Tamil translation keys for UI display"
    )
