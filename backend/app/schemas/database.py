"""
AgriSense-AI: Database Schemas for Farm Profiles, History & Harvest Tracking.
Validates inputs and formats responses for SQLite-persisted entities.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# --- Field Details Schemas ---
class FieldDetailBase(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=50, examples=["North Paddy Plot"])
    area_hectares: float = Field(..., gt=0.0, le=1000.0, examples=[2.5])
    soil_type: str = Field(..., examples=["Alluvial"])
    soil_ph: Optional[float] = Field(None, ge=4.0, le=9.5, examples=[6.8])
    irrigation_source: Optional[str] = Field(None, examples=["Canal"])


class FieldDetailCreate(FieldDetailBase):
    pass


class FieldDetailResponse(FieldDetailBase):
    id: int
    farm_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Farm Profile Schemas ---
class FarmBase(BaseModel):
    farmer_name: str = Field(..., min_length=2, max_length=100, examples=["K. Murugan"])
    contact_phone: Optional[str] = Field(None, max_length=20, examples=["+91 98765 43210"])
    district: str = Field(..., examples=["Thanjavur"])
    taluk: Optional[str] = Field(None, max_length=50, examples=["Kumbakonam"])
    village: Optional[str] = Field(None, max_length=50, examples=["Swamimalai"])
    total_area_hectares: float = Field(..., gt=0.0, le=5000.0, examples=[5.0])

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


class FarmCreate(FarmBase):
    fields: Optional[List[FieldDetailCreate]] = Field(default_factory=list)


class FarmUpdate(BaseModel):
    farmer_name: Optional[str] = Field(None, min_length=2, max_length=100)
    contact_phone: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    total_area_hectares: Optional[float] = Field(None, gt=0.0)


class FarmResponse(FarmBase):
    id: int
    created_at: datetime
    updated_at: datetime
    field_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class FarmDetailResponse(FarmResponse):
    fields: List[FieldDetailResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Prediction Record Schemas ---
class PredictionRecordCreate(BaseModel):
    farm_id: Optional[int] = None
    field_id: Optional[int] = None

    district: str
    season: str
    soil_type: str
    area_hectares: float = Field(..., gt=0.0)

    rainfall_mm: float = Field(..., ge=0.0)
    temperature_c: float = Field(..., ge=10.0, le=50.0)
    humidity_pct: float = Field(..., ge=10.0, le=100.0)
    soil_ph: float = Field(..., ge=4.0, le=9.5)
    soil_moisture_pct: float = Field(..., ge=10.0, le=100.0)
    nitrogen_kg_ha: float = Field(..., ge=10.0, le=300.0)
    phosphorus_kg_ha: float = Field(..., ge=5.0, le=150.0)
    potassium_kg_ha: float = Field(..., ge=10.0, le=250.0)
    previous_yield_tonnes_per_hectare: float = Field(..., ge=0.0, le=15.0)

    predicted_yield_tonnes_per_hectare: float = Field(..., ge=0.0)
    predicted_yield_quintals_per_hectare: float = Field(..., ge=0.0)
    predicted_yield_kg_per_hectare: float = Field(..., ge=0.0)
    confidence_lower_tonnes: Optional[float] = None
    confidence_upper_tonnes: Optional[float] = None
    model_name: str = "RandomForestRegressor"
    model_version: str = "1.0.0"
    notes: Optional[str] = None


class RecommendationRecordResponse(BaseModel):
    id: int
    prediction_id: Optional[int] = None
    district: str
    season: str
    growth_stage: str
    category: str
    title: str
    action: str
    reason: str
    urgency: str
    warnings: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HarvestResultResponse(BaseModel):
    id: int
    prediction_id: Optional[int] = None
    farm_id: Optional[int] = None
    field_id: Optional[int] = None
    harvest_date: str
    actual_yield_tonnes_per_hectare: float
    actual_yield_quintals_per_hectare: float
    actual_yield_kg_per_hectare: float
    actual_total_production_tonnes: Optional[float] = None
    variance_tonnes: Optional[float] = None
    variance_pct: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionRecordResponse(BaseModel):
    id: int
    farm_id: Optional[int] = None
    field_id: Optional[int] = None
    district: str
    season: str
    soil_type: str
    area_hectares: float

    rainfall_mm: float
    temperature_c: float
    humidity_pct: float
    soil_ph: float
    soil_moisture_pct: float
    nitrogen_kg_ha: float
    phosphorus_kg_ha: float
    potassium_kg_ha: float
    previous_yield_tonnes_per_hectare: float

    predicted_yield_tonnes_per_hectare: float
    predicted_yield_quintals_per_hectare: float
    predicted_yield_kg_per_hectare: float
    confidence_lower_tonnes: Optional[float] = None
    confidence_upper_tonnes: Optional[float] = None
    model_name: str
    model_version: str
    notes: Optional[str] = None
    created_at: datetime

    harvest_result: Optional[HarvestResultResponse] = None
    recommendations: Optional[List[RecommendationRecordResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# --- Harvest Record Submission Schema ---
class HarvestResultCreate(BaseModel):
    prediction_id: Optional[int] = Field(None, description="Optional link to original prediction record")
    farm_id: Optional[int] = None
    field_id: Optional[int] = None
    harvest_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", examples=["2026-10-14"])
    actual_yield_tonnes_per_hectare: float = Field(..., ge=0.0, le=20.0, description="Actual harvest yield in tonnes/ha", examples=[4.85])
    actual_total_production_tonnes: Optional[float] = Field(None, ge=0.0, description="Total harvest across the plot in tonnes")
    notes: Optional[str] = Field(None, max_length=500, examples=["Healthy harvest with minimal pest pressure."])


# --- Recommendation Record Submission Schema ---
class RecommendationRecordCreate(BaseModel):
    prediction_id: Optional[int] = None
    farm_id: Optional[int] = None
    district: str
    season: str
    growth_stage: str
    category: str
    title: str
    action: str
    reason: str
    urgency: str
    warnings: Optional[str] = None
    conditions_triggered: Optional[Dict[str, Any]] = None
