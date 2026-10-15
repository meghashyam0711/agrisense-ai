"""
AgriSense-AI: Bilingual Localization Engine (English & Tamil / தமிழ்).
Provides verified agricultural terminology, validation error messages,
recommendation labels, and system status translations.
"""

from typing import Dict, Any, Optional

I18N_BACKEND_DICTIONARY: Dict[str, Dict[str, str]] = {
    "en": {
        # Navigation & Brand
        "brand_title": "AgriSense-AI",
        "brand_subtitle": "Paddy Precision Farming",
        "nav_dashboard": "Dashboard",
        "nav_prediction": "Yield Prediction",
        "nav_weather": "Weather",
        "nav_soil": "Soil Analysis",
        "nav_recommendations": "Recommendations",
        "nav_history": "History",
        "nav_farms": "Farm Profiles",

        # Forms & Labels
        "label_district": "District",
        "label_season": "Cropping Season",
        "label_soil_type": "Soil Type",
        "label_area": "Cultivation Area (Hectares)",
        "label_previous_yield": "Previous Yield (tonnes/ha)",
        "label_soil_ph": "Soil pH",
        "label_soil_moisture": "Soil Moisture (%)",
        "label_nitrogen": "Nitrogen (N) - kg/ha",
        "label_phosphorus": "Phosphorus (P) - kg/ha",
        "label_potassium": "Potassium (K) - kg/ha",
        "label_rainfall": "Seasonal Rainfall (mm)",
        "label_temperature": "Average Temperature (°C)",
        "label_humidity": "Relative Humidity (%)",

        # Farm Profile Labels
        "label_farmer_name": "Farmer Name",
        "label_farm_name": "Farm / Holding Name",
        "label_taluk": "Taluk",
        "label_village": "Village",
        "label_field_name": "Field / Plot Name",
        "label_irrigation_source": "Irrigation Source",
        "label_harvest_date": "Harvest Date",
        "label_actual_yield": "Actual Harvest Yield (tonnes/ha)",
        "label_variance": "Prediction Variance",

        # Recommendation Categories & Urgency
        "cat_irrigation": "Irrigation Guidance (AWD)",
        "cat_fertilizer": "Fertilizer Schedule (TNAU)",
        "cat_soil_health": "Soil Health & Amendments",
        "cat_pest_disease": "Pest & Disease Surveillance",
        "urgency_routine": "Routine Practice",
        "urgency_advisory": "Agronomic Advisory",
        "urgency_warning": "Precautionary Warning",
        "urgency_critical": "Critical Action Required",

        # Validation Messages
        "val_required_district": "Please select a valid Tamil Nadu district.",
        "val_required_season": "Cropping season is required (Kuruvai, Samba, Thaladi, Navarai).",
        "val_area_positive": "Cultivation area must be greater than 0 hectares.",
        "val_ph_range": "Soil pH must be between 4.0 and 9.5.",
        "val_moisture_range": "Soil moisture must be between 10% and 100%.",
        "val_nitrogen_range": "Soil Nitrogen must be between 10 and 300 kg/ha.",
        "val_phosphorus_range": "Soil Phosphorus must be between 5 and 150 kg/ha.",
        "val_potassium_range": "Soil Potassium must be between 10 and 250 kg/ha.",
        "val_rainfall_non_negative": "Rainfall must be non-negative.",
        "val_actual_yield_positive": "Actual harvest yield must be 0 or greater.",
        "val_harvest_date_format": "Harvest date must follow YYYY-MM-DD format.",

        # Error & Status Messages
        "err_server_error": "An internal server error occurred.",
        "err_not_found": "The requested resource was not found.",
        "err_validation_failed": "Input validation failed. Please check submitted parameters.",
        "err_weather_unavailable": "Weather service is currently unavailable; using default regional baselines.",
        "err_db_save_failed": "Failed to persist record to database.",
        "msg_success_saved": "Record saved successfully to database.",
        "msg_record_deleted": "Record deleted successfully.",

        # Authoritative Source & Disclaimer
        "authoritative_source": "Tamil Nadu Agricultural University (TNAU) Crop Production Guide (Paddy) & Agritech Portal",
        "disclaimer": "Agricultural Advisory Disclaimer: Recommendations are rule-based expert guidelines aligned with TNAU benchmarks. They do not guarantee increased crop yield and must be cross-verified with local field observations and Krishi Vigyan Kendra (KVK) advisors."
    },

    "ta": {
        # Navigation & Brand
        "brand_title": "அக்ரிசென்ஸ்-AI",
        "brand_subtitle": "நெல் துல்லிய விவசாயம்",
        "nav_dashboard": "முகப்பு",
        "nav_prediction": "விளைச்சல் கணிப்பு",
        "nav_weather": "வானிலை",
        "nav_soil": "மண் பரிசோதனை",
        "nav_recommendations": "பரிந்துரைகள்",
        "nav_history": "வரலாறு",
        "nav_farms": "பண்ணை விவரங்கள்",

        # Forms & Labels
        "label_district": "மாவட்டம்",
        "label_season": "சாகுபடி பருவம்",
        "label_soil_type": "மண் வகை",
        "label_area": "சாகுபடி பரப்பளவு (ஹெக்டேர்)",
        "label_previous_yield": "முந்தைய விளைச்சல் (டன்/ஹெக்)",
        "label_soil_ph": "மண் அமில/கார நிலை (pH)",
        "label_soil_moisture": "மண் ஈரப்பதம் (%)",
        "label_nitrogen": "தழைச்சத்து (N) - கிலோ/ஹெக்",
        "label_phosphorus": "மணிச்சத்து (P) - கிலோ/ஹெக்",
        "label_potassium": "சாம்பல் சத்து (K) - கிலோ/ஹெக்",
        "label_rainfall": "பருவ மழைப்பொழிவு (மி.மீ)",
        "label_temperature": "சராசரி வெப்பநிலை (°C)",
        "label_humidity": "காற்று ஈரப்பதம் (%)",

        # Farm Profile Labels
        "label_farmer_name": "விவசாயி பெயர்",
        "label_farm_name": "பண்ணை / நிலத்தின் பெயர்",
        "label_taluk": "வட்டம் (தாலுகா)",
        "label_village": "கிராமம்",
        "label_field_name": "வயல் / பாத்தி பெயர்",
        "label_irrigation_source": "பாசன நீர் ஆதாரம்",
        "label_harvest_date": "அறுவடை தேதி",
        "label_actual_yield": "உண்மை அறுவடை விளைச்சல் (டன்/ஹெக்)",
        "label_variance": "கணிப்பு வேறுபாடு",

        # Recommendation Categories & Urgency
        "cat_irrigation": "பாசன மேலாண்மை (AWD)",
        "cat_fertilizer": "உரமிடுதல் அட்டவணை (TNAU)",
        "cat_soil_health": "மண் வள மேம்பாடு & திருத்தங்கள்",
        "cat_pest_disease": "பூச்சி & நோய் கண்காணிப்பு",
        "urgency_routine": "வழக்கமான முறை",
        "urgency_advisory": "விவசாய ஆலோசனை",
        "urgency_warning": "முன்னெச்சரிக்கை",
        "urgency_critical": "அவசரக் களப்பணி தேவை",

        # Validation Messages
        "val_required_district": "சரியான தமிழ்நாடு மாவட்டத்தைத் தேர்ந்தெடுக்கவும்.",
        "val_required_season": "பயிர் சாகுபடி பருவம் அவசியமானது (குறுவை, சம்பா, தாளடி, நவரை).",
        "val_area_positive": "சாகுபடி பரப்பளவு 0 ஹெக்டேருக்கு மேல் இருக்க வேண்டும்.",
        "val_ph_range": "மண் pH அளவு 4.0 முதல் 9.5க்குள் இருக்க வேண்டும்.",
        "val_moisture_range": "மண் ஈரப்பதம் 10% முதல் 100%க்குள் இருக்க வேண்டும்.",
        "val_nitrogen_range": "தழைச்சத்து அளவு 10 முதல் 300 கிலோ/ஹெக் வரை இருக்க வேண்டும்.",
        "val_phosphorus_range": "மணிச்சத்து அளவு 5 முதல் 150 கிலோ/ஹெக் வரை இருக்க வேண்டும்.",
        "val_potassium_range": "சாம்பல் சத்து அளவு 10 முதல் 250 கிலோ/ஹெக் வரை இருக்க வேண்டும்.",
        "val_rainfall_non_negative": "மழைப்பொழிவு 0 அல்லது அதற்கு மேல் இருக்க வேண்டும்.",
        "val_actual_yield_positive": "உண்மை விளைச்சல் 0 அல்லது அதற்கு மேல் இருக்க வேண்டும்.",
        "val_harvest_date_format": "அறுவடை தேதி YYYY-MM-DD வடிவில் இருக்க வேண்டும்.",

        # Error & Status Messages
        "err_server_error": "சேவையகத்தில் எதிர்பாராத பிழை ஏற்பட்டது.",
        "err_not_found": "கோரப்பட்ட தகவல் கிடைக்கவில்லை.",
        "err_validation_failed": "உள்ளீட்டு சரிபார்ப்பு தோல்வியடைந்தது. விவரங்களைச் சரிபார்க்கவும்.",
        "err_weather_unavailable": "வானிலை சேவை தற்போது கிடைக்கவில்லை; பிராந்திய இயல்பு அளவுகள் பயன்படுத்தப்படுகின்றன.",
        "err_db_save_failed": "தரவுத்தளத்தில் பதிவைச் சேமிக்க முடியவில்லை.",
        "msg_success_saved": "பதிவு தரவுத்தளத்தில் வெற்றிகரமாகச் சேமிக்கப்பட்டது.",
        "msg_record_deleted": "பதிவு வெற்றிகரமாக நீக்கப்பட்டது.",

        # Authoritative Source & Disclaimer
        "authoritative_source": "தமிழ்நாடு வேளாண்மைப் பல்கலைக்கழகம் (TNAU) பயிர் சாகுபடி கையேடு (நெல்) & அக்ரிடெக் போர்டல்",
        "disclaimer": "விவசாய ஆலோசனை மறுப்புரை: பரிந்துரைகள் TNAU அளவுகோல்களுடன் கூடிய விதிமுறை வழிகாட்டுதல்கள் மட்டுமே. இவை விளைச்சல் அதிகரிப்பை உறுதிப்படுத்தாது; உள்ளூர் வயல் நிலவரங்கள் மற்றும் கிருஷி விஞ்ஞான் கேந்திரா (KVK) ஆலோசகர்களுடன் உறுதிப்படுத்தப்பட வேண்டும்."
    }
}


def get_translation(key: str, lang: str = "en", default: Optional[str] = None) -> str:
    """Returns localized string for given key and language with fallback to English."""
    lang_dict = I18N_BACKEND_DICTIONARY.get(lang.lower(), I18N_BACKEND_DICTIONARY["en"])
    if key in lang_dict:
        return lang_dict[key]
    # Fallback to English if key missing in selected language
    return I18N_BACKEND_DICTIONARY["en"].get(key, default or key)


def get_all_translations(lang: str = "en") -> Dict[str, str]:
    """Returns entire dictionary for requested language, merging with English fallback."""
    target_lang = lang.lower() if lang.lower() in I18N_BACKEND_DICTIONARY else "en"
    base = dict(I18N_BACKEND_DICTIONARY["en"])
    if target_lang != "en":
        base.update(I18N_BACKEND_DICTIONARY[target_lang])
    return base
