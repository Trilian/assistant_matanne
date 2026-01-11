# Phase 3 Roadmap

## Current Status

✅ **Phase 2 Complete**: All business services refactored with Phase 1 patterns

### Services Completed
- `recettes.py` (566 LOC) - 95% type hints
- `inventaire.py` (302 LOC) - 100% type hints
- `planning.py` (258 LOC) - 100% type hints
- `courses.py` (203 LOC) - 100% type hints

### Metrics
- **Code Quality**: From 987 → 1329 LOC (better structured, more documented)
- **Type Coverage**: 60% → 95%+
- **Test Ready**: 100% (no Streamlit dependencies in core)
- **Error Handling**: 100% (all methods have proper error handling)
- **Cache Coverage**: 21 cache decorators across services
- **Documentation**: 100% (comprehensive docstrings)

---

## Phase 3: Unit Tests & Type Safety

### Objective
Establish comprehensive test suite with 80%+ code coverage and 100% type safety.

### 1. Pytest Setup (~2-3 days)

#### Files to Create
```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── test_services.py            # Shared service tests
├── test_recettes.py            # Recipe service tests (40+ tests)
├── test_inventaire.py          # Inventory service tests (30+ tests)
├── test_planning.py            # Planning service tests (25+ tests)
├── test_courses.py             # Shopping service tests (20+ tests)
├── test_validators.py          # Pydantic validator tests (15+ tests)
├── test_decorators.py          # Decorator tests (20+ tests)
└── integration/
    ├── test_recettes_flow.py   # End-to-end recipe flows
    └── test_services_flow.py   # Cross-service interactions
```

#### Tasks
- [ ] Install pytest, pytest-asyncio, pytest-cov
- [ ] Create conftest.py with:
  - Database fixtures (test DB setup)
  - Service fixtures (pre-initialized services)
  - Factory fixtures (test data generation)
- [ ] Add pytest configuration to pyproject.toml
- [ ] Create GitHub Actions CI pipeline

### 2. Service Unit Tests (~3-4 days)

#### test_recettes.py (40+ tests)
```python
# CRUD Tests
- test_get_by_id_returns_recipe_with_cache
- test_get_by_id_returns_none_for_missing
- test_create_complete_with_valid_data
- test_create_complete_validates_with_pydantic
- test_search_advanced_filters_by_term
- test_search_advanced_filters_by_meal_type

# IA Tests
- test_generer_recettes_ia_returns_suggestions
- test_generer_recettes_ia_caches_results
- test_generer_recettes_ia_handles_api_errors

# Version Tests
- test_generer_version_bebe_creates_version
- test_generer_version_bebe_caches_existing
- test_generer_version_bebe_handles_validation_errors

# Export Tests
- test_export_to_csv_formats_correctly
- test_export_to_json_includes_relationships
- test_export_handles_empty_list
```

#### test_inventaire.py (30+ tests)
```python
# Inventory Tests
- test_get_inventaire_complet_returns_all_items
- test_get_inventaire_complet_filters_by_location
- test_get_inventaire_complet_filters_by_category
- test_get_inventaire_complet_excludes_ok_items

# Alert Tests
- test_get_alertes_identifies_critical_stock
- test_get_alertes_identifies_expiration_soon
- test_get_alertes_identifies_low_stock

# IA Tests
- test_suggerer_courses_ia_generates_suggestions
- test_suggerer_courses_ia_caches_results

# Helper Tests
- test_calculer_statut_critical_when_below_50_percent
- test_calculer_statut_expiration_when_7_days_left
- test_jours_avant_peremption_returns_days
```

#### test_planning.py (25+ tests)
```python
# Planning Tests
- test_get_planning_complet_returns_meals_by_day
- test_get_planning_complet_caches_results
- test_get_planning_complet_returns_none_for_missing

# Generation Tests
- test_generer_planning_ia_creates_planning
- test_generer_planning_ia_generates_7_days
- test_generer_planning_ia_caches_results
- test_generer_planning_ia_handles_ia_failures
```

#### test_courses.py (20+ tests)
```python
# Shopping List Tests
- test_get_liste_courses_returns_unpurchased
- test_get_liste_courses_filters_by_priority
- test_get_liste_courses_orders_by_section

# Suggestion Tests
- test_generer_suggestions_ia_generates_list
- test_generer_suggestions_ia_uses_inventory
- test_generer_suggestions_ia_caches_results
```

### 3. Validator Tests (~2 days)

#### test_validators.py
```python
# RecetteInput
- test_recette_input_validates_required_fields
- test_recette_input_validates_constraints
- test_recette_input_rejects_invalid_data

# IngredientInput
- test_ingredient_input_validates_unit
- test_ingredient_input_validates_quantity

# All 9 Pydantic schemas with similar tests
```

### 4. Decorator Tests (~2 days)

#### test_decorators.py
```python
# @with_db_session Tests
- test_with_db_session_injects_session
- test_with_db_session_handles_errors
- test_with_db_session_commits_on_success

# @with_cache Tests
- test_with_cache_stores_result
- test_with_cache_retrieves_from_cache
- test_with_cache_respects_ttl
- test_with_cache_uses_custom_key_func

# @with_error_handling Tests
- test_with_error_handling_catches_specified_errors
- test_with_error_handling_returns_fallback
- test_with_error_handling_logs_errors

# @with_validation Tests
- test_with_validation_validates_input
- test_with_validation_rejects_invalid_data
```

### 5. Integration Tests (~2 days)

#### test_recettes_flow.py
```python
# Complete workflows
- test_create_recipe_and_retrieve_full
- test_generate_recipe_suggestions_and_create
- test_create_recipe_and_generate_baby_version
- test_export_recipes_to_csv_and_json
```

