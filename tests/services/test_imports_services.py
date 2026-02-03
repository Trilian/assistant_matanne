import pytest
import importlib

# Liste des modules de services à tester
MODULES_SERVICES = [
    "action_history_service",
    "auth_service",
    "backup_service",
    "barcode_service",
    "courses_service",
    "famille_service",
    "inventaire_service",
    "maison_service",
    "notifications_service",
    "notifications_push_service",
    "pdf_export_service",
    "planning_service",
    "planning_unified_service",
    "predictions_service",
    "push_notifications",
    "rapports_pdf",
    "recettes_service",
    "recipe_import_service",
    "reminders",
    "realtime_sync",
    "sante_service",
    "suggestions_ia_service",
    "telegram",
    "types_service",
    "user_preferences_service",
    "users",
    "weather_service",
    "weekly_report",
    "wellness_service",
    "wellness_sync",
    "wellness_utils",
    "wellness_v2",
    "wellness_v3",
]

@pytest.mark.parametrize("module_name", MODULES_SERVICES)
def test_import_services_modules(module_name):
    """Test paramétrique d'import des modules de services"""
    module = importlib.import_module(f"src.services.{module_name}")
    assert module is not None
