"""
AgriSense-AI: Weather API Request and Response Schemas.
Defines contracts for Open-Meteo current observations and short-term forecasts.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class WeatherCoordinatesQuery(BaseModel):
    """Query parameters with coordinate validation."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees", examples=[10.7870])
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees", examples=[79.1378])
    location: Optional[str] = Field(None, description="Optional name of location or district", examples=["Thanjavur"])

class CurrentWeatherResponse(BaseModel):
    """Normalized response schema for current meteorological conditions."""
    location: Optional[str] = Field(None, description="District or location name", examples=["Thanjavur"])
    latitude: float = Field(..., description="Latitude coordinate", examples=[10.7870])
    longitude: float = Field(..., description="Longitude coordinate", examples=[79.1378])
    temperature_c: float = Field(..., description="Current temperature in Celsius", examples=[31.5])
    relative_humidity_pct: float = Field(..., description="Relative humidity percentage", examples=[78.0])
    precipitation_mm: float = Field(..., description="Precipitation in mm during the past hour", examples=[0.0])
    wind_speed_kmh: float = Field(..., description="Wind speed in km/h", examples=[14.2])
    weather_code: int = Field(..., description="WMO weather interpretation code", examples=[1])
    weather_condition: str = Field(..., description="Human-readable condition description", examples=["Mainly Clear"])
    observation_time: str = Field(..., description="ISO observation timestamp", examples=["2026-10-15T12:00"])
    provider: str = Field("Open-Meteo", description="Data provider name")
    cached: bool = Field(False, description="Whether response was served from cache")
    disclaimer: str = Field(
        "Current meteorological observation. Not a substitute for seasonal cumulative rainfall in crop yield models.",
        description="Agronomic usage disclaimer"
    )

class DailyForecastItem(BaseModel):
    """Daily forecast metrics for agricultural planning."""
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)", examples=["2026-10-16"])
    temperature_max_c: float = Field(..., description="Maximum temperature in °C", examples=[33.2])
    temperature_min_c: float = Field(..., description="Minimum temperature in °C", examples=[24.5])
    precipitation_sum_mm: float = Field(..., description="Total expected precipitation in mm", examples=[4.5])
    precipitation_probability_pct: Optional[int] = Field(None, description="Maximum precipitation probability %", examples=[65])
    wind_speed_max_kmh: float = Field(..., description="Peak wind speed in km/h", examples=[18.0])
    weather_code: int = Field(..., description="WMO weather interpretation code", examples=[61])
    weather_condition: str = Field(..., description="Condition description", examples=["Slight Rain"])

class ForecastWeatherResponse(BaseModel):
    """Short-term multi-day forecast response schema."""
    location: Optional[str] = Field(None, description="District or location name", examples=["Thanjavur"])
    latitude: float = Field(..., description="Latitude coordinate", examples=[10.7870])
    longitude: float = Field(..., description="Longitude coordinate", examples=[79.1378])
    timezone: str = Field("Asia/Kolkata", description="Timezone of forecast")
    elevation: Optional[float] = Field(None, description="Elevation above sea level in meters")
    forecast_days: int = Field(..., description="Number of forecast days returned", examples=[5])
    daily_forecast: List[DailyForecastItem] = Field(..., description="List of daily forecast projections")
    provider: str = Field("Open-Meteo", description="Data provider name")
    cached: bool = Field(False, description="Whether response was served from cache")
    disclaimer: str = Field(
        "Short-term meteorological forecast. Subject to atmospheric uncertainty beyond 72 hours.",
        description="Forecast disclaimer"
    )
