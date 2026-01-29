"""
Script pour réorganiser les tests selon PLAN_ORGANISATION_TESTS.md
97 fichiers → ~32 fichiers organisés dans des dossiers
"""
import os
import shutil
from pathlib import Path

BASE = Path("tests")

# Créer structure
FOLDERS = ["logic", "integration", "services", "core", "ui", "utils", "e2e"]
for folder in FOLDERS:
    (BASE / folder).mkdir(exist_ok=True)
    (BASE / folder / "__init__.py").touch()

# Plan de déplacement
MOVES = {
    # Tests logic (garder séparés, ne pas fusionner)
    "logic": [
        "test_all_logic_clean.py",
        "test_logic_modules_pure.py",
        "test_all_logic_modules.py",
    ],
    
    # Tests e2e
    "e2e": [
        "test_e2e.py",
        "test_e2e_streamlit.py",
    ],
    
    # Tests services (accès BD)
    "services": [
        "test_recettes.py",
        "test_inventaire.py",
        "test_courses.py",
        "test_planning.py",
        "test_planning_unified.py",
        "test_base_service.py",
        "test_base_service_unified.py",
        "test_services_comprehensive.py",
        "test_rapports_pdf_service.py",
        "test_suggestions_ia_service.py",
        "test_notifications_service.py",
        "test_backup.py",
        "test_predictions.py",
        "test_weather.py",
    ],
    
    # Tests core (infrastructure)
    "core": [
        "test_database.py",
        "test_cache.py",
        "test_cache_multi.py",
        "test_decorators.py",
        "test_state.py",
        "test_lazy_loader.py",
        "test_errors_base.py",
        "test_ai_cache.py",
        "test_ai_parser.py",
        "test_ai_agent_sync.py",
        "test_parser_ai.py",
    ],
    
    # Tests UI
    "ui": [
        "test_ui_components.py",
        "test_ui_atoms.py",
        "test_ui_forms.py",
        "test_ui_base_form.py",
        "test_ui_layouts.py",
        "test_ui_data.py",
        "test_ui_progress.py",
        "test_ui_spinners.py",
        "test_ui_toasts.py",
        "test_ui_tablet_mode.py",
        "test_dashboard_widgets.py",
        "test_planning_components.py",
    ],
    
    # Tests utils
    "utils": [
        "test_formatters.py",
        "test_formatters_dates.py",
        "test_formatters_numbers.py",
        "test_formatters_text.py",
        "test_formatters_units.py",
        "test_validators.py",
        "test_validators_common.py",
        "test_validators_food.py",
        "test_validators_pydantic.py",
        "test_utils_validators.py",
        "test_helpers.py",
        "test_helpers_data.py",
        "test_helpers_stats.py",
        "test_dates_helpers.py",
        "test_food_helpers.py",
        "test_utils_helpers_extended.py",
        "test_utils_and_pydantic_fix.py",
        "test_image_recipe_utils.py",
        "test_recipe_import.py",
        "test_barcode.py",
    ],
    
    # Tests integration (modules complets)
    "integration": [
        "test_modules_cuisine.py",
        "test_modules_famille.py",
        "test_modules_maison.py",
        "test_modules_planning.py",
        "test_modules_integration.py",
        "test_module_cuisine_courses.py",
        "test_module_cuisine_recettes.py",
        "test_module_famille_helpers.py",
        "test_module_maison.py",
        "test_module_maison_helpers.py",
        "test_module_planning_vue_ensemble.py",
        "test_courses_module.py",
        "test_planning_module.py",
        "test_accueil.py",
        "test_famille.py",
        "test_parametres.py",
        "test_rapports.py",
    ],
}

# Déplacer les fichiers
moved = 0
skipped = 0
errors = []

for folder, files in MOVES.items():
    for filename in files:
        src = BASE / filename
        dst = BASE / folder / filename
        
        if src.exists() and src.is_file():
            try:
                shutil.move(str(src), str(dst))
                moved += 1
                print(f"✅ {filename} → {folder}/")
            except Exception as e:
                errors.append(f"❌ {filename}: {e}")
                print(f"❌ {filename}: {e}")
        else:
            skipped += 1
            print(f"⚠️  {filename} n'existe pas")

print(f"\n📊 Résumé:")
print(f"  ✅ Déplacés: {moved}")
print(f"  ⚠️  Ignorés: {skipped}")
print(f"  ❌ Erreurs: {len(errors)}")

if errors:
    print("\nErreurs rencontrées:")
    for err in errors:
        print(f"  {err}")

# Liste des fichiers restants
remaining = [f.name for f in BASE.iterdir() if f.is_file() and f.name.startswith("test_")]
if remaining:
    print(f"\n📁 Fichiers restants à la racine ({len(remaining)}):")
    for f in sorted(remaining):
        print(f"  - {f}")
