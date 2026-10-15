"""
API v1 Router Aggregator.
Consolidates endpoints for prediction, weather, and history.
"""

from fastapi import APIRouter
from .endpoints import predict, weather, history, recommendations, farms, i18n

api_router = APIRouter()
api_router.include_router(predict.router, prefix="/crop", tags=["Crop Yield & Optimization"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Integration"])
api_router.include_router(history.router, prefix="/history", tags=["History & Logs"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Smart Farming Recommendations"])
api_router.include_router(farms.router, prefix="/farms", tags=["Farm Profiles & Field Details"])
api_router.include_router(i18n.router, prefix="/i18n", tags=["Bilingual Localization (i18n)"])



