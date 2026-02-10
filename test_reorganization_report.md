# Plan de Réorganisation des Tests

## Résumé

- **Fichiers source**: 228
- **Fichiers de test**: 375
- **Fichiers avec tests**: 174
- **Fichiers sans tests**: 54
- **Fonctions de test totales**: 14809

## Actions Recommandées

### 1. Créer 54 fichiers de test manquants

Fichiers sans tests:

- `utils/recipe_importer.py` → `utils/test_recipe_importer.py`
- `utils/helpers/stats.py` → `utils/helpers/test_stats.py`
- `utils/helpers/food.py` → `utils/helpers/test_food.py`
- `utils/helpers/strings.py` → `utils/helpers/test_strings.py`
- `utils/helpers/dates.py` → `utils/helpers/test_dates.py`
- `utils/validators/food.py` → `utils/validators/test_food.py`
- `utils/validators/common.py` → `utils/validators/test_common.py`
- `utils/validators/dates.py` → `utils/validators/test_dates.py`
- `utils/formatters/units.py` → `utils/formatters/test_units.py`
- `utils/formatters/numbers.py` → `utils/formatters/test_numbers.py`
- `utils/formatters/text.py` → `utils/formatters/test_text.py`
- `utils/formatters/dates.py` → `utils/formatters/test_dates.py`
- `domains/jeux/logic/api_service.py` → `domains/jeux/logic/test_api_service.py`
- `domains/jeux/ui/paris/sync.py` → `domains/jeux/ui/paris/test_sync.py`
- `domains/jeux/ui/paris/gestion.py` → `domains/jeux/ui/paris/test_gestion.py`
- `domains/jeux/ui/paris/crud.py` → `domains/jeux/ui/paris/test_crud.py`
- `domains/jeux/ui/paris/prediction.py` → `domains/jeux/ui/paris/test_prediction.py`
- `domains/jeux/ui/loto/sync.py` → `domains/jeux/ui/loto/test_sync.py`
- `domains/jeux/ui/loto/simulation.py` → `domains/jeux/ui/loto/test_simulation.py`
- `domains/jeux/ui/loto/crud.py` → `domains/jeux/ui/loto/test_crud.py`
- ... et 34 autres

### 2. Consolider 114 fichiers avec tests dupliqués

- `app.py`:
  - Garder: `core/test_app.py`
  - Fusionner: `core/test_app_coverage.py`, `core/test_app_main.py`
- `api/main.py`:
  - Garder: `api/test_main.py`
  - Fusionner: `e2e/test_main_flows.py`
- `api/rate_limiting.py`:
  - Garder: `api/test_rate_limiting_comprehensive.py`
  - Fusionner: `api/test_rate_limiting.py`
- `services/courses.py`:
  - Garder: `services/test_courses_intelligentes_service.py`
  - Fusionner: `domains/cuisine/test_courses_ui.py`, `services/test_courses_service.py`, `domains/maison/ui/test_courses.py`, `services/test_courses_intelligentes_coverage.py`, `domains/cuisine/test_courses_logic.py`
- `services/barcode.py`:
  - Garder: `domains/utils/test_barcode_logic_coverage.py`
  - Fusionner: `services/test_barcode_service.py`, `domains/utils/test_barcode_logic.py`, `services/test_barcode_coverage_deep.py`, `domains/utils/ui/test_barcode.py`, `services/test_barcode_coverage.py`
- `services/calendar_sync.py`:
  - Garder: `services/test_calendar_sync_coverage.py`
  - Fusionner: `services/test_calendar_sync_comprehensive.py`, `services/test_calendar_sync_service.py`
- `services/base_service.py`:
  - Garder: `services/test_base_service_coverage.py`
  - Fusionner: `services/test_base_service.py`
- `services/garmin_sync_utils.py`:
  - Garder: `services/test_garmin_sync_utils.py`
  - Fusionner: `services/test_garmin_sync_utils_integration.py`
- `services/io_service.py`:
  - Garder: `services/test_io_service_coverage.py`
  - Fusionner: `services/test_io_service.py`
- `services/planning_unified.py`:
  - Garder: `services/test_planning_unified_coverage.py`
  - Fusionner: `services/test_planning_unified_service.py`
- ... et 104 autres
