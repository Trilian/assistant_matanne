# Rapport d'Analyse de Couverture de Tests

**Seuil de couverture**: 80.0%
**Seuil de taille de fichier**: 1000 lignes

## Résumé Global

## .

- **Fichiers totaux**: 1
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 1
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `app.py` - 📊 0.0% couverture, ❌ Pas de tests

###   api

- **Fichiers totaux**: 2
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 2
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `api/main.py` - 📊 0.0% couverture
  - Tests: test_main.py
- `api/rate_limiting.py` - 📊 0.0% couverture
  - Tests: test_rate_limiting.py, test_rate_limiting_comprehensive.py

###   utils

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `utils/recipe_importer.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/constants.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/image_generator.py` - 📊 0.0% couverture
  - Tests: test_image_generator_deep_v2.py
- `utils/media.py` - 📊 0.0% couverture
  - Tests: test_media_deep.py

####     utils/helpers

- **Fichiers totaux**: 6
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 6
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `utils/helpers/stats.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/helpers/food.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/helpers/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/helpers/strings.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/helpers/data.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/helpers/dates.py` - 📊 0.0% couverture, ❌ Pas de tests

####     utils/validators

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `utils/validators/food.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/validators/common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/validators/dates.py` - 📊 0.0% couverture, ❌ Pas de tests

####     utils/formatters

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `utils/formatters/units.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/formatters/numbers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/formatters/text.py` - 📊 0.0% couverture, ❌ Pas de tests
- `utils/formatters/dates.py` - 📊 0.0% couverture, ❌ Pas de tests

###   services

- **Fichiers totaux**: 41
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 41
- **Fichiers volumineux (>1000 lignes)**: 5

### ⚠️ Fichiers nécessitant une attention:

- `services/courses.py` - 📊 0.0% couverture
  - Tests: test_courses_service.py, test_courses_intelligentes_coverage.py, test_courses_intelligentes_service.py
- `services/budget_utils.py` - 📊 0.0% couverture
  - Tests: test_budget_utils.py
- `services/barcode.py` - 📊 0.0% couverture
  - Tests: test_barcode_coverage.py, test_barcode_coverage_deep.py, test_barcode_service.py
- `services/realtime_sync.py` - 📊 0.0% couverture
  - Tests: test_realtime_sync_coverage.py
- `services/calendar_sync.py` - 📏 1295 lignes, 📊 0.0% couverture
  - Tests: test_calendar_sync_service.py, test_calendar_sync_coverage.py, test_calendar_sync_comprehensive.py
- `services/base_service.py` - 📊 0.0% couverture
  - Tests: test_base_service.py, test_base_service_coverage.py
- `services/garmin_sync_utils.py` - 📊 0.0% couverture
  - Tests: test_garmin_sync_utils_integration.py, test_garmin_sync_utils.py
- `services/io_service.py` - 📊 0.0% couverture
  - Tests: test_io_service.py, test_io_service_coverage.py
- `services/push_notifications_utils.py` - 📊 0.0% couverture
  - Tests: test_push_notifications_utils.py
- `services/planning_unified.py` - 📊 0.0% couverture
  - Tests: test_planning_unified_service.py, test_planning_unified_coverage.py
- `services/auth.py` - 📊 0.0% couverture
  - Tests: test_auth_comprehensive.py, test_auth_service.py, test_auth_coverage.py
- `services/recettes_utils.py` - 📊 0.0% couverture
  - Tests: test_recettes_utils.py
- `services/weather_utils.py` - 📊 0.0% couverture
  - Tests: test_weather_utils.py, test_weather_utils_full.py
- `services/types.py` - 📊 0.0% couverture
  - Tests: test_types_service.py, test_types_coverage.py
- `services/garmin_sync.py` - 📊 0.0% couverture
  - Tests: test_garmin_sync_utils_integration.py, test_garmin_sync_coverage.py, test_garmin_sync_utils.py, test_garmin_sync.py
- `services/backup_utils.py` - 📊 0.0% couverture
  - Tests: test_backup_utils.py
- `services/user_preferences.py` - 📊 0.0% couverture
  - Tests: test_user_preferences_service.py, test_user_preferences_coverage.py
- `services/batch_cooking_utils.py` - 📊 0.0% couverture
  - Tests: test_batch_cooking_utils.py
- `services/batch_cooking.py` - 📊 0.0% couverture
  - Tests: test_batch_cooking_utils.py, test_batch_cooking_integration.py, test_batch_cooking_service.py, test_batch_cooking_full_coverage.py, test_batch_cooking_coverage.py
