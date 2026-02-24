# Audit Report: `src/services/` Directory

**Date**: 2026-02-24  
**Scope**: Full pattern audit of `src/services/` — 200 files, 40,185 LOC  
**Auditor**: GitHub Copilot (Claude Opus 4.6)

---

## Executive Summary

| Metric                           | Value                  |
| -------------------------------- | ---------------------- |
| Total files                      | **200**                |
| Total LOC                        | **40,185**             |
| Sub-packages                     | **8** + 1 root file    |
| `@service_factory` registrations | **55** unique          |
| `BaseService[T]` adopters        | **16** classes         |
| `BaseAIService` adopters         | **16** classes         |
| `@avec_cache` usages             | **86**                 |
| `@avec_session_db` usages        | **100+**               |
| `@avec_gestion_erreurs` usages   | **100+**               |
| `@avec_resilience` usages        | **14**                 |
| Event bus emissions (`emettre`)  | **28** service methods |
| **Overall Score**                | **8.5 / 10**           |

---

## Sub-Package Breakdown

---

## 🚦 Sprint 1 — Corrections critiques (Phase 1 Audit)

### Synthèse des 5 items critiques

| Item                               | Statut | Détail                                                                                                                               |
| ---------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Persister maison/ en DB            | ✅     | Remplacement du stockage session_state par persistance DB (entretien, jardin, charges). CRUD via db_access.py, mutations persistées. |
| ServiceSuggestions → BaseAIService | ✅     | Refactorisation : héritage BaseAIService, call_with_cache_sync(), rate limiting automatique, circuit breaker intégré.                |
| JWT rate limiting flaw             | ✅     | Correction de la faille : verify_signature=False supprimé, usage de valider_token() avec vérification signature.                     |
| Protéger /metrics                  | ✅     | Ajout de require_role("admin") sur /metrics, accès restreint, 403 pour non-admin.                                                    |
| Tests API suggestions              | ✅     | 47 tests créés : endpoints, validation, sécurité JWT, protection /metrics.                                                           |

#### Fichiers créés/modifiés (voir ROADMAP.md)

- `src/modules/maison/entretien/db_access.py`, `jardin/db_access.py`, `charges/db_access.py` : CRUD et chargement DB
- `src/services/cuisine/suggestions/service.py` : refactorisation BaseAIService
- `src/api/rate_limiting/middleware.py` : sécurisation JWT
- `src/api/main.py` : protection /metrics
- `tests/api/test_routes_suggestions.py` : nouvelle suite de tests

#### Patterns appliqués

- Adoption systématique de `BaseAIService` pour suggestions (cache, rate limiting, circuit breaker)
- Usage de `@service_factory` sur tous les services refactorés
- Sécurisation accrue des endpoints critiques
- Tests d'intégration exhaustifs sur suggestions

#### Conformité Roadmap

Tous les objectifs critiques du Sprint 1 sont atteints : la persistance, la sécurité API et la robustesse des suggestions sont alignées avec la roadmap et validées par les tests.

---

### 1. `services/core/` — Framework Layer

| Metric | Value    |
| ------ | -------- |
| Files  | 49       |
| LOC    | 8,584    |
| Score  | **9/10** |

**Sub-structure**:

- `base/` (13 files): `BaseService[T]` (types.py:28), `BaseAIService` (ai_service.py:33), mixins (streaming, diagnostics, prompts, advanced, pipeline), protocols, async_utils, io_service
- `events/` (4 files): Event bus pub/sub (bus.py:311 LOC), event types, subscribers
- `notifications/` (9 files): ntfy, web push, inventory alerts, templates, persistence
- `observability/` (4 files): health checks, metrics, spans
- `utilisateur/` (10 files): auth, permissions, profile, session, tokens, preferences, historique
- `backup/` (8 files): export, restore, serialization, identity utils
- `registry.py` (364 LOC): `ServiceRegistry` + `@service_factory` decorator

**`@service_factory` found**: `backup`, `authentification`, `historique_actions`, `preferences_utilisateur`, `webpush`, `notifications_inventaire` (6 total)

