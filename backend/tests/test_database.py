"""
AgriSense-AI: Automated Database & CRUD Unit Tests.
Verifies SQLite schema creation, Farm and Field relationships,
Prediction history logging, Harvest outcome variance analysis,
and REST API endpoints under /api/v1/farms and /api/v1/history.
"""

import sys
import unittest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Ensure backend and project root are importable
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.session import Base, get_db
from app.db import crud
from app.db.init_db import init_db
from app.schemas.database import (
    FarmCreate,
    FarmUpdate,
    FieldDetailCreate,
    PredictionRecordCreate,
    HarvestResultCreate,
    RecommendationRecordCreate
)
from main import app

# Create in-memory SQLite engine for fast, isolated test execution
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestDatabaseCRUD(unittest.TestCase):
    """Direct database model and CRUD tests."""

    @classmethod
    def setUpClass(cls):
        init_db(test_engine)

    def setUp(self):
        Base.metadata.create_all(bind=test_engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=test_engine)

    def test_create_and_get_farm(self):
        """Tests creating a farm with child fields and retrieving it."""
        farm_in = FarmCreate(
            farmer_name="K. Murugan",
            contact_phone="+91 98765 43210",
            district="Thanjavur",
            taluk="Kumbakonam",
            village="Swamimalai",
            total_area_hectares=4.5,
            fields=[
                FieldDetailCreate(
                    field_name="North Paddy Plot",
                    area_hectares=2.5,
                    soil_type="Alluvial",
                    soil_ph=6.8,
                    irrigation_source="Canal"
                ),
                FieldDetailCreate(
                    field_name="South Paddy Plot",
                    area_hectares=2.0,
                    soil_type="Clay Loam",
                    soil_ph=7.1,
                    irrigation_source="Borewell"
                )
            ]
        )
        farm = crud.create_farm(self.db, farm_in)
        self.assertIsNotNone(farm.id)
        self.assertEqual(farm.farmer_name, "K. Murugan")
        self.assertEqual(farm.district, "Thanjavur")
        self.assertEqual(len(farm.fields), 2)

        retrieved = crud.get_farm(self.db, farm.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved.fields), 2)
        self.assertEqual(retrieved.fields[0].field_name, "North Paddy Plot")

    def test_list_and_filter_farms(self):
        """Tests filtering farms by district."""
        f1 = FarmCreate(farmer_name="Farmer A", district="Thanjavur", total_area_hectares=2.0)
        f2 = FarmCreate(farmer_name="Farmer B", district="Madurai", total_area_hectares=3.0)
        crud.create_farm(self.db, f1)
        crud.create_farm(self.db, f2)

        thanjavur_farms = crud.list_farms(self.db, district="Thanjavur")
        self.assertEqual(len(thanjavur_farms), 1)
        self.assertEqual(thanjavur_farms[0].farmer_name, "Farmer A")

    def test_delete_farm_cascades_to_fields(self):
        """Tests deleting a farm removes all associated fields."""
        farm_in = FarmCreate(
            farmer_name="To Delete",
            district="Tiruvarur",
            total_area_hectares=1.5,
            fields=[
                FieldDetailCreate(
                    field_name="Field 1",
                    area_hectares=1.5,
                    soil_type="Alluvial"
                )
            ]
        )
        farm = crud.create_farm(self.db, farm_in)
        farm_id = farm.id
        self.assertTrue(crud.delete_farm(self.db, farm_id))
        self.assertIsNone(crud.get_farm(self.db, farm_id))
        self.assertEqual(len(crud.list_fields_by_farm(self.db, farm_id)), 0)

    def test_prediction_history_logging_and_filtering(self):
        """Tests persisting and filtering prediction audit records."""
        pred_in = PredictionRecordCreate(
            district="Nagapattinam",
            season="Samba",
            soil_type="Coastal Saline",
            area_hectares=3.0,
            rainfall_mm=1200.0,
            temperature_c=29.0,
            humidity_pct=84.0,
            soil_ph=7.2,
            soil_moisture_pct=78.0,
            nitrogen_kg_ha=145.0,
            phosphorus_kg_ha=42.0,
            potassium_kg_ha=40.0,
            previous_yield_tonnes_per_hectare=4.2,
            predicted_yield_tonnes_per_hectare=4.65,
            predicted_yield_quintals_per_hectare=46.5,
            predicted_yield_kg_per_hectare=4650.0,
            confidence_lower_tonnes=4.25,
            confidence_upper_tonnes=5.05
        )
        record = crud.create_prediction_record(self.db, pred_in)
        self.assertIsNotNone(record.id)
        self.assertEqual(record.predicted_yield_quintals_per_hectare, 46.5)

        records = crud.list_prediction_records(self.db, district="Nagapattinam")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].season, "Samba")

    def test_harvest_result_recording_and_variance(self):
        """Tests actual harvest recording calculates variance against predicted yield."""
        pred_in = PredictionRecordCreate(
            district="Thanjavur",
            season="Kuruvai",
            soil_type="Alluvial",
            area_hectares=2.0,
            rainfall_mm=850.0,
            temperature_c=31.0,
            humidity_pct=75.0,
            soil_ph=6.7,
            soil_moisture_pct=70.0,
            nitrogen_kg_ha=120.0,
            phosphorus_kg_ha=38.0,
            potassium_kg_ha=38.0,
            previous_yield_tonnes_per_hectare=4.0,
            predicted_yield_tonnes_per_hectare=4.50,
            predicted_yield_quintals_per_hectare=45.0,
            predicted_yield_kg_per_hectare=4500.0
        )
        pred = crud.create_prediction_record(self.db, pred_in)

        # Actual harvest is 4.80 tonnes/ha (higher than predicted)
        harvest_in = HarvestResultCreate(
            prediction_id=pred.id,
            harvest_date="2026-10-10",
            actual_yield_tonnes_per_hectare=4.80,
            notes="Excellent weather during flowering."
        )
        harvest = crud.create_harvest_result(self.db, harvest_in)

        self.assertEqual(harvest.actual_yield_quintals_per_hectare, 48.0)
        self.assertEqual(harvest.actual_yield_kg_per_hectare, 4800.0)
        self.assertAlmostEqual(harvest.variance_tonnes, 0.30, places=2)
        # Variance pct: (4.8 - 4.5) / 4.5 * 100 = +6.67%
        self.assertAlmostEqual(harvest.variance_pct, 6.67, places=2)