- `services/inventaire.py` - 📏 1096 lignes, 📊 0.0% couverture
  - Tests: test_inventaire_sqlite_int.py, test_inventaire_integration.py, test_inventaire_methods.py, test_inventaire_service.py, test_inventaire_coverage_deep.py
- `services/backup.py` - 📊 0.0% couverture
  - Tests: test_backup_integration.py, test_backup_service.py, test_backup_coverage.py, test_backup_utils.py
- `services/budget.py` - 📏 1154 lignes, 📊 0.0% couverture
  - Tests: test_budget_integration.py, test_budget_coverage_deep.py, test_budget_service.py, test_budget_utils.py, test_budget_coverage.py, test_budget_comprehensive.py, test_budget_methods.py, test_budget_extra.py
- `services/facture_ocr.py` - 📊 0.0% couverture
  - Tests: test_facture_ocr_coverage.py
- `services/action_history.py` - 📊 0.0% couverture
  - Tests: test_action_history_service.py, test_action_history_coverage.py
- `services/notifications.py` - 📊 0.0% couverture
  - Tests: test_notifications_push_coverage.py, test_notifications_coverage.py, test_notifications_service.py, test_notifications_push_service.py
- `services/weather.py` - 📊 0.0% couverture
  - Tests: test_weather_utils.py, test_weather_utils_full.py, test_weather_service.py, test_weather_coverage.py
- `services/notifications_push.py` - 📊 0.0% couverture
  - Tests: test_notifications_push_coverage.py, test_notifications_push_service.py
- `services/base_ai_service.py` - 📊 0.0% couverture
  - Tests: test_base_ai_service_coverage.py, test_base_ai_service.py
- `services/push_notifications.py` - 📊 0.0% couverture
  - Tests: test_push_notifications_utils.py, test_push_notifications.py, test_push_notifications_deep.py
- `services/pwa.py` - 📊 0.0% couverture
  - Tests: test_pwa.py
- `services/planning.py` - 📊 0.0% couverture
  - Tests: test_planning_extended.py, test_planning_unified_service.py, test_planning_utils.py, test_planning_unified_coverage.py, test_planning_service.py, test_planning_coverage.py
- `services/recipe_import.py` - 📊 0.0% couverture
  - Tests: test_recipe_import_extra.py, test_recipe_import_service.py, test_recipe_import_integration.py
- `services/openfoodfacts.py` - 📊 0.0% couverture
  - Tests: test_openfoodfacts_coverage.py, test_openfoodfacts.py
- `services/rapports_pdf.py` - 📏 1161 lignes, 📊 0.0% couverture
  - Tests: test_rapports_pdf_generation.py, test_rapports_pdf_service.py
- `services/suggestions_ia.py` - 📊 0.0% couverture
  - Tests: test_suggestions_ia_coverage.py, test_suggestions_ia_service.py, test_suggestions_ia_utils.py, test_suggestions_ia_utils_full.py
- `services/suggestions_ia_utils.py` - 📊 0.0% couverture
  - Tests: test_suggestions_ia_utils.py, test_suggestions_ia_utils_full.py
- `services/recettes.py` - 📏 1236 lignes, 📊 0.0% couverture
  - Tests: test_recettes_service.py, test_recettes_coverage_deep.py, test_recettes_utils.py, test_recettes_coverage.py, test_recettes_integration.py, test_recettes_cov_boost.py, test_recettes_import.py
- `services/planning_utils.py` - 📊 0.0% couverture
  - Tests: test_planning_utils.py
- `services/predictions.py` - 📊 0.0% couverture
  - Tests: test_predictions_service.py, test_predictions_coverage.py
- `services/courses_intelligentes.py` - 📊 0.0% couverture
  - Tests: test_courses_intelligentes_coverage.py, test_courses_intelligentes_service.py
- `services/pdf_export.py` - 📊 0.0% couverture
  - Tests: test_pdf_export_db_methods.py, test_pdf_export_coverage_deep.py, test_pdf_export_coverage.py, test_pdf_export_service.py

###   domains

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

####     domains/jeux

- **Fichiers totaux**: 2
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 2
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/jeux/setup.py` - 📊 0.0% couverture
  - Tests: test_setup.py
- `domains/jeux/integration.py` - 📊 0.0% couverture
  - Tests: test_integration.py

#####       domains/jeux/logic

- **Fichiers totaux**: 6
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 6
- **Fichiers volumineux (>1000 lignes)**: 1

### ⚠️ Fichiers nécessitant une attention:

- `domains/jeux/logic/ui_helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/logic/api_service.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/logic/paris_logic.py` - 📏 1265 lignes, 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/logic/loto_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/logic/scraper_loto.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/logic/api_football.py` - 📊 0.0% couverture, ❌ Pas de tests

