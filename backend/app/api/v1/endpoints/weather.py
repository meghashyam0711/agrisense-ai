"""
AgriSense-AI: Weather API Endpoints.
Connects FastAPI to Open-Meteo client with district resolution and coordinate validation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from ....schemas.weather import CurrentWeatherResponse, ForecastWeatherResponse
from ....services.weather_service import weather_service

router = APIRouter()

# Coordinates mapping for Tamil Nadu districts
DISTRICT_COORDINATES = {
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "Tiruvarur": {"lat": 10.7725, "lon": 79.6365},
    "Nagapattinam": {"lat": 10.7672, "lon": 79.8449},
    "Mayiladuthurai": {"lat": 11.1075, "lon": 79.6524},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714},
    "Villupuram": {"lat": 11.9401, "lon": 79.4861},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Kancheepuram": {"lat": 12.8342, "lon": 79.7036},
    "Thiruvallur": {"lat": 13.1432, "lon": 79.9083},
    "Erode": {"lat": 11.3410, "lon": 77.7172},
}

def resolve_coords(
    lat: Optional[float],
    lon: Optional[float],
    district: Optional[str]
) -> tuple[float, float, str]:
    if lat is not None and lon is not None:
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Coordinates out of valid geographical bounds (lat [-90, 90], lon [-180, 180])."
            )
        loc_name = district or f"Lat: {lat:.2f}, Lon: {lon:.2f}"
        return lat, lon, loc_name

    if district:
        # Match case-insensitive
        match_key = next((k for k in DISTRICT_COORDINATES if k.lower() == district.strip().lower()), None)
        if match_key:
            return DISTRICT_COORDINATES[match_key]["lat"], DISTRICT_COORDINATES[match_key]["lon"], match_key
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown Tamil Nadu district '{district}'. Please provide latitude/longitude or a valid district name."
        )

    # Default to Thanjavur (Cauvery Delta center) if nothing provided
    return 10.7870, 79.1378, "Thanjavur"


@router.get(
    "/current",
    response_model=CurrentWeatherResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current weather",
    description="Retrieves current meteorological observation via Open-Meteo for coordinates or district."
)
async def get_current_weather(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude in decimal degrees"),
    district: Optional[str] = Query(None, description="Tamil Nadu district name (e.g. Thanjavur, Tiruvarur)")
) -> CurrentWeatherResponse:
    lat, lon, loc = resolve_coords(latitude, longitude, district)
    return await weather_service.get_current_weather(latitude=lat, longitude=lon, location=loc)


@router.get(
    "/forecast",
    response_model=ForecastWeatherResponse,
    status_code=status.HTTP_200_OK,
    summary="Get short-term agricultural forecast",
    description="Retrieves 5-day daily agricultural forecast (temperatures, precipitation, rain probability) via Open-Meteo."
)
async def get_weather_forecast(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Longitude in decimal degrees"),
    district: Optional[str] = Query(None, description="Tamil Nadu district name (e.g. Thanjavur)"),
    days: int = Query(5, ge=1, le=7, description="Number of forecast days (1-7)")
) -> ForecastWeatherResponse:
    lat, lon, loc = resolve_coords(latitude, longitude, district)
    return await weather_service.get_forecast(latitude=lat, longitude=lon, location=loc, forecast_days=days)
