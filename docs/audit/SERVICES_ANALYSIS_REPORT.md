# 📊 Rapport d'Analyse Détaillé — `src/services/`

**Date**: 2026-02-24  
**Scope**: `d:\Projet_streamlit\assistant_matanne\src\services\`  
**Auteur**: Audit automatisé

---

## 1. Vue d'Ensemble

| Métrique | Valeur |
|---|---|
| **Total fichiers .py** | **196** |
| **Total LOC** | **39 700** |
| **Sous-packages** | 8 + root (core, cuisine, famille, integrations, inventaire, jeux, maison, rapports) |
| **@service_factory registrations** | **56** |
| **get_*_service() factories** | **45** |
| **BaseAIService subclasses** | **16** |
| **BaseService[T] adopters** | **5** (+ 7 combinés avec BaseAIService) |
| **Event bus emitters (obtenir_bus().emettre)** | **28** |
| **@avec_cache usages** | **~80** |
| **@avec_resilience usages** | **~14** |

---

## 2. Inventaire par Sous-Package

### 2.1 `core/` — Infrastructure & Base Services

| Métrique | Valeur |
|---|---|
| **Fichiers** | 49 |
| **LOC** | 8 580 |

**Sous-packages internes:**

| Sous-package | Fichiers | LOC | Description |
|---|---|---|---|
| `base/` | 13 (+ 1 empty `mixins/`) | ~1 715 | BaseService, BaseAIService, IOService, protocols, pipeline, async_utils |
| `events/` | 3 | 696 | BusEvenements, EvenementDomaine, subscribers |
| `backup/` | 7 | 1 187 | ServiceBackup, export/restore mixins, utils |
| `notifications/` | 8 | 1 639 | ServiceWebPush, ServiceNtfy, inventaire notifs |
| `observability/` | 4 | 989 | health checks, metrics collector, spans/tracing |
| `utilisateur/` | 9 | 1 664 | AuthService, historique, preferences, auth mixins |
| `registry.py` | 1 | 364 | ServiceRegistry + @service_factory |

**Key classes:**
- `BaseService[T]` — Generic CRUD service (types.py, 216 LOC)
- `BaseAIService` — IA service with rate limiting + cache (ai_service.py, 333 LOC)
- `IOService` — CSV/JSON import/export (io_service.py, 170 LOC)
- `BusEvenements` — Domain event bus with wildcards (bus.py, 311 LOC)
- `ServiceRegistry` — Singleton registry with `@service_factory` (registry.py, 364 LOC)
- `AuthService` — Authentication with mixins (authentification.py, 304 LOC)
- `ActionHistoryService` — Audit trail (historique.py, 509 LOC)
- `ServiceBackup` — Full DB backup/restore (service.py, 230 LOC)

**Pattern adoption:**
- ✅ `@service_factory`: backup, webpush, notifications_inventaire, authentification, historique_actions, preferences_utilisateur (6 registrations)
- ✅ `@avec_cache`: Not applicable (infrastructure layer)
- ✅ `@avec_resilience`: notif_ntfy (1 usage)
- ✅ Event bus: BusEvenements defined here, subscribers registered

**Issues:**
- ⚠️ `ServiceNtfy` + `PlanificateurNtfy` — have `get_ntfy_service()` but **no `@service_factory`**
- ⚠️ `core/base/mixins/` — empty directory (should be cleaned up)

---

### 2.2 `cuisine/` — Recipes, Planning, Courses, Batch Cooking, Suggestions

| Métrique | Valeur |
|---|---|
| **Fichiers** | 51 |
| **LOC** | 9 576 |

**Sous-packages internes:**

| Sous-package | Fichiers | LOC | Description |
|---|---|---|---|
| `recettes/` | 12 | 3 131 | ServiceRecettes, IA suggestions/versions, import URL, parsers |
| `planning/` | 14 | 2 903 | ServicePlanning, global planning, IA mixin, templates, recurrence, rappels |
| `courses/` | 5 | 953 | ServiceCourses, smart shopping suggestions |
| `batch_cooking/` | 7 | 1 275 | ServiceBatchCooking, IA, stats, utils |
| `suggestions/` | 10 | 1 350 | ServiceSuggestions, predictions, scoring, saisons, equilibre |
| `__init__.py` | 1 | 38 | Lazy imports |

**Key classes:**
- `ServiceRecettes(BaseService[Recette], BaseAIService, RecipeAIMixin, RecettesIAGenerationMixin)` — 558 LOC
- `ServicePlanning(BaseService[Planning], BaseAIService, PlanningAIMixin, PlanningIAGenerationMixin)` — 333 LOC
- `ServiceCourses(BaseService[ArticleCourses], BaseAIService)` — 480 LOC
- `ServiceBatchCooking(BaseService[...], BaseAIService)` — 379 LOC
- `ServicePlanningUnifie(BaseService[CalendarEvent], BaseAIService, PlanningAIMixin)` — 505 LOC
- `ServiceCoursesIntelligentes(BaseAIService)` — 271 LOC
- `RecipeImportService(BaseAIService)` — 260 LOC
- `ServiceSuggestions` — 442 LOC (standalone, no base class)
- `PredictionService` — 291 LOC (standalone)
- `ServiceRecurrence` — 237 LOC
- `ServiceTemplates` — 242 LOC
- `ServiceRappels` — 177 LOC

**Pattern adoption:**
- ✅ `@service_factory`: 12 registrations (recettes, planning, courses, courses_intelligentes, batch_cooking, suggestions, predictions, templates, recurrence, rappels, import_recettes, + registry duplicate "recettes")
- ✅ `@avec_cache`: ~18 usages (service.py, global_planning, batch_cooking, courses, recettes_ia_*)
- ✅ `@avec_resilience`: 1 (import_url.py)
- ✅ BaseAIService: 7 classes inherit
- ✅ BaseService[T]: 4 classes adopt
- ✅ Event bus: 5 emitters (recettes.service, courses.service, planning.service, batch_cooking.service)
- ✅ `obtenir_client_ia()`: Used consistently (7 usages, no direct Mistral)

**Issues:**
- ⚠️ `ServiceSuggestions` does NOT inherit from `BaseAIService` — uses `obtenir_client_ia()` directly + manual `AnalyseurIA` + `RateLimitIA` (legacy pattern)
- ⚠️ `PredictionService` does NOT inherit from `BaseAIService` nor `BaseService[T]`
- ⚠️ `ServiceRecurrence`, `ServiceTemplates`, `ServiceRappels` — no base class inheritance
- ⚠️ Duplicate `@service_factory("recettes")` — once in `cuisine/recettes/service.py`, once as example in `core/registry.py` docstring

---

### 2.3 `famille/` — Family services (Jules, routines, achats, weekends, santé, etc.)

| Métrique | Valeur |
|---|---|
| **Fichiers** | 22 |
| **LOC** | 4 807 |

**Sous-packages internes:**

| Sous-package | Fichiers | LOC | Description |
|---|---|---|---|
| `budget/` | 5 | 1 245 | BudgetService with alertes & analyses mixins |
| `calendrier/` | 5 | 1 156 | CalendarSyncService, Google Calendar, schemas |
| Root files | 12 | 2 406 | jules, routines, activites, achats, weekend, sante, suivi_perso, AI services |

**Key classes:**
- `ServiceRoutines` — 366 LOC
- `ServiceWeekend` — 303 LOC
- `ServiceSante` — 300 LOC
- `ServiceAchatsFamille` — 287 LOC
- `ServiceSuiviPerso` — 259 LOC
- `ServiceCalendrierPlanning` — 321 LOC
- `CalendarSyncService(GoogleCalendarMixin)` — 433 LOC
- `BudgetService(BudgetAnalysesMixin, BudgetAlertesMixin)` — 312 LOC
- `JulesAIService(BaseAIService)` — 123 LOC
- `WeekendAIService(BaseAIService)` — 96 LOC
- `ServiceJules` — 133 LOC
- `ServiceActivites` — 156 LOC

**Pattern adoption:**
- ✅ `@service_factory`: 12 registrations (jules, routines, activites, achats_famille, weekend, sante, suivi_perso, calendrier_planning, calendrier, budget, jules_ai, weekend_ai)
- ✅ `@avec_cache`: ~25 usages (heavily used across all services)
- ✅ `@avec_resilience`: 1 (calendrier/service.py)
- ✅ BaseAIService: JulesAIService, WeekendAIService (2)
- ✅ Event bus: 12 emitters (activites, routines, achats, weekend, suivi_perso)
- ✅ `obtenir_client_ia()`: Used in jules_ai.py, weekend_ai.py

**Issues:**
- ⚠️ Most domain services (ServiceRoutines, ServiceWeekend, ServiceSante, etc.) — **no base class inheritance** (standalone classes)
- ℹ️ Good practice: AI services are properly separated (jules.py vs jules_ai.py, weekend.py vs weekend_ai.py)

---

### 2.4 `integrations/` — External APIs & integrations

| Métrique | Valeur |
|---|---|
| **Fichiers** | 30 |
| **LOC** | 5 862 |

**Sous-packages internes:**

| Sous-package | Fichiers | LOC | Description |
|---|---|---|---|
| `garmin/` | 6 | 1 148 | ServiceGarmin, OAuth, stats/sync utils |
| `images/` | 2 | 520 | Image generation (Leonardo, Unsplash, Pexels, etc.) |
| `weather/` | 8 | 1 627 | ServiceMeteo, alertes, arrosage, jardin meteo, saisons |
| `web/` | 5 | 1 632 | RealtimeSyncService, PWA service worker, templates |
| Root files | 3 | 849 | BarcodeService, FactureOCRService, OpenFoodFactsService |

**Key classes:**
- `BarcodeService(BaseService[ArticleInventaire])` — 397 LOC
- `FactureOCRService(BaseAIService)` — 202 LOC
- `OpenFoodFactsService` — 250 LOC
- `ServiceMeteo(MeteoJardinMixin)` — 463 LOC
- `ServiceGarmin` — 445 LOC
- `RealtimeSyncService` — 418 LOC
- `generer_image_recette()` — standalone function (498 LOC in generator.py)

**Pattern adoption:**
- ✅ `@service_factory`: 6 registrations (codes_barres, openfoodfacts, facture_ocr, meteo, garmin, sync_temps_reel)
- ✅ `@avec_cache`: 2 usages (codes_barres)
- ✅ `@avec_resilience`: 7 usages (garmin×3, weather×2, produit×1, images×1)
- ✅ BaseAIService: FactureOCRService (1)
- ✅ BaseService[T]: BarcodeService (1)
- ✅ `obtenir_client_ia()`: facture.py

**Issues:**
- ⚠️ `images/generator.py` — **no service class**, exports standalone functions only. No `@service_factory`, no `get_*_service()`.
- ⚠️ `OpenFoodFactsService` — no base class inheritance
- ⚠️ `ServiceMeteo`, `ServiceGarmin` — no base class inheritance (use mixin for weather only)
- ⚠️ `RealtimeSyncService` — no base class inheritance

---

### 2.5 `inventaire/` — Inventory management

| Métrique | Valeur |
|---|---|
| **Fichiers** | 7 |
| **LOC** | 1 135 |

**Key classes:**
- `ServiceInventaire(InventaireIOMixin, InventaireStockMixin, InventaireStatsMixin, InventaireOperationsMixin, BaseAIService)` — 177 LOC (service.py)
- 4 Mixins: InventaireOperationsMixin (346), InventaireIOMixin (189), InventaireStatsMixin (166), InventaireStockMixin (178)

**Pattern adoption:**
- ✅ `@service_factory("inventaire")`: Yes
- ✅ `@avec_cache`: 2 usages (service.py, operations.py)
- ✅ BaseAIService: ServiceInventaire inherits
- ✅ Event bus: 3 emitters (inventaire_operations.py)
- ✅ `obtenir_client_ia()`: Yes

**Issues:**
- None significant. Well-structured with mixins.

---

### 2.6 `jeux/` — Betting, loto, predictions

| Métrique | Valeur |
|---|---|
| **Fichiers** | 15 |
| **LOC** | 5 130 |

**Structure:** All services under `_internal/` (encapsulated), facade at `__init__.py` (232 LOC).

**Key classes:**
- `JeuxAIService(BaseAIService)` — 427 LOC
- `ParisCrudService(BaseService[PariSportif])` — 607 LOC
- `LotoCrudService(BaseService[GrilleLoto])` — 356 LOC
- `BacktestService` — 450 LOC
- `PredictionService` — 470 LOC
- `FootballDataService` — 501 LOC
- `SeriesService` — 435 LOC
- `NotificationJeuxService` — 375 LOC
- `SchedulerService` — 366 LOC
- `SyncService` — 293 LOC
- `LotoDataService` — 324 LOC

**Pattern adoption:**
- ✅ `@service_factory`: 11 registrations (jeux_ai, loto_crud, paris_crud, backtest, prediction, series, scheduler, sync, notification_jeux, loto_data, football_data)
- ✅ `@avec_cache`: 10+ usages (football_helpers, football_data)
- ✅ `@avec_resilience`: 2 usages (football_data, loto_data)
- ✅ BaseAIService: JeuxAIService (1)
- ✅ BaseService[T]: ParisCrudService, LotoCrudService (2)
- ✅ `obtenir_client_ia()`: ai_service.py

**Issues:**
- ⚠️ `BacktestService`, `PredictionService`, `FootballDataService`, `SeriesService`, `SchedulerService`, `SyncService`, `LotoDataService`, `NotificationJeuxService` — **no base class inheritance** (standalone)
- ℹ️ Good: facade pattern in `__init__.py` re-exports all factories

---

### 2.7 `maison/` — Home management

| Métrique | Valeur |
|---|---|
| **Fichiers** | 13 |
| **LOC** | 2 854 |

**Key classes:**
- `EntretienService(EntretienGamificationMixin, BaseAIService)` — 365 LOC (+ gamification mixin 448 LOC)
- `JardinService(JardinGamificationMixin, BaseAIService)` — 374 LOC (+ 3 mixins: catalogue 94, taches 175, gamification 312)
- `ProjetsService(BaseAIService)` — 391 LOC
- `DepensesCrudService` — 197 LOC
- `HubDataService` — 66 LOC

**Pattern adoption:**
- ✅ `@service_factory`: 5 registrations (entretien, jardin, projets, depenses_crud, hub_data)
- ✅ `@avec_cache`: 8 usages
- ✅ `@avec_session_db`: Heavily used (10+ usages)
- ✅ BaseAIService: EntretienService, JardinService, ProjetsService (3)
- ✅ Event bus: 2 emitters (entretien_service.py)
- ✅ `obtenir_client_ia()`: 3 usages

**Issues:**
- ⚠️ `DepensesCrudService`, `HubDataService` — no base class inheritance
- ℹ️ Good mixin patterns for gamification (entretien, jardin)

---

### 2.8 `rapports/` — PDF reports & export

| Métrique | Valeur |
|---|---|
| **Fichiers** | 7 |
| **LOC** | 1 684 |

**Key classes:**
- `ServiceRapportsPDF(BudgetReportMixin, GaspillageReportMixin, PlanningReportMixin)` — 354 LOC
- `ServiceExportPDF` — 436 LOC
- 3 Mixins: BudgetReportMixin (209), GaspillageReportMixin (238), PlanningReportMixin (313)

**Pattern adoption:**
- ✅ `@service_factory`: 2 registrations (rapports_pdf, export_pdf)
- ✅ `@avec_cache`: 3 usages
- ✅ `@avec_session_db`: 2 usages (rapports_budget.py)

**Issues:**
- None significant. Clean mixin-based composition.

---

### 2.9 Root files

| Fichier | LOC | Description |
|---|---|---|
| `__init__.py` | 25 | Package docstring + lazy imports |
| `accueil_data_service.py` | 47 | AccueilDataService (dashboard data) |

**Pattern adoption:**
- ✅ `@service_factory("accueil_data")`: Yes
- ✅ `@avec_session_db`: Yes
- ✅ `@avec_gestion_erreurs`: Yes

---

## 3. Vérifications Spécifiques

### 3.1 Répertoires supprimés (confirmé)

| Répertoire | Statut |
|---|---|
| `services/specifications/` | ✅ **SUPPRIMÉ** |
| `services/middleware/` | ✅ **SUPPRIMÉ** |
| `services/core/middleware/` | ✅ **SUPPRIMÉ** |
| `services/cqrs/` | ✅ **SUPPRIMÉ** |
| `services/CQRS/` | ✅ **SUPPRIMÉ** |

### 3.2 Direct Mistral Client Instantiation

✅ **AUCUNE** importation directe de `from mistralai` trouvée dans `src/services/`.  
✅ **Tous** les services utilisent `obtenir_client_ia()` de `src.core.ai` (34 usages vérifiés).

### 3.3 `@service_factory` Registrations (56 total)

| Package | Count | Service Names |
|---|---|---|
| `core/` | 6 | backup, webpush, notifications_inventaire, authentification, historique_actions, preferences_utilisateur |
| `cuisine/` | 12 | recettes, planning, courses, courses_intelligentes, batch_cooking, suggestions, predictions, templates, recurrence, rappels, import_recettes |
| `famille/` | 12 | jules, jules_ai, routines, activites, achats_famille, weekend, weekend_ai, sante, suivi_perso, calendrier, calendrier_planning, budget |
| `integrations/` | 6 | codes_barres, openfoodfacts, facture_ocr, meteo, garmin, sync_temps_reel |
| `inventaire/` | 1 | inventaire |
| `jeux/` | 11 | jeux_ai, loto_crud, paris_crud, backtest, prediction, series, scheduler, sync, notification_jeux, loto_data, football_data |
| `maison/` | 5 | entretien, jardin, projets, depenses_crud, hub_data |
| `rapports/` | 2 | rapports_pdf, export_pdf |
| `root` | 1 | accueil_data |

> **Note:** `core/registry.py` contains an example `@service_factory("recettes")` in a docstring — this is harmless but counts in grep.

### 3.4 Services WITH `get_*_service()` but WITHOUT `@service_factory`

| Service | Factory Function | Status |
|---|---|---|
| `ServiceNtfy` | `get_ntfy_service()` | ⚠️ **Missing @service_factory** |

### 3.5 Services WITHOUT `get_*_service()` factory function

| Service | File | Issue |
|---|---|---|
| `images/generator.py` | Standalone functions | No service class at all. Functions only. |
| `PlanificateurNtfy` | `core/notifications/notif_ntfy.py` | Helper class, not a primary service |

### 3.6 All BaseAIService Subclasses (16 unique)

| Class | File | Also inherits |
|---|---|---|
| `ServiceRecettes` | cuisine/recettes/service.py | BaseService[Recette], RecipeAIMixin, RecettesIAGenerationMixin |
| `ServicePlanning` | cuisine/planning/service.py | BaseService[Planning], PlanningAIMixin, PlanningIAGenerationMixin |
| `ServicePlanningUnifie` | cuisine/planning/global_planning.py | BaseService[CalendarEvent], PlanningAIMixin |
| `ServiceCourses` | cuisine/courses/service.py | BaseService[ArticleCourses] |
| `ServiceBatchCooking` | cuisine/batch_cooking/service.py | BaseService[...] |
| `ServiceCoursesIntelligentes` | cuisine/courses/suggestion.py | — |
| `RecipeImportService` | cuisine/recettes/import_url.py | — |
| `ServiceInventaire` | inventaire/service.py | InventoryAIMixin + 4 operation mixins |
| `JeuxAIService` | jeux/_internal/ai_service.py | — |
| `EntretienService` | maison/entretien_service.py | EntretienGamificationMixin |
| `JardinService` | maison/jardin_service.py | JardinGamificationMixin |
| `ProjetsService` | maison/projets_service.py | — |
| `FactureOCRService` | integrations/facture.py | — |
| `JulesAIService` | famille/jules_ai.py | — |
| `WeekendAIService` | famille/weekend_ai.py | — |

> Note: count is 15 unique concrete classes (ServicePlanningUnifie may be secondary).

### 3.7 BaseService[T] Adopters (7 classes)

| Class | Type Parameter |
|---|---|
| `ServiceRecettes` | `Recette` |
| `ServicePlanning` | `Planning` |
| `ServicePlanningUnifie` | `CalendarEvent` |
| `ServiceCourses` | `ArticleCourses` |
| `ParisCrudService` | `PariSportif` |
| `LotoCrudService` | `GrilleLoto` |
| `BarcodeService` | `ArticleInventaire` |

### 3.8 Event Bus Usage

**Emitters (28 total):**

| Package | Count | Services |
|---|---|---|
| `cuisine/` | 5 | recettes.service, courses.service, planning.service, batch_cooking.service (×2) |
| `famille/` | 12 | activites (×3), routines (×5), achats (×3), weekend (×3), suivi_perso (×1) |
| `inventaire/` | 3 | inventaire_operations (×3) |
| `maison/` | 2 | entretien_service (×2) |

**Subscribers (in core/events/subscribers.py, 259 LOC):**
- 12 cache invalidation subscribers (recettes, stock, courses, entretien, planning, batch_cooking, activites, routines, weekend, achats, food_log)
- 2 observability subscribers (metrics, error logging)
- 1 audit subscriber

---

## 4. Dead Code & Potential Issues

### 4.1 Confirmed Issues

| Issue | Severity | Details |
|---|---|---|
| Empty `core/base/mixins/` directory | Low | Empty folder, should be deleted |
| `ServiceNtfy` missing `@service_factory` | Medium | Has `get_ntfy_service()` but isn't registered in the service registry |
| `images/generator.py` — no service pattern | Low | Standalone functions, not wrapped in a service class. Acceptable for utility functions. |
| `ServiceSuggestions` — legacy IA pattern | Medium | Uses `obtenir_client_ia()` + manual `AnalyseurIA` + `RateLimitIA` instead of inheriting `BaseAIService` |

### 4.2 No Base Class Inheritance (standalone services)

16 service classes that don't inherit from `BaseService[T]` or `BaseAIService`:

| Service | Package | Justified? |
|---|---|---|
| `ServiceSuggestions` | cuisine/suggestions | ❌ Uses IA, should inherit BaseAIService |
| `PredictionService` | cuisine/suggestions | ⚠️ ML-focused, arguably OK |
| `ServiceRecurrence` | cuisine/planning | ✅ Pure logic, no DB/IA |
| `ServiceTemplates` | cuisine/planning | ✅ Pure logic |
| `ServiceRappels` | cuisine/planning | ✅ Pure logic + notifications |
| `ServiceRoutines` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceWeekend` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceSante` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceAchatsFamille` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceSuiviPerso` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceActivites` | famille | ⚠️ CRUD service, could use BaseService |
| `ServiceJules` | famille | ✅ Orchestrator, delegates to JulesAIService |
| `BudgetService` | famille/budget | ⚠️ Uses mixins, could also inherit base |
| `DepensesCrudService` | maison | ⚠️ CRUD, name says "crud" but no BaseService |
| `HubDataService` | maison | ✅ Data aggregation only |
| `AccueilDataService` | root | ✅ Data aggregation only |