#####       domains/jeux/ui

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

######         domains/jeux/ui/paris

- **Fichiers totaux**: 7
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 7
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/jeux/ui/paris/dashboard.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/sync.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/gestion.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/crud.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/paris/prediction.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/jeux/ui/loto

- **Fichiers totaux**: 7
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 7
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/jeux/ui/loto/sync.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/simulation.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/crud.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/statistiques.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/jeux/ui/loto/generateur.py` - 📊 0.0% couverture, ❌ Pas de tests

####     domains/famille

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

#####       domains/famille/logic

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/logic/activites_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/logic/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/logic/routines_logic.py` - 📊 0.0% couverture, ❌ Pas de tests

#####       domains/famille/ui

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/ui/jules_planning.py` - 📊 0.0% couverture
  - Tests: test_jules_planning.py, test_jules_planning_extended.py
- `domains/famille/ui/activites.py` - 📊 0.0% couverture
  - Tests: test_activites.py
- `domains/famille/ui/hub_famille.py` - 📊 0.0% couverture
  - Tests: test_hub_famille.py
- `domains/famille/ui/routines.py` - 📊 0.0% couverture
  - Tests: test_routines.py

######         domains/famille/ui/suivi_perso

- **Fichiers totaux**: 6
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 6
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/ui/suivi_perso/alimentation.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/suivi_perso/dashboard.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/suivi_perso/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/suivi_perso/activities.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/suivi_perso/settings.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/suivi_perso/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/famille/ui/weekend

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/ui/weekend/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/weekend/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/weekend/ai_service.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/weekend/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/famille/ui/achats_famille

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/ui/achats_famille/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/achats_famille/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/achats_famille/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/famille/ui/jules

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/famille/ui/jules/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/jules/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/jules/ai_service.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/famille/ui/jules/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests

####     domains/utils

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

#####       domains/utils/logic

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/utils/logic/accueil_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/utils/logic/parametres_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/utils/logic/barcode_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/utils/logic/rapports_logic.py` - 📊 0.0% couverture, ❌ Pas de tests

#####       domains/utils/ui

- **Fichiers totaux**: 5
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 5
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/utils/ui/barcode.py` - 📊 0.0% couverture
  - Tests: test_barcode.py
- `domains/utils/ui/parametres.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/utils/ui/notifications_push.py` - 📊 0.0% couverture
  - Tests: test_notifications_push.py
- `domains/utils/ui/accueil.py` - 📊 0.0% couverture
  - Tests: test_accueil.py
- `domains/utils/ui/rapports.py` - 📊 0.0% couverture, ❌ Pas de tests

####     domains/maison

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

#####       domains/maison/logic

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/maison/logic/projets_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/maison/logic/entretien_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/maison/logic/jardin_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/maison/logic/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests

#####       domains/maison/ui

- **Fichiers totaux**: 9
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 9
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/maison/ui/meubles.py` - 📊 0.0% couverture
  - Tests: test_meubles.py
- `domains/maison/ui/entretien.py` - 📊 0.0% couverture
  - Tests: test_entretien.py
- `domains/maison/ui/jardin_zones.py` - 📊 0.0% couverture
  - Tests: test_jardin_zones.py
- `domains/maison/ui/energie.py` - 📊 0.0% couverture
  - Tests: test_energie.py
- `domains/maison/ui/hub_maison.py` - 📊 0.0% couverture
  - Tests: test_hub_maison.py
- `domains/maison/ui/jardin.py` - 📊 0.0% couverture
  - Tests: test_jardin_zones.py, test_jardin.py
- `domains/maison/ui/scan_factures.py` - 📊 0.0% couverture
  - Tests: test_scan_factures.py
- `domains/maison/ui/eco_tips.py` - 📊 0.0% couverture
  - Tests: test_eco_tips.py
- `domains/maison/ui/projets.py` - 📊 0.0% couverture
  - Tests: test_projets.py

######         domains/maison/ui/depenses

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/maison/ui/depenses/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/maison/ui/depenses/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/maison/ui/depenses/crud.py` - 📊 0.0% couverture, ❌ Pas de tests

####     domains/cuisine

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

#####       domains/cuisine/logic

- **Fichiers totaux**: 7
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 7
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/logic/batch_cooking_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/recettes_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/courses_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/inventaire_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/planning_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/schemas.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/logic/planificateur_repas_logic.py` - 📊 0.0% couverture, ❌ Pas de tests

