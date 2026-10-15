"""
SQLAlchemy ORM model for storing farmer queries and historical crop yield predictions.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from ..db.session import Base

class PredictionLog(Base):
    """Stores user input parameters and generated predictions in SQLite."""
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Farmer / Location Inputs
    district = Column(String(50), nullable=False, index=True)
    season = Column(String(30), nullable=False)
    soil_type = Column(String(50), nullable=False)
    area_hectares = Column(Float, nullable=False)

    # Soil Chemistry
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)

    # Weather Parameters
    rainfall_mm = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)

    # ML Output
    predicted_yield_kg_ha = Column(Float, nullable=False)
    model_version = Column(String(50), default="rf-tn-paddy-v1")