### 4.3 `recettes_ia_generation.py` — Backward Compatibility Shim

- 15 LOC, only re-exports from `recettes_ia_suggestions.py` and `recettes_ia_versions.py`
- Acceptable pattern for backward compatibility
- Could be removed if all imports are updated

---

## 5. Architecture Quality Assessment

### 5.1 Strengths

1. **Excellent `@service_factory` adoption** — 56 registrations covering virtually all services
2. **Consistent `get_*_service()` pattern** — 45 factory functions, often with French aliases (`obtenir_service_*`)
3. **Zero direct Mistral imports** — All IA goes through `obtenir_client_ia()`
4. **Strong event bus adoption** — 28 emitters + 15 subscribers with proper cache invalidation
5. **Clean directory structure** — All deprecated directories (specifications, middleware, CQRS) confirmed deleted
6. **Good mixin decomposition** — Jardin (3 mixins), entretien (1), inventaire (4), rapports (3), auth (4), budget (2)
7. **Heavy `@avec_cache` usage** — ~80 usages with proper TTL configuration
8. **Proper `@avec_resilience`** — Applied to all external API calls (garmin, weather, produit, images, loto_data)
9. **Lazy imports everywhere** — `__getattr__` pattern in all `__init__.py` files
10. **Well-structured `jeux/` package** — Facade pattern with `_internal/` encapsulation

