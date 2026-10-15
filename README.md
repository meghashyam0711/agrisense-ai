# Tamil Nadu AgriYield AI: Crop Yield Prediction & Optimization

An AI-driven agronomic advisory platform tailored specifically for **paddy (rice) farming in Tamil Nadu**, providing localized yield predictions, weather integration, and fertilizer optimization guidance in English and Tamil (தமிழ்).

---

## 1. Requirements & Feature Summary

### Core Capabilities
- **Target Agronomy:** Paddy (*Oryza sativa*) across Tamil Nadu's agro-climatic zones (Cauvery Delta, Northern, Southern, and Western zones) across 4 major cropping seasons: *Kuruvai*, *Samba*, *Thaladi*, and *Navarai*.
- **Machine Learning Yield Prediction:** Random Forest Regressor predicting yield (kg/ha and quintals/ha) based on district, season, soil type, N-P-K nutrient levels, pH, rainfall, temperature, and humidity.
- **Nutrient & Crop Optimization:** Actionable recommendations comparing farmer soil N-P-K values against Tamil Nadu Agricultural University (TNAU) Agritech baselines to maximize yield potential and minimize fertilizer wastage.
- **Agro-Weather Integration:** Real-time and seasonal meteorological indicators (rainfall, temperature, relative humidity) via Open-Meteo / OpenWeather API using district geospatial coordinates.
- **Multilingual User Interface:** Native bilingual support (English and Tamil) accessible via a clean, frosted **Liquid Glass UI** built using standard vanilla web technologies.
- **Persistence & Audit:** SQLite database logging farmer queries, environmental inputs, and yield estimates for historical tracking.

---

## 2. Missing Requirements, Assumptions & Technical Risks

### Missing Requirements & Unspecified Details
1. **Paddy Variety Differentiation:** Tamil Nadu cultivates diverse varieties (e.g., CR 1009, ADT 36, CO 51, BPT 5204). The baseline problem statement lacks variety-specific yield potentials and maturity durations (short, medium, long).
2. **Pest and Disease Factors:** Real-world yield variation in the Cauvery delta is heavily impacted by blast, brown planthopper, and stem borer outbreaks, which are not currently modeled in the tabular input schema.
3. **Data Freshness & Retraining Schedule:** Frequency and pipeline for updating historical district agricultural datasets.

### Working Assumptions
- **Unit Standard:** Inputs and outputs are normalized to metric standards: land in **Hectares**, yield in **kg/hectare** and **Quintals/hectare** (1 Quintal = 100 kg), nutrients in **kg/ha**.
- **Weather Availability:** When a farmer does not have immediate soil testing or localized weather data, the platform automatically retrieves current agro-meteorological metrics for the selected district as a default baseline.
- **Dataset Nature & Disclaimer:**
  > [!IMPORTANT]
  > **Agricultural Accuracy Disclaimer:** Model training utilizing synthetic or historical aggregated proxy data serves as a functional demonstration for the hackathon. It must not be claimed as certified real-world agronomic advice for actual farm crop investments without validation against ground-truth field trials and local Krishi Vigyan Kendra (KVK) consultation.

### Technical Risks & Mitigations
| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Out-of-Distribution Inputs** | Farmer enters unrealistic N-P-K or pH values leading to nonsensical yield outputs. | Strict Pydantic input validation bounds based on TNAU agronomic limits (pH 3.5–10, N 0–300 kg/ha). |
| **External Weather API Latency / Rate Limits** | Slow page response or failed API calls if weather provider is down. | Asynchronous HTTP client (`httpx`), 5s request timeouts, and client-side graceful degradation allowing manual inputs. |
| **Language Context Loss** | Inaccurate translation of agricultural terminology in Tamil. | Pre-curated static terminology dictionary (`I18N_DICTIONARY`) verified against Tamil agricultural terminology rather than dynamic machine translation. |

---

## 3. System Architecture & Component Responsibilities

