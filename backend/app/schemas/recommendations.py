"""
AgriSense-AI: Smart Farming Recommendation Schemas.
Defines contracts for agronomic expert rules covering irrigation (AWD),
TNAU fertilizer schedules, soil amendments, and pest monitoring alerts.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class CropStage(str, Enum):
    """Paddy crop phenological growth stages."""
    NURSERY = "nursery"
    VEGETATIVE_TILLERING = "vegetative_tillering"
    PANICLE_INITIATION = "panicle_initiation"
    FLOWERING_HEADING = "flowering_heading"
    GRAIN_FILLING_MATURITY = "grain_filling_maturity"

class RecommendationUrgency(str, Enum):
    """Urgency level of recommendation action."""
    ROUTINE = "routine"
    ADVISORY = "advisory"
    WARNING = "warning"
    CRITICAL = "critical"

class RecommendationCategory(str, Enum):
    """Category classification of recommendation."""
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    SOIL_HEALTH = "soil_health"
    PEST_DISEASE = "pest_disease"

class RecommendationRequest(BaseModel):
    """
    Input parameters for smart farming recommendation generation.
    Supports farm chemistry, environment, crop phenology, and weather indicators.
    """
    district: str = Field(..., description="Tamil Nadu district", examples=["Thanjavur"])
    season: str = Field("Samba", description="Cropping season (Kuruvai, Samba, Thaladi, Navarai)", examples=["Samba"])
    growth_stage: CropStage = Field(
        CropStage.VEGETATIVE_TILLERING,
        description="Current crop growth stage",
        examples=[CropStage.VEGETATIVE_TILLERING]
    )
    soil_type: str = Field("Alluvial", description="Soil classification", examples=["Alluvial"])

    # Soil Chemistry & Moisture
    soil_ph: float = Field(..., ge=4.0, le=9.5, description="Soil pH level", examples=[6.8])
    soil_moisture_pct: float = Field(..., ge=10.0, le=100.0, description="Field soil moisture percentage", examples=[74.0])
    nitrogen_kg_ha: float = Field(..., ge=10.0, le=300.0, description="Nitrogen level in kg/ha", examples=[135.0])
    phosphorus_kg_ha: float = Field(..., ge=5.0, le=150.0, description="Phosphorus level in kg/ha", examples=[45.0])
    potassium_kg_ha: float = Field(..., ge=10.0, le=250.0, description="Potassium level in kg/ha", examples=[42.0])

    # Environmental indicators
    temperature_c: Optional[float] = Field(None, ge=15.0, le=48.0, description="Current or forecast temperature in °C", examples=[30.5])
    humidity_pct: Optional[float] = Field(None, ge=20.0, le=100.0, description="Relative humidity percentage", examples=[82.0])
    rainfall_mm: Optional[float] = Field(None, ge=0.0, le=3500.0, description="Recent or seasonal rainfall in mm", examples=[5.0])

    # Short-term weather forecast triggers (can be provided or fetched via weather service)
    forecast_rain_expected_mm: Optional[float] = Field(
        None, ge=0.0, le=500.0, description="Expected precipitation in next 48-72h in mm", examples=[25.0]
    )
    forecast_rain_prob_pct: Optional[int] = Field(
        None, ge=0, le=100, description="Rainfall probability in next 48-72h %", examples=[75]
    )

    @field_validator("district")
    def validate_district(cls, v: str) -> str:
        valid_districts = [
            "Thanjavur", "Tiruvarur", "Nagapattinam", "Mayiladuthurai",
            "Cuddalore", "Villupuram", "Tiruchirappalli", "Madurai",
            "Tirunelveli", "Kancheepuram", "Thiruvallur", "Erode"
        ]
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


class RecommendationItem(BaseModel):
    """Individual actionable recommendation unit."""
    category: RecommendationCategory
    title: str
    action: str
    reason: str
    urgency: RecommendationUrgency
    conditions_triggered: Dict[str, Any]
    warnings: Optional[str] = None


class RecommendationsResponse(BaseModel):
    """
    Standardized response payload for smart farming recommendations.
    Clearly distinguishes rule-based agronomic guidance from ML statistical predictions.
    """
    rule_type: str = Field(
        "agronomic_expert_system",
        description="Methodology label (explicitly distinguished from ML yield predictions)"
    )
    district: str
    season: str
    growth_stage: CropStage
    irrigation_advisory: List[RecommendationItem]
    fertilizer_advisory: List[RecommendationItem]
    soil_health_advisory: List[RecommendationItem]
    pest_monitoring_alerts: List[RecommendationItem]
    conflicts_detected: List[str] = Field(
        default_factory=list,
        description="Active conflicting agricultural factors detected (e.g., dry soil vs imminent downpour)"
    )
    data_limitations: List[str] = Field(
        default_factory=list,
        description="Limitations or absent metrics that qualified the generated advice"
    )
    authoritative_source: str = Field(
        "Tamil Nadu Agricultural University (TNAU) Crop Production Guide (Paddy) & Agritech Portal",
        description="Authoritative agronomic foundation"
    )
    disclaimer: str = Field(
        "Agricultural Advisory Disclaimer: Recommendations are rule-based expert guidelines aligned with TNAU benchmarks. "
        "They do not guarantee increased crop yield and must be cross-verified with local field observations and Krishi Vigyan Kendra (KVK) advisors.",
        description="Mandatory advisory disclaimer"
    )
