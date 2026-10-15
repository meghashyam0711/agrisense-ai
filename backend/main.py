"""
AgriSense-AI: FastAPI Application Server.
Exposes root status, health check, prediction inference, and model metadata endpoints.
Loads Scikit-Learn model once at startup and configures CORS.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.ml_service import ml_service
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.model_info import RootResponse, HealthResponse, ModelInfoResponse
from app.schemas.recommendations import RecommendationRequest, RecommendationsResponse
from app.api.v1.endpoints.recommendations import generate_recommendations
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager: Initializes SQLite database schema,
    loads machine learning model bundle once at startup, and manages graceful shutdown.
    """
    print("[*] Server starting up: Initializing SQLite database schema...")
    init_db()
    print("[+] Database schema ready.")

    print("[*] Initializing ML model service...")
    ml_service.load_model()
    if ml_service.is_healthy():
        print(f"[+] Model loaded successfully. Target: {settings.MODEL_PATH}")
    else:
        print(f"[!] Warning: Model loading failed: {ml_service.load_error}")
    yield
    print("[*] Server shutting down.")



def create_application() -> FastAPI:
    """Application factory for AgriSense-AI FastAPI backend."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="AI-powered crop yield prediction platform for paddy farming in Tamil Nadu",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # 1. CORS Configuration (Strict Whitelist)
    origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


    # 2. Custom Validation Error Handler for consistent JSON responses
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_details = []
        for error in exc.errors():
            loc = " -> ".join([str(l) for l in error.get("loc", [])])
            msg = error.get("msg", "Invalid input")
            error_details.append(f"{loc}: {msg}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation Error",
                "details": error_details
            }
        )

    # 3. Core Root Endpoints
    @app.get(
        "/",
        response_model=RootResponse,
        status_code=status.HTTP_200_OK,
        tags=["API Status"],
        summary="API Service Status"
    )
    async def get_root_status():
        """Returns API status, version, and documentation availability."""
        return RootResponse(
            name=settings.APP_NAME,
            status="operational",
            version="1.0.0",
            description="FastAPI service for Tamil Nadu Paddy Crop Yield Prediction",
            docs_url="/docs" if settings.DEBUG else None
        )

    @app.get(
        "/health",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
        tags=["Health Check"],
        summary="Service and Model Health"
    )
    async def get_health_status():
        """Returns service uptime and model readiness."""
        is_model_ready = ml_service.is_healthy()
        return HealthResponse(
            status="healthy" if is_model_ready else "degraded",
            model_loaded=is_model_ready,
            model_version=ml_service.predictor.metadata.get("version", "1.0.0") if is_model_ready else None,
            environment=settings.APP_ENV,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    @app.post(
        "/predict",
        response_model=PredictionResponse,
        status_code=status.HTTP_200_OK,
        tags=["Crop Yield Prediction"],
        summary="Predict Paddy Yield (tonnes/ha)",
        description="Accepts farm, soil chemistry, and weather parameters and returns Random Forest yield predictions in tonnes/ha, quintals/ha, and kg/ha."
    )
    async def predict_yield(payload: PredictionRequest) -> PredictionResponse:
        """Inference endpoint using the loaded Random Forest model."""
        if not ml_service.is_healthy():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Paddy yield prediction model is unavailable: {ml_service.load_error or 'Not loaded.'}"
            )

        try:
            return ml_service.predict_yield(payload)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal calculation error occurred while computing the prediction."
            )

    @app.get(
        "/model-info",
        response_model=ModelInfoResponse,
        status_code=status.HTTP_200_OK,
        tags=["Model Information"],
        summary="Trained Model Metadata and Limitations"
    )
    async def get_model_information():
        """Returns model version, feature dimensions, evaluation metrics, and disclaimer."""
        if not ml_service.is_healthy():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model information is unavailable because the model is not loaded."
            )
        return ml_service.get_model_info()

    @app.post(
        "/recommendations",
        response_model=RecommendationsResponse,
        status_code=status.HTTP_200_OK,
        tags=["Smart Farming Recommendations"],
        summary="Generate Smart Farming Recommendations",
        description="Generates explainable, rule-based agronomic recommendations for irrigation, fertilizer, soil health, and pest management based on TNAU guidelines."
    )
    async def get_smart_recommendations(payload: RecommendationRequest) -> RecommendationsResponse:
        """Endpoint generating stage-aware, rule-based agronomic advice with weather enrichment."""
        return await generate_recommendations(payload)

    # 4. Include v1 API Routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
