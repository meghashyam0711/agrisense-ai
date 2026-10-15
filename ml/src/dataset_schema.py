"""
Dataset Schema and Agricultural Domain Specifications for Tamil Nadu Paddy Farming.
Defines valid parameters, district mappings, soil types, cropping seasons, and feature boundaries.
Updated for Phase 3 to support tonnes/hectare metrics, soil moisture, and previous yield features.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class TNDistrict(str, Enum):
    """Major rice-producing districts in Tamil Nadu."""
    THANJAVUR = "Thanjavur"
    TIRUVARUR = "Tiruvarur"
    NAGAPATTINAM = "Nagapattinam"
    MAYILADUTHURAI = "Mayiladuthurai"
    CUDDALORE = "Cuddalore"
    VILLUPURAM = "Villupuram"
    TIRUCHIRAPPALLI = "Tiruchirappalli"
    MADURAI = "Madurai"
    TIRUNELVELI = "Tirunelveli"
    KANCHEEPURAM = "Kancheepuram"
    THIRUVALLUR = "Thiruvallur"
    ERODE = "Erode"

class PaddySeason(str, Enum):
    """Tamil Nadu agro-climatic paddy growing seasons."""
    KURUVAI = "Kuruvai"         # Short duration (Jun - Sep)
    SAMBA = "Samba"             # Medium/Long duration (Aug - Jan)
    THALADI = "Thaladi"         # Late season (Sep/Oct - Feb/Mar)
    NAVARAI = "Navarai"         # Dry/Summer season (Dec/Jan - Apr/May)

class SoilType(str, Enum):
    """Common soil types for Tamil Nadu paddy cultivation."""
    ALLUVIAL = "Alluvial"
    CLAYEY = "Clayey"
    RED_LOAM = "Red Loam"
    COASTAL_SALINE = "Coastal Saline"

class PaddyDatasetRecord(BaseModel):
    """
    Schema for individual dataset records used in ML training and evaluation.
    Primary target metric: yield_tonnes_per_hectare (1 tonne = 1,000 kg = 10 quintals).
    """
    district: TNDistrict = Field(..., description="Tamil Nadu district")
    season: PaddySeason = Field(..., description="Cropping season")
    soil_type: SoilType = Field(..., description="Soil classification")
    
    # Climatic Features
    rainfall_mm: float = Field(..., ge=100.0, le=3500.0, description="Seasonal cumulative rainfall in mm")
    temperature_c: float = Field(..., ge=15.0, le=48.0, description="Average temperature in Celsius")
    humidity_pct: float = Field(..., ge=20.0, le=100.0, description="Average relative humidity percentage")
    
    # Soil Chemistry & Moisture
    soil_ph: float = Field(..., ge=4.0, le=9.5, description="Soil pH level")
    soil_moisture_pct: float = Field(..., ge=15.0, le=100.0, description="Field soil moisture content percentage")
    nitrogen_kg_ha: float = Field(..., ge=10.0, le=300.0, description="Nitrogen content (kg/ha)")
    phosphorus_kg_ha: float = Field(..., ge=5.0, le=150.0, description="Phosphorus content (kg/ha)")
    potassium_kg_ha: float = Field(..., ge=10.0, le=250.0, description="Potassium content (kg/ha)")
    
    # Historical / Baseline Feature
    previous_yield_tonnes_per_hectare: float = Field(
        ..., ge=1.0, le=10.0, description="Previous season crop yield in tonnes per hectare"
    )
    
    # Prediction Target Variable
    yield_tonnes_per_hectare: float = Field(
        ..., ge=1.0, le=10.0, description="Actual harvest crop yield in tonnes per hectare"
    )


# Valid Feature Ranges (Physical and Agronomic Boundaries for Data Validation)
FEATURE_BOUNDS = {
    "rainfall_mm": {"min": 100.0, "max": 3500.0, "default_median": 1050.0, "unit": "mm"},
    "temperature_c": {"min": 15.0, "max": 48.0, "default_median": 31.5, "unit": "°C"},
    "humidity_pct": {"min": 20.0, "max": 100.0, "default_median": 76.0, "unit": "%"},
    "soil_ph": {"min": 4.0, "max": 9.5, "default_median": 6.8, "unit": "pH"},
    "soil_moisture_pct": {"min": 15.0, "max": 100.0, "default_median": 72.0, "unit": "%"},
    "nitrogen_kg_ha": {"min": 10.0, "max": 300.0, "default_median": 135.0, "unit": "kg/ha"},
    "phosphorus_kg_ha": {"min": 5.0, "max": 150.0, "default_median": 45.0, "unit": "kg/ha"},
    "potassium_kg_ha": {"min": 10.0, "max": 250.0, "default_median": 45.0, "unit": "kg/ha"},
    "previous_yield_tonnes_per_hectare": {"min": 1.0, "max": 10.0, "default_median": 4.3, "unit": "tonnes/ha"},
    "yield_tonnes_per_hectare": {"min": 1.0, "max": 10.0, "default_median": 4.5, "unit": "tonnes/ha"},
}

# District Lat/Lon coordinates for Tamil Nadu weather API lookup
DISTRICT_COORDINATES: Dict[str, Dict[str, float]] = {
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "Tiruvarur": {"lat": 10.7725, "lon": 79.6365},
    "Nagapattinam": {"lat": 10.7672, "lon": 79.8449},
    "Mayiladuthurai": {"lat": 11.1075, "lon": 79.6524},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714},
    "Villupuram": {"lat": 11.9401, "lon": 79.4861},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Kancheepuram": {"lat": 12.8342, "lon": 79.7036},
    "Thiruvallur": {"lat": 13.1432, "lon": 79.9083},
    "Erode": {"lat": 11.3410, "lon": 77.7172},
}

# TNAU Recommended NPK baselines (kg/ha) for paddy optimization calculations
TNAU_RECOMMENDED_NPK = {
    "Kuruvai": {"N": 120, "P": 40, "K": 40, "typical_yield_tonnes": 4.8},
    "Samba": {"N": 150, "P": 50, "K": 50, "typical_yield_tonnes": 5.2},
    "Thaladi": {"N": 150, "P": 50, "K": 50, "typical_yield_tonnes": 4.9},
    "Navarai": {"N": 120, "P": 40, "K": 40, "typical_yield_tonnes": 4.4},
}
