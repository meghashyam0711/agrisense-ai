"""
AgriSense-AI: Bilingual Localization (i18n) Automated Tests.
Validates English and Tamil dictionaries, Unicode character integrity,
localization API endpoints, and fallback behavior.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend and project root are importable
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.i18n import (
    I18N_BACKEND_DICTIONARY,
    get_translation,
    get_all_translations
)
from main import app


class TestBilingualLocalization(unittest.TestCase):
    """Unit tests for the bilingual translation system and Unicode rendering."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_supported_languages_list(self):
        """Tests GET /api/v1/i18n/languages returns English and Tamil."""
        res = self.client.get("/api/v1/i18n/languages")
        self.assertEqual(res.status_code, 200)
        langs = res.json()
        codes = [item["code"] for item in langs]
        self.assertIn("en", codes)
        self.assertIn("ta", codes)

        # Check native name in Tamil renders correctly
        ta_meta = next(item for item in langs if item["code"] == "ta")
        self.assertEqual(ta_meta["native_name"], "தமிழ்")

    def test_english_dictionary_endpoint(self):
        """Tests GET /api/v1/i18n/en returns complete English dictionary."""
        res = self.client.get("/api/v1/i18n/en")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["brand_title"], "AgriSense-AI")
        self.assertIn("val_ph_range", data)
        self.assertIn("cat_irrigation", data)
        self.assertIn("err_server_error", data)

    def test_tamil_dictionary_endpoint_and_unicode_rendering(self):
        """Tests GET /api/v1/i18n/ta returns complete Tamil dictionary with valid Unicode."""
        res = self.client.get("/api/v1/i18n/ta")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Check critical Tamil Unicode text
        self.assertEqual(data["brand_title"], "அக்ரிசென்ஸ்-AI")
        self.assertEqual(data["brand_subtitle"], "நெல் துல்லிய விவசாயம்")
        self.assertEqual(data["nav_dashboard"], "முகப்பு")
        self.assertEqual(data["nav_prediction"], "விளைச்சல் கணிப்பு")
        self.assertEqual(data["cat_irrigation"], "பாசன மேலாண்மை (AWD)")

        # Verify validation error messages render in Tamil
        self.assertIn("தமிழ்நாடு", data["val_required_district"])
        self.assertIn("மண் pH அளவு", data["val_ph_range"])

    def test_unsupported_language_returns_404(self):
        """Tests GET /api/v1/i18n/{unsupported} returns 404."""
        res = self.client.get("/api/v1/i18n/french")
        self.assertEqual(res.status_code, 404)
        self.assertIn("not supported", res.json()["detail"].lower())

    def test_translation_helper_fallback(self):
        """Tests get_translation helper falls back to English when key is missing in target."""
        # Existing key in both
        self.assertEqual(get_translation("nav_weather", "ta"), "வானிலை")
        self.assertEqual(get_translation("nav_weather", "en"), "Weather")

        # Fallback to key itself if not found anywhere
        self.assertEqual(get_translation("non_existent_key_xyz", "ta"), "non_existent_key_xyz")

    def test_dictionary_key_parity(self):
        """Verifies that both English and Tamil dictionaries share essential core keys."""
        en_keys = set(I18N_BACKEND_DICTIONARY["en"].keys())
        ta_keys = set(I18N_BACKEND_DICTIONARY["ta"].keys())

        # Essential keys that must exist in both
        mandatory_keys = [
            "brand_title", "nav_dashboard", "nav_prediction", "nav_weather",
            "nav_soil", "nav_recommendations", "nav_history", "nav_farms",
            "label_district", "label_season", "label_area", "label_soil_ph",
            "val_required_district", "val_ph_range", "val_moisture_range",
            "cat_irrigation", "cat_fertilizer", "cat_soil_health", "cat_pest_disease",
            "err_server_error", "err_validation_failed", "msg_success_saved"
        ]

        for k in mandatory_keys:
            self.assertIn(k, en_keys, f"Missing key '{k}' in English dictionary")
            self.assertIn(k, ta_keys, f"Missing key '{k}' in Tamil dictionary")


if __name__ == "__main__":
    unittest.main()