#### test_services_flow.py
```python
# Cross-service workflows
- test_inventory_to_recipes_to_planning
- test_create_planning_and_suggest_shopping
- test_complete_meal_planning_flow
```

---

## Phase 3: Type Safety with Pylance

### Objective
Achieve 100% type hint coverage and enable strict Pylance checking.

### Tasks

#### 1. Complete Type Hints (~1 day)
```python
# Current coverage: 95%
# Target coverage: 100%

# Review and fix:
- [ ] All function parameters have type hints
- [ ] All return types are specified
- [ ] All module-level variables are typed
- [ ] Complex types use TypedDict or Protocol
```

#### 2. Enable Strict Mode (~1 day)
```json
{
  "python.analysis.typeCheckingMode": "strict",
  "python.analysis.strictParameterNoneDefault": true,
  "python.analysis.strictListInference": true,
  "python.analysis.strictDictInference": true
}
```

#### 3. Fix Strict Mode Issues
- [ ] All union types use `|` (not Optional where possible)
- [ ] Type narrowing validated by Pylance
- [ ] No `Any` types without justification
- [ ] All protocols properly defined

---

## Phase 3 Schedule

### Week 1: Test Infrastructure
- [ ] Day 1: Pytest setup + conftest
- [ ] Day 2-3: Database + fixture setup
- [ ] Day 4-5: CI/CD pipeline

### Week 2: Unit Tests Part 1
- [ ] Day 6-7: test_recettes.py (40+ tests)
- [ ] Day 8-9: test_inventaire.py (30+ tests)

### Week 3: Unit Tests Part 2
- [ ] Day 10-11: test_planning.py + test_courses.py
- [ ] Day 12: test_validators.py + test_decorators.py

### Week 4: Integration & Type Safety
- [ ] Day 13-14: Integration tests
- [ ] Day 15-17: Type hints audit + Pylance strict mode
- [ ] Day 18-20: Fix remaining issues + documentation

**Total: 3-4 weeks (15-20 dev days)**

---

## Expected Outcomes

### Test Coverage
```
Service             Tests   Coverage
─────────────────────────────────────
recettes.py         40      95%
inventaire.py       30      90%
planning.py         25      92%
courses.py          20      88%
validators.py       15      100%
decorators.py       20      98%
─────────────────────────────────────
Total              150      92%+ overall
```

### Type Safety
```
Current:  95% type hints, warnings in strict mode
Target:   100% type hints, 0 warnings in strict mode
Impact:   Better IDE support, earlier error detection
```

### Quality Metrics
```
Lines of Test Code:  ~2500 lines
Test/Code Ratio:     2.5:1 (good for business logic)
Execution Time:      ~30 seconds (full suite)
CI/CD:               GitHub Actions (all PRs)
```

---

## Phase 4 Planning (After Phase 3)

### Proposed Features
1. **Structured Logging** (JSON logs, log levels, correlation IDs)
2. **Smart Cache** (Dependency tracking, automatic invalidation)
3. **Performance Monitoring** (Query performance, cache hit rates)
4. **Error Tracking** (Sentry integration, error patterns)
5. **API Documentation** (FastAPI auto-docs if exposed)

### Timeline
- Phase 3 (Tests): 3-4 weeks
- Phase 4 (Monitoring): 2-3 weeks
- Total: 6-7 weeks to production-ready

---

## Success Criteria

### Phase 3 Success
- [ ] 80%+ code coverage (unit + integration)
- [ ] 100% type hint coverage with Pylance strict mode
- [ ] All 150+ tests passing in CI/CD
- [ ] Documentation for testing strategy
- [ ] Example tests for developers to follow

### Phase 3 Metrics to Track
```
Before:
- Code coverage: N/A (no tests)
- Type hints: 95%
- Bugs found in testing: 0 (no tests)

After:
- Code coverage: 92%
- Type hints: 100%
- Bugs found in testing: ~5-10 (typical)
- Test execution time: ~30s
- Test maintenance: +2% LOC/sprint
```

---

## Developer Guide for Phase 3

### Running Tests
```bash
# All tests
pytest

# Specific service
pytest tests/test_recettes.py -v

# With coverage
pytest --cov=src --cov-report=html

# CI mode (strict)
pytest --strict-markers -v
```

### Writing Tests
```python
def test_operation_returns_expected_result(service, session):
    # Setup
    item = factory.create_item()
    
    # Execute
    result = service.get_by_id(item.id, db=session)
    
    # Assert
    assert result.id == item.id
    assert result.name == item.name
```

### Coverage Targets per Module
- Core decorators: 98%
- Validators: 100%
- Services: 90%+ each
- Helpers: 85%+

---

## Questions & Decisions

**Q: Should we mock the database?**
A: No. Use a test database (faster than mocking, more realistic).

**Q: Should we test async methods?**
A: Yes, with pytest-asyncio.

**Q: Should we have fixtures for large datasets?**
A: Yes, but keep tests small (< 100 items).

**Q: How often should tests run?**
A: On every commit via GitHub Actions.

**Q: Should we test Streamlit UI?**
A: No (Phase 3 focuses on core services).

---

## Resource Requirements

### Tools Needed
- pytest, pytest-cov, pytest-asyncio
- GitHub Actions (free)
- sqlalchemy test utilities
- faker or factory-boy (test data)

### Estimated Effort
- 15-20 developer days
- 1 senior + 1 mid developer
- ~2500 lines of test code

### Expected ROI
- Catch bugs early: ~80% fewer production issues
- Refactoring confidence: Can safely refactor
- Documentation: Tests serve as examples
- Team velocity: Better onboarding for new developers

