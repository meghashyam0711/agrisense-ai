"""
AgriSense-AI: Prediction History & Harvest Audit Endpoints.
Provides SQLite-backed persistence for yield predictions, recommendations,
and actual harvest validation outcomes.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....db import crud
from ....schemas.database import (
    PredictionRecordCreate,
    PredictionRecordResponse,
    HarvestResultCreate,
    HarvestResultResponse,
    RecommendationRecordCreate,
    RecommendationRecordResponse
)

router = APIRouter()


@router.get(
    "/logs",
    response_model=List[PredictionRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="List past prediction queries",
    description="Fetches historical crop yield predictions from SQLite with optional district and season filters."
)
def list_prediction_history(
    district: Optional[str] = Query(None, description="Filter by Tamil Nadu district"),
    season: Optional[str] = Query(None, description="Filter by cropping season"),
    farm_id: Optional[int] = Query(None, description="Filter by farm ID"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
) -> List[PredictionRecordResponse]:
    """Retrieves paginated prediction audit records."""
    records = crud.list_prediction_records(
        db=db,
        district=district,
        season=season,
        farm_id=farm_id,
        limit=limit,
        offset=offset
    )
    return records


@router.post(
    "/predictions",
    response_model=PredictionRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a prediction record",
    description="Saves a crop yield inference outcome and input parameters to SQLite."
)
def save_prediction_record(
    payload: PredictionRecordCreate,
    db: Session = Depends(get_db)
) -> PredictionRecordResponse:
    """Creates a new historical prediction log entry."""
    try:
        record = crud.create_prediction_record(db, payload)
        return record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to persist prediction record: {str(e)}"
        )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prediction details",
    description="Retrieves a specific prediction record by ID, including any associated harvest results and recommendations."
)
def get_prediction_record(
    prediction_id: int,
    db: Session = Depends(get_db)
) -> PredictionRecordResponse:
    """Fetches a single prediction record with nested associations."""
    record = crud.get_prediction_record(db, prediction_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction record with ID {prediction_id} not found."
        )
    return record


@router.post(
    "/harvest",
    response_model=HarvestResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record actual harvest outcome",
    description="Records ground-truth harvest yield, automatically calculating variance against predicted yield if linked."
)
def record_actual_harvest(
    payload: HarvestResultCreate,
    db: Session = Depends(get_db)
) -> HarvestResultResponse:
    """Records real-world harvest yield for post-season accuracy audits."""
    try:
        harvest_entry = crud.create_harvest_result(db, payload)
        return harvest_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record harvest outcome: {str(e)}"
        )


@router.get(
    "/harvest",
    response_model=List[HarvestResultResponse],
    status_code=status.HTTP_200_OK,
    summary="List actual harvest records",
    description="Retrieves recorded ground-truth harvest results with variance analyses."
)
def list_harvest_history(
    farm_id: Optional[int] = Query(None, description="Filter by farm ID"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[HarvestResultResponse]:
    """Lists actual harvest results."""
    return crud.list_harvest_results(db, farm_id=farm_id, limit=limit)


@router.post(
    "/recommendations",
    response_model=List[RecommendationRecordResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Save recommendation items",
    description="Persists generated agronomic recommendations into SQLite for audit tracking."
)
def save_recommendations_batch(
    payload: List[RecommendationRecordCreate],
    db: Session = Depends(get_db)
) -> List[RecommendationRecordResponse]:
    """Persists a batch of agronomic recommendations."""
    try:
        recs = crud.create_recommendation_records(db, payload)
        return recs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save recommendation records: {str(e)}"
        )


@router.get(
    "/recommendations",
    response_model=List[RecommendationRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="List saved recommendations",
    description="Retrieves saved recommendation records."
)
def list_recommendations_history(
    prediction_id: Optional[int] = Query(None, description="Filter by prediction ID"),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
) -> List[RecommendationRecordResponse]:
    """Lists saved recommendations."""
    return crud.list_recommendation_records(db, prediction_id=prediction_id, limit=limit)