#####       domains/cuisine/ui

- **Fichiers totaux**: 2
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 2
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/ui/recettes_import.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/batch_cooking_detaille.py` - 📊 0.0% couverture
  - Tests: test_batch_cooking_detaille.py

######         domains/cuisine/ui/planificateur_repas

- **Fichiers totaux**: 5
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 5
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/ui/planificateur_repas/generation.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/planificateur_repas/pdf.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/planificateur_repas/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/planificateur_repas/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/planificateur_repas/preferences.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/cuisine/ui/inventaire

- **Fichiers totaux**: 11
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 11
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/ui/inventaire/categories.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/historique.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/stock.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/notifications.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/alertes.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/suggestions.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/predictions.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/photos.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/inventaire/tools.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/cuisine/ui/courses

- **Fichiers totaux**: 8
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 8
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/ui/courses/historique.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/realtime.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/liste_active.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/outils.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/planning.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/suggestions_ia.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/courses/modeles.py` - 📊 0.0% couverture, ❌ Pas de tests

######         domains/cuisine/ui/recettes

- **Fichiers totaux**: 6
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 6
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/cuisine/ui/recettes/ajout.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/recettes/liste.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/recettes/helpers.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/recettes/generation_image.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/recettes/detail.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/cuisine/ui/recettes/generation_ia.py` - 📊 0.0% couverture, ❌ Pas de tests

####     domains/planning

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

#####       domains/planning/logic

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/planning/logic/vue_ensemble_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/planning/logic/vue_semaine_logic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/planning/logic/calendrier_unifie_logic.py` - 📊 0.0% couverture
  - Tests: test_calendrier_unifie_logic.py

#####       domains/planning/ui