### 5.2 Weaknesses

1. **Inconsistent BaseService[T] adoption** — Only 7/~40 services use the generic CRUD base class
2. **Many standalone service classes** — 16 services don't inherit base classes (especially `famille/` package)
3. **ServiceSuggestions legacy pattern** — Manual IA client management instead of BaseAIService
4. **Empty `mixins/` directory** — Dead directory in `core/base/`
5. **ServiceNtfy missing registry** — Only service with factory function but no `@service_factory`
6. **No event bus usage in `jeux/`** — 11 services but 0 event emitters
7. **No event bus usage in `rapports/`** — Could emit report generation events
8. **`images/generator.py`** — 498 LOC of standalone functions, not service-wrapped

---

## 6. Scoring

| Critère | Score | Note |
|---|---|---|
| Structure & organisation | 9/10 | Clean packages, proper `__init__.py`, lazy imports |
| @service_factory adoption | 9/10 | 56 registrations, only 1 missing (ServiceNtfy) |
| Factory function coverage | 9/10 | 45 get_*_service() functions, only images missing |
| BaseAIService adoption | 8/10 | 15 subclasses, but ServiceSuggestions is legacy |
| BaseService[T] adoption | 5/10 | Only 7 adopters, many CRUD services are standalone |
| Event bus integration | 7/10 | 28 emitters but jeux/ and rapports/ have none |
| Cache strategy | 9/10 | ~80 @avec_cache, proper TTLs |
| Resilience | 8/10 | All external APIs covered |
| Dead code cleanup | 8/10 | Deprecated dirs deleted, one empty dir remains |
| obtenir_client_ia() compliance | 10/10 | Perfect, zero direct Mistral imports |

### **Overall Score: 8.2 / 10**

---

## 7. Recommandations Prioritaires

### P1 (Quick wins)
1. **Supprimer** `core/base/mixins/` — empty directory
2. **Ajouter `@service_factory`** à `ServiceNtfy` dans `notif_ntfy.py`

### P2 (Medium effort)
3. **Migrer `ServiceSuggestions`** vers `BaseAIService` inheritance (éliminer manual `AnalyseurIA`/`RateLimitIA`)
4. **Ajouter event bus** aux services `jeux/` (au minimum pour paris créés, grilles validées)
5. **Wrapper `images/generator.py`** dans un `ImageService` avec `@service_factory`

### P3 (Future roadmap)
6. **Migrer les services famille/** vers `BaseService[T]` (ServiceRoutines, ServiceWeekend, etc.)
7. **Migrer `DepensesCrudService`** vers `BaseService[Depense]`
8. **Ajouter event bus** aux rapports (emit on PDF generated)
