"""
AgriSense-AI: Open-Meteo Weather Service Integration.
Fetches live and forecast agro-meteorological indicators with in-memory TTL caching,
request timeouts, WMO code interpretation, and network resilience.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple, List
import httpx
from fastapi import HTTPException, status

from ..core.config import settings
from ..schemas.weather import (
    CurrentWeatherResponse,
    DailyForecastItem,
    ForecastWeatherResponse
)

logger = logging.getLogger("agrisense.weather_service")

# WMO Weather Interpretation Code Mapping (World Meteorological Organization standards)
WMO_CODE_MAP: Dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def get_wmo_description(code: int) -> str:
    """Returns human-readable description for WMO weather interpretation code."""
    return WMO_CODE_MAP.get(code, f"Weather Code {code}")


class OpenMeteoWeatherService:
    """
    Asynchronous client for Open-Meteo Weather API.
    Includes in-memory TTL caching (15 mins) and strict timeout configurations.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    CACHE_TTL_SECONDS = 900  # 15 minutes cache

    def __init__(self, timeout_seconds: Optional[int] = None):
        self.timeout = timeout_seconds or getattr(settings, "WEATHER_API_TIMEOUT_SECONDS", 5)
        # In-memory cache: (cache_type, lat, lon, days) -> (timestamp, data_dict)
        self._cache: Dict[Tuple[str, float, float, int], Tuple[float, Any]] = {}

    def clear_cache(self) -> None:
        """Utility to clear cached entries (useful for testing)."""
        self._cache.clear()

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        location: Optional[str] = None
    ) -> CurrentWeatherResponse:
        """
        Retrieves current weather observation for the given coordinates.
        Uses cached response if request was made within CACHE_TTL_SECONDS.
        """
        cache_key = ("current", round(latitude, 3), round(longitude, 3), 0)
        now = time.time()

        if cache_key in self._cache:
            timestamp, cached_res = self._cache[cache_key]
            if now - timestamp < self.CACHE_TTL_SECONDS:
                # Return cached copy with cached=True
                res_dict = cached_res.model_dump()
                res_dict["cached"] = True
                if location and not res_dict.get("location"):
                    res_dict["location"] = location
                return CurrentWeatherResponse(**res_dict)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "Asia/Kolkata"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.BASE_URL, params=params)
        except httpx.TimeoutException:
            logger.error(f"Open-Meteo request timed out after {self.timeout}s for lat={latitude}, lon={longitude}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Weather service upstream request timed out. Please try again later."
            )
        except httpx.RequestError as exc:
            logger.error(f"Open-Meteo connection error: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to communicate with external weather service. Check network connectivity."
            )

        if response.status_code != 200:
            logger.error(f"Open-Meteo error response {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Weather service responded with error code {response.status_code}."
            )

        data = response.json()
        current_data = data.get("current", {})

        weather_code = int(current_data.get("weather_code", 0))
        result = CurrentWeatherResponse(
            location=location,
            latitude=float(data.get("latitude", latitude)),
            longitude=float(data.get("longitude", longitude)),
            temperature_c=float(current_data.get("temperature_2m", 0.0)),
            relative_humidity_pct=float(current_data.get("relative_humidity_2m", 0.0)),
            precipitation_mm=float(current_data.get("precipitation", 0.0)),
            wind_speed_kmh=float(current_data.get("wind_speed_10m", 0.0)),
            weather_code=weather_code,
            weather_condition=get_wmo_description(weather_code),
            observation_time=str(current_data.get("time", "")),
            provider="Open-Meteo",
            cached=False
        )

        # Store in cache
        self._cache[cache_key] = (now, result)
        return result

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        location: Optional[str] = None,
        forecast_days: int = 5
    ) -> ForecastWeatherResponse:
        """
        Retrieves daily agricultural weather forecast (default 5 days).
        """
        days = min(max(forecast_days, 1), 7)
        cache_key = ("forecast", round(latitude, 3), round(longitude, 3), days)
        now = time.time()

        if cache_key in self._cache:
            timestamp, cached_res = self._cache[cache_key]
            if now - timestamp < self.CACHE_TTL_SECONDS:
                res_dict = cached_res.model_dump()
                res_dict["cached"] = True
                if location and not res_dict.get("location"):
                    res_dict["location"] = location
                return ForecastWeatherResponse(**res_dict)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code",
            "forecast_days": days,
            "timezone": "Asia/Kolkata"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.BASE_URL, params=params)
        except httpx.TimeoutException:
            logger.error(f"Open-Meteo forecast timed out after {self.timeout}s")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Weather forecast service request timed out."
            )
        except httpx.RequestError as exc:
            logger.error(f"Open-Meteo connection error: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to connect to external forecast service."
            )

        if response.status_code != 200:
            logger.error(f"Open-Meteo forecast error {response.status_code}: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Forecast service responded with error code {response.status_code}."
            )

        data = response.json()
        daily = data.get("daily", {})
        dates = daily.get("time", [])

        forecast_items: List[DailyForecastItem] = []
        for i, d in enumerate(dates):
            w_code = int(daily.get("weather_code", [0])[i])
            prob = daily.get("precipitation_probability_max", [None])[i]
            item = DailyForecastItem(
                date=d,
                temperature_max_c=float(daily.get("temperature_2m_max", [0.0])[i]),
                temperature_min_c=float(daily.get("temperature_2m_min", [0.0])[i]),
                precipitation_sum_mm=float(daily.get("precipitation_sum", [0.0])[i]),
                precipitation_probability_pct=int(prob) if prob is not None else None,
                wind_speed_max_kmh=float(daily.get("wind_speed_10m_max", [0.0])[i]),
                weather_code=w_code,
                weather_condition=get_wmo_description(w_code)
            )
            forecast_items.append(item)

        result = ForecastWeatherResponse(
            location=location,
            latitude=float(data.get("latitude", latitude)),
            longitude=float(data.get("longitude", longitude)),
            timezone=str(data.get("timezone", "Asia/Kolkata")),
            elevation=float(data.get("elevation", 0.0)) if "elevation" in data else None,
            forecast_days=len(forecast_items),
            daily_forecast=forecast_items,
            provider="Open-Meteo",
            cached=False
        )

        self._cache[cache_key] = (now, result)
        return result


# Module singleton instance
weather_service = OpenMeteoWeatherService()
