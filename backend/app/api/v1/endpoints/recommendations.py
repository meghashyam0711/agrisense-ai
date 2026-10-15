"""
AgriSense-AI: Smart Farming Recommendations Endpoint.
Provides rule-based agronomic guidance for irrigation, nutrient balance,
soil health amendments, and pest monitoring based on TNAU standards.
Integrates live weather forecast data when environmental metrics are missing.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status

from ....schemas.recommendations import (
    RecommendationRequest,
    RecommendationsResponse
)
from ....services.recommendation_engine import recommendation_engine
from ....services.weather_service import weather_service
from .weather import DISTRICT_COORDINATES

logger = logging.getLogger("agrisense.recommendations")

router = APIRouter()


async def enrich_with_weather_if_needed(payload: RecommendationRequest) -> tuple[RecommendationRequest, Optional[str]]:
    """
    Enriches missing environmental parameters with live Open-Meteo weather data
    for the specified Tamil Nadu district. Fails gracefully if offline or unavailable.
    """
    missing_temp = payload.temperature_c is None
    missing_hum = payload.humidity_pct is None
    missing_rain = payload.forecast_rain_expected_mm is None or payload.forecast_rain_prob_pct is None

    # If all environmental parameters are already provided by the client, no lookup needed
    if not (missing_temp or missing_hum or missing_rain):
        return payload, None

    coords = DISTRICT_COORDINATES.get(payload.district)
    if not coords:
        return payload, f"District '{payload.district}' coordinates not in lookup table; using regional defaults."

    updates: Dict[str, Any] = {}
    weather_note: Optional[str] = None

    try:
        # Fetch current conditions if temperature or humidity is missing
        if missing_temp or missing_hum:
            current_weather = await weather_service.get_current_weather(
                latitude=coords["lat"],
                longitude=coords["lon"],
                location=payload.district
            )
            if missing_temp and current_weather.temperature_c is not None:
                updates["temperature_c"] = max(15.0, min(48.0, current_weather.temperature_c))
            if missing_hum and current_weather.relative_humidity_pct is not None:
                updates["humidity_pct"] = max(20.0, min(100.0, current_weather.relative_humidity_pct))

        # Fetch short-term forecast if rain expectation is missing
        if missing_rain:
            forecast_weather = await weather_service.get_forecast(
                latitude=coords["lat"],
                longitude=coords["lon"],
                location=payload.district,
                forecast_days=3
            )
            if forecast_weather.daily_forecast:
                # Aggregate next 48-72h
                rain_sum = sum(d.precipitation_sum_mm for d in forecast_weather.daily_forecast[:3])
                max_prob = max((d.precipitation_probability_pct or 0) for d in forecast_weather.daily_forecast[:3])
                if payload.forecast_rain_expected_mm is None:
                    updates["forecast_rain_expected_mm"] = max(0.0, min(500.0, rain_sum))
                if payload.forecast_rain_prob_pct is None:
                    updates["forecast_rain_prob_pct"] = max(0, min(100, max_prob))

        if updates:
            weather_note = (
                f"Live weather data integrated for {payload.district} from Open-Meteo: "
                + ", ".join(f"{k}={v}" for k, v in updates.items())
            )
            return payload.model_copy(update=updates), weather_note

    except Exception as e:
        logger.warning(f"Could not enrich weather for {payload.district}: {e}")
        weather_note = (
            f"Live weather lookup for {payload.district} was unavailable ({type(e).__name__}); "
            "recommendations generated using available soil and stage metrics."
        )

    return payload, weather_note


@router.post(
    "/",
    response_model=RecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Smart Farming Recommendations",
    description=(
        "Generates rule-based agronomic recommendations for irrigation (AWD), "
        "fertilizer split dosages, soil health amendments, and pest monitoring alerts "
        "grounded in verified TNAU standards. Distinguishes expert system logic from ML predictions."
    )
)
async def generate_recommendations(payload: RecommendationRequest) -> RecommendationsResponse:
    """
    Main recommendation endpoint. Enriches environmental parameters with live weather
    if missing, validates crop stages, and executes the TNAU agronomic rule engine.
    """
    try:
        enriched_payload, weather_note = await enrich_with_weather_if_needed(payload)
        response = recommendation_engine.generate_recommendations(enriched_payload)
        if weather_note:
            response.data_limitations.append(weather_note)
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as exc:
        logger.error(f"Error generating recommendations: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating agronomic recommendations."
        )
