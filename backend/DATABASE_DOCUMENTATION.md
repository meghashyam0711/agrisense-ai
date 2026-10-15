# AgriSense-AI: Database & Bilingual Language Documentation (Phase 8)
## SQLite Relational Schema, Endpoints, Tamil (தமிழ்) Support & Setup Guide

---

### 1. Database Architecture & Relational Schema

AgriSense-AI utilizes **SQLite** with SQLAlchemy ORM for lightweight, zero-configuration local persistence. The schema enforces relational integrity using foreign keys, check constraints, consistent units, and UTC timestamps.

#### SQLite Configuration
- **Engine URL:** `sqlite:///./data/agri_crop.db`
- **Foreign Key Enforcement:** Enforced on every connection via SQLite event listener:
  ```python
  @event.listens_for(Engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      if type(dbapi_connection).__module__ == "sqlite3":
          cursor = dbapi_connection.cursor()
          cursor.execute("PRAGMA foreign_keys=ON")
          cursor.close()
  ```
- **Concurrency & Multithreading:** Configured with `connect_args={"check_same_thread": False}` to support concurrent async FastAPI requests.
- **Privacy & Security:** No passwords, access tokens, API secrets, or sensitive identity documents are stored.

---

### 2. Entity Relationship Overview

```
+-----------------------------------+
|               farms               |
|-----------------------------------|
| PK  id (INTEGER)                  |
|     farmer_name (VARCHAR)         |
|     contact_phone (VARCHAR)       |
|     district (VARCHAR)            |
|     taluk (VARCHAR)               |
|     village (VARCHAR)             |
|     total_area_hectares (FLOAT)   |
|     created_at (DATETIME)         |
|     updated_at (DATETIME)         |
+-----------------+-----------------+
                  |
        1:N       |       1:N
   +--------------+--------------+
   |                             |
   v                             v
+-----------------------+   +-----------------------------------------------+
|     field_details     |   |              prediction_records               |
|-----------------------|   |-----------------------------------------------|
| PK  id (INTEGER)      |   | PK  id (INTEGER)                              |
| FK  farm_id (INTEGER) |   | FK  farm_id (INTEGER, NULLABLE)               |
|     field_name        |   | FK  field_id (INTEGER, NULLABLE)              |
|     area_hectares     |   |     district, season, soil_type               |
|     soil_type         |   |     rainfall_mm, temperature_c, humidity_pct  |
|     soil_ph           |   |     soil_ph, soil_moisture_pct, N-P-K (kg/ha) |
|     irrigation_source |   |     previous_yield_tonnes_per_hectare         |
|     created_at        |   |     predicted_yield_tonnes_per_hectare        |
|     updated_at        |   |     predicted_yield_quintals_per_hectare      |
+-----------------------+   |     predicted_yield_kg_per_hectare            |
                            |     confidence_lower/upper_tonnes             |
                            |     model_name, model_version                 |
                            |     created_at (DATETIME)                     |
                            +-----------------------+-----------------------+
                                                    |
                                          1:1 (opt) | 1:N
                               +--------------------+--------------------+
                               |                                         |
                               v                                         v
            +------------------------------------+   +---------------------------------------+
            |          harvest_results           |   |         recommendation_records        |
            |------------------------------------|   |---------------------------------------|
            | PK  id (INTEGER)                   |   | PK  id (INTEGER)                      |
            | FK  prediction_id (INTEGER, UNIQUE)|   | FK  prediction_id (INTEGER)           |
            | FK  farm_id (INTEGER)              |   | FK  farm_id (INTEGER)                 |
            |     harvest_date (VARCHAR)         |   |     district, season, growth_stage    |
            |     actual_yield_tonnes_per_ha     |   |     category (irrigation/fert/etc)    |
            |     actual_yield_quintals_per_ha   |   |     title, action, reason             |
            |     actual_yield_kg_per_ha         |   |     urgency, warnings                 |
            |     variance_tonnes (act - pred)   |   |     conditions_triggered (JSON)       |
            |     variance_pct                   |   |     created_at (DATETIME)             |
            |     notes, created_at              |   +---------------------------------------+
            +------------------------------------+
```

---

### 3. Database Table Definitions

#### `farms`
Stores agricultural landholding profiles.
- `id` (INTEGER, Primary Key, Auto-increment)
- `farmer_name` (VARCHAR(100), NOT NULL)
- `contact_phone` (VARCHAR(20), NULLABLE)
- `district` (VARCHAR(50), NOT NULL, Indexed)
- `taluk` (VARCHAR(50), NULLABLE)
- `village` (VARCHAR(50), NULLABLE)
- `total_area_hectares` (FLOAT, NOT NULL, `CHECK (total_area_hectares > 0)`)
- `created_at` (DATETIME, Default UTC now)
- `updated_at` (DATETIME, Default UTC now)

#### `field_details`
Stores individual plot demarcations within a farm holding.
- `id` (INTEGER, Primary Key, Auto-increment)
- `farm_id` (INTEGER, NOT NULL, Foreign Key `farms.id` ON DELETE CASCADE, Indexed)
- `field_name` (VARCHAR(50), NOT NULL)
- `area_hectares` (FLOAT, NOT NULL, `CHECK (area_hectares > 0)`)
- `soil_type` (VARCHAR(50), NOT NULL)
- `soil_ph` (FLOAT, NULLABLE)
- `irrigation_source` (VARCHAR(50), NULLABLE)
- `created_at` (DATETIME, Default UTC now)
- `updated_at` (DATETIME, Default UTC now)

