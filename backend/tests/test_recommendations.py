"""
AgriSense-AI: Comprehensive Unit Tests for Smart Farming Recommendations.
Covers normal conditions, extreme inputs, missing information, conflicting weather,
pest triggers, and API endpoints (POST /recommendations and POST /api/v1/recommendations).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Ensure backend and project root are importable
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import app
from app.schemas.recommendations import (
    CropStage,
    RecommendationCategory,
    RecommendationUrgency,
    RecommendationRequest,
    RecommendationsResponse
)
from app.services.recommendation_engine import recommendation_engine


class TestRecommendationEngineRules(unittest.TestCase):
    """Direct unit tests for the AgronomicRecommendationEngine rule logic."""

    def test_normal_tillering_conditions(self):
        """Tests standard vegetative tillering with balanced NPK and AWD."""
        req = RecommendationRequest(
            district="Thanjavur",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_type="Alluvial",
            soil_ph=6.8,
            soil_moisture_pct=65.0,
            nitrogen_kg_ha=140.0,
            phosphorus_kg_ha=45.0,
            potassium_kg_ha=45.0,
            temperature_c=29.0,
            humidity_pct=72.0,
            rainfall_mm=5.0,
            forecast_rain_expected_mm=2.0,
            forecast_rain_prob_pct=20
        )
        res: RecommendationsResponse = recommendation_engine.generate_recommendations(req)

        self.assertEqual(res.rule_type, "agronomic_expert_system")
        self.assertEqual(res.district, "Thanjavur")
        self.assertEqual(res.growth_stage, CropStage.VEGETATIVE_TILLERING)

        # Irrigation: Optimal AWD monitoring
        irrig_titles = [item.title for item in res.irrigation_advisory]
        self.assertTrue(any("AWD" in t for t in irrig_titles))

        # Fertilizer: Active tillering 20-25 DAT split
        fert_titles = [item.title for item in res.fertilizer_advisory]
        self.assertTrue(any("Tillering" in t for t in fert_titles))

        # Soil: Optimal reaction
        soil_titles = [item.title for item in res.soil_health_advisory]
        self.assertTrue(any("Optimal" in t for t in soil_titles))

        # No weather conflicts
        self.assertEqual(len(res.conflicts_detected), 0)

    def test_extreme_acidic_soil_lime_alert(self):
        """Tests soil pH < 6.0 triggers lime (CaCO3) amendment alert."""
        req = RecommendationRequest(
            district="Tiruvarur",
            season="Kuruvai",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=4.8,  # Strongly acidic
            soil_moisture_pct=70.0,
            nitrogen_kg_ha=120.0,
            phosphorus_kg_ha=30.0,
            potassium_kg_ha=35.0
        )
        res = recommendation_engine.generate_recommendations(req)

        soil_items = res.soil_health_advisory
        acid_alerts = [i for i in soil_items if "Acidic" in i.title or "Lime" in i.title]
        self.assertEqual(len(acid_alerts), 1)
        self.assertEqual(acid_alerts[0].urgency, RecommendationUrgency.WARNING)
        self.assertIn("CaCO3", acid_alerts[0].action)
        self.assertIn("soil_ph", acid_alerts[0].conditions_triggered)

    def test_extreme_alkaline_soil_gypsum_alert(self):
        """Tests soil pH > 8.0 triggers gypsum (CaSO4) amendment alert."""
        req = RecommendationRequest(
            district="Tiruchirappalli",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=8.6,  # Alkaline / Sodic
            soil_moisture_pct=65.0,
            nitrogen_kg_ha=140.0,
            phosphorus_kg_ha=40.0,
            potassium_kg_ha=40.0
        )
        res = recommendation_engine.generate_recommendations(req)

        soil_items = res.soil_health_advisory
        alkali_alerts = [i for i in soil_items if "Alkaline" in i.title or "Gypsum" in i.title]
        self.assertEqual(len(alkali_alerts), 1)
        self.assertEqual(alkali_alerts[0].urgency, RecommendationUrgency.WARNING)
        self.assertIn("Gypsum", alkali_alerts[0].action)

    def test_extreme_excess_nitrogen_warning(self):
        """Tests Nitrogen > 180 kg/ha triggers reduction advisory and pest warnings."""
        req = RecommendationRequest(
            district="Thanjavur",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=6.5,
            soil_moisture_pct=70.0,
            nitrogen_kg_ha=220.0,  # Excessively high
            phosphorus_kg_ha=45.0,
            potassium_kg_ha=45.0
        )
        res = recommendation_engine.generate_recommendations(req)

        fert_items = [i for i in res.fertilizer_advisory if i.urgency == RecommendationUrgency.WARNING]
        self.assertTrue(len(fert_items) >= 1)
        self.assertIn("excessively high", fert_items[0].reason.lower())

    def test_flowering_critical_water_requirement(self):
        """Tests flowering stage requires continuous standing water and raises CRITICAL urgency if moisture drops."""
        req = RecommendationRequest(
            district="Nagapattinam",
            season="Samba",
            growth_stage=CropStage.FLOWERING_HEADING,
            soil_ph=7.0,
            soil_moisture_pct=55.0,  # Below critical 70% threshold
            nitrogen_kg_ha=130.0,
            phosphorus_kg_ha=40.0,
            potassium_kg_ha=40.0
        )
        res = recommendation_engine.generate_recommendations(req)

        critical_irrig = [i for i in res.irrigation_advisory if i.urgency == RecommendationUrgency.CRITICAL]
        self.assertEqual(len(critical_irrig), 1)
        self.assertIn("Critical", critical_irrig[0].title)
        self.assertIn("sterility", critical_irrig[0].reason.lower())

    def test_grain_filling_terminal_drainage(self):
        """Tests maturity stage recommends terminal field drainage 10-15 days before harvest."""
        req = RecommendationRequest(
            district="Mayiladuthurai",
            season="Samba",
            growth_stage=CropStage.GRAIN_FILLING_MATURITY,
            soil_ph=6.7,
            soil_moisture_pct=80.0,
            nitrogen_kg_ha=120.0,
            phosphorus_kg_ha=35.0,
            potassium_kg_ha=40.0
        )
        res = recommendation_engine.generate_recommendations(req)

        terminal_drainage = [i for i in res.irrigation_advisory if "Terminal Drainage" in i.title]
        self.assertEqual(len(terminal_drainage), 1)
        self.assertIn("drain", terminal_drainage[0].action.lower())

    def test_conflicting_conditions_dry_soil_vs_forecast_rain(self):
        """Tests conflict handling when soil is dry (<60%) but heavy rain (>=20mm) is imminent."""
        req = RecommendationRequest(
            district="Cuddalore",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=6.5,
            soil_moisture_pct=48.0,  # Dry soil
            nitrogen_kg_ha=120.0,
            phosphorus_kg_ha=35.0,
            potassium_kg_ha=40.0,
            forecast_rain_expected_mm=35.0,  # Impending heavy rain
            forecast_rain_prob_pct=85
        )
        res = recommendation_engine.generate_recommendations(req)

        self.assertTrue(len(res.conflicts_detected) >= 1)
        self.assertTrue(any("rainfall is forecast" in c.lower() for c in res.conflicts_detected))

        # Check that irrigation advisory advises postponing irrigation
        postpone_advisories = [i for i in res.irrigation_advisory if "Postpone" in i.title]
        self.assertEqual(len(postpone_advisories), 1)
        self.assertEqual(postpone_advisories[0].urgency, RecommendationUrgency.WARNING)

    def test_conflicting_conditions_urea_topdressing_vs_forecast_rain(self):
        """Tests conflict handling when urea topdressing is scheduled but rain (>=15mm) is forecast."""
        req = RecommendationRequest(
            district="Thanjavur",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=6.8,
            soil_moisture_pct=72.0,
            nitrogen_kg_ha=130.0,
            phosphorus_kg_ha=40.0,
            potassium_kg_ha=45.0,
            forecast_rain_expected_mm=25.0,
            forecast_rain_prob_pct=75
        )
        res = recommendation_engine.generate_recommendations(req)

        self.assertTrue(len(res.conflicts_detected) >= 1)
        fert_warnings = [i for i in res.fertilizer_advisory if "Withhold" in i.title or "Postpone" in i.action]
        self.assertEqual(len(fert_warnings), 1)
        self.assertIn("leaching", fert_warnings[0].reason.lower())

    def test_pest_monitoring_blast_trigger(self):
        """Tests high humidity (>=85%), moderate temp (<=29°C), and high N (>=145) trigger Rice Blast alert."""
        req = RecommendationRequest(
            district="Madurai",
            season="Samba",
            growth_stage=CropStage.VEGETATIVE_TILLERING,
            soil_ph=6.5,
            soil_moisture_pct=75.0,
            nitrogen_kg_ha=165.0,
            phosphorus_kg_ha=40.0,
            potassium_kg_ha=40.0,
            temperature_c=27.5,
            humidity_pct=88.0
        )
        res = recommendation_engine.generate_recommendations(req)

        blast_alerts = [i for i in res.pest_monitoring_alerts if "Blast" in i.title]
        self.assertEqual(len(blast_alerts), 1)
        self.assertEqual(blast_alerts[0].urgency, RecommendationUrgency.WARNING)
        self.assertIn("Pseudomonas", blast_alerts[0].action)

    def test_pest_monitoring_bph_trigger(self):
        """Tests high N (>=160) and high humidity (>=80%) trigger BPH alert."""
        req = RecommendationRequest(
            district="Tiruvarur",
            season="Samba",
            growth_stage=CropStage.PANICLE_INITIATION,
            soil_ph=6.9,
            soil_moisture_pct=78.0,
            nitrogen_kg_ha=175.0,
            phosphorus_kg_ha=45.0,
            potassium_kg_ha=40.0,
            humidity_pct=85.0
        )
        res = recommendation_engine.generate_recommendations(req)

        bph_alerts = [i for i in res.pest_monitoring_alerts if "Planthopper" in i.title or "BPH" in i.title]
        self.assertEqual(len(bph_alerts), 1)
        self.assertEqual(bph_alerts[0].urgency, RecommendationUrgency.WARNING)
        self.assertIn("drain", bph_alerts[0].action.lower())

    def test_missing_optional_environmental_metrics(self):
        """Tests engine records data limitations transparently when temperature and forecast are None."""
        req = RecommendationRequest(
            district="Villupuram",
            season="Kuruvai",
            growth_stage=CropStage.NURSERY,
            soil_ph=6.6,
            soil_moisture_pct=70.0,
            nitrogen_kg_ha=110.0,
            phosphorus_kg_ha=35.0,
            potassium_kg_ha=35.0,
            temperature_c=None,
            humidity_pct=None,
            forecast_rain_expected_mm=None
        )
        res = recommendation_engine.generate_recommendations(req)

        self.assertTrue(len(res.data_limitations) >= 2)
        limit_text = " ".join(res.data_limitations)
        self.assertIn("Temperature was not provided", limit_text)
        self.assertIn("forecast was not provided", limit_text)


class TestRecommendationAPIEndpoints(unittest.TestCase):
    """API endpoint integration tests using FastAPI TestClient."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.valid_body = {
            "district": "Thanjavur",
            "season": "Samba",
            "growth_stage": "vegetative_tillering",
            "soil_type": "Alluvial",
            "soil_ph": 6.8,
            "soil_moisture_pct": 74.0,
            "nitrogen_kg_ha": 135.0,
            "phosphorus_kg_ha": 45.0,
            "potassium_kg_ha": 42.0,
            "temperature_c": 30.5,
            "humidity_pct": 82.0,
            "forecast_rain_expected_mm": 5.0,
            "forecast_rain_prob_pct": 20
        }

    def test_post_recommendations_root_endpoint(self):
        """Tests POST /recommendations returns 200 and valid schema."""
        resp = self.client.post("/recommendations", json=self.valid_body)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["rule_type"], "agronomic_expert_system")
        self.assertEqual(data["district"], "Thanjavur")
        self.assertEqual(data["growth_stage"], "vegetative_tillering")
        self.assertIsInstance(data["irrigation_advisory"], list)
        self.assertIsInstance(data["fertilizer_advisory"], list)
        self.assertIsInstance(data["soil_health_advisory"], list)
        self.assertIsInstance(data["pest_monitoring_alerts"], list)
        self.assertIn("TNAU", data["authoritative_source"])
        self.assertIn("do not guarantee", data["disclaimer"].lower())

    def test_post_recommendations_v1_endpoint(self):
        """Tests POST /api/v1/recommendations returns 200 and matching schema."""
        resp = self.client.post("/api/v1/recommendations/", json=self.valid_body)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["rule_type"], "agronomic_expert_system")

    def test_invalid_district_validation(self):
        """Tests 422 error on invalid/unsupported district."""
        bad_payload = dict(self.valid_body)
        bad_payload["district"] = "London"
        resp = self.client.post("/recommendations", json=bad_payload)
        self.assertEqual(resp.status_code, 422)

    def test_out_of_range_soil_ph_validation(self):
        """Tests 422 error on impossible soil pH."""
        bad_payload = dict(self.valid_body)
        bad_payload["soil_ph"] = 13.5  # Max is 9.5
        resp = self.client.post("/recommendations", json=bad_payload)
        self.assertEqual(resp.status_code, 422)

    def test_missing_required_soil_moisture(self):
        """Tests 422 error when required soil_moisture_pct is omitted."""
        bad_payload = dict(self.valid_body)
        del bad_payload["soil_moisture_pct"]
        resp = self.client.post("/recommendations", json=bad_payload)
        self.assertEqual(resp.status_code, 422)

    @patch("app.api.v1.endpoints.recommendations.weather_service.get_forecast")
    @patch("app.api.v1.endpoints.recommendations.weather_service.get_current_weather")
    def test_weather_enrichment_fallback_on_network_failure(self, mock_curr, mock_fore):
        """Tests endpoint gracefully handles external weather service downtime."""
        mock_curr.side_effect = Exception("Connection refused / upstream down")
        mock_fore.side_effect = Exception("Timeout")

        body_missing_weather = dict(self.valid_body)
        body_missing_weather["temperature_c"] = None
        body_missing_weather["humidity_pct"] = None
        body_missing_weather["forecast_rain_expected_mm"] = None

        resp = self.client.post("/recommendations", json=body_missing_weather)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data["data_limitations"]) >= 1)
        self.assertTrue(any("unavailable" in lim.lower() for lim in data["data_limitations"]))


if __name__ == "__main__":
    unittest.main()