- **Fichiers totaux**: 2
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 2
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/planning/ui/vue_ensemble.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/planning/ui/vue_semaine.py` - 📊 0.0% couverture
  - Tests: test_vue_semaine.py

######         domains/planning/ui/components

- **Fichiers totaux**: 0
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 0
- **Fichiers volumineux (>1000 lignes)**: 0

######         domains/planning/ui/calendrier_unifie

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `domains/planning/ui/calendrier_unifie/_common.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/planning/ui/calendrier_unifie/components.py` - 📊 0.0% couverture, ❌ Pas de tests
- `domains/planning/ui/calendrier_unifie/data.py` - 📊 0.0% couverture, ❌ Pas de tests

###   ui

- **Fichiers totaux**: 2
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 2
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `ui/domain.py` - 📊 0.0% couverture
  - Tests: test_domain_ui.py
- `ui/tablet_mode.py` - 📊 0.0% couverture
  - Tests: test_tablet_mode_deep.py, test_tablet_mode.py

####     ui/feedback

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `ui/feedback/spinners.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/feedback/toasts.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/feedback/progress.py` - 📊 0.0% couverture, ❌ Pas de tests

####     ui/components

- **Fichiers totaux**: 8
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 8
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `ui/components/forms.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/dynamic.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/dashboard_widgets.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/camera_scanner.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/atoms.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/layouts.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/data.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/components/google_calendar_sync.py` - 📊 0.0% couverture, ❌ Pas de tests

####     ui/core

- **Fichiers totaux**: 3
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 3
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `ui/core/base_module.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/core/base_io.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/core/base_form.py` - 📊 0.0% couverture, ❌ Pas de tests

####     ui/layout

- **Fichiers totaux**: 5
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 5
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `ui/layout/styles.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/layout/init.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/layout/header.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/layout/footer.py` - 📊 0.0% couverture, ❌ Pas de tests
- `ui/layout/sidebar.py` - 📊 0.0% couverture, ❌ Pas de tests

###   core

- **Fichiers totaux**: 21
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 21
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `core/offline.py` - 📊 0.0% couverture
  - Tests: test_offline.py, test_offline_deep.py
- `core/multi_tenant.py` - 📊 0.0% couverture
  - Tests: test_multi_tenant_deep.py, test_multi_tenant.py
- `core/constants.py` - 📊 0.0% couverture
  - Tests: test_constants.py
- `core/database.py` - 📊 0.0% couverture
  - Tests: test_database_deep.py, test_database.py, test_database_extended.py
- `core/state.py` - 📊 0.0% couverture
  - Tests: test_state.py
- `core/notifications.py` - 📊 0.0% couverture
  - Tests: test_notifications.py, test_notifications_deep.py
- `core/performance_optimizations.py` - 📊 0.0% couverture
  - Tests: test_performance_optimizations_deep.py, test_performance_optimizations.py
- `core/cache.py` - 📊 0.0% couverture
  - Tests: test_cache_deep.py, test_cache_multi.py, test_cache_multi_deep.py, test_cache_coverage.py, test_cache.py
- `core/validation.py` - 📊 0.0% couverture
  - Tests: test_validation.py, test_validation_pydantic.py
- `core/logging.py` - 📊 0.0% couverture
  - Tests: test_logging.py
- `core/performance.py` - 📊 0.0% couverture
  - Tests: test_performance_deep.py, test_performance.py, test_performance_optimizations_deep.py, test_performance_optimizations.py
- `core/decorators.py` - 📊 0.0% couverture
  - Tests: test_decorators_basic.py, test_decorators.py, test_decorators_extended.py, test_decorators_deep.py, test_decorators_edge_cases.py
- `core/lazy_loader.py` - 📊 0.0% couverture
  - Tests: test_lazy_loader_extended.py, test_lazy_loader_deep.py, test_lazy_loader.py
- `core/cache_multi.py` - 📊 0.0% couverture
  - Tests: test_cache_multi.py, test_cache_multi_deep.py
- `core/errors_base.py` - 📊 0.0% couverture
  - Tests: test_errors_base.py
- `core/config.py` - 📊 0.0% couverture
  - Tests: test_config_extended.py, test_config_deep.py, test_config.py
- `core/redis_cache.py` - 📊 0.0% couverture
  - Tests: test_redis_cache_deep.py, test_redis_cache.py
- `core/sql_optimizer.py` - 📊 0.0% couverture
  - Tests: test_sql_optimizer_deep.py, test_sql_optimizer.py
- `core/ai_agent.py` - 📊 0.0% couverture
  - Tests: test_ai_agent.py, test_ai_agent_sync.py
- `core/errors.py` - 📊 0.0% couverture
  - Tests: test_errors.py, test_errors_deep.py, test_errors_base.py, test_errors_advanced.py
- `core/validators_pydantic.py` - 📊 0.0% couverture
  - Tests: test_validators_pydantic_deep.py, test_validators_pydantic.py

####     core/ai

- **Fichiers totaux**: 4
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 4
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `core/ai/rate_limit.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/ai/cache.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/ai/client.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/ai/parser.py` - 📊 0.0% couverture, ❌ Pas de tests

####     core/models

- **Fichiers totaux**: 14
- **Couverture moyenne**: 0.00%
- **Fichiers sous le seuil**: 14
- **Fichiers volumineux (>1000 lignes)**: 0

### ⚠️ Fichiers nécessitant une attention:

- `core/models/users.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/courses.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/maison_extended.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/sante.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/nouveaux.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/user_preferences.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/batch_cooking.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/inventaire.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/famille.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/planning.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/maison.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/recettes.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/jeux.py` - 📊 0.0% couverture, ❌ Pas de tests
- `core/models/base.py` - 📊 0.0% couverture, ❌ Pas de tests

## 📋 Recommandations

### Fichiers à diviser (>1000 lignes):

1. `services/calendar_sync.py` (1295 lignes)
2. `domains/jeux/logic/paris_logic.py` (1265 lignes)
3. `services/recettes.py` (1236 lignes)
4. `services/rapports_pdf.py` (1161 lignes)
5. `services/budget.py` (1154 lignes)
6. `services/inventaire.py` (1096 lignes)

### Fichiers sans tests ou avec faible couverture (<80%):

1. `app.py` - ❌ Aucun test
2. `api/main.py` - 📊 0.0%
3. `api/rate_limiting.py` - 📊 0.0%
4. `utils/recipe_importer.py` - ❌ Aucun test
5. `utils/constants.py` - ❌ Aucun test
6. `utils/image_generator.py` - 📊 0.0%
7. `utils/media.py` - 📊 0.0%
8. `utils/helpers/stats.py` - ❌ Aucun test
9. `utils/helpers/food.py` - ❌ Aucun test
10. `utils/helpers/helpers.py` - ❌ Aucun test
11. `utils/helpers/strings.py` - ❌ Aucun test
12. `utils/helpers/data.py` - ❌ Aucun test
13. `utils/helpers/dates.py` - ❌ Aucun test
14. `utils/validators/food.py` - ❌ Aucun test
15. `utils/validators/common.py` - ❌ Aucun test
16. `utils/validators/dates.py` - ❌ Aucun test
17. `utils/formatters/units.py` - ❌ Aucun test
18. `utils/formatters/numbers.py` - ❌ Aucun test
19. `utils/formatters/text.py` - ❌ Aucun test
20. `utils/formatters/dates.py` - ❌ Aucun test