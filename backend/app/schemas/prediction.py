"""
Pydantic schemas for Crop Yield Prediction API requests and responses.
Defines strict physical boundary validations, field aliases, and response contracts.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator

class PredictionRequest(BaseModel):
    """
    Input schema for farmer field parameters.
    Supports standard field names and aliases.
    """
    district: str = Field(..., description="Tamil Nadu District", examples=["Thanjavur"])
    season: str = Field(..., description="Cropping Season (Kuruvai, Samba, Thaladi, Navarai)", examples=["Samba"])
    soil_type: str = Field("Alluvial", description="Soil classification (Alluvial, Clayey, Red Loam, Coastal Saline)", examples=["Alluvial"])
    
    # Climate factors
    rainfall_mm: float = Field(..., ge=100.0, le=3500.0, description="Seasonal rainfall in mm", examples=[1150.0])
    temperature_c: float = Field(..., ge=15.0, le=48.0, description="Mean temperature in Celsius", examples=[29.5])
    humidity_pct: float = Field(..., ge=20.0, le=100.0, description="Relative humidity percentage", examples=[82.0])
    
    # Soil factors
    soil_ph: float = Field(..., ge=4.0, le=9.5, description="Soil pH level", examples=[6.8])
    soil_moisture_pct: float = Field(74.0, ge=15.0, le=100.0, description="Soil moisture percentage", examples=[76.0])
    
    # Nutrients (N-P-K)
    nitrogen_kg_ha: float = Field(..., ge=10.0, le=300.0, description="Nitrogen content (kg/ha)", examples=[140.0])
    phosphorus_kg_ha: float = Field(..., ge=5.0, le=150.0, description="Phosphorus content (kg/ha)", examples=[48.0])
    potassium_kg_ha: float = Field(..., ge=10.0, le=250.0, description="Potassium content (kg/ha)", examples=[45.0])
    
    # Previous yield baseline & Area
    previous_yield_tonnes_per_hectare: float = Field(
        4.3, ge=1.0, le=10.0, description="Previous season yield in tonnes/ha", examples=[4.5]
    )
    area_hectares: Optional[float] = Field(
        1.0, gt=0.0, le=500.0, description="Plot cultivation area in hectares", examples=[2.5]
    )

    @field_validator("district")
    def validate_district(cls, v: str) -> str:
        valid_districts = [
            "Thanjavur", "Tiruvarur", "Nagapattinam", "Mayiladuthurai",
            "Cuddalore", "Villupuram", "Tiruchirappalli", "Madurai",
            "Tirunelveli", "Kancheepuram", "Thiruvallur", "Erode"
        ]
        # Case-insensitive match
        match = next((d for d in valid_districts if d.lower() == v.strip().lower()), None)
        if not match:
            raise ValueError(f"Invalid district '{v}'. Must be one of: {', '.join(valid_districts)}")
        return match

    @field_validator("season")
    def validate_season(cls, v: str) -> str:
        valid_seasons = ["Kuruvai", "Samba", "Thaladi", "Navarai"]
        match = next((s for s in valid_seasons if s.lower() == v.strip().lower()), None)
        if not match:
            raise ValueError(f"Invalid season '{v}'. Must be one of: {', '.join(valid_seasons)}")
        return match

    @field_validator("soil_type")
    def validate_soil_type(cls, v: str) -> str:
        valid_soils = ["Alluvial", "Clayey", "Red Loam", "Coastal Saline"]
        match = next((s for s in valid_soils if s.lower() == v.strip().lower()), None)
        if not match:
            raise ValueError(f"Invalid soil type '{v}'. Must be one of: {', '.join(valid_soils)}")
        return match

    @model_validator(mode="before")
    @classmethod
    def support_legacy_aliases(cls, data: Any) -> Any:
        """Allows fallback aliases such as 'nitrogen' -> 'nitrogen_kg_ha', 'ph' -> 'soil_ph'."""
        if isinstance(data, dict):
            if "nitrogen" in data and "nitrogen_kg_ha" not in data:
                data["nitrogen_kg_ha"] = data["nitrogen"]
            if "phosphorus" in data and "phosphorus_kg_ha" not in data:
                data["phosphorus_kg_ha"] = data["phosphorus"]
            if "potassium" in data and "potassium_kg_ha" not in data:
                data["potassium_kg_ha"] = data["potassium"]
            if "ph" in data and "soil_ph" not in data:
                data["soil_ph"] = data["ph"]
            if "moisture" in data and "soil_moisture_pct" not in data:
                data["soil_moisture_pct"] = data["moisture"]
            if "previous_yield" in data and "previous_yield_tonnes_per_hectare" not in data:
                data["previous_yield_tonnes_per_hectare"] = data["previous_yield"]
        return data


class ConfidenceInterval(BaseModel):
    lower_tonnes_ha: float
    upper_tonnes_ha: float
    lower_quintals_ha: float
    upper_quintals_ha: float


class PredictionResponse(BaseModel):
    """
    Standard response payload for crop yield predictions.
    """
    success: bool = True
    crop: str = "Paddy (Oryza sativa)"
    district: str
    season: str
    soil_type: str
    predicted_yield_tonnes_per_hectare: float
    predicted_yield_quintals_per_hectare: float
    predicted_yield_kg_per_hectare: float
    confidence_interval_90: ConfidenceInterval
    total_estimated_production_tonnes: Optional[float] = None
    total_estimated_production_quintals: Optional[float] = None
    tnau_potential_realization_pct: float
    model_version: str
    disclaimer: str
