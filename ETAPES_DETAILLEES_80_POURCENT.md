# 📝 ÉTAPES DÉTAILLÉES - PLAN 80% COUVERTURE

## Comment utiliser ce plan

1. **Suivre l'ordre des phases** - Commencer par Phase 1 (Core) car c'est la fondation
2. **Vérifier après chaque modification** - `pytest tests/module/ --cov=src/module --cov-report=term-missing`
3. **Respecter la structure tests/ ↔ src/** - Chaque fichier source a son fichier test correspondant

---

## 🔴 PHASE 1: CORE FOUNDATION (Priorité CRITIQUE)

### Jour 1-2: Module AI

#### 1.1 `src/core/ai/client.py` (12.50% → 80%)
**Fichier test**: `tests/core/test_ai_client.py`

```python
# Tests à ajouter/compléter:
class TestClientIA:
    def test_init_with_valid_api_key(self): ...
    def test_init_with_missing_api_key(self): ...
    def test_generate_response_success(self): ...
    def test_generate_response_rate_limit(self): ...
    def test_generate_response_timeout(self): ...
    def test_generate_response_invalid_json(self): ...
    def test_streaming_response(self): ...
    def test_retry_on_failure(self): ...
    def test_context_manager(self): ...
```

**Commande de validation**:
```bash
pytest tests/core/test_ai_client.py --cov=src/core/ai/client.py --cov-report=term-missing -v
```

#### 1.2 `src/core/ai/parser.py` (10.92% → 80%)
**Fichier test**: `tests/core/test_ai_parser.py`

```python
class TestAnalyseurIA:
    def test_parse_json_valid(self): ...
    def test_parse_json_invalid(self): ...
    def test_parse_json_with_markdown(self): ...
    def test_parse_list_response(self): ...
    def test_parse_pydantic_model(self): ...
    def test_extract_json_from_text(self): ...
    def test_handle_nested_json(self): ...
    def test_handle_empty_response(self): ...
```

#### 1.3 `src/core/ai/cache.py` (37.31% → 80%)
**Fichier test**: `tests/core/test_ai_cache.py`

```python
class TestCacheIA:
    def test_get_cached_response(self): ...
    def test_set_cached_response(self): ...
    def test_cache_expiration(self): ...
    def test_semantic_similarity_hit(self): ...
    def test_semantic_similarity_miss(self): ...
    def test_clear_cache(self): ...
    def test_cache_statistics(self): ...
```

#### 1.4 `src/core/ai/rate_limit.py` (34.48% → 80%)
**Fichier test**: `tests/core/test_ai_rate_limit.py`

```python
class TestRateLimitIA:
    def test_check_rate_limit_allowed(self): ...
    def test_check_rate_limit_exceeded(self): ...
    def test_increment_usage(self): ...
    def test_reset_daily_limit(self): ...
    def test_reset_hourly_limit(self): ...
    def test_get_remaining_quota(self): ...
```

### Jour 3-4: Infrastructure Core

#### 1.5 `src/core/database.py` (25.00% → 80%)
**Fichier test**: `tests/core/test_database.py`

```python
class TestDatabase:
    def test_get_engine_creates_engine(self): ...
    def test_get_session_returns_session(self): ...
    def test_get_db_context_commits(self): ...
    def test_get_db_context_rollback_on_error(self): ...
    
class TestGestionnaireMigrations:
    def test_obtenir_version_courante(self): ...
    def test_appliquer_migrations(self): ...
    def test_verifier_coherence_schema(self): ...
    def test_creer_tables_si_necessaire(self): ...
```

#### 1.6 `src/core/decorators.py` (27.45% → 80%)
**Fichier test**: `tests/core/test_decorators.py`

```python
class TestWithDbSession:
    def test_injects_session(self): ...
    def test_commits_on_success(self): ...
    def test_rollback_on_error(self): ...
    
class TestWithCache:
    def test_caches_result(self): ...
    def test_cache_ttl_expiration(self): ...
    def test_cache_key_generation(self): ...
    
class TestWithErrorHandling:
    def test_catches_exceptions(self): ...
    def test_logs_errors(self): ...
    def test_returns_default_on_error(self): ...
```

#### 1.7 `src/core/errors.py` (19.85% → 80%)
**Fichier test**: `tests/core/test_errors.py`

```python
class TestErreurBaseDeDonnees:
    def test_raise_with_message(self): ...
    def test_error_code(self): ...
    
class TestErreurValidation:
    def test_raise_with_field(self): ...
    def test_multiple_errors(self): ...
    
class TestErreurAuthentification:
    def test_unauthorized_access(self): ...
    
class TestErreurConfiguration:
    def test_missing_config(self): ...
    
class TestGererErreurs:
    def test_decorator_catches_all(self): ...
    def test_decorator_specific_exception(self): ...
```

#### 1.8 `src/core/lazy_loader.py` (0.00% → 80%)
**Fichier test**: `tests/core/test_lazy_loader.py`

```python
class TestLazyModuleLoader:
    def test_load_module_on_first_access(self): ...
    def test_cache_loaded_module(self): ...
    def test_handle_import_error(self): ...
    
class TestOptimizedRouter:
    def test_register_module(self): ...
    def test_get_module_lazy(self): ...
    def test_list_available_modules(self): ...
    def test_reload_module(self): ...
```

#### 1.9 `src/core/ai_agent.py` (0.00% → 80%)
**Fichier test**: `tests/core/test_ai_agent.py`

```python
class TestAIAgent:
    def test_create_agent(self): ...
    def test_execute_task(self): ...
    def test_handle_error(self): ...
```

### Jour 5: Cache & Performance

#### 1.10 `src/core/cache.py` (33.65% → 80%)
**Fichier test**: `tests/core/test_cache.py`

```python
class TestCache:
    def test_get_existing_key(self): ...
    def test_get_missing_key(self): ...
    def test_set_with_ttl(self): ...
    def test_delete_key(self): ...
    def test_clear_by_prefix(self): ...
    def test_get_stats(self): ...
    def test_memory_limit(self): ...
```

#### 1.11 `src/core/cache_multi.py` (32.64% → 80%)
**Fichier test**: `tests/core/test_cache_multi.py`

```python
class TestMultiCache:
    def test_l1_cache_hit(self): ...
    def test_l2_cache_fallback(self): ...
    def test_write_through(self): ...
    def test_invalidate_all_levels(self): ...
    def test_concurrent_access(self): ...
```

#### 1.12 `src/core/config.py` (37.31% → 80%)
**Fichier test**: `tests/core/test_config.py`

```python
class TestConfig:
    def test_load_from_env_file(self): ...
    def test_load_from_env_local(self): ...
    def test_load_from_streamlit_secrets(self): ...
    def test_validation_required_fields(self): ...
    def test_default_values(self): ...
    def test_type_coercion(self): ...
    
class TestObtenir Parametres:
    def test_singleton_pattern(self): ...
    def test_reload_config(self): ...
```

---

## 🟠 PHASE 2: API MODULE (Priorité HAUTE)

#### 2.1 `src/api/main.py` (34.52% → 80%)
**Fichier test**: `tests/api/test_main.py`

```python
class TestAPIEndpoints:
    # Health & Info
    def test_health_check(self): ...
    def test_api_info(self): ...
    
    # CRUD Recettes
    def test_get_recettes(self): ...
    def test_get_recette_by_id(self): ...
    def test_create_recette(self): ...
    def test_update_recette(self): ...
    def test_delete_recette(self): ...
    
    # CRUD Courses
    def test_get_courses(self): ...
    def test_add_to_courses(self): ...
    
    # Planning
    def test_get_planning(self): ...
    def test_update_planning(self): ...
    
    # Error handling
    def test_404_not_found(self): ...
    def test_422_validation_error(self): ...
    def test_500_server_error(self): ...
```

#### 2.2 `src/api/rate_limiting.py` (30.21% → 80%)
**Fichier test**: `tests/api/test_rate_limiting.py`

```python
class TestRateLimiting:
    def test_allow_under_limit(self): ...
    def test_block_over_limit(self): ...
    def test_reset_after_window(self): ...
    def test_per_user_limits(self): ...
    def test_global_limits(self): ...
```

---

## 🟠 PHASE 3: SERVICES (Priorité HAUTE)

Structure: Pour CHAQUE fichier dans `src/services/`, créer un fichier test correspondant:

| Source | Test |
|--------|------|
| `src/services/recettes.py` | `tests/services/test_recettes.py` |
| `src/services/courses.py` | `tests/services/test_courses.py` |
| `src/services/planning.py` | `tests/services/test_planning.py` |
| `src/services/inventaire.py` | `tests/services/test_inventaire.py` |
| `src/services/auth.py` | `tests/services/test_auth.py` |
| ... | ... |

**Pattern de test pour chaque service**:
```python
class TestNomService:
    # CRUD Operations
    def test_create(self): ...
    def test_read(self): ...
    def test_update(self): ...
    def test_delete(self): ...
    def test_list(self): ...
    
    # Business Logic
    def test_specific_logic_1(self): ...
    def test_specific_logic_2(self): ...
    
    # Error Cases
    def test_not_found(self): ...
    def test_validation_error(self): ...
    def test_database_error(self): ...
```

---

## 🟡 PHASE 4: DOMAINS (Priorité MOYENNE)

Structure par domaine:

### 4.1 Cuisine
```
tests/domains/cuisine/
├── services/
│   ├── test_batch_cooking_logic.py  → src/domains/cuisine/logic/batch_cooking_logic.py
│   ├── test_courses_logic.py        → src/domains/cuisine/logic/courses_logic.py
│   ├── test_inventaire_logic.py     → src/domains/cuisine/logic/inventaire_logic.py
│   ├── test_recettes_logic.py       → src/domains/cuisine/logic/recettes_logic.py
│   └── test_planning_logic.py       → src/domains/cuisine/logic/planning_logic.py
└── ui/
    ├── test_courses_ui.py           → src/domains/cuisine/ui/courses.py
    ├── test_inventaire_ui.py        → src/domains/cuisine/ui/inventaire.py
    └── test_recettes_ui.py          → src/domains/cuisine/ui/recettes.py
```

### 4.2 Famille
```
tests/domains/famille/
├── services/
│   ├── test_activites_logic.py      → src/domains/famille/logic/activites_logic.py
│   └── test_routines_logic.py       → src/domains/famille/logic/routines_logic.py
└── ui/
    ├── test_hub_famille.py          → src/domains/famille/ui/hub_famille.py
    └── test_jules.py                → src/domains/famille/ui/jules.py
```

### 4.3 Maison
```
tests/domains/maison/
├── services/
│   ├── test_entretien_logic.py      → src/domains/maison/logic/entretien_logic.py
│   └── test_projets_logic.py        → src/domains/maison/logic/projets_logic.py
└── ui/
    └── test_hub_maison.py           → src/domains/maison/ui/hub_maison.py
```

### 4.4 Planning
```
tests/domains/planning/
├── logic/
│   ├── test_calendrier_logic.py     → src/domains/planning/logic/calendrier_unifie_logic.py
│   └── test_vue_semaine_logic.py    → src/domains/planning/logic/vue_semaine_logic.py
└── ui/
    └── test_calendrier_ui.py        → src/domains/planning/ui/calendrier_unifie.py
```

### 4.5 Jeux
```
tests/domains/jeux/
└── ui/
    ├── test_loto.py                 → src/domains/jeux/ui/loto.py
    └── test_paris.py                → src/domains/jeux/ui/paris.py
```

---

## 🟢 PHASE 5: UI & UTILS (Priorité MOYENNE)

### 5.1 UI Components
```
tests/ui/
├── test_atoms.py          → src/ui/components/atoms.py
├── test_data.py           → src/ui/components/data.py
├── test_forms.py          → src/ui/components/forms.py
├── test_layouts.py        → src/ui/components/layouts.py
├── test_base_form.py      → src/ui/core/base_form.py
├── test_base_module.py    → src/ui/core/base_module.py
├── test_progress.py       → src/ui/feedback/progress.py
├── test_spinners.py       → src/ui/feedback/spinners.py
└── test_toasts.py         → src/ui/feedback/toasts.py
```

### 5.2 Utils
```
tests/utils/
├── test_formatters_dates.py    → src/utils/formatters/dates.py
├── test_formatters_numbers.py  → src/utils/formatters/numbers.py
├── test_formatters_text.py     → src/utils/formatters/text.py
├── test_helpers_data.py        → src/utils/helpers/data.py
├── test_helpers_dates.py       → src/utils/helpers/dates.py
├── test_helpers_strings.py     → src/utils/helpers/strings.py
├── test_validators_common.py   → src/utils/validators/common.py
├── test_validators_dates.py    → src/utils/validators/dates.py
└── test_validators_food.py     → src/utils/validators/food.py
```

---

## 🔵 PHASE 6: TRANSVERSAL

### Tests d'intégration
```
tests/integration/
├── test_api_to_database.py
├── test_services_integration.py
└── test_domains_integration.py
```

### Tests E2E
```
tests/e2e/
├── test_user_flow_recettes.py
├── test_user_flow_courses.py
└── test_user_flow_planning.py
```

---

## 📋 COMMANDES DE VALIDATION

```bash
# Valider Phase 1
pytest tests/core/ --cov=src/core --cov-report=term-missing --cov-fail-under=80

# Valider Phase 2
pytest tests/api/ --cov=src/api --cov-report=term-missing --cov-fail-under=80

# Valider Phase 3
pytest tests/services/ --cov=src/services --cov-report=term-missing --cov-fail-under=80

# Valider Phase 4
pytest tests/domains/ --cov=src/domains --cov-report=term-missing --cov-fail-under=80

# Valider Phase 5
pytest tests/ui/ tests/utils/ --cov=src/ui,src/utils --cov-report=term-missing --cov-fail-under=80

# Validation finale globale
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80
```

---

**Dernière mise à jour**: 2026-02-04
