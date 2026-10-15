# 🌾 AgriSense-AI: AI-Powered Paddy Yield Prediction & Smart Farming Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4%2B-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![UI](https://img.shields.io/badge/UI-Liquid%20Glass-4CAF50.svg)](#-user-interface)
[![Tests](https://img.shields.io/badge/Tests-60%2F60%20Passed-brightgreen.svg)](#-running-automated-tests)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D-purple.svg)](#-bilingual-support)

> **AgriSense-AI** is an intelligent decision-support system built for **paddy (rice) farmers in Tamil Nadu**.  
> It accurately forecasts crop yield using Machine Learning and delivers scientific farming advisories (irrigation, fertilizer split schedules, and pest alerts) based on **Tamil Nadu Agricultural University (TNAU)** standards — in both **English** and **Tamil (`தமிழ்`)**.

---

## 📖 Table of Contents
1. [What is AgriSense-AI?](#-what-is-agrisense-ai)
2. [Key Features](#-key-features)
3. [How to Clone & Pull the Project](#-how-to-clone--pull-the-project)
4. [How to Run the Application (All Commands)](#-how-to-run-the-application)
   - [Method 1: One-Click Startup Scripts (Easiest)](#method-1-one-click-startup-scripts-easiest)
   - [Method 2: Docker Compose (Containerized)](#method-2-docker-compose-containerized)
   - [Method 3: Manual Step-by-Step (Terminal)](#method-3-manual-step-by-step-terminal)
5. [Application URLs & Access Points](#-application-urls--access-points)
6. [Testing the APIs with cURL](#-testing-the-apis-with-curl)
7. [Running Automated Tests](#-running-automated-tests)
8. [Project Folder Structure](#-project-folder-structure)
9. [Hackathon Demo & Presentation Guide](#-hackathon-demo--presentation-guide)
10. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🌱 What is AgriSense-AI?

Smallholder paddy farmers across Tamil Nadu face unpredictable monsoon shifts, soil nutrient imbalances from indiscriminate fertilizer use, and groundwater depletion. 

**AgriSense-AI solves this by bringing three technologies together:**
1. **Machine Learning Yield Prediction:** An AI model predicts harvest output ($t/\text{ha}$) before sowing, based on district, season, soil tests, and environmental conditions.
2. **TNAU Expert Advisory:** Rule-based agronomic guidance for **Alternate Wetting and Drying (AWD)** water management (saving 25–30% water), stage-aware urea split dosing, and pest risk alerts (blast and BPH).
3. **Hyperlocal Weather:** Real-time weather and 5-day forecasts via Open-Meteo across all 38 Tamil Nadu districts.
4. **Bilingual Accessibility:** Instant toggle between English and native Tamil (`தமிழ்`) for grassroots usability.

---

## ✨ Key Features

- **🌾 AI Yield Predictor:** Random Forest Regressor calibrated on Tamil Nadu paddy data ($R^2 \approx 0.87$, $\text{MAE} \approx 0.33\,t/\text{ha}$).
- **💧 Alternate Wetting & Drying (AWD):** Tells farmers when to irrigate and when to dry the soil to conserve delta groundwater.
- **🧪 Soil Health & NPK Optimization:** Compares farmer soil test readings ($N, P, K, \text{pH}$) against TNAU standards and recommends exact corrective dosages.
- **🐛 Prophylactic Pest Monitoring:** Triggers early warnings for fungal blast and Brown Planthopper (BPH) based on temperature, humidity, and growth stage.
- **🎨 Liquid Glass UI:** Clean, responsive, glassmorphic interface with zero build dependencies — works smoothly on desktop and mobile browsers.
- **🌐 100% Bilingual:** Full localization in **English** and **Tamil (`தமிழ்`)** without reloading the page.
- **💾 SQLite Audit Trail:** Saves prediction history, logs actual harvest outcomes, and calculates yield variance.

---

## 📥 How to Clone & Pull the Project

### 1. Clone the Repository
Open your terminal (PowerShell, Command Prompt, or Bash) and run:

```bash
# Clone the repository from GitHub
git clone https://github.com/meghashyam0711/agrisense-ai.git

# Move into the project directory
cd agrisense-ai
```

### 2. Pull Latest Changes (If already cloned)
If you already cloned the repository and want the newest updates:

```bash
# Fetch and pull the latest commits from the main branch
git pull origin main
```

---

## 🚀 How to Run the Application

You can run AgriSense-AI using any of the 3 methods below.

---

### Method 1: One-Click Startup Scripts (Easiest)

We provide pre-configured startup scripts that launch both the **FastAPI Backend (port 8000)** and the **Frontend Web App (port 3000)** simultaneously:

#### On Windows (Command Prompt):
```cmd
run.bat
```
*(Or simply double-click the `run.bat` file in Windows File Explorer)*

#### On Windows (PowerShell):
```powershell
.\run.ps1
```

#### On Linux / macOS:
```bash
# Grant execution permissions (first time only)
chmod +x run.sh

# Run the script
./run.sh
```

---

### Method 2: Docker Compose (Containerized)

If you have Docker and Docker Compose installed, run the entire stack with zero manual environment configuration:

```bash
# Build images and start all containers in background
docker compose up --build

# To stop the containers when finished
docker compose down
```

---

### Method 3: Manual Step-by-Step (Terminal)

If you prefer running the backend and frontend separately:

#### Step 1: Create a Python Virtual Environment & Install Dependencies
```bash
# 1. Create a virtual environment (Python 3.10, 3.11, or 3.12 recommended)
python -m venv venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On Linux / macOS:
source venv/bin/activate

# 3. Upgrade pip and install all required packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 2: Start the FastAPI Backend
Open a terminal window and run:
```bash
# Navigate to backend directory
cd backend

# Start the FastAPI server with auto-reload
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
*(The backend is now live at `http://127.0.0.1:8000`)*

#### Step 3: Start the Frontend Web App
Open a **second** terminal window and run:
```bash
# Navigate to frontend directory
cd frontend

# Start a lightweight Python HTTP server on port 3000
python -m http.server 3000
```
*(The frontend is now accessible at `http://127.0.0.1:3000`)*

---

## 🌐 Application URLs & Access Points

Once running, access the services using these links:

| Service | URL | Description |
|:---|:---|:---|
| **🌾 Frontend Application** | [http://127.0.0.1:3000](http://127.0.0.1:3000) | Main user interface (Yield prediction, weather, advisory, history) |
| **⚡ Backend API Root** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | Operational status and API metadata |
| **📖 Interactive API Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive Swagger UI (test endpoints directly in browser) |
| **❤️ Health Check Endpoint** | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | Verifies model status (`v1.0.0`) and database readiness |

---

## 💡 Testing the APIs with cURL

You can test the backend directly using your terminal:

### 1. Check System Health
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### 2. Predict Crop Yield (Sample Payload for Thanjavur Kuruvai)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/crop/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Thanjavur",
    "season": "Kuruvai",
    "soil_type": "Clayey",
    "area_hectares": 1.0,
    "nitrogen_kg_ha": 120.0,
    "phosphorus_kg_ha": 45.0,
    "potassium_kg_ha": 45.0,
    "soil_ph": 6.8,
    "rainfall_mm": 950.0,
    "temperature_c": 28.5,
    "humidity_pct": 78.0,
    "soil_moisture_pct": 68.0,
    "previous_yield_tonnes_ha": 4.8
  }'
```

### 3. Fetch Live Weather for a District
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/weather/current?district=Thanjavur"
```

### 4. Fetch Tamil (`தமிழ்`) Translation Dictionary
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/i18n/ta"
```

---

## 🧪 Running Automated Tests

AgriSense-AI includes **60 automated tests** across ML inference, FastAPI routes, SQLite database operations, TNAU rules, and bilingual localization:

```bash
# Run the complete test suite with verbose output
pytest -v
```

### Expected Output:
```
============================= test session starts ==============================
backend/tests/test_api.py (10 tests) .............. PASSED [ 16%]
backend/tests/test_database.py (8 tests) ........... PASSED [ 30%]
backend/tests/test_i18n.py (6 tests) ............... PASSED [ 40%]
backend/tests/test_integration.py (8 tests) ........ PASSED [ 53%]
backend/tests/test_recommendations.py (17 tests) ... PASSED [ 81%]
ml/tests/test_model.py (6 tests) ................... PASSED [ 91%]
ml/tests/test_preprocessing.py (5 tests) ........... PASSED [100%]

============================= 60 passed in 3.51s ===============================
```

---

## 📁 Project Folder Structure

```
agrisense-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST routes (predict, weather, history, etc.)
│   │   ├── core/                # Config, CORS settings, and i18n helpers
│   │   ├── db/                  # SQLite models, engine, and CRUD methods
│   │   ├── schemas/             # Pydantic v2 validation contracts
│   │   └── services/            # ML service, Open-Meteo client, TNAU rules
│   ├── tests/                   # Backend and integration pytest suites
│   └── main.py                  # FastAPI application entry point
├── frontend/
│   ├── css/style.css            # Liquid Glass design system & styling
│   ├── js/
│   │   ├── api.js               # REST client with timeouts & error handlers
│   │   ├── app.js               # Main UI event logic & preset fillers
│   │   ├── charts.js            # Responsive SVG charts
│   │   ├── data.js              # District agro-climatic coordinates
│   │   └── i18n.js              # English/Tamil translation dictionary
│   └── index.html               # Semantic single-page application
├── ml/
│   ├── data/raw/                # Tamil Nadu paddy dataset
│   ├── saved_models/            # Trained Random Forest model (.joblib)
│   ├── src/                     # Preprocessing, training, and inference scripts
│   └── tests/                   # Model and preprocessing unit tests
├── Dockerfile                   # Production backend container definition
├── docker-compose.yml           # Multi-container orchestration (Backend + Nginx)
├── run.bat                      # Windows Command Prompt launcher
├── run.ps1                      # Windows PowerShell launcher
├── run.sh                       # Linux / macOS Bash launcher
├── requirements.txt             # Pinned Python package dependencies
├── HACKATHON_DEMO_GUIDE.md      # 5-minute pitch script, test presets, and FAQ
└── README.md                    # Project documentation
```

---

## 🏆 Hackathon Demo & Presentation Guide

If you are demonstrating this project to hackathon judges or evaluators:
- Review the **5-minute live pitch script**
- Use the **pre-tested demo presets** (Thanjavur Kuruvai, Nagapattinam Flood Risk, Madurai Drought)
- Read the technical FAQ and architectural justification

👉 **[Open HACKATHON_DEMO_GUIDE.md](HACKATHON_DEMO_GUIDE.md)**

---

## 🔧 Troubleshooting & FAQs

### Q: Port 8000 or Port 3000 is already in use?
**A:** If another application is using port 8000 or 3000, specify a different port:
```bash
# Run backend on port 8080:
python -m uvicorn main:app --reload --port 8080

# Run frontend on port 3001:
python -m http.server 3001
```

### Q: Does this work completely offline without internet?
**A:** **Yes!** The frontend, FastAPI backend, SQLite database, and ML prediction model have zero cloud dependencies and run fully offline. Only real-time weather uses Open-Meteo, and if the network is disconnected, it gracefully falls back to cached climatological normals.

### Q: Why did we use Random Forest over Deep Learning?
**A:** Tabular agricultural data has non-linear feature interactions (such as pH buffering nutrient uptake). Random Forest prevents overfitting on regional datasets, outputs feature importances, and infers in **under 15 milliseconds** on low-power devices.

---

## 📜 Responsible AI Disclaimer

> [!NOTE]
> **Advisory Purpose:** Predictions and recommendations generated by AgriSense-AI are designed as **decision-support estimates** for farmers and agricultural extension officers. They do not constitute crop insurance or financial yield guarantees. Real-world yields depend on localized micro-climates, seed varieties, canal water rotations, and unforeseen pest outbreaks.