**Patterns**:

- ✅ `BaseService` and `BaseAIService` properly defined as generic composable bases
- ✅ `ServiceMeta` metaclass auto-generates `_sync` wrappers for all async methods
- ✅ Event bus with `emettre()` / `souscrire()` / wildcard support
- ✅ `@service_factory` on all service factories
- ⚠️ `IOService` in `io_service.py` has no `@service_factory` (intended — utility class, not a singleton)

---

### 2. `services/cuisine/` — Cooking Domain

| Metric | Value    |
| ------ | -------- |
| Files  | 51       |
| LOC    | 9,579    |
| Score  | **9/10** |

**Sub-structure**:

- `recettes/` (14 files, ~2,600 LOC): `ServiceRecettes(BaseService[Recette], BaseAIService, RecipeAIMixin, RecettesIAGenerationMixin)` — full multi-inheritance
- `planning/` (15 files, ~2,800 LOC): `ServicePlanning(BaseService[Planning], BaseAIService, PlanningAIMixin)` + `ServicePlanningUnifie(BaseService[CalendarEvent], BaseAIService)`
- `courses/` (5 files, ~1,200 LOC): `ServiceCourses(BaseService[ArticleCourses], BaseAIService)` + `ServiceCoursesIntelligentes(BaseAIService)`
- `suggestions/` (10 files, ~1,500 LOC): `ServiceSuggestions(BaseAIService)`
- `batch_cooking/` (7 files, ~1,200 LOC): `ServiceBatchCooking(BaseService[SessionBatchCooking], BaseAIService)`

**`@service_factory` found**: `recettes`, `planning`, `courses`, `courses_intelligentes`, `suggestions`, `predictions`, `batch_cooking`, `rappels`, `templates`, `recurrence`, `import_recettes` (11 total)

**BaseService[T]**: `ServiceRecettes[Recette]`, `ServicePlanning[Planning]`, `ServicePlanningUnifie[CalendarEvent]`, `ServiceCourses[ArticleCourses]`, `ServiceBatchCooking[SessionBatchCooking]` — **5 adopters**

**BaseAIService**: `ServiceRecettes`, `ServicePlanning`, `ServicePlanningUnifie`, `ServiceCourses`, `ServiceCoursesIntelligentes`, `ServiceSuggestions`, `ServiceBatchCooking` — **7 adopters**

**Patterns**:

- ✅ All main services have `@service_factory`
- ✅ Heavy `@avec_cache`, `@avec_session_db`, `@avec_gestion_erreurs` usage
- ✅ Event bus emissions in recettes, planning, courses, batch_cooking
- ✅ `@avec_resilience` on `import_url.py` (HTTP scraping)
- ✅ Multiple inheritance (BaseService + BaseAIService + domain mixins) used consistently

---

### 3. `services/famille/` — Family Domain

| Metric | Value    |
| ------ | -------- |
| Files  | 23       |
| LOC    | 5,240    |
| Score  | **9/10** |

**Services & inheritance**:
| Service | Inheritance | `@service_factory` | `@avec_cache` | Event bus |
|---------|------------|-------------------|---------------|-----------|
| `ServiceWeekend` | `BaseService[WeekendActivity]` | ✅ `"weekend"` | ✅ 4x | ✅ 3 emissions |
| `ServiceSante` | `BaseService[HealthEntry]` | ✅ `"sante"` | ✅ 7x | — |
| `BudgetService` | `BaseService[FamilyBudget]` + mixins | ✅ `"budget"` | ✅ 3x | — |
| `ServiceActivites` | `BaseService[FamilyActivity]` | ✅ `"activites"` | ✅ 1x | ✅ 3 emissions |
| `ServiceAchatsFamille` | `BaseService[FamilyPurchase]` | ✅ `"achats_famille"` | ✅ 5x | ✅ 3 emissions |
| `ServiceRoutines` | `BaseService[Routine]` | ✅ `"routines"` | ✅ 6x | ✅ 5 emissions |
| `WeekendAIService` | `BaseAIService` | ✅ `"weekend_ai"` | — (cache via BaseAI) | — |
| `JulesAIService` | `BaseAIService` | ✅ `"jules_ai"` | — (cache via BaseAI) | — |
| `ServiceResumeHebdo` | `BaseAIService` | ✅ `"resume_hebdo"` | ✅ 1x (86400s) | — |
| `ServiceJules` | plain class | ✅ `"jules"` | ✅ 3x | — |
| `ServiceSuiviPerso` | plain class | ✅ `"suivi_perso"` | ✅ 2x | ✅ 1 emission |
| `ServiceCalendrierPlanning` | plain class | ✅ `"calendrier_planning"` | ✅ 2x | — |
| `CalendarSyncService` | `GoogleCalendarMixin` | ✅ `"calendrier"` | — | — |

