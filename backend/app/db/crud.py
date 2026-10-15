"""
AgriSense-AI: Reusable Database Operations (CRUD).
Implements safe, parameterized queries with transaction rollbacks on failure.
"""

import json
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from .models import Farm, FieldDetail, PredictionRecord, RecommendationRecord, HarvestResult
from ..schemas.database import (
    FarmCreate,
    FarmUpdate,
    FieldDetailCreate,
    PredictionRecordCreate,
    HarvestResultCreate,
    RecommendationRecordCreate
)


# ==============================================================================
# Farm & Field Operations
# ==============================================================================

def create_farm(db: Session, farm_in: FarmCreate) -> Farm:
    """Creates a new farm profile and any associated initial fields in a transaction."""
    try:
        db_farm = Farm(
            farmer_name=farm_in.farmer_name,
            contact_phone=farm_in.contact_phone,
            district=farm_in.district,
            taluk=farm_in.taluk,
            village=farm_in.village,
            total_area_hectares=farm_in.total_area_hectares
        )
        db.add(db_farm)
        db.flush()  # Populates db_farm.id

        if farm_in.fields:
            for field_data in farm_in.fields:
                db_field = FieldDetail(
                    farm_id=db_farm.id,
                    field_name=field_data.field_name,
                    area_hectares=field_data.area_hectares,
                    soil_type=field_data.soil_type,
                    soil_ph=field_data.soil_ph,
                    irrigation_source=field_data.irrigation_source
                )
                db.add(db_field)

        db.commit()
        db.refresh(db_farm)
        return db_farm
    except Exception:
        db.rollback()
        raise


def get_farm(db: Session, farm_id: int) -> Optional[Farm]:
    """Retrieves a farm profile with its fields loaded."""
    return db.query(Farm).options(joinedload(Farm.fields)).filter(Farm.id == farm_id).first()


def list_farms(db: Session, district: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Farm]:
    """Lists farm profiles with optional district filtering."""
    query = db.query(Farm).options(joinedload(Farm.fields))
    if district:
        query = query.filter(Farm.district.ilike(f"%{district}%"))
    return query.order_by(desc(Farm.created_at)).offset(offset).limit(limit).all()


def update_farm(db: Session, farm_id: int, farm_update: FarmUpdate) -> Optional[Farm]:
    """Updates farm profile fields."""
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        return None

    try:
        update_data = farm_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_farm, key, value)
        db.commit()
        db.refresh(db_farm)
        return db_farm
    except Exception:
        db.rollback()
        raise


def delete_farm(db: Session, farm_id: int) -> bool:
    """Deletes a farm profile and cascades deletion to child fields."""
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        return False
    try:
        db.delete(db_farm)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def create_field(db: Session, farm_id: int, field_in: FieldDetailCreate) -> FieldDetail:
    """Adds a new field to an existing farm."""
    try:
        db_field = FieldDetail(
            farm_id=farm_id,
            field_name=field_in.field_name,
            area_hectares=field_in.area_hectares,
            soil_type=field_in.soil_type,
            soil_ph=field_in.soil_ph,
            irrigation_source=field_in.irrigation_source
        )
        db.add(db_field)
        db.commit()
        db.refresh(db_field)
        return db_field
    except Exception:
        db.rollback()
        raise


def list_fields_by_farm(db: Session, farm_id: int) -> List[FieldDetail]:
    """Lists all fields for a given farm."""
    return db.query(FieldDetail).filter(FieldDetail.farm_id == farm_id).all()


# ==============================================================================
# Yield Prediction History Operations
# ==============================================================================

