"""
Core configuration module utilizing pydantic-settings.
Reads from environment variables and provides typed settings across the application.
"""

import os
import sys
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving project-level paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def resolve_model_path(relative_path: str) -> str:
    """Resolves model path regardless of whether CWD is root or backend/."""
    candidates = [
        relative_path,
        os.path.join("..", relative_path),
        str(PROJECT_ROOT / relative_path),
        str(PROJECT_ROOT / relative_path.lstrip("./"))
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.abspath(str(PROJECT_ROOT / relative_path.lstrip("./")))

class Settings(BaseSettings):
    APP_NAME: str = "AgriSense-AI Paddy Yield Prediction API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Origins (Explicit whitelist for security)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./data/agri_crop.db"

    # ML Artifacts (Dynamically resolved)
    MODEL_PATH: str = resolve_model_path("ml/saved_models/rf_paddy_yield_model.joblib")
    FEATURE_COLUMNS_PATH: str = resolve_model_path("ml/saved_models/feature_metadata.json")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