**`@service_factory` found**: 13 total  
**`@avec_resilience`**: on `CalendarSyncService` (1x) + `GoogleCalendarMixin` (2x)

**Patterns**:

- ✅ All 6 BaseService[T] migrations confirmed (Weekend, Sante, Budget, Activites, Achats, Routines)
- ✅ JulesAI + WeekendAI properly use BaseAIService + `@service_factory`
- ✅ Heavy decorator coverage: `@avec_gestion_erreurs` + `@avec_cache` + `@avec_session_db` on every query method
- ⚠️ `ServiceJules`, `ServiceSuiviPerso`, `ServiceCalendrierPlanning` are **plain classes** (no BaseService[T]) — acceptable since they aren't CRUD-for-one-model services

---

### 4. `services/integrations/` — External APIs

| Metric | Value    |
| ------ | -------- |
| Files  | 30       |
| LOC    | 5,862    |
| Score  | **8/10** |

**Services**:
| Service | Inheritance | `@service_factory` | `@avec_resilience` |
|---------|------------|-------------------|--------------------|
| `BarcodeService` | `BaseService[ArticleInventaire]` | ✅ `"codes_barres"` | — |
| `FactureOCRService` | `BaseAIService` | ✅ `"facture_ocr"` | — |
| `OpenFoodFactsService` | plain class | ✅ `"openfoodfacts"` | ✅ 1x |
| `ServiceMeteo` | `MeteoJardinMixin` | ✅ `"meteo"` | ✅ 2x |
| `ServiceGarmin` | plain class | ✅ `"garmin"` | ✅ 3x |
| `RealtimeSyncService` | plain class | ✅ `"sync_temps_reel"` | — |
| `ImageGenerator` | plain function | ❌ no factory | ✅ 1x |

**`@service_factory` found**: 6 total

**Patterns**:

- ✅ `@avec_resilience` used heavily on all HTTP-calling services (garmin, weather, produit, images)
- ✅ `@avec_cache` on barcode (2x), weather (1x)
- ⚠️ `ImageGenerator` has no `@service_factory` — it's a module-level function, not a class singleton
- ⚠️ `ServiceMeteo` doesn't inherit BaseService or BaseAIService (inherits only `MeteoJardinMixin`) — acceptable for HTTP-only service

---

### 5. `services/inventaire/` — Inventory

| Metric | Value      |
| ------ | ---------- |
| Files  | 7          |
| LOC    | 1,135      |
| Score  | **9.5/10** |

**Main service**: `ServiceInventaire(BaseService[ArticleInventaire], BaseAIService, InventoryAIMixin, InventaireIOMixin, InventaireStatsMixin, InventaireStockMixin, InventaireOperationsMixin)`

**Patterns**:

- ✅ Full multi-inheritance (BaseService + BaseAIService + 5 mixins)
- ✅ `@service_factory("inventaire")`
- ✅ `@avec_cache`, `@avec_session_db`, `@avec_gestion_erreurs` throughout all mixins
- ✅ Event bus emissions in `inventaire_operations.py` (3x)
- ✅ Clean separation into operation/stats/stock/IO mixins

---

### 6. `services/jeux/` — Games (Paris Sportifs & Loto)

