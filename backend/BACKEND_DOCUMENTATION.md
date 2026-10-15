# AgriSense-AI: Backend REST API Documentation

## 1. Overview & Architecture

The **AgriSense-AI Backend** is built using **Python and FastAPI**. It exposes a high-performance REST API for predicting Tamil Nadu paddy crop yield in **tonnes per hectare** using the pre-trained Scikit-Learn Random Forest Regressor developed in Phase 4.

### Key Architectural Highlights
- **Single-Load Lifecycle:** The Random Forest model bundle (`rf_paddy_yield_model.joblib`), preprocessor (`preprocessor.joblib`), and metadata are loaded **once at startup** via FastAPI's `lifespan` context manager.
- **Strict Input Validation:** Powered by Pydantic v2 schemas validating physical agronomic boundaries (e.g., pH 4.0–9.5, rainfall 100–3,500 mm).
- **Graceful Error Handling:** If model artifacts are missing or fail to load, the service continues running and returns `503 Service Unavailable` on inference requests rather than crashing.
- **CORS Whitelist:** Explicitly restricted to trusted frontend development origins (`http://localhost:3000`, `http://127.0.0.1:3000`, `http://127.0.0.1:5500`, `http://localhost:8000`).

---

## 2. API Endpoints Specification

### 2.1 `GET /` — API Status
Returns root service status, application name, version, and documentation link.

**Response (200 OK):**
```json
{
  "name": "AgriSense-AI Paddy Yield Prediction API",
  "status": "operational",
  "version": "1.0.0",
  "description": "FastAPI service for Tamil Nadu Paddy Crop Yield Prediction",
  "docs_url": "/docs"
}
```

---

### 2.2 `GET /health` — Service and Model Health
Checks service uptime and verifies whether the machine learning model is in memory and ready to serve inference.

**Response (200 OK — Model Ready):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-10-15T12:26:00.570111+00:00"
}
```

**Response (200 OK — Model Unloaded/Missing):**
```json
{
  "status": "degraded",
  "model_loaded": false,
  "model_version": null,
  "environment": "development",
  "timestamp": "2026-10-15T12:26:00.570111+00:00"
}
```

---

### 2.3 `POST /predict` — Paddy Crop Yield Prediction
Accepts soil chemistry, environmental parameters, location, and season, and executes Random Forest inference.

**Request Payload:**
```json
{
  "district": "Thanjavur",
  "season": "Samba",
  "soil_type": "Alluvial",
  "rainfall_mm": 1150.0,
  "temperature_c": 29.5,
  "humidity_pct": 82.0,
  "soil_ph": 6.8,
  "soil_moisture_pct": 76.0,
  "nitrogen_kg_ha": 140.0,
  "phosphorus_kg_ha": 48.0,
  "potassium_kg_ha": 45.0,
  "previous_yield_tonnes_per_hectare": 4.5,
  "area_hectares": 2.5
}
```
*Note: Supports field aliases: `nitrogen` -> `nitrogen_kg_ha`, `ph` -> `soil_ph`, `moisture` -> `soil_moisture_pct`, `previous_yield` -> `previous_yield_tonnes_per_hectare`.*

**Response (200 OK):**
```json
{
  "success": true,
  "crop": "Paddy (Oryza sativa)",
  "district": "Thanjavur",
  "season": "Samba",
  "soil_type": "Alluvial",
  "predicted_yield_tonnes_per_hectare": 5.16,
  "predicted_yield_quintals_per_hectare": 51.6,
  "predicted_yield_kg_per_hectare": 5163.0,
  "confidence_interval_90": {
    "lower_tonnes_ha": 4.92,
    "upper_tonnes_ha": 5.41,
    "lower_quintals_ha": 49.2,
    "upper_quintals_ha": 54.1
  },
  "total_estimated_production_tonnes": 12.9,
  "total_estimated_production_quintals": 129.0,
  "tnau_potential_realization_pct": 99.2,
  "model_version": "1.0.0",
  "disclaimer": "DEMONSTRATION MODEL ONLY: Trained on synthetic proxy data informed by TNAU guidelines. Not validated for commercial agricultural investment decisions."
}
```

**Error Responses:**
- `422 Unprocessable Entity`: Input validation failure (missing fields, out-of-range pH/rainfall, invalid district).
- `503 Service Unavailable`: ML model artifact is missing or not loaded.

---

### 2.4 `GET /model-info` — Model Metadata & Limitations
Returns evaluation metrics, feature rankings, and model boundaries without exposing internal file paths.

**Response (200 OK):**
```json
{
  "model_name": "AgriSense Random Forest Paddy Yield Regressor",
  "version": "1.0.0",
  "target_variable": "yield_tonnes_per_hectare",
  "target_unit": "tonnes_per_hectare",
  "created_at": "2026-10-15T12:12:41.469545Z",
  "features_count": 35,
  "feature_columns": ["rainfall_mm", "temperature_c", "humidity_pct", "..."],
  "top_10_feature_importances": {
    "season_Navarai": 0.2235,
    "rainfall_mm": 0.1492,
    "season_Samba": 0.1413,
    "rainfall_temp_ratio": 0.1040,
    "previous_yield_tonnes_per_hectare": 0.0904
  },
  "evaluation_metrics": {
    "random_forest": {
      "test_mae": 0.1536,
      "test_rmse": 0.1933,
      "test_r2": 0.8751,
      "cv_5fold_r2_mean": 0.8609
    }
  },
  "disclaimer": "DEMONSTRATION MODEL ONLY: Trained on synthetic proxy data informed by TNAU guidelines. Not validated for commercial agricultural investment decisions."
}
```

---

## 3. Running & Testing

### 3.1 Start the API Server
```powershell
# From project root
python -m uvicorn main:app --port 8000 --app-dir backend --reload
```
Interactive Swagger UI: `http://localhost:8000/docs`

### 3.2 Run Automated Tests
```powershell
# Run backend API test suite (10 tests)
python -m pytest backend/tests

# Run all test suites across the project (21 tests)
python -m pytest
```
