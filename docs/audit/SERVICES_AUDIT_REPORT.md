# Audit Complet — `src/services/`

> **Date**: 2026-02-23 | **Fichiers**: 202 | **LOC totales**: 40 968

---

## 1. Inventaire Fichiers par Package

### Root (`src/services/`)

| Fichier                   | LOC                     |
| ------------------------- | ----------------------- |
| `__init__.py`             | 25                      |
| `accueil_data_service.py` | 47                      |
| **Total**                 | **72 LOC — 2 fichiers** |

### `core/` — Infrastructure (55 fichiers, 9 862 LOC)

| Sous-package        | Fichier                    | LOC |
| ------------------- | -------------------------- | --- |
| **base/**           | `__init__.py`              | 57  |
|                     | `advanced.py`              | 183 |
|                     | `ai_diagnostics.py`        | 98  |
|                     | `ai_mixins.py`             | 83  |
|                     | `ai_prompts.py`            | 35  |
|                     | `ai_service.py`            | 333 |
|                     | `ai_streaming.py`          | 110 |
|                     | `async_utils.py`           | 237 |
|                     | `io_service.py`            | 170 |
|                     | `pipeline.py`              | 95  |
|                     | `protocols.py`             | 144 |
|                     | `types.py`                 | 170 |
| **backup/**         | `__init__.py`              | 97  |
|                     | `backup_export.py`         | 166 |
|                     | `backup_restore.py`        | 167 |
|                     | `service.py`               | 230 |
|                     | `types.py`                 | 44  |
|                     | `utils_identity.py`        | 163 |
|                     | `utils_operations.py`      | 167 |
|                     | `utils_serialization.py`   | 153 |
| **events/**         | `__init__.py`              | 47  |
|                     | `bus.py`                   | 311 |
|                     | `events.py`                | 126 |
|                     | `subscribers.py`           | 154 |
| **middleware/**     | `__init__.py`              | 67  |
|                     | `pipeline.py`              | 517 |
| **notifications/**  | `__init__.py`              | 123 |
|                     | `inventaire.py`            | 228 |
|                     | `notif_ntfy.py`            | 220 |
|                     | `notif_web.py`             | 25  |
|                     | `notif_web_core.py`        | 239 |
|                     | `notif_web_persistence.py` | 256 |
|                     | `notif_web_templates.py`   | 99  |
|                     | `types.py`                 | 200 |
|                     | `utils.py`                 | 448 |
| **observability/**  | `__init__.py`              | 57  |
|                     | `health.py`                | 362 |
|                     | `metrics.py`               | 292 |
|                     | `spans.py`                 | 278 |
| **specifications/** | `__init__.py`              | 63  |
|                     | `base.py`                  | 192 |
|                     | `inventaire.py`            | 262 |
|                     | `recettes.py`              | 278 |
| **utilisateur/**    | `__init__.py`              | 74  |
|                     | `authentification.py`      | 304 |
|                     | `auth_permissions.py`      | 113 |
|                     | `auth_profile.py`          | 107 |
|                     | `auth_schemas.py`          | 65  |
|                     | `auth_session.py`          | 78  |
|                     | `auth_token.py`            | 72  |
|                     | `historique.py`            | 509 |
|                     | `historique_types.py`      | 73  |
|                     | `preferences.py`           | 269 |
| `__init__.py`       | 88                         |
| `registry.py`       | 364                        |

### `cuisine/` — Recettes, Planning, Courses (51 fichiers, 9 579 LOC)

| Sous-package       | Fichier                      | LOC |
| ------------------ | ---------------------------- | --- |
|                    | `__init__.py`                | 38  |
| **batch_cooking/** | `__init__.py`                | 74  |
|                    | `batch_cooking_ia.py`        | 164 |
|                    | `batch_cooking_stats.py`     | 172 |
|                    | `constantes.py`              | 25  |
|                    | `service.py`                 | 379 |
|                    | `types.py`                   | 36  |
|                    | `utils.py`                   | 425 |
| **courses/**       | `__init__.py`                | 67  |
|                    | `constantes.py`              | 61  |
|                    | `service.py`                 | 480 |
|                    | `suggestion.py`              | 271 |
|                    | `types.py`                   | 74  |
| **planning/**      | `__init__.py`                | 93  |
|                    | `agregation.py`              | 89  |
|                    | `formatters.py`              | 83  |
|                    | `global_analysis.py`         | 114 |
|                    | `global_loaders.py`          | 173 |
|                    | `global_planning.py`         | 505 |
|                    | `nutrition.py`               | 122 |
|                    | `planning_ia_mixin.py`       | 257 |
|                    | `prompts.py`                 | 72  |
|                    | `rappels.py`                 | 177 |
|                    | `recurrence.py`              | 237 |
|                    | `service.py`                 | 333 |
|                    | `templates.py`               | 242 |
|                    | `types.py`                   | 80  |
|                    | `validators.py`              | 52  |
| **recettes/**      | `__init__.py`                | 80  |
|                    | `importer.py`                | 134 |
|                    | `import_url.py`              | 260 |
|                    | `parsers.py`                 | 391 |
|                    | `recettes_ia_generation.py`  | 15  |
|                    | `recettes_ia_suggestions.py` | 162 |
|                    | `recettes_ia_versions.py`    | 437 |
|                    | `service.py`                 | 561 |
|                    | `types.py`                   | 74  |
|                    | `utils.py`                   | 542 |
|                    | `utils_calcul.py`            | 182 |
|                    | `utils_filtrage.py`          | 107 |
|                    | `utils_io.py`                | 189 |
| **suggestions/**   | `__init__.py`                | 80  |
|                    | `analyse_historique.py`      | 127 |
|                    | `constantes_suggestions.py`  | 103 |
|                    | `equilibre.py`               | 157 |
|                    | `formatage.py`               | 89  |
|                    | `predictions.py`             | 291 |
|                    | `saisons.py`                 | 63  |
|                    | `scoring.py`                 | 154 |
|                    | `service.py`                 | 442 |
|                    | `types.py`                   | 44  |

### `famille/` — Vie familiale (22 fichiers, 4 806 LOC)

| Fichier                  | LOC |
| ------------------------ | --- |
| `__init__.py`            | 62  |
| `achats.py`              | 287 |
| `activites.py`           | 156 |
| `calendrier_planning.py` | 321 |
| `jules.py`               | 133 |
| `jules_ai.py`            | 123 |
| `routines.py`            | 366 |
| `sante.py`               | 300 |
| `suivi_perso.py`         | 259 |
| `weekend.py`             | 303 |
| `weekend_ai.py`          | 96  |
| **budget/**              |     |
| `__init__.py`            | 93  |
| `budget_alertes.py`      | 176 |
| `budget_analyses.py`     | 172 |
| `schemas.py`             | 139 |
| `service.py`             | 312 |
| `utils.py`               | 353 |
| **calendrier/**          |     |
| `__init__.py`            | 39  |
| `generateur.py`          | 121 |
| `google_calendar.py`     | 497 |
| `schemas.py`             | 66  |
| `service.py`             | 432 |

### `integrations/` — APIs externes (30 fichiers, 5 860 LOC)

| Sous-package | Fichier              | LOC |
| ------------ | -------------------- | --- |
|              | `__init__.py`        | 107 |
|              | `codes_barres.py`    | 397 |
|              | `facture.py`         | 202 |
|              | `produit.py`         | 250 |
| **garmin/**  | `__init__.py`        | 121 |
|              | `service.py`         | 445 |
|              | `types.py`           | 56  |
|              | `utils_format.py`    | 74  |
|              | `utils_parsing.py`   | 137 |
|              | `utils_stats.py`     | 206 |
|              | `utils_sync.py`      | 109 |
| **images/**  | `__init__.py`        | 22  |
|              | `generator.py`       | 496 |
| **weather/** | `__init__.py`        | 125 |
|              | `alertes_meteo.py`   | 254 |
|              | `arrosage.py`        | 120 |
|              | `meteo_jardin.py`    | 190 |
|              | `parsing.py`         | 89  |
|              | `saisons.py`         | 146 |
|              | `service.py`         | 463 |
|              | `types.py`           | 78  |
|              | `weather_codes.py`   | 162 |
| **web/**     | `__init__.py`        | 76  |
|              | `pwa_templates.py`   | 470 |
|              | `synchronisation.py` | 418 |
| **web/pwa/** | `__init__.py`        | 23  |
|              | `config.py`          | 159 |
|              | `generation.py`      | 60  |
|              | `offline.py`         | 96  |
|              | `service_worker.py`  | 309 |

### `inventaire/` (7 fichiers, 1 135 LOC)

| Fichier                    | LOC |
| -------------------------- | --- |
| `__init__.py`              | 36  |
| `inventaire_io.py`         | 189 |
| `inventaire_operations.py` | 346 |
| `inventaire_stats.py`      | 166 |
| `inventaire_stock.py`      | 178 |
| `service.py`               | 177 |
| `types.py`                 | 43  |

### `jeux/` — Loto & Paris (15 fichiers, 5 130 LOC)

| Fichier                   | LOC |
| ------------------------- | --- |
| `__init__.py`             | 232 |
| **\_internal/**           |     |
| `__init__.py`             | 1   |
| `ai_service.py`           | 427 |
| `backtest_service.py`     | 450 |
| `football_data.py`        | 501 |
| `football_helpers.py`     | 219 |
| `football_types.py`       | 74  |
| `loto_crud_service.py`    | 356 |
| `loto_data.py`            | 324 |
| `notification_service.py` | 375 |
| `paris_crud_service.py`   | 607 |
| `prediction_service.py`   | 470 |
| `scheduler_service.py`    | 366 |
| `series_service.py`       | 435 |
| `sync_service.py`         | 293 |

### `maison/` (13 fichiers, 2 843 LOC)

| Fichier                           | LOC |
| --------------------------------- | --- |
| `__init__.py`                     | 121 |
| `depenses_crud_service.py`        | 194 |
| `entretien_gamification_mixin.py` | 448 |
| `entretien_service.py`            | 363 |
| `hub_data_service.py`             | 64  |
| `jardin_catalogue_mixin.py`       | 94  |
| `jardin_gamification_mixin.py`    | 312 |
| `jardin_service.py`               | 372 |
| `jardin_taches_mixin.py`          | 175 |
| `projets_service.py`              | 389 |
| `schemas.py`                      | 165 |
| `schemas_enums.py`                | 55  |
| `schemas_jardin.py`               | 91  |

### `rapports/` (7 fichiers, 1 681 LOC)

| Fichier                  | LOC |
| ------------------------ | --- |
| `__init__.py`            | 48  |
| `export.py`              | 436 |
| `generation.py`          | 353 |
| `planning_pdf.py`        | 313 |
| `rapports_budget.py`     | 208 |
| `rapports_gaspillage.py` | 237 |
| `types.py`               | 86  |

---

## 2. Analyse par Package

### Résumé décorateurs par package

| Package          | Fichiers | LOC        | `@service_factory` | `@avec_cache` | `@avec_session_db` | `@avec_gestion_erreurs` | `@avec_resilience` |
| ---------------- | -------- | ---------- | ------------------ | ------------- | ------------------ | ----------------------- | ------------------ |
| **core**         | 55       | 9 862      | 6 (+1 doc)         | 0             | ~15                | ~6                      | 0                  |
| **cuisine**      | 51       | 9 579      | 11                 | 15            | ~70                | ~40                     | 1                  |
| **famille**      | 22       | 4 806      | 12                 | 35            | ~60                | ~55                     | 0                  |
| **integrations** | 30       | 5 860      | 6                  | 3             | ~18                | 2                       | 6                  |
| **inventaire**   | 7        | 1 135      | 1                  | 2             | ~10                | ~16                     | 0                  |
| **jeux**         | 15       | 5 130      | 11                 | 10            | ~38                | ~11                     | 2                  |
| **maison**       | 13       | 2 843      | 5                  | 0             | ~17                | ~5                      | 0                  |
| **rapports**     | 7        | 1 681      | 2                  | 0             | ~8                 | 3                       | 0                  |
| **root**         | 2        | 72         | 1                  | 0             | 0                  | 1                       | 0                  |
| **TOTAL**        | **202**  | **40 968** | **55**             | **65**        | **~236**           | **~139**                | **9**              |

### Services & Base Classes

| Package                   | Service Class                   | Base Class                                           | `@service_factory`         |
| ------------------------- | ------------------------------- | ---------------------------------------------------- | -------------------------- |
| **root**                  | `AccueilDataService`            | standalone                                           | `accueil_data`             |
| **core/backup**           | `BackupService`                 | standalone                                           | `backup`                   |
| **core/utilisateur**      | `AuthService`                   | mixins only                                          | `authentification`         |
| **core/utilisateur**      | `ActionHistoryService`          | standalone                                           | `historique_actions`       |
| **core/utilisateur**      | `UserPreferenceService`         | standalone                                           | `preferences_utilisateur`  |
| **core/notifications**    | `NotificationWebPushService`    | standalone                                           | `webpush`                  |
| **core/notifications**    | `NotificationInventaireService` | standalone                                           | `notifications_inventaire` |
| **cuisine/recettes**      | `ServiceRecettes`               | `BaseService[Recette]` + `BaseAIService`             | `recettes`                 |
| **cuisine/recettes**      | `RecipeImportService`           | `BaseAIService`                                      | `import_recettes`          |
| **cuisine/planning**      | `ServicePlanning`               | `BaseService[Planning]` + `BaseAIService`            | `planning`                 |
| **cuisine/planning**      | `ServicePlanningUnifie`         | `BaseService[CalendarEvent]` + `BaseAIService`       | ❌ **NONE**                |
| **cuisine/planning**      | `ServiceRecurrence`             | standalone                                           | `recurrence`               |
| **cuisine/planning**      | `ServiceTemplates`              | standalone                                           | `templates`                |
| **cuisine/planning**      | `ServiceRappels`                | standalone                                           | `rappels`                  |
| **cuisine/courses**       | `ServiceCourses`                | `BaseService[ArticleCourses]` + `BaseAIService`      | `courses`                  |
| **cuisine/courses**       | `ServiceCoursesIntelligentes`   | `BaseAIService`                                      | `courses_intelligentes`    |
| **cuisine/batch_cooking** | `ServiceBatchCooking`           | `BaseService[SessionBatchCooking]` + `BaseAIService` | `batch_cooking`            |
| **cuisine/suggestions**   | `ServiceSuggestions`            | standalone                                           | `suggestions`              |
| **cuisine/suggestions**   | `PredictionService`             | standalone                                           | `predictions`              |
| **famille**               | `ServiceActivites`              | standalone                                           | `activites`                |
| **famille**               | `ServiceRoutines`               | standalone                                           | `routines`                 |
| **famille**               | `ServiceWeekend`                | standalone                                           | `weekend`                  |
| **famille**               | `ServiceSante`                  | standalone                                           | `sante`                    |
| **famille**               | `ServiceSuiviPerso`             | standalone                                           | `suivi_perso`              |
| **famille**               | `ServiceJules`                  | standalone                                           | `jules`                    |
| **famille**               | `ServiceCalendrierPlanning`     | standalone                                           | `calendrier_planning`      |
| **famille**               | `ServiceAchatsFamille`          | standalone                                           | `achats_famille`           |
| **famille**               | `JulesAIService`                | `BaseAIService`                                      | `jules_ai`                 |
| **famille**               | `WeekendAIService`              | `BaseAIService`                                      | `weekend_ai`               |
| **famille/budget**        | `BudgetService`                 | mixins only                                          | `budget`                   |
| **famille/calendrier**    | `CalendarSyncService`           | `GoogleCalendarMixin`                                | `calendrier`               |
| **integrations**          | `BarcodeService`                | `BaseService[ArticleInventaire]`                     | `codes_barres`             |
| **integrations**          | `FactureOCRService`             | `BaseAIService`                                      | `facture_ocr`              |
| **integrations**          | `OpenFoodFactsService`          | standalone                                           | `openfoodfacts`            |
| **integrations/garmin**   | `ServiceGarmin`                 | standalone                                           | `garmin`                   |
| **integrations/weather**  | `ServiceMeteo`                  | `MeteoJardinMixin`                                   | `meteo`                    |
| **integrations/web**      | `RealtimeSyncService`           | standalone                                           | `sync_temps_reel`          |
| **inventaire**            | `ServiceInventaire`             | `BaseService[ArticleInventaire]` + `BaseAIService`   | `inventaire`               |
| **jeux**                  | `JeuxAIService`                 | `BaseAIService`                                      | `jeux_ai`                  |
| **jeux**                  | `LotoCrudService`               | `BaseService[GrilleLoto]`                            | `loto_crud`                |
| **jeux**                  | `ParisCrudService`              | `BaseService[PariSportif]`                           | `paris_crud`               |
| **jeux**                  | `FootballDataService`           | standalone                                           | `football_data`            |
| **jeux**                  | `LotoDataService`               | standalone                                           | `loto_data`                |
| **jeux**                  | `NotificationJeuxService`       | standalone                                           | `notification_jeux`        |
| **jeux**                  | `PredictionService`             | standalone                                           | `prediction`               |
| **jeux**                  | `SchedulerService`              | standalone                                           | `scheduler`                |
| **jeux**                  | `SeriesService`                 | standalone                                           | `series`                   |
| **jeux**                  | `SyncService`                   | standalone                                           | `sync`                     |
| **jeux**                  | `BacktestService`               | standalone                                           | `backtest`                 |
| **maison**                | `HubDataService`                | standalone                                           | `hub_data`                 |
| **maison**                | `DepensesCrudService`           | standalone                                           | `depenses_crud`            |
| **maison**                | `EntretienService`              | `EntretienGamificationMixin` + `BaseAIService`       | `entretien`                |
| **maison**                | `JardinService`                 | `JardinGamificationMixin` + `BaseAIService`          | `jardin`                   |
| **maison**                | `ProjetsService`                | `BaseAIService`                                      | `projets`                  |
| **rapports**              | `ServiceExportPDF`              | standalone                                           | `export_pdf`               |
| **rapports**              | `ServiceRapportsPDF`            | mixins (Budget+Gaspillage+Planning)                  | `rapports_pdf`             |

---

## 3. Concept Adoption Audit

### 3a. `@service_factory` — Services WITHOUT registration

| Service Class           | Fichier                                         | Raison probable                            |
| ----------------------- | ----------------------------------------------- | ------------------------------------------ |
| `ServicePlanningUnifie` | `cuisine/planning/global_planning.py` (505 LOC) | Alt implementation, pas exposé via factory |
| `IOService`             | `core/base/io_service.py`                       | Base class — normal                        |
| `BaseService[T]`        | `core/base/types.py`                            | Base class — normal                        |
| `BaseAIService`         | `core/base/ai_service.py`                       | Base class — normal                        |

**Score: 55/56 services enregistreurs** (1 service métier sans factory: `ServicePlanningUnifie`)

### 3b. `@avec_cache` — Services WITHOUT caching (qui devraient en avoir)

Services avec lectures DB récurrentes mais SANS `@avec_cache`:

| Service                 | Fichier                                | Remarque                               |
| ----------------------- | -------------------------------------- | -------------------------------------- |
| `DepensesCrudService`   | `maison/depenses_crud_service.py`      | 7 méthodes DB, 0 cache                 |
| `HubDataService`        | `maison/hub_data_service.py`           | 2 méthodes DB, 0 cache                 |
| `ServiceExportPDF`      | `rapports/export.py`                   | Lectures + génération PDF, 0 cache     |
| `ServiceRapportsPDF`    | `rapports/generation.py`               | Lectures multiples, 0 cache            |
| `PlanningReportMixin`   | `rapports/planning_pdf.py`             | Lectures DB, 0 cache                   |
| `BudgetReportMixin`     | `rapports/rapports_budget.py`          | Lectures DB, 0 cache                   |
| `GaspillageReportMixin` | `rapports/rapports_gaspillage.py`      | Lectures DB, 0 cache                   |
| `EntretienService`      | `maison/entretien_service.py`          | Grande service, 0 `@avec_cache` direct |
| `JardinService`         | `maison/jardin_service.py`             | Grande service, 0 `@avec_cache` direct |
| `ProjetsService`        | `maison/projets_service.py`            | Grande service, 0 `@avec_cache` direct |
| `SeriesService`         | `jeux/_internal/series_service.py`     | 11 méthodes DB, 0 cache                |
| `SyncService`           | `jeux/_internal/sync_service.py`       | Lectures DB, 0 cache                   |
| `ParisCrudService`      | `jeux/_internal/paris_crud_service.py` | 17 méthodes DB, 0 cache                |
| `LotoCrudService`       | `jeux/_internal/loto_crud_service.py`  | 9 méthodes DB, 0 cache                 |
| `CalendarSyncService`   | `famille/calendrier/service.py`        | 4 méthodes DB, 0 cache                 |

**Score: 65 usages `@avec_cache`** — packages `maison/` (0) et `rapports/` (0) complètement sans cache.

### 3c. `@avec_gestion_erreurs` — Services WITHOUT error handling

| Service               | Fichier                               | Remarque                                                        |
| --------------------- | ------------------------------------- | --------------------------------------------------------------- |
| `ServiceGarmin`       | `integrations/garmin/service.py`      | 445 LOC, 0 `@avec_gestion_erreurs`                              |
| `ServiceMeteo`        | `integrations/weather/service.py`     | Only 1 usage sur 6+ méthodes DB                                 |
| `RealtimeSyncService` | `integrations/web/synchronisation.py` | 418 LOC, 0 error decorator                                      |
| `EntretienService`    | `maison/entretien_service.py`         | 363 LOC, 0 `@avec_gestion_erreurs` (utilise try/except manuels) |
| `JardinService`       | `maison/jardin_service.py`            | 372 LOC, 0 error decorator                                      |
| `ProjetsService`      | `maison/projets_service.py`           | 389 LOC, 0 error decorator                                      |
| `PlanningReportMixin` | `rapports/planning_pdf.py`            | 0 error decorator                                               |
| `SeriesService`       | `jeux/_internal/series_service.py`    | 435 LOC, 0 error decorator                                      |
| `SchedulerService`    | `jeux/_internal/scheduler_service.py` | 366 LOC, 0 error decorator                                      |

**Score: ~139 usages** — bonne couverture sauf `maison/` services IA, `integrations/` et `jeux/` standalone.

### 3d. `obtenir_client_ia()` vs `ClientIA()` direct

**Tous les services utilisent `obtenir_client_ia()`** — 0 appels directs `ClientIA()`.

17 services passent par `obtenir_client_ia()`:

- `cuisine/recettes/service.py`, `cuisine/planning/service.py`, `cuisine/courses/service.py`
- `cuisine/courses/suggestion.py`, `cuisine/batch_cooking/service.py`, `cuisine/suggestions/service.py`
- `cuisine/planning/global_planning.py`, `cuisine/recettes/import_url.py`
- `famille/jules_ai.py`, `famille/weekend_ai.py`
- `integrations/facture.py`
- `maison/entretien_service.py`, `maison/jardin_service.py`, `maison/projets_service.py`
- `inventaire/service.py`
- `jeux/_internal/ai_service.py`

**Score: 17/17 ✅ — compliance parfaite**

### 3e. `@avec_resilience` — Services with external HTTP calls WITHOUT resilience

| Service                 | Fichier                                 | HTTP client             | `@avec_resilience` |
| ----------------------- | --------------------------------------- | ----------------------- | ------------------ |
| `FootballDataService`   | `jeux/_internal/football_data.py`       | `httpx.Client`          | ✅ 1               |
| `LotoDataService`       | `jeux/_internal/loto_data.py`           | `httpx.Client`          | ✅ 1               |
| `ServiceMeteo`          | `integrations/weather/service.py`       | `httpx.Client`          | ✅ 2               |
| `OpenFoodFactsService`  | `integrations/produit.py`               | `httpx.Client`          | ✅ 1               |
| `ServiceGarmin`         | `integrations/garmin/service.py`        | `httpx.Client`          | ✅ 3               |
| `RecipeImportService`   | `cuisine/recettes/import_url.py`        | `httpx.Client`          | ✅ 1               |
| **ImageGenerator**      | `integrations/images/generator.py`      | `requests.*` (6 appels) | ❌ **AUCUN**       |
| **CalendarSyncService** | `famille/calendrier/service.py`         | `httpx.Client`          | ❌ **AUCUN**       |
| **GoogleCalendarMixin** | `famille/calendrier/google_calendar.py` | `httpx.Client`          | ❌ **AUCUN**       |
| **NtfyService**         | `core/notifications/notif_ntfy.py`      | `httpx.AsyncClient`     | ❌ **AUCUN**       |

**Score: 9 usages `@avec_resilience`** — manque sur 3 services (images, calendrier, ntfy).

### 3f. Event Bus — Émissions par service

| Total: 27 événements émis par 10 services, 7 abonnements.

---

## 4. Vérification ROADMAP

| Item                                                        | Statut                                        | Détail                                                                                            |
| ----------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **CQRS supprimé** (`services/core/cqrs/`)                   | ✅ **DONE**                                   | Répertoire n'existe plus                                                                          |
| **ReactiveServiceMixin supprimé** (`core/base/reactive.py`) | ✅ **DONE**                                   | Fichier n'existe plus, 0 référence                                                                |
| **Middleware pipeline supprimé** (`core/middleware/`)       | ❌ **ENCORE PRÉSENT**                         | 2 fichiers, 584 LOC. 1 seul consommateur: `cuisine/recettes/service.py` (import `service_method`) |
| **Specification pattern supprimé**                          | ❌ **ENCORE PRÉSENT**                         | 4 fichiers, 795 LOC. **0 consommateur externe** — auto-référentiel uniquement                     |
| **`@service_factory` ≥ 19**                                 | ✅ **55 registrations**                       | Largement dépassé (objectif: 19)                                                                  |
| **`@avec_cache` ≥ 50 usages**                               | ✅ **65 usages**                              | Objectif atteint                                                                                  |
| **`@avec_resilience` ≥ 11 usages**                          | ❌ **9 usages**                               | Manque 2. Images/calendrier/ntfy non couverts                                                     |
| **N+1 fixés (joinedload/selectinload)**                     | ✅ **~50 usages** (99 occurrences du pattern) | Bonne couverture dans tous les packages                                                           |

---

## 5. Event Bus — Détail Complet

### Événements émis (`emettre()`)

| Événement                     | Fichier source                        | Service                     |
| ----------------------------- | ------------------------------------- | --------------------------- |
| `stock.modifie` ×3            | `inventaire/inventaire_operations.py` | `InventaireOperationsMixin` |
| `recette.creee`               | `cuisine/recettes/service.py`         | `ServiceRecettes`           |
| `recette.importee`            | `cuisine/recettes/service.py`         | `ServiceRecettes`           |
| `planning.cree`               | `cuisine/planning/service.py`         | `ServicePlanning`           |
| `batch_cooking.session_creee` | `cuisine/batch_cooking/service.py`    | `ServiceBatchCooking`       |
| `batch_cooking.termine`       | `cuisine/batch_cooking/service.py`    | `ServiceBatchCooking`       |
| `courses.ingredients_ajoutes` | `cuisine/courses/service.py`          | `ServiceCourses`            |
| `entretien.routine_creee`     | `maison/entretien_service.py`         | `EntretienService`          |
| `entretien.semaine_optimisee` | `maison/entretien_service.py`         | `EntretienService`          |
| `activites.cree`              | `famille/activites.py`                | `ServiceActivites`          |
| `activites.terminee`          | `famille/activites.py`                | `ServiceActivites`          |
| `activites.supprimee`         | `famille/activites.py`                | `ServiceActivites`          |
| `routines.cree`               | `famille/routines.py`                 | `ServiceRoutines`           |
| `routines.tache_ajoutee`      | `famille/routines.py`                 | `ServiceRoutines`           |
| `routines.tache_complete`     | `famille/routines.py`                 | `ServiceRoutines`           |
| `routines.supprimee`          | `famille/routines.py`                 | `ServiceRoutines`           |
| `routines.desactivee`         | `famille/routines.py`                 | `ServiceRoutines`           |
| `weekend.cree`                | `famille/weekend.py`                  | `ServiceWeekend`            |
| `weekend.termine`             | `famille/weekend.py`                  | `ServiceWeekend`            |
| `weekend.note`                | `famille/weekend.py`                  | `ServiceWeekend`            |
| `food_log.ajoute`             | `famille/suivi_perso.py`              | `ServiceSuiviPerso`         |
| `achats.cree`                 | `famille/achats.py`                   | `ServiceAchatsFamille`      |
| `achats.achete`               | `famille/achats.py`                   | `ServiceAchatsFamille`      |
| `achats.supprime`             | `famille/achats.py`                   | `ServiceAchatsFamille`      |
| `service.error`               | `core/middleware/pipeline.py`         | Middleware (auto)           |

### Abonnements (`souscrire()`) — dans `core/events/subscribers.py`

| Pattern         | Handler                           | Priorité |
| --------------- | --------------------------------- | -------- |
| `recette.*`     | `_invalider_cache_recettes`       | 100      |
| `stock.*`       | `_invalider_cache_stock`          | 100      |
| `courses.*`     | `_invalider_cache_courses`        | 100      |
| `entretien.*`   | `_invalider_cache_entretien`      | 100      |
| `*`             | `_enregistrer_metrique_evenement` | 50       |
| `service.error` | `_enregistrer_erreur_service`     | 50       |
| `*`             | `_logger_evenement_audit`         | 10       |

### Événements émis SANS subscriber de cache dédié

| Pattern émis      | Subscribers       | Gap                                       |
| ----------------- | ----------------- | ----------------------------------------- |
| `activites.*`     | `*` wildcard only | ❌ Pas d'invalidation cache activités     |
| `routines.*`      | `*` wildcard only | ❌ Pas d'invalidation cache routines      |
| `weekend.*`       | `*` wildcard only | ❌ Pas d'invalidation cache weekend       |
| `achats.*`        | `*` wildcard only | ❌ Pas d'invalidation cache achats        |
| `food_log.*`      | `*` wildcard only | ❌ Pas d'invalidation cache food_log      |
| `batch_cooking.*` | `*` wildcard only | ❌ Pas d'invalidation cache batch_cooking |
| `planning.*`      | `*` wildcard only | ❌ Pas d'invalidation cache planning      |

**7 domaines émettent des événements sans subscriber de cache dédié.** Seuls `recette.*`, `stock.*`, `courses.*`, `entretien.*` ont une invalidation automatique.

---

## 6. Dead Code / Infrastructure Inutilisée

### 🔴 Aucun consommateur externe (candidats à suppression)

| Fichier/Package                      | LOC     | Raison                                                                                  |
| ------------------------------------ | ------- | --------------------------------------------------------------------------------------- |
| `core/specifications/` (4 fichiers)  | **795** | 0 import externe. Auto-référentiel uniquement. Pattern jamais utilisé par les services. |
| `core/base/ai_diagnostics.py`        | **98**  | Non importé par aucun service. Diagnostics IA inutilisés.                               |
| `core/base/ai_prompts.py`            | **35**  | Non importé par aucun service. Constantes de prompts.                                   |
| `core/observability/spans.py`        | **278** | Framework de tracing, non utilisé dans les services.                                    |
| `integrations/web/pwa_templates.py`  | **470** | Templates HTML bruts, probablement legacy.                                              |
| `integrations/web/pwa/offline.py`    | **96**  | Stratégie offline, aucun consommateur visible.                                          |
| `integrations/web/pwa/generation.py` | **60**  | Génération PWA, usage douteux.                                                          |

### 🟡 Usage minimal (1 seul consommateur)

| Fichier/Package                 | LOC     | Consommateur unique                                                            |
| ------------------------------- | ------- | ------------------------------------------------------------------------------ |
| `core/middleware/` (2 fichiers) | **584** | `cuisine/recettes/service.py` (import `service_method`, 1 usage sur 1 méthode) |
| `core/base/pipeline.py`         | **95**  | Utilisé via `BaseService` mais rarement appelé directement                     |
| `core/base/async_utils.py`      | **237** | Utilitaires async, usage sporadique                                            |
| `core/base/ai_streaming.py`     | **110** | Streaming IA, probablement non utilisé en production                           |

### 🟢 Infrastructure bien utilisée

| Module                                 | Consommateurs                          |
| -------------------------------------- | -------------------------------------- |
| `core/base/ai_service.py` + `types.py` | 15+ services via héritage              |
| `core/events/`                         | 10 services émetteurs, 7 subscribers   |
| `core/registry.py`                     | 55 `@service_factory` enregistrements  |
| `core/backup/`                         | Service standalone, 1 factory          |
| `core/utilisateur/`                    | 3 services, bien structuré             |
| `core/notifications/`                  | 4+ modules liés, dependencies internes |

---

## 7. Scores par Package

| Package          | `@service_factory` | `@avec_cache` | `@avec_gestion_erreurs` | Event Bus    | `@avec_resilience` | N+1 fixes | Score             |
| ---------------- | ------------------ | ------------- | ----------------------- | ------------ | ------------------ | --------- | ----------------- |
| **cuisine**      | ✅ 11/11           | ✅ 15         | ✅ 40+                  | ✅ 5 events  | ⚠️ 1/2             | ✅ 15+    | **A**             |
| **famille**      | ✅ 12/12           | ✅ 35         | ✅ 55+                  | ✅ 15 events | ❌ 0/2             | ✅ 8+     | **A-**            |
| **inventaire**   | ✅ 1/1             | ⚠️ 2          | ✅ 16+                  | ✅ 3 events  | —                  | ✅ 3      | **B+**            |
| **jeux**         | ✅ 11/11           | ✅ 10         | ⚠️ 11 (sur 13 services) | ❌ 0 events  | ✅ 2/2             | ✅ 12+    | **B+**            |
| **integrations** | ✅ 6/6             | ⚠️ 3          | ❌ 2 seulement          | ❌ 0 events  | ⚠️ 6/9             | ✅ 3      | **B-**            |
| **maison**       | ✅ 5/5             | ❌ 0          | ❌ 5 seulement          | ⚠️ 2 events  | ❌ 0/0             | ✅ 1      | **C+**            |
| **rapports**     | ✅ 2/2             | ❌ 0          | ⚠️ 3                    | ❌ 0 events  | —                  | ✅ 5      | **C**             |
| **core**         | ✅ 6/6             | — (infra)     | — (infra)               | ✅ Hub       | —                  | —         | **B** (dead code) |

---

## 8. Résumé Exécutif

### Points forts

- **55 `@service_factory`** — adoption massive, tous les services enregistrés
- **65 `@avec_cache`** — bon coverage (cuisine + famille exemplaires)
- **~236 `@avec_session_db`** — injection DB systématique
- **~139 `@avec_gestion_erreurs`** — bon error handling
- **27 événements domaine** émis par 10 services
- **`obtenir_client_ia()` 17/17** — aucun `ClientIA()` direct
- **~50 `joinedload`/`selectinload`** — N+1 bien gérés
- **CQRS et ReactiveServiceMixin** supprimés ✅

### Points faibles / Actions requises

| Priorité  | Action                                                                                                                                                        | Impact                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| 🔴 **P0** | Supprimer `core/specifications/` (795 LOC dead code, 0 consommateur)                                                                                          | -795 LOC                     |
| 🔴 **P0** | Supprimer `core/middleware/` (584 LOC, 1 consommateur unique → remplacer par `@avec_cache` + `@avec_session_db` dans `cuisine/recettes/service.py`)           | -584 LOC                     |
| 🟠 **P1** | Ajouter `@avec_resilience` sur `images/generator.py` (6 appels HTTP), `famille/calendrier/service.py`, `core/notifications/notif_ntfy.py` → objectif 11+      | +3 → 12 total                |
| 🟠 **P1** | Ajouter `@avec_cache` dans `maison/` (0 usages!) et `rapports/` (0 usages!)                                                                                   | Performance                  |
| 🟠 **P1** | Ajouter subscribers cache pour `activites.*`, `routines.*`, `weekend.*`, `achats.*`, `planning.*`, `batch_cooking.*`, `food_log.*`                            | 7 patterns sans invalidation |
| 🟡 **P2** | Ajouter `@avec_gestion_erreurs` dans `maison/entretien_service.py`, `maison/jardin_service.py`, `maison/projets_service.py`, `integrations/garmin/service.py` | Résilience                   |
| 🟡 **P2** | Auditer dead code dans `core/observability/spans.py` (278 LOC), `core/base/ai_diagnostics.py` (98 LOC), `integrations/web/pwa_templates.py` (470 LOC)         | ~846 LOC potentiel           |
| 🟢 **P3** | Ajouter `@service_factory` à `ServicePlanningUnifie` si utilisé en prod                                                                                       | Consistency                  |