| Metric | Value      |
| ------ | ---------- |
| Files  | 18         |
| LOC    | 5,169      |
| Score  | **8.5/10** |

**Services**:
| Service | Inheritance | `@service_factory` |
|---------|------------|-------------------|
| `ParisCrudService` | `BaseService[PariSportif]` + 3 mixins | ✅ `"paris_crud"` |
| `LotoCrudService` | `BaseService[GrilleLoto]` | ✅ `"loto_crud"` |
| `JeuxAIService` | `BaseAIService` | ✅ `"jeux_ai"` |
| `FootballDataService` | plain class | ✅ `"football_data"` |
| `LotoDataService` | plain class | ✅ `"loto_data"` |
| `PredictionService` | plain class | ✅ `"prediction"` |
| `SeriesService` | plain class | ✅ `"series"` |
| `BacktestService` | plain class | ✅ `"backtest"` |
| `SyncService` | plain class | ✅ `"sync"` |
| `SchedulerService` | plain class | ✅ `"scheduler"` |
| `NotificationJeuxService` | plain class | ✅ `"notification_jeux"` |

**`@service_factory` found**: 11 total

**Patterns**:

- ✅ `ParisCrudService(BaseService[PariSportif])` and `LotoCrudService(BaseService[GrilleLoto])` confirmed
- ✅ `JeuxAIService(BaseAIService)` with full rate limiting + cache
- ✅ `@avec_resilience` on `football_data.py` (1x), `loto_data.py` (1x) — HTTP-protected
- ✅ `@avec_cache` heavily used in football_data (5x) and football_helpers (5x)
- ✅ `@avec_gestion_erreurs` used on all query methods
- ⚠️ Most utility services (Series, Backtest, Prediction, etc.) are **plain classes** — acceptable as they're not single-model CRUD

---

### 7. `services/maison/` — House Management

| Metric | Value      |
| ------ | ---------- |
| Files  | 13         |
| LOC    | 2,860      |
| Score  | **8.5/10** |

**Services**:
| Service | Inheritance | `@service_factory` |
|---------|------------|-------------------|
| `DepensesCrudService` | `BaseService[HouseExpense]` | ✅ `"depenses_crud"` |
| `EntretienService` | `BaseAIService` + gamification mixin | ✅ `"entretien"` |
| `JardinService` | `BaseAIService` + gamification mixin | ✅ `"jardin"` |
| `ProjetsService` | `BaseAIService` | ✅ `"projets"` |
| `HubDataService` | plain class | ✅ `"hub_data"` |

**`@service_factory` found**: 5 total

**Patterns**:

- ✅ `DepensesCrudService(BaseService[HouseExpense])` confirmed
- ✅ `@avec_cache` on all services (entretien 2x, jardin 2x, projets 2x, depenses 3x, hub_data 2x)
- ✅ `@avec_session_db` on all DB methods
- ✅ Event bus emissions in `entretien_service.py` (2x)
- ⚠️ `EntretienService`, `JardinService`, `ProjetsService` use `BaseAIService` only (no `BaseService[T]`) — they don't have a primary CRUD model, so this is acceptable

---

### 8. `services/rapports/` — Reports & PDF Generation

| Metric | Value      |
| ------ | ---------- |
| Files  | 7          |
| LOC    | 1,684      |
| Score  | **7.5/10** |

**Services**:
| Service | Inheritance | `@service_factory` |
|---------|------------|-------------------|
| `ServiceRapportsPDF` | 3 report mixins | ✅ `"rapports_pdf"` |
| `ServiceExportPDF` | plain class | ✅ `"export_pdf"` |

**Patterns**:

- ✅ `@service_factory` on both services
- ✅ `@avec_cache` (3x), `@avec_session_db` (6x), `@avec_gestion_erreurs` (3x)
- ⚠️ No `BaseService[T]` or `BaseAIService` — acceptable (report generation, not CRUD or AI)

---

### 9. Root: `services/accueil_data_service.py`

| Metric | Value    |
| ------ | -------- |
| Files  | 1        |
| LOC    | 47       |
| Score  | **7/10** |