#### `prediction_records`
Audit trail of inference queries and estimated yield outputs.
- `id` (INTEGER, Primary Key, Auto-increment)
- `farm_id` (INTEGER, NULLABLE, Foreign Key `farms.id` ON DELETE SET NULL)
- `field_id` (INTEGER, NULLABLE, Foreign Key `field_details.id` ON DELETE SET NULL)
- Location & Season: `district`, `season`, `soil_type`, `area_hectares`
- Inputs: `rainfall_mm`, `temperature_c`, `humidity_pct`, `soil_ph`, `soil_moisture_pct`, `nitrogen_kg_ha`, `phosphorus_kg_ha`, `potassium_kg_ha`, `previous_yield_tonnes_per_hectare`
- Outputs: `predicted_yield_tonnes_per_hectare`, `predicted_yield_quintals_per_hectare`, `predicted_yield_kg_per_hectare`, `confidence_lower_tonnes`, `confidence_upper_tonnes`
- Metadata: `model_name`, `model_version`, `notes`, `created_at`

#### `harvest_results`
Ground-truth harvest outcomes for accuracy benchmarking and post-season model validation.
- `id` (INTEGER, Primary Key, Auto-increment)
- `prediction_id` (INTEGER, NULLABLE, UNIQUE, Foreign Key `prediction_records.id` ON DELETE SET NULL)
- `farm_id` (INTEGER, NULLABLE, Foreign Key `farms.id` ON DELETE SET NULL)
- `harvest_date` (VARCHAR(20), NOT NULL — format `YYYY-MM-DD`)
- `actual_yield_tonnes_per_hectare` (FLOAT, NOT NULL, `CHECK (actual_yield_tonnes_per_hectare >= 0)`)
- `actual_yield_quintals_per_hectare` (FLOAT, NOT NULL — auto-computed as `tonnes * 10`)
- `actual_yield_kg_per_hectare` (FLOAT, NOT NULL — auto-computed as `tonnes * 1000`)
- `actual_total_production_tonnes` (FLOAT, NULLABLE)
- `variance_tonnes` (FLOAT, NULLABLE — computed as `actual - predicted`)
- `variance_pct` (FLOAT, NULLABLE — computed as `(actual - predicted) / predicted * 100`)
- `notes` (TEXT, NULLABLE)
- `created_at` (DATETIME, Default UTC now)

#### `recommendation_records`
Audited agronomic advisory items associated with predictions or field checks.
- `id` (INTEGER, Primary Key, Auto-increment)
- `prediction_id` (INTEGER, NULLABLE, Foreign Key `prediction_records.id` ON DELETE CASCADE)
- `farm_id` (INTEGER, NULLABLE, Foreign Key `farms.id` ON DELETE SET NULL)
- `district`, `season`, `growth_stage`, `category`, `title`, `action`, `reason`, `urgency`, `warnings`
- `conditions_triggered` (TEXT, JSON string)
- `created_at` (DATETIME, Default UTC now)

---

### 4. Database REST API Endpoints

#### Farm Profiles (`/api/v1/farms`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/farms/` | Create a new farm profile with optional initial fields |
| `GET` | `/api/v1/farms/` | List farm profiles (with optional `district` filter) |
| `GET` | `/api/v1/farms/{id}` | Get farm profile and nested field details |
| `PUT` | `/api/v1/farms/{id}` | Update farm holding details |
| `DELETE`| `/api/v1/farms/{id}` | Delete farm profile (cascades deletion to child fields) |
| `POST` | `/api/v1/farms/{id}/fields` | Add a field plot to an existing farm |

#### Prediction History & Harvest Tracking (`/api/v1/history`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/history/logs` | Fetch paginated prediction history (filters: `district`, `season`, `farm_id`, `limit`, `offset`) |
| `POST` | `/api/v1/history/predictions` | Save a prediction record to SQLite |
| `GET` | `/api/v1/history/predictions/{id}` | Retrieve specific prediction with attached harvest and recommendations |
| `POST` | `/api/v1/history/harvest` | Record actual harvest outcome (auto-computes variance vs predicted) |
| `GET` | `/api/v1/history/harvest` | List ground-truth harvest records |
| `POST` | `/api/v1/history/recommendations` | Persist a batch of generated recommendations |
| `GET` | `/api/v1/history/recommendations` | List saved recommendation records |

---

### 5. Bilingual Language Support (English & Tamil / தமிழ்)

AgriSense-AI provides full bilingual internationalization across navigation, forms, validation messages, recommendation categories, urgency badges, and error alerts.

#### Architecture
- **Frontend Localization:** Driven by `I18N_DICTIONARY` in `frontend/js/i18n.js`.
- **Backend Localization:** Driven by `I18N_BACKEND_DICTIONARY` in `backend/app/core/i18n.py`.
- **Unicode Support:** Native UTF-8 encoding ensures Tamil script (`தமிழ்`) renders without truncation or encoding loss.
- **Language Persistence:**
  - Selected language is persisted in the browser's `localStorage` under key `agrisense_language`.
  - On application startup, the persisted language preference is retrieved and applied automatically to `document.documentElement.lang`.

#### Localization Endpoints (`/api/v1/i18n`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/i18n/languages` | Returns supported language codes and native display names (`en`, `ta`) |
| `GET` | `/api/v1/i18n/{lang}` | Returns complete translation dictionary for requested language code |

---

### 6. Setup & Execution Instructions

#### Automatic Initialization
The SQLite schema initializes automatically upon FastAPI server startup via the lifespan context manager:
```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Ensures all tables and foreign keys are created
    ...
```

#### Manual Initialization via CLI
```powershell
# From the backend directory
python -m app.db.init_db
```

#### Running Tests
```powershell
python -m pytest backend/tests/test_database.py backend/tests/test_i18n.py -v
```