```
+-------------------------------------------------------------------------------+
|                       VANILLA FRONTEND (Liquid Glass UI)                      |
|   - index.html (Semantic Structure)   - style.css (Glassmorphic Design System)|
|   - api.js (Backend Client Contract)   - i18n.js (English / Tamil Dictionary)  |
+---------------------------------------+---------------------------------------+
                                        | HTTP / JSON REST
                                        v
+-------------------------------------------------------------------------------+
|                          FASTAPI BACKEND SERVICE                              |
|   - app/api/v1/endpoints/predict.py   : Prediction & Optimization Endpoints   |
|   - app/api/v1/endpoints/weather.py   : Weather API Broker                    |
|   - app/api/v1/endpoints/history.py   : Prediction Query History              |
|   - app/core/config.py                : Environment Settings & CORS           |
|   - app/db/session.py                 : SQLite Database Engine & Session      |
+-------------------+-----------------------------------+-----------------------+
                    |                                   |
                    v                                   v
+-----------------------------------+   +---------------------------------------+
|        SQLITE DATABASE            |   |          ML INFERENCE ENGINE          |
| - PredictionLog (Inputs, Yield,   |   | - Scikit-learn Random Forest Model    |
|   Timestamp, District, Season)    |   | - Feature Scaler & Preprocessor       |
+-----------------------------------+   | - TNAU Optimization Rule Evaluator    |
                                        +---------------------------------------+
```

### Component Responsibilities
- **Frontend Layer:** Delivers a responsive, lightweight, dependency-free Liquid Glass aesthetic with bilingual toggle and input validation.
- **FastAPI Backend:** Handles routing, CORS negotiation, request payload validation via Pydantic, orchestrates ML inference, queries SQLite, and contacts external weather APIs.
- **ML Engine (`ml/`):** Manages dataset schemas, Random Forest regression training, feature encoding, model serialization (`joblib`), and metric evaluation (MAE, RMSE, R²).
- **SQLite Database:** Local, zero-configuration relational storage tracking farmer queries and audit logs.

---

## 4. Project Directory Structure

```
AGRI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py                      # API router registration
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── predict.py              # Prediction & advisory stubs
│   │   │           ├── weather.py              # District weather stubs
│   │   │           └── history.py              # Query log stubs
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py                       # App settings (Pydantic)
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── session.py                      # SQLite engine & sessionmaker
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── history.py                      # SQLAlchemy ORM schemas
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── prediction.py                   # Prediction request/response contracts
│   │   │   ├── weather.py                      # Weather request/response contracts
│   │   │   └── advisory.py                     # Optimization advisory contracts
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ml_service.py                   # ML service abstract interface
│   │       └── weather_service.py              # Weather service abstract interface
│   └── main.py                                 # FastAPI app factory & health check
├── frontend/
│   ├── css/
│   │   └── style.css                           # Liquid Glass tokens & components
│   ├── js/
│   │   ├── api.js                              # Frontend API client contract
│   │   ├── app.js                              # UI controller & i18n triggers
│   │   └── i18n.js                             # English/Tamil bilingual dictionary
│   └── index.html                              # Semantic HTML5 app skeleton
├── ml/
│   ├── data/
│   │   ├── raw/                                # Raw CSV dataset storage
│   │   └── processed/                          # Scaled and encoded datasets
│   ├── notebooks/                              # EDA & exploratory notebooks
│   ├── saved_models/                           # Trained .joblib models & metadata
│   └── src/
│       ├── __init__.py
│       ├── dataset_schema.py                   # TN paddy dataset specification
│       └── interface.py                        # ModelInterface contract
├── .env.example                                # Environment variable template
├── .gitignore                                  # Git exclusion rules
├── requirements.txt                            # Pinned Python dependencies
└── README.md                                   # Project documentation
```

---

## 5. Contract & Interface Specifications

### 5.1 API Contracts (`backend/app/schemas/`)
- **`POST /api/v1/crop/predict`**: Accepts `PredictionRequest` (district, season, soil_type, area_hectares, N, P, K, pH, rainfall_mm, temperature_c, humidity_pct) and responds with `PredictionResponse` (yield estimates in kg/ha, quintals/ha, total quintals, confidence intervals, model version).
- **`POST /api/v1/crop/optimize`**: Accepts `PredictionRequest` and returns `OptimizationAdvisoryResponse` (nutrient adjustments vs. TNAU guidelines, irrigation tips, and bilingual advice).
- **`GET /api/v1/weather/current?district={name}`**: Fetches normalized `CurrentWeatherResponse` for Tamil Nadu districts.
- **`GET /api/v1/history/logs`**: Returns recent prediction entries from SQLite.