- ✅ `@service_factory("accueil_data")`
- ✅ `@avec_gestion_erreurs` + `@avec_session_db`
- ⚠️ Plain class (no BaseService) — acceptable, it's a simple dashboard data fetcher
- ⚠️ Only file living outside a sub-package — could be moved to a dedicated package

---

## Complete `@service_factory` Registration List (55 unique)

| #   | Name                       | File                                     | Tags                             |
| --- | -------------------------- | ---------------------------------------- | -------------------------------- |
| 1   | `accueil_data`             | `accueil_data_service.py`                | accueil, data                    |
| 2   | `recettes`                 | `cuisine/recettes/service.py`            | cuisine, ia, crud                |
| 3   | `planning`                 | `cuisine/planning/service.py`            | cuisine, ia, crud                |
| 4   | `courses`                  | `cuisine/courses/service.py`             | cuisine, ia, crud                |
| 5   | `courses_intelligentes`    | `cuisine/courses/suggestion.py`          | cuisine, ia                      |
| 6   | `suggestions`              | `cuisine/suggestions/service.py`         | cuisine, ia                      |
| 7   | `predictions`              | `cuisine/suggestions/predictions.py`     | cuisine, ia, ml                  |
| 8   | `batch_cooking`            | `cuisine/batch_cooking/service.py`       | cuisine, ia                      |
| 9   | `rappels`                  | `cuisine/planning/rappels.py`            | cuisine, planning, notifications |
| 10  | `templates`                | `cuisine/planning/templates.py`          | cuisine, planning                |
| 11  | `recurrence`               | `cuisine/planning/recurrence.py`         | cuisine, planning                |
| 12  | `import_recettes`          | `cuisine/recettes/import_url.py`         | cuisine, ia, import              |
| 13  | `weekend`                  | `famille/weekend.py`                     | famille, crud                    |
| 14  | `weekend_ai`               | `famille/weekend_ai.py`                  | famille, ia, weekend             |
| 15  | `sante`                    | `famille/sante.py`                       | famille, sante                   |
| 16  | `budget`                   | `famille/budget/service.py`              | famille, crud                    |
| 17  | `activites`                | `famille/activites.py`                   | famille, crud                    |
| 18  | `achats_famille`           | `famille/achats.py`                      | famille, crud                    |
| 19  | `routines`                 | `famille/routines.py`                    | famille, crud                    |
| 20  | `jules`                    | `famille/jules.py`                       | famille, enfant                  |
| 21  | `jules_ai`                 | `famille/jules_ai.py`                    | famille, ia, enfant              |
| 22  | `suivi_perso`              | `famille/suivi_perso.py`                 | famille, sante                   |
| 23  | `resume_hebdo`             | `famille/resume_hebdo.py`                | famille, ia                      |
| 24  | `calendrier_planning`      | `famille/calendrier_planning.py`         | planning, calendrier             |
| 25  | `calendrier`               | `famille/calendrier/service.py`          | famille, integration             |
| 26  | `inventaire`               | `inventaire/service.py`                  | cuisine, ia, crud, stock         |
| 27  | `paris_crud`               | `jeux/_internal/paris_crud_service.py`   | jeux, crud, paris                |
| 28  | `loto_crud`                | `jeux/_internal/loto_crud_service.py`    | jeux, crud, loto                 |
| 29  | `jeux_ai`                  | `jeux/_internal/ai_service.py`           | jeux, ia                         |
| 30  | `football_data`            | `jeux/_internal/football_data.py`        | jeux, data, football             |
| 31  | `loto_data`                | `jeux/_internal/loto_data.py`            | jeux, data, loto                 |
| 32  | `prediction`               | `jeux/_internal/prediction_service.py`   | jeux, ia, prediction             |
| 33  | `series`                   | `jeux/_internal/series_service.py`       | jeux, crud, series               |
| 34  | `backtest`                 | `jeux/_internal/backtest_service.py`     | jeux, ia, backtest               |
| 35  | `sync`                     | `jeux/_internal/sync_service.py`         | jeux, sync                       |
| 36  | `scheduler`                | `jeux/_internal/scheduler_service.py`    | jeux, scheduler                  |
| 37  | `notification_jeux`        | `jeux/_internal/notification_service.py` | jeux, notification               |
| 38  | `entretien`                | `maison/entretien_service.py`            | maison, crud, entretien          |
| 39  | `jardin`                   | `maison/jardin_service.py`               | maison, crud, jardin             |
| 40  | `projets`                  | `maison/projets_service.py`              | maison, crud, projets            |
| 41  | `depenses_crud`            | `maison/depenses_crud_service.py`        | maison, crud, depenses           |
| 42  | `hub_data`                 | `maison/hub_data_service.py`             | maison, data                     |
| 43  | `codes_barres`             | `integrations/codes_barres.py`           | integrations, scan               |
| 44  | `facture_ocr`              | `integrations/facture.py`                | integrations, ia, ocr            |
| 45  | `openfoodfacts`            | `integrations/produit.py`                | integrations, api                |
| 46  | `meteo`                    | `integrations/weather/service.py`        | integrations, api                |
| 47  | `garmin`                   | `integrations/garmin/service.py`         | integrations, garmin             |
| 48  | `sync_temps_reel`          | `integrations/web/synchronisation.py`    | integrations, web                |
| 49  | `rapports_pdf`             | `rapports/generation.py`                 | rapports, export                 |
| 50  | `export_pdf`               | `rapports/export.py`                     | rapports, export                 |
| 51  | `backup`                   | `core/backup/service.py`                 | core, maintenance                |
| 52  | `authentification`         | `core/utilisateur/authentification.py`   | utilisateur, auth                |
| 53  | `historique_actions`       | `core/utilisateur/historique.py`         | utilisateur, audit               |
| 54  | `preferences_utilisateur`  | `core/utilisateur/preferences.py`        | utilisateur, config              |
| 55  | `webpush`                  | `core/notifications/notif_web_core.py`   | notifications, web               |
| 56  | `notifications_inventaire` | `core/notifications/inventaire.py`       | notifications, inventaire        |

