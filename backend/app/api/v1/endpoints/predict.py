"""
AgriSense-AI: Prediction API Endpoints.
Handles yield prediction requests using the loaded Random Forest model.
"""

from fastapi import APIRouter, HTTPException, status
from ....schemas.prediction import PredictionRequest, PredictionResponse
from ....services.ml_service import ml_service

router = APIRouter()

@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict paddy crop yield in tonnes per hectare",
    description="Validates farm inputs (rainfall, temp, humidity, soil pH, moisture, NPK, previous yield) and returns predicted yield."
)
async def predict_crop_yield(payload: PredictionRequest) -> PredictionResponse:
    """
    Inference endpoint returning expected harvest yield with 90% confidence bounds.
    """
    if not ml_service.is_healthy():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Paddy crop yield model is not available or failed to load. Check service health."
        )

    try:
        response = ml_service.predict_yield(payload)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during crop yield prediction calculation."
        )
