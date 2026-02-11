import pytest
import importlib

# Liste des modules de services à tester (corrigé pour correspondre aux fichiers réels)
MODULES_SERVICES = [
    "backup",
    "base",  # Package unifié (remplace base_ai_service.py, types.py, io_service.py)
    "batch_cooking",
    "budget",
    "calendrier",
    "courses",  # Package unifie (remplace courses.py, courses_intelligentes.py)
    "garmin",  # Package unifié (remplace garmin_sync.py, garmin_sync_utils.py)
    "integrations",  # Package unifié (codes-barres, openfoodfacts, facture_ocr)
    "inventaire",
    "notifications",  # Package unifié qui remplace notifications.py, notifications_push.py, push_notifications.py
    "rapports",  # Package unifié qui remplace pdf_export.py, rapports_pdf.py
    "planning",  # Package unifie (remplace planning.py, planning_unified.py, planning_utils.py)
    # predictions -> fusionné dans suggestions/
    "web",  # Package unifié (sync + pwa fusionnés)
    "recettes",  # Package unifié (inclut import_url.py via recettes.import_url)
    "suggestions",
    "utilisateur",  # Package unifié (remplace auth.py, action_history.py, user_preferences.py)
    "weather",  # Package unifié (remplace weather.py, weather_utils.py)
]

@pytest.mark.parametrize("module_name", MODULES_SERVICES)
def test_import_services_modules(module_name):
    """Test paramétrique d'import des modules de services"""
    module = importlib.import_module(f"src.services.{module_name}")
    assert module is not None
