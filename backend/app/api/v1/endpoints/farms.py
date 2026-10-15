"""
AgriSense-AI: Farm Profile & Field Management Endpoints.
Provides CRUD capabilities for farmer holdings, soil baselines, and plot details.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....db import crud
from ....schemas.database import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
    FarmDetailResponse,
    FieldDetailCreate,
    FieldDetailResponse
)

router = APIRouter()


@router.post(
    "/",
    response_model=FarmDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new farm profile",
    description="Registers a farmer holding with location, total area, and optional initial field details."
)
def create_farm_profile(
    payload: FarmCreate,
    db: Session = Depends(get_db)
) -> FarmDetailResponse:
    """Creates a new farm profile with fields in a single transaction."""
    try:
        farm = crud.create_farm(db, payload)
        return farm
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create farm profile: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[FarmDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List farm profiles",
    description="Retrieves registered farm profiles with their fields and optional district filtering."
)
def list_farm_profiles(
    district: Optional[str] = Query(None, description="Filter by district"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[FarmDetailResponse]:
    """Lists registered farm profiles."""
    return crud.list_farms(db, district=district, limit=limit, offset=offset)


@router.get(
    "/{farm_id}",
    response_model=FarmDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get farm profile details",
    description="Retrieves a specific farm profile by ID including all child field plots."
)
def get_farm_profile(
    farm_id: int,
    db: Session = Depends(get_db)
) -> FarmDetailResponse:
    """Fetches a single farm profile."""
    farm = crud.get_farm(db, farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm profile with ID {farm_id} not found."
        )
    return farm


@router.put(
    "/{farm_id}",
    response_model=FarmDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update farm profile",
    description="Updates non-primary fields of an existing farm profile."
)
def update_farm_profile(
    farm_id: int,
    payload: FarmUpdate,
    db: Session = Depends(get_db)
) -> FarmDetailResponse:
    """Updates farm details."""
    farm = crud.update_farm(db, farm_id, payload)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm profile with ID {farm_id} not found."
        )
    return farm


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete farm profile",
    description="Deletes a farm profile and cascades deletion to all associated fields."
)
def delete_farm_profile(
    farm_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Deletes a farm profile."""
    success = crud.delete_farm(db, farm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm profile with ID {farm_id} not found."
        )
    return {"success": True, "message": f"Farm {farm_id} deleted successfully."}


@router.post(
    "/{farm_id}/fields",
    response_model=FieldDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add field plot to farm",
    description="Adds a new field plot to an existing farm."
)
def add_field_to_farm(
    farm_id: int,
    payload: FieldDetailCreate,
    db: Session = Depends(get_db)
) -> FieldDetailResponse:
    """Appends a field plot to a farm."""
    farm = crud.get_farm(db, farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm profile with ID {farm_id} not found."
        )
    try:
        field = crud.create_field(db, farm_id, payload)
        return field
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add field: {str(e)}"
        )
