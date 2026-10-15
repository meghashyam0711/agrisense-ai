"""
AgriSense-AI: Bilingual Localization (i18n) Endpoints.
Serves English and Tamil translations for navigation, forms, validation messages,
recommendations, and error states.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, status
from ....core.i18n import get_all_translations, I18N_BACKEND_DICTIONARY

router = APIRouter()


@router.get(
    "/languages",
    response_model=List[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="List supported languages",
    description="Returns metadata of all supported languages in AgriSense-AI."
)
def list_supported_languages() -> List[Dict[str, str]]:
    """Returns supported languages."""
    return [
        {"code": "en", "name": "English", "native_name": "English"},
        {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"}
    ]


@router.get(
    "/{lang}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Get translations dictionary",
    description="Retrieves the complete translation dictionary for English (en) or Tamil (ta)."
)
def get_language_dictionary(lang: str) -> Dict[str, str]:
    """Returns translation dictionary for requested language."""
    if lang.lower() not in I18N_BACKEND_DICTIONARY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang}' is not supported. Supported languages: en, ta."
        )
    return get_all_translations(lang)
