"""
AgriSense-AI: SQLite Database Models.
Defines relational entities for Farm Profiles, Field Details,
Yield Prediction History, Farming Recommendations, and Actual Harvest Outcomes.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base


class Farm(Base):
    """Farm profile and geographical boundary information."""
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_name = Column(String(100), nullable=False, index=True)
    contact_phone = Column(String(20), nullable=True)
    district = Column(String(50), nullable=False, index=True)
    taluk = Column(String(50), nullable=True)
    village = Column(String(50), nullable=True)
    total_area_hectares = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("total_area_hectares > 0", name="chk_farm_area_positive"),
    )

    # Relationships
    fields = relationship("FieldDetail", back_populates="farm", cascade="all, delete-orphan")
    predictions = relationship("PredictionRecord", back_populates="farm")
    harvest_results = relationship("HarvestResult", back_populates="farm")


class FieldDetail(Base):
    """Specific field or plot details belonging to a farm profile."""
    __tablename__ = "field_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(50), nullable=False)
    area_hectares = Column(Float, nullable=False)
    soil_type = Column(String(50), nullable=False)
    soil_ph = Column(Float, nullable=True)
    irrigation_source = Column(String(50), nullable=True)  # Canal, Borewell, Tank, Rainfed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("area_hectares > 0", name="chk_field_area_positive"),
    )

    # Relationships
    farm = relationship("Farm", back_populates="fields")


class PredictionRecord(Base):
    """Historical audit log of crop yield predictions and environmental conditions."""
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True, index=True)
    field_id = Column(Integer, ForeignKey("field_details.id", ondelete="SET NULL"), nullable=True)

    # Location & Crop parameters
    district = Column(String(50), nullable=False, index=True)
    season = Column(String(30), nullable=False, index=True)
    soil_type = Column(String(50), nullable=False)
    area_hectares = Column(Float, nullable=False)

    # Environmental & Soil inputs
    rainfall_mm = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    soil_ph = Column(Float, nullable=False)
    soil_moisture_pct = Column(Float, nullable=False)
    nitrogen_kg_ha = Column(Float, nullable=False)
    phosphorus_kg_ha = Column(Float, nullable=False)
    potassium_kg_ha = Column(Float, nullable=False)
    previous_yield_tonnes_per_hectare = Column(Float, nullable=False)

    # Output predictions
    predicted_yield_tonnes_per_hectare = Column(Float, nullable=False)
    predicted_yield_quintals_per_hectare = Column(Float, nullable=False)
    predicted_yield_kg_per_hectare = Column(Float, nullable=False)
    confidence_lower_tonnes = Column(Float, nullable=True)
    confidence_upper_tonnes = Column(Float, nullable=True)

    # Metadata
    model_name = Column(String(50), nullable=False, default="RandomForestRegressor")
    model_version = Column(String(20), nullable=False, default="1.0.0")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="predictions")
    field = relationship("FieldDetail")
    recommendations = relationship("RecommendationRecord", back_populates="prediction", cascade="all, delete-orphan")
    harvest_result = relationship("HarvestResult", back_populates="prediction", uselist=False, cascade="all, delete-orphan")


class RecommendationRecord(Base):
    """Audited agronomic advisory items associated with farm queries or predictions."""
    __tablename__ = "recommendation_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("prediction_records.id", ondelete="CASCADE"), nullable=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True, index=True)

    district = Column(String(50), nullable=False)
    season = Column(String(30), nullable=False)
    growth_stage = Column(String(50), nullable=False)
    category = Column(String(30), nullable=False)  # irrigation, fertilizer, soil_health, pest_disease
    title = Column(String(150), nullable=False)
    action = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    urgency = Column(String(20), nullable=False)  # routine, advisory, warning, critical
    warnings = Column(Text, nullable=True)
    conditions_triggered = Column(Text, nullable=True)  # JSON-encoded dictionary
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    prediction = relationship("PredictionRecord", back_populates="recommendations")


class HarvestResult(Base):
    """Actual harvest results recorded by farmers to track real-world yield vs ML forecasts."""
    __tablename__ = "harvest_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("prediction_records.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), nullable=True, index=True)
    field_id = Column(Integer, ForeignKey("field_details.id", ondelete="SET NULL"), nullable=True)

    harvest_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    actual_yield_tonnes_per_hectare = Column(Float, nullable=False)
    actual_yield_quintals_per_hectare = Column(Float, nullable=False)
    actual_yield_kg_per_hectare = Column(Float, nullable=False)
    actual_total_production_tonnes = Column(Float, nullable=True)

    # Variance analysis vs predicted yield (if linked to a prediction)
    variance_tonnes = Column(Float, nullable=True)  # actual - predicted
    variance_pct = Column(Float, nullable=True)     # (actual - predicted) / predicted * 100
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("actual_yield_tonnes_per_hectare >= 0", name="chk_actual_yield_non_negative"),
    )

    # Relationships
    prediction = relationship("PredictionRecord", back_populates="harvest_result")
    farm = relationship("Farm", back_populates="harvest_results")
