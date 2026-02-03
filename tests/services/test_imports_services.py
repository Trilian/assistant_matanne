import pytest
import importlib

# Liste des modules de services à tester (corrigé pour correspondre aux fichiers réels)
MODULES_SERVICES = [
    "action_history",
    "auth",
    "backup",
    "barcode",
    "batch_cooking",
    "budget",
    "calendar_sync",
    "courses",
    "courses_intelligentes",
    "facture_ocr",
    "garmin_sync",
    "inventaire",
    "notifications",
    "notifications_push",
    "openfoodfacts",
    "pdf_export",
    "planning",
    "planning_unified",
    "predictions",
    "push_notifications",
    "pwa",
    "rapports_pdf",
    "realtime_sync",
    "recettes",
    "recipe_import",
    "suggestions_ia",
    "types",
    "user_preferences",
    "weather",
]

@pytest.mark.parametrize("module_name", MODULES_SERVICES)
def test_import_services_modules(module_name):
    """Test paramétrique d'import des modules de services"""
    module = importlib.import_module(f"src.services.{module_name}")
    assert module is not None