class TestDatabaseAPIEndpoints(unittest.TestCase):
    """API endpoint integration tests with SQLite backend."""

    @classmethod
    def setUpClass(cls):
        init_db(test_engine)
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        Base.metadata.create_all(bind=test_engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=test_engine)

    def test_api_create_and_list_farms(self):
        """Tests POST /api/v1/farms/ and GET /api/v1/farms/."""
        payload = {
            "farmer_name": "R. Selvam",
            "contact_phone": "+91 94433 11223",
            "district": "Tiruvarur",
            "taluk": "Mannargudi",
            "village": "Pamani",
            "total_area_hectares": 3.2,
            "fields": [
                {
                    "field_name": "Plot 1",
                    "area_hectares": 3.2,
                    "soil_type": "Clay Loam",
                    "soil_ph": 7.0,
                    "irrigation_source": "Canal"
                }
            ]
        }
        res_create = self.client.post("/api/v1/farms/", json=payload)
        self.assertEqual(res_create.status_code, 201)
        farm_data = res_create.json()
        self.assertEqual(farm_data["farmer_name"], "R. Selvam")
        self.assertEqual(len(farm_data["fields"]), 1)

        farm_id = farm_data["id"]
        res_get = self.client.get(f"/api/v1/farms/{farm_id}")
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()["district"], "Tiruvarur")

    def test_api_save_and_retrieve_prediction_history(self):
        """Tests POST /api/v1/history/predictions and GET /api/v1/history/logs."""
        pred_payload = {
            "district": "Cuddalore",
            "season": "Samba",
            "soil_type": "Alluvial",
            "area_hectares": 2.0,
            "rainfall_mm": 1100.0,
            "temperature_c": 30.0,
            "humidity_pct": 80.0,
            "soil_ph": 6.8,
            "soil_moisture_pct": 74.0,
            "nitrogen_kg_ha": 135.0,
            "phosphorus_kg_ha": 45.0,
            "potassium_kg_ha": 42.0,
            "previous_yield_tonnes_per_hectare": 4.1,
            "predicted_yield_tonnes_per_hectare": 4.55,
            "predicted_yield_quintals_per_hectare": 45.5,
            "predicted_yield_kg_per_hectare": 4550.0,
            "model_name": "RandomForestRegressor",
            "model_version": "1.0.0"
        }
        res_post = self.client.post("/api/v1/history/predictions", json=pred_payload)
        self.assertEqual(res_post.status_code, 201)
        pred_id = res_post.json()["id"]

        # Fetch history logs
        res_logs = self.client.get("/api/v1/history/logs?district=Cuddalore")
        self.assertEqual(res_logs.status_code, 200)
        logs = res_logs.json()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["id"], pred_id)

    def test_api_record_harvest_and_variance(self):
        """Tests POST /api/v1/history/harvest and GET /api/v1/history/harvest."""
        # 1. Create a prediction first
        pred_res = self.client.post("/api/v1/history/predictions", json={
            "district": "Madurai",
            "season": "Navarai",
            "soil_type": "Red Loam",
            "area_hectares": 1.5,
            "rainfall_mm": 700.0,
            "temperature_c": 33.0,
            "humidity_pct": 65.0,
            "soil_ph": 6.5,
            "soil_moisture_pct": 62.0,
            "nitrogen_kg_ha": 115.0,
            "phosphorus_kg_ha": 35.0,
            "potassium_kg_ha": 35.0,
            "previous_yield_tonnes_per_hectare": 3.8,
            "predicted_yield_tonnes_per_hectare": 4.00,
            "predicted_yield_quintals_per_hectare": 40.0,
            "predicted_yield_kg_per_hectare": 4000.0
        })
        pred_id = pred_res.json()["id"]

        # 2. Record actual harvest
        harvest_payload = {
            "prediction_id": pred_id,
            "harvest_date": "2026-10-12",
            "actual_yield_tonnes_per_hectare": 4.20,
            "notes": "Good yield despite minor water deficit."
        }
        res_h = self.client.post("/api/v1/history/harvest", json=harvest_payload)
        self.assertEqual(res_h.status_code, 201)
        h_data = res_h.json()
        self.assertEqual(h_data["actual_yield_quintals_per_hectare"], 42.0)
        self.assertAlmostEqual(h_data["variance_tonnes"], 0.20, places=2)
        self.assertAlmostEqual(h_data["variance_pct"], 5.0, places=2)

        # 3. Retrieve harvest listing
        res_list = self.client.get("/api/v1/history/harvest")
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()), 1)


if __name__ == "__main__":
    unittest.main()