### 5.2 Dataset Schema (`ml/src/dataset_schema.py`)
- Standardized enumerations for 12 major Tamil Nadu paddy districts (`TNDistrict`), 4 seasons (`Kuruvai`, `Samba`, `Thaladi`, `Navarai`), and 4 soil types (`Alluvial`, `Clayey`, `Red Loam`, `Coastal Saline`).
- Prescribed boundary ranges for features (N: 10–250 kg/ha, P: 5–120 kg/ha, K: 10–200 kg/ha, pH: 4.5–9.0, rainfall: 0–3000 mm).

### 5.3 ML Model Contract (`ml/src/interface.py`)
- Defines `CropYieldModelInterface` requiring `train()`, `predict()`, `save()`, and `load()` implementations.
- Standardized `EvaluationMetrics` reporting Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and $R^2$ Score.

---

## 6. Setup & Execution Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Web browser (Chrome / Edge / Firefox)

### Step 1: Clone & Configure Environment
```powershell
# Copy environment template
cp .env.example .env

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run FastAPI Backend
```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Step 4: Open Frontend
Serve the `frontend/` folder with any static web server:
```powershell
# Using Python built-in server in a new terminal:
cd frontend
python -m http.server 3000
```
Open `http://localhost:3000` in your browser.

### Step 5: One-Click Startup (Alternative)
You can launch both the FastAPI backend and frontend simultaneously with a single command:
- **Windows (Command Prompt):** Double-click or run `run.bat`
- **Windows (PowerShell):** Run `.\run.ps1`
- **Linux / macOS:** Run `./run.sh`

### Step 6: Docker Containerization
Run the full platform with Docker Compose:
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Step 7: Running Automated Tests
Run the comprehensive 60-test automated validation suite:
```bash
pytest -v
```

---

## 7. Status & Roadmap

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Requirements analysis, architecture, folder structure, contracts & interfaces | **COMPLETED** |
| **Phase 2** | AgriSense-AI Frontend (Liquid Glass UI, 6 modules, bilingual EN/Tamil, SVG charts) | **COMPLETED** |
| **Phase 3** | Agricultural Dataset Preparation (Schema, preprocessing pipeline, synthetic data & tests) | **COMPLETED** |
| **Phase 4** | ML Model Training & Evaluation (Random Forest regressor, metrics, joblib serialization) | **COMPLETED** |
| **Phase 5** | FastAPI Backend API Development (Endpoints, Pydantic schemas, single-load model, tests) | **COMPLETED** |
| **Phase 6** | Weather API Integration (Open-Meteo client, current/forecast endpoints, caching, resilience) | **COMPLETED** |
| **Phase 7** | Smart Farming Recommendations (TNAU agronomic rules, AWD, NPK splits, pest alerts, POST /recommendations) | **COMPLETED** |
| **Phase 8** | Database & Language Support (SQLite schema, history audit, harvest tracking, bilingual EN/Tamil) | **COMPLETED** |
| **Phase 9** | Frontend–Backend Integration (Full end-to-end connectivity, live ML inference, weather, history, reports) | **COMPLETED** |
| **Phase 10** | Testing, Deployment & Hackathon Demo (60/60 tests, Docker, launch scripts, [HACKATHON_DEMO_GUIDE.md](file:///d:/PROJECTS/AGRI/HACKATHON_DEMO_GUIDE.md)) | **COMPLETED** |

---

## 8. Hackathon Demonstration

For live judging, presentation walkthroughs, and test scenario presets (Thanjavur, Nagapattinam, Madurai), refer to:
👉 **[HACKATHON_DEMO_GUIDE.md](file:///d:/PROJECTS/AGRI/HACKATHON_DEMO_GUIDE.md)**