> 55 unique service names (registry.py docstring example excluded).

---

## `BaseService[T]` Adopters (16 classes)

| #   | Class                   | Model `T`             | File                                   |
| --- | ----------------------- | --------------------- | -------------------------------------- |
| 1   | `ServiceWeekend`        | `WeekendActivity`     | `famille/weekend.py`                   |
| 2   | `ServiceSante`          | `HealthEntry`         | `famille/sante.py`                     |
| 3   | `BudgetService`         | `FamilyBudget`        | `famille/budget/service.py`            |
| 4   | `ServiceActivites`      | `FamilyActivity`      | `famille/activites.py`                 |
| 5   | `ServiceAchatsFamille`  | `FamilyPurchase`      | `famille/achats.py`                    |
| 6   | `ServiceRoutines`       | `Routine`             | `famille/routines.py`                  |
| 7   | `DepensesCrudService`   | `HouseExpense`        | `maison/depenses_crud_service.py`      |
| 8   | `ParisCrudService`      | `PariSportif`         | `jeux/_internal/paris_crud_service.py` |
| 9   | `LotoCrudService`       | `GrilleLoto`          | `jeux/_internal/loto_crud_service.py`  |
| 10  | `ServiceRecettes`       | `Recette`             | `cuisine/recettes/service.py`          |
| 11  | `ServicePlanning`       | `Planning`            | `cuisine/planning/service.py`          |
| 12  | `ServicePlanningUnifie` | `CalendarEvent`       | `cuisine/planning/global_planning.py`  |
| 13  | `ServiceCourses`        | `ArticleCourses`      | `cuisine/courses/service.py`           |
| 14  | `ServiceBatchCooking`   | `SessionBatchCooking` | `cuisine/batch_cooking/service.py`     |
| 15  | `ServiceInventaire`     | `ArticleInventaire`   | `inventaire/service.py`                |
| 16  | `BarcodeService`        | `ArticleInventaire`   | `integrations/codes_barres.py`         |