def create_prediction_record(db: Session, record_in: PredictionRecordCreate) -> PredictionRecord:
    """Persists a crop yield prediction query and inference outcome to SQLite."""
    try:
        db_record = PredictionRecord(
            farm_id=record_in.farm_id,
            field_id=record_in.field_id,
            district=record_in.district,
            season=record_in.season,
            soil_type=record_in.soil_type,
            area_hectares=record_in.area_hectares,
            rainfall_mm=record_in.rainfall_mm,
            temperature_c=record_in.temperature_c,
            humidity_pct=record_in.humidity_pct,
            soil_ph=record_in.soil_ph,
            soil_moisture_pct=record_in.soil_moisture_pct,
            nitrogen_kg_ha=record_in.nitrogen_kg_ha,
            phosphorus_kg_ha=record_in.phosphorus_kg_ha,
            potassium_kg_ha=record_in.potassium_kg_ha,
            previous_yield_tonnes_per_hectare=record_in.previous_yield_tonnes_per_hectare,
            predicted_yield_tonnes_per_hectare=record_in.predicted_yield_tonnes_per_hectare,
            predicted_yield_quintals_per_hectare=record_in.predicted_yield_quintals_per_hectare,
            predicted_yield_kg_per_hectare=record_in.predicted_yield_kg_per_hectare,
            confidence_lower_tonnes=record_in.confidence_lower_tonnes,
            confidence_upper_tonnes=record_in.confidence_upper_tonnes,
            model_name=record_in.model_name,
            model_version=record_in.model_version,
            notes=record_in.notes
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception:
        db.rollback()
        raise


def get_prediction_record(db: Session, record_id: int) -> Optional[PredictionRecord]:
    """Retrieves a single prediction record with its harvest result and recommendations."""
    return db.query(PredictionRecord).options(
        joinedload(PredictionRecord.harvest_result),
        joinedload(PredictionRecord.recommendations)
    ).filter(PredictionRecord.id == record_id).first()


def list_prediction_records(
    db: Session,
    district: Optional[str] = None,
    season: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> List[PredictionRecord]:
    """Retrieves recent prediction records with filtering."""
    query = db.query(PredictionRecord).options(
        joinedload(PredictionRecord.harvest_result),
        joinedload(PredictionRecord.recommendations)
    )
    if district:
        query = query.filter(PredictionRecord.district.ilike(f"%{district}%"))
    if season:
        query = query.filter(PredictionRecord.season.ilike(f"%{season}%"))
    if farm_id is not None:
        query = query.filter(PredictionRecord.farm_id == farm_id)

    return query.order_by(desc(PredictionRecord.created_at)).offset(offset).limit(limit).all()


def count_prediction_records(db: Session) -> int:
    """Returns the total number of recorded predictions."""
    return db.query(PredictionRecord).count()


# ==============================================================================
# Harvest Outcome Operations
# ==============================================================================

def create_harvest_result(db: Session, harvest_in: HarvestResultCreate) -> HarvestResult:
    """
    Records ground-truth harvest yield, calculating quintals/kg conversions
    and variance analysis against predicted yield if linked to a prediction.
    """
    try:
        actual_tonnes = harvest_in.actual_yield_tonnes_per_hectare
        actual_quintals = round(actual_tonnes * 10.0, 2)
        actual_kg = round(actual_tonnes * 1000.0, 2)

        variance_tonnes: Optional[float] = None
        variance_pct: Optional[float] = None

        if harvest_in.prediction_id:
            pred = db.query(PredictionRecord).filter(PredictionRecord.id == harvest_in.prediction_id).first()
            if pred:
                pred_tonnes = pred.predicted_yield_tonnes_per_hectare
                variance_tonnes = round(actual_tonnes - pred_tonnes, 3)
                if pred_tonnes > 0:
                    variance_pct = round(((actual_tonnes - pred_tonnes) / pred_tonnes) * 100.0, 2)

        db_harvest = HarvestResult(
            prediction_id=harvest_in.prediction_id,
            farm_id=harvest_in.farm_id,
            field_id=harvest_in.field_id,
            harvest_date=harvest_in.harvest_date,
            actual_yield_tonnes_per_hectare=actual_tonnes,
            actual_yield_quintals_per_hectare=actual_quintals,
            actual_yield_kg_per_hectare=actual_kg,
            actual_total_production_tonnes=harvest_in.actual_total_production_tonnes,
            variance_tonnes=variance_tonnes,
            variance_pct=variance_pct,
            notes=harvest_in.notes
        )
        db.add(db_harvest)
        db.commit()
        db.refresh(db_harvest)
        return db_harvest
    except Exception:
        db.rollback()
        raise


def list_harvest_results(db: Session, farm_id: Optional[int] = None, limit: int = 100) -> List[HarvestResult]:
    """Lists harvest outcomes ordered by date."""
    query = db.query(HarvestResult)
    if farm_id is not None:
        query = query.filter(HarvestResult.farm_id == farm_id)
    return query.order_by(desc(HarvestResult.created_at)).limit(limit).all()


# ==============================================================================
# Recommendation Records Operations
# ==============================================================================

def create_recommendation_records(
    db: Session,
    recs_in: List[RecommendationRecordCreate]
) -> List[RecommendationRecord]:
    """Persists a batch of recommendations linked to a prediction or farm."""
    try:
        created_items: List[RecommendationRecord] = []
        for r in recs_in:
            cond_json = json.dumps(r.conditions_triggered) if r.conditions_triggered else None
            db_item = RecommendationRecord(
                prediction_id=r.prediction_id,
                farm_id=r.farm_id,
                district=r.district,
                season=r.season,
                growth_stage=r.growth_stage,
                category=r.category,
                title=r.title,
                action=r.action,
                reason=r.reason,
                urgency=r.urgency,
                warnings=r.warnings,
                conditions_triggered=cond_json
            )
            db.add(db_item)
            created_items.append(db_item)

        db.commit()
        for item in created_items:
            db.refresh(item)
        return created_items
    except Exception:
        db.rollback()
        raise


def list_recommendation_records(
    db: Session,
    prediction_id: Optional[int] = None,
    limit: int = 100
) -> List[RecommendationRecord]:
    """Lists saved recommendations."""
    query = db.query(RecommendationRecord)
    if prediction_id is not None:
        query = query.filter(RecommendationRecord.prediction_id == prediction_id)
    return query.order_by(desc(RecommendationRecord.created_at)).limit(limit).all()
