# AgriSense-AI: AI-Powered Paddy Yield Prediction & Smart Farming Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4%2B-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![UI](https://img.shields.io/badge/UI-Liquid%20Glass-4CAF50.svg)](#frontend-ui)
[![Tests](https://img.shields.io/badge/Tests-60%2F60%20Passed-brightgreen.svg)](#testing)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D-purple.svg)](#bilingual-support)

**AgriSense-AI** is a smart agricultural decision-support platform designed specifically for **paddy (rice) farming in Tamil Nadu**. It combines machine learning yield forecasting, real-time agro-meteorology, and expert agronomic rules grounded in **Tamil Nadu Agricultural University (TNAU)** standards, accessible in both **English** and **Tamil (`தமிழ்`)**.

---

## 1. Key Capabilities & Features

- **🌾 AI Yield Prediction:** Scikit-learn Random Forest Regressor calibrated on Tamil Nadu agro-climatic zones, predicting paddy yield ($t/\text{ha}$, $\text{quintals/ha}$, and $\text{kg/ha}$) using rainfall, temperature, humidity, soil pH, NPK, and moisture.
- **🌿 TNAU Smart Farming Advisory:** Rule engine delivering actionable Alternate Wetting and Drying (AWD) water management (saving 25–30% irrigation water), stage-aware NPK split schedules, and pest alerts (blast and Brown Planthopper).
- **🌦️ Hyperlocal Weather Integration:** Real-time conditions and 5-day forecasts via Open-Meteo API across all 38 Tamil Nadu districts, with offline fallback to climatological normals.
- **💧 Liquid Glass UI:** Ultra-lightweight, zero-build Vanilla HTML5/CSS3/JavaScript interface featuring a frosted glass aesthetic with subtle transparency, backdrop filters, and responsive layout.
- **🌐 Full Bilingual Localization:** Instant zero-reload switching between **English** and **Tamil (`தமிழ்`)** across all interface cards, validation messages, and agronomic recommendations.
- **📊 Farm Records & Harvest Tracking:** Relational SQLite persistence for farm profiles, prediction history audit logs, and post-harvest yield variance analysis.

---

## 2. Engineering & Development Lifecycle

AgriSense-AI was developed as a complete end-to-end platform spanning **10 modular engineering milestones**:
1. **System Architecture & Requirements:** Contract-driven interface definitions for ML, weather, database, and bilingual localization.
2. **Liquid Glass Frontend:** Zero-dependency, responsive UI with custom SVG data visualizations.
3. **Agro-Dataset Engineering:** Data schema, cleaning, deduplication, and preprocessors for Tamil Nadu cropping seasons (*Kuruvai*, *Samba*, *Thaladi*, *Navarai*).
4. **Machine Learning Model:** Random Forest Regressor achieving $R^2 \approx 0.87$ and $\text{MAE} \approx 0.33\,t/\text{ha}$, serialized with Joblib.
5. **FastAPI REST Backend:** Asynchronous endpoints with strict Pydantic v2 schemas and CORS negotiation.
6. **Agro-Weather Service:** Open-Meteo integration with in-memory caching and resilient network fallbacks.
7. **TNAU Expert Recommendation Engine:** Explainable agronomic rules for irrigation, soil amendments, and pest monitoring.
8. **Relational Database & Localization:** SQLite schema with foreign key cascades and complete English/Tamil dictionaries.
9. **Full Stack Integration:** Live end-to-end API wiring, history audit trail, and client-side report generation.
10. **Testing & Containerization:** 60/60 automated pytest suite, Docker Compose orchestration, and one-click launch scripts.

---

## 3. System Architecture

```
+-------------------------------------------------------------------------------+
|                       VANILLA FRONTEND (Liquid Glass UI)                      |
|   - index.html (Semantic Structure)   - style.css (Glassmorphic Design System)|
|   - api.js (Backend Client Contract)   - i18n.js (English / Tamil Dictionary)  |
+---------------------------------------+---------------------------------------+
                                        | HTTP / JSON REST (Port 3000 -> 8000)
                                        v
+-------------------------------------------------------------------------------+
|                          FASTAPI BACKEND SERVICE                              |
|   - POST /api/v1/crop/predict         : Random Forest Yield Inference         |
|   - POST /recommendations             : TNAU Agronomic Rule Engine            |
|   - GET  /api/v1/weather/current      : Open-Meteo Weather Broker             |
|   - GET  /api/v1/history/logs         : SQLite History & Harvest Tracking     |
|   - GET  /api/v1/i18n/{lang}          : Bilingual Translation Dictionaries    |
+-------------------+-----------------------------------+-----------------------+
                    |                                   |
                    v                                   v
+-----------------------------------+   +---------------------------------------+
|        SQLITE DATABASE            |   |          ML INFERENCE ENGINE          |
| - Farms & Fields                  |   | - Scikit-Learn Random Forest Model    |
| - Prediction History Logs         |   | - ColumnTransformer Preprocessor      |
| - Actual Harvest Variance Logs    |   | - TNAU Agronomic Expert Rules         |
+-----------------------------------+   +---------------------------------------+
```

---

## 4. Project Structure

```
AGRI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/           # REST endpoints (predict, weather, history, etc.)
│   │   ├── core/                       # App settings, CORS, and localization helpers
│   │   ├── db/                         # SQLite session, ORM models, and CRUD operations
│   │   ├── schemas/                    # Pydantic v2 request/response schemas
│   │   └── services/                   # ML inference, weather, and recommendation engine
│   ├── tests/                          # 49 automated pytest backend test cases
│   └── main.py                         # FastAPI application entry point
├── frontend/
│   ├── css/style.css                   # Liquid Glass design system and typography
│   ├── js/
│   │   ├── api.js                      # REST API client with timeout and error extraction
│   │   ├── app.js                      # UI controller, event handlers, and presets
│   │   ├── charts.js                   # Lightweight SVG data charts
│   │   ├── data.js                     # District agro-climatic lookup tables
│   │   └── i18n.js                     # Client-side English/Tamil translation dictionary
│   └── index.html                      # Semantic HTML5 single-page application
├── ml/
│   ├── data/raw/                       # Tamil Nadu paddy dataset
│   ├── saved_models/                   # Trained model (.joblib) and feature metadata
│   ├── src/                            # Training, preprocessing, and validation scripts
│   └── tests/                          # 11 automated pytest ML test cases
├── Dockerfile                          # Production backend container definition
├── docker-compose.yml                  # Multi-container orchestration (Backend + Frontend)
├── run.bat / run.ps1 / run.sh          # One-click startup scripts
├── requirements.txt                    # Pinned Python dependencies
├── HACKATHON_DEMO_GUIDE.md             # 5-minute pitch script, test presets, and FAQ
└── README.md                           # Project documentation
```

---

## 5. Quick Start & Execution

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Web browser (Chrome, Edge, Firefox, Safari)

### Option A: One-Click Startup Scripts (Recommended)
Launch both the FastAPI backend (`:8000`) and the frontend (`:3000`) with a single command:
- **Windows (Command Prompt):** Double-click or run `run.bat`
- **Windows (PowerShell):** Run `.\run.ps1`
- **Linux / macOS:** Run `./run.sh`

### Option B: Docker Compose
Run the entire stack in isolated containers:
```bash
docker compose up --build
```
- **Frontend UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Option C: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run backend in Terminal 1
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 3. Serve frontend in Terminal 2
cd frontend
python -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 6. Automated Testing Suite

AgriSense-AI includes **60 automated tests** covering ML models, API contracts, database constraints, recommendation logic, and Tamil Unicode rendering:

```bash
pytest -v
```

```
backend/tests/test_api.py (10 tests) .............. PASSED
backend/tests/test_database.py (8 tests) ........... PASSED
backend/tests/test_i18n.py (6 tests) ............... PASSED
backend/tests/test_integration.py (8 tests) ........ PASSED
backend/tests/test_recommendations.py (17 tests) ... PASSED
ml/tests/test_model.py (6 tests) ................... PASSED
ml/tests/test_preprocessing.py (5 tests) ........... PASSED
============================= 60 passed in 3.51s ==============================
```

---

## 7. Hackathon Demo & Presentation

A comprehensive presentation guide with a 5-minute judging script, test presets (Thanjavur, Nagapattinam, Madurai), and agronomic rationale is available in:

👉 **[HACKATHON_DEMO_GUIDE.md](HACKATHON_DEMO_GUIDE.md)**

---

## 8. Responsible AI & Agronomic Disclaimers

> [!NOTE]
> **Decision-Support Notice:** Predictions and recommendations provided by AgriSense-AI are intended as **decision-support tools** and do not constitute certified financial or crop insurance guarantees. Real-world crop yields depend on localized micro-climates, seed varieties, canal water rotations, and unforeseen pest outbreaks. Farmers are encouraged to consult their local **Krishi Vigyan Kendra (KVK)** or Village Agricultural Extension Officer (VAO).