---

## `BaseAIService` Adopters (16 classes)

| #   | Class                         | File                                                  |
| --- | ----------------------------- | ----------------------------------------------------- |
| 1   | `ServiceSuggestions`          | `cuisine/suggestions/service.py`                      |
| 2   | `ServiceRecettes`             | `cuisine/recettes/service.py` (+ BaseService)         |
| 3   | `ServicePlanning`             | `cuisine/planning/service.py` (+ BaseService)         |
| 4   | `ServicePlanningUnifie`       | `cuisine/planning/global_planning.py` (+ BaseService) |
| 5   | `ServiceCourses`              | `cuisine/courses/service.py` (+ BaseService)          |
| 6   | `ServiceCoursesIntelligentes` | `cuisine/courses/suggestion.py`                       |
| 7   | `ServiceBatchCooking`         | `cuisine/batch_cooking/service.py` (+ BaseService)    |
| 8   | `ServiceInventaire`           | `inventaire/service.py` (+ BaseService)               |
| 9   | `WeekendAIService`            | `famille/weekend_ai.py`                               |
| 10  | `JulesAIService`              | `famille/jules_ai.py`                                 |
| 11  | `ServiceResumeHebdo`          | `famille/resume_hebdo.py`                             |
| 12  | `JeuxAIService`               | `jeux/_internal/ai_service.py`                        |
| 13  | `EntretienService`            | `maison/entretien_service.py`                         |
| 14  | `JardinService`               | `maison/jardin_service.py`                            |
| 15  | `ProjetsService`              | `maison/projets_service.py`                           |
| 16  | `FactureOCRService`           | `integrations/facture.py`                             |

---

## `@avec_resilience` Coverage (14 usages)

| File                                    | Method count | Config                  |
| --------------------------------------- | ------------ | ----------------------- |
| `integrations/garmin/service.py`        | 3            | retry=2, timeout=30s    |
| `integrations/weather/service.py`       | 2            | retry=2, timeout=15-30s |
| `integrations/produit.py`               | 1            | retry=2, timeout=10s    |
| `integrations/images/generator.py`      | 1            | retry=2, timeout=60s    |
| `jeux/_internal/football_data.py`       | 1            | retry=2, timeout=30s    |
| `jeux/_internal/loto_data.py`           | 1            | retry=2, timeout=60s    |
| `famille/calendrier/service.py`         | 1            | retry=2, timeout=30s    |
| `famille/calendrier/google_calendar.py` | 2            | retry=2, timeout varies |
| `cuisine/recettes/import_url.py`        | 1            | retry=2, timeout=30s    |
| `core/notifications/notif_ntfy.py`      | 1            | retry=2, timeout=15s    |

> All external HTTP-calling services are properly protected.

---

## Roadmap v5 Claims Verification

### Phase 1: ServiceSuggestions → BaseAIService ✅ CONFIRMED

- `ServiceSuggestions(BaseAIService)` in `cuisine/suggestions/service.py:33`
- Uses `call_with_cache_sync()` — confirmed via BaseAIService inheritance
- Rate limiting automatic via BaseAIService

### Phase 2: BaseService for Weekend/Sante/Budget ✅ CONFIRMED

- `ServiceWeekend(BaseService[WeekendActivity])` in `famille/weekend.py:34`
- `ServiceSante(BaseService[HealthEntry])` in `famille/sante.py:43`
- `BudgetService(BaseService[FamilyBudget])` in `famille/budget/service.py:38`
- All 3 use `super().__init__(model=..., cache_ttl=...)` pattern

### Phase 3: @service_factory 19, @avec_cache 10, @avec_resilience 4, JulesAI+WeekendAI moved ✅ CONFIRMED+EXCEEDED

- **`@service_factory`**: Roadmap claimed 19 — actual count is **55 unique registrations** (far exceeded, additional services created since Phase 3)
- **`@avec_cache`**: Roadmap claimed 10 added — actual count is **86 usages** (exceeded)
- **`@avec_resilience`**: Roadmap claimed 4 HTTP protected — actual count is **14 usages** across 10 files (exceeded)
- **JulesAI + WeekendAI moved**: `famille/jules_ai.py` and `famille/weekend_ai.py` both exist in `services/famille/` ✅

### Phase 6: ParisCrudService + LotoCrudService ✅ CONFIRMED

- `ParisCrudService(ParisQueryMixin, ParisMutationMixin, ParisSyncMixin, BaseService[PariSportif])` in `jeux/_internal/paris_crud_service.py:35`
- `LotoCrudService(BaseService[GrilleLoto])` in `jeux/_internal/loto_crud_service.py:43`
- Both have `@service_factory` and proper `super().__init__`

### Phase 10: 4 more BaseService migrations ✅ CONFIRMED

- `ServiceActivites(BaseService[FamilyActivity])` in `famille/activites.py:25` ✅
- `ServiceAchatsFamille(BaseService[FamilyPurchase])` in `famille/achats.py:37` ✅
- `ServiceRoutines(BaseService[Routine])` in `famille/routines.py:50` ✅
- `DepensesCrudService(BaseService[HouseExpense])` in `maison/depenses_crud_service.py:44` ✅

---

## Anti-Patterns Found

### Minor Issues (Low Severity)

| #   | Issue                                                                                                          | File                                  | Severity |
| --- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------- | -------- |
| 1   | `accueil_data_service.py` lives at package root, not in a sub-package                                          | `services/accueil_data_service.py`    | Low      |
| 2   | `DepensesCrudService` has `_instance: Optional` class attribute — redundant with `@service_factory` singleton  | `maison/depenses_crud_service.py:51`  | Low      |
| 3   | `ServiceMeteo` doesn't inherit `BaseService` or `BaseAIService` — inherits only mixin                          | `integrations/weather/service.py`     | Low      |
| 4   | `ImageGenerator` functions lack `@service_factory`                                                             | `integrations/images/generator.py`    | Low      |
| 5   | Some plain-class services (Jules, SuiviPerso, CalendrierPlanning) could benefit from BaseService if CRUD grows | `famille/jules.py`, etc.              | Info     |
| 6   | `ServiceBatchCooking` MRO puts mixins before `BaseService`/`BaseAIService` — works but non-standard ordering   | `cuisine/batch_cooking/service.py:42` | Info     |

### No Critical or High Severity Anti-Patterns Found

---

## Scoring Breakdown

| Criterion                      | Weight | Score  | Notes                                                           |
| ------------------------------ | ------ | ------ | --------------------------------------------------------------- |
| `@service_factory` coverage    | 20%    | 9.5/10 | 55/~57 services covered (ImageGenerator missing)                |
| `BaseService[T]` adoption      | 15%    | 9/10   | 16 adopters, all CRUD services covered                          |
| `BaseAIService` adoption       | 15%    | 10/10  | 16 adopters, all AI services covered                            |
| Decorator stacking (`@avec_*`) | 20%    | 9/10   | Heavy adoption: 86 cache, 100+ session_db, 100+ gestion_erreurs |
| `@avec_resilience` on HTTP     | 10%    | 9/10   | 14 usages, all external APIs protected                          |
| Event bus emission             | 10%    | 7.5/10 | 28 emissions across 10 services — some services could emit more |
| Code organization              | 10%    | 8.5/10 | Clean sub-packages, mixins, 1 file at root level                |

### **Overall Score: 8.5 / 10**

**Strengths**:

- Excellent pattern uniformity — all Roadmap v5 claims verified and exceeded
- Consistent multi-inheritance pattern (BaseService + BaseAIService + domain mixins)
- Heavy decorator coverage eliminates boilerplate
- All external HTTP calls protected with `@avec_resilience`
- `@service_factory` on every service factory function

**Improvement opportunities**:

- Event bus could be more widely adopted (Sante, Budget, Jules don't emit events)
- `accueil_data_service.py` should be moved into a sub-package
- Remove redundant `_instance` attribute from `DepensesCrudService`
- Consider `BaseService[T]` for maison AI services if they manage a primary model
