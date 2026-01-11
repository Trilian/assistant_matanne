# 🗺️ Refactoring Roadmap - Phases 2-4

## 📋 Overview

Cette feuille de route montre les services et modules qui doivent être refactorisés dans les phases suivantes, en utilisant les patterns établis en Phase 1.

---

## 🔄 Phase 2: Refactoring Services Métier (1 semaine)

### Services à refactoriser

#### 1. `src/services/recettes.py` (457 lignes)
**Status:** 🟡 PARTIELLEMENT OPTIMISÉ  
**Priority:** 🔴 HIGH

**Current Issues:**
- [ ] Utilise encore `@gerer_erreurs` au lieu de `@with_db_session`
- [ ] Validation manuelle mélangée au code métier
- [ ] Type hints incomplets
- [ ] Cache manuel en plusieurs endroits

**Refactoring Tasks:**
- [ ] Remplacer `@gerer_erreurs` + `_with_session` par `@with_db_session`
- [ ] Ajouter `RecetteInput`, `IngredientInput`, `EtapeInput` validators
- [ ] Ajouter `@with_cache` pour les méthodes de lecture
- [ ] Ajouter type hints complets
- [ ] Ajouter docstrings Sphinx

**Affected Methods:**
```python
- creer_recette()           # Create + validation
- get_by_id_full()          # Read + cache
- lister_recettes()         # List + filter
- search_recettes()         # Search
- generer_avec_ia()         # IA integration
- importer_csv()            # Import
- exporter_csv()            # Export
```

**Effort:** 2-3 days  
**Expected Gain:** -50% code, +100% testability

---

#### 2. `src/services/inventaire.py` (420 lignes)
**Status:** 🟡 PARTIELLEMENT OPTIMISÉ  
**Priority:** 🟠 MEDIUM

**Current Issues:**
- [ ] Cache manuel pour get_all
- [ ] Validations manuelles
- [ ] Type hints manquants

**Refactoring Tasks:**
- [ ] Utiliser `@with_db_session` sur tous les CRUD
- [ ] Ajouter `IngredientStockInput` validator
- [ ] Ajouter `@with_cache` sur lister_articles()
- [ ] Compléter type hints

**Affected Methods:**
```python
- lister_articles()         # Cache manual
- get_article()            # Type hints
- ajouter_article()        # Validation
- modifier_article()       # Validation
- supprimer_article()      # Error handling
```

**Effort:** 1-2 days  
**Expected Gain:** -40% code

---

#### 3. `src/services/planning.py` (390 lignes)
**Status:** 🟡 PARTIELLEMENT OPTIMISÉ  
**Priority:** 🟠 MEDIUM

**Current Issues:**
- [ ] Cache manuels avec timestamps
- [ ] Validation date/heure manuelle
- [ ] Pas de type hints sur dates

**Refactoring Tasks:**
- [ ] Utiliser `@with_db_session`
- [ ] Ajouter `RepasInput` validator
- [ ] Utiliser `@with_cache` sur listing
- [ ] Type hints complets (datetime, date)

**Affected Methods:**
```python
- lister_repas()           # Cache + types
- planifier_repas()        # Validation + cache
- get_semaine()            # Caching
```

**Effort:** 1-2 days  
**Expected Gain:** -30% code

---

#### 4. `src/services/courses.py` (280 lignes)
**Status:** 🟡 PARTIELLEMENT OPTIMISÉ  
**Priority:** 🟡 LOW

**Current Issues:**
- [ ] Pas d'erreur handling unifié
- [ ] Validation articles manuelles
- [ ] Type hints partiels

**Refactoring Tasks:**
- [ ] Ajouter `@with_db_session`
- [ ] Ajouter validation Pydantic
- [ ] Ajouter type hints

**Effort:** 1 day  
**Expected Gain:** -25% code

---

### Modules à vérifier/mettre à jour

#### `src/modules/cuisine.py` (529 lignes)
**Status:** 🟢 OK  
**Priority:** 🟡 LOW

**Quick Checks:**
- [x] Utilisation correcte des services
- [x] Pas de duplication validation
- [ ] Utiliser validators Pydantic directement

**Minor Updates:**
```python
# Before: Manual validation in form
if not nom: st.error("...")
if temps <= 0: st.error("...")

# After: Use validators directly
try:
    validated = RecetteInput(nom=nom, temps_prep=temps)
    service.create(validated.model_dump())
except ValidationError as e:
    st.error(f"Erreur: {e}")
```

**Effort:** 0.5 days

---

#### `src/modules/famille/*.py` (Multiple)
**Status:** 🟡 À VÉRIFIER  
**Priority:** 🟡 LOW

Files to check:
- `bien_etre.py` - Validation manuelle?
- `routines.py` - Type hints?
- `suivi_jules.py` - Cache usage?

**Effort:** 2-3 hours per file

---

## 🧪 Phase 3: Tests & Type Hints (1 semaine)

### Setup Tests Infrastructure

#### 1. Create `tests/conftest.py`
```python
# Fixtures for:
- Database session (fixture)
- Clean database (autouse)
- Service instances
- Pydantic validators
```

**Priority:** 🔴 CRITICAL  
**Effort:** 1 day

#### 2. Create `tests/unit/`
```
tests/unit/
├── test_services_base.py         # BaseService CRUD
├── test_validators.py             # Pydantic validators
├── test_decorators.py             # @with_db_session, etc.
├── test_recettes_service.py       # Recipe service
├── test_inventaire_service.py     # Inventory service
└── test_planning_service.py       # Planning service
```

**Target Coverage:** >80%  
**Priority:** 🔴 CRITICAL  
**Effort:** 3-4 days

#### 3. Add Type Hints (Pylance Strict)

Set in `pyrightconfig.json`:
```json
{
  "typeCheckingMode": "strict",
  "pythonVersion": "3.11"
}
```

Files to update:
- [ ] All services (complete type hints)
- [ ] All validators (types for all params)
- [ ] All decorators (full generic types)
- [ ] All models (type all fields)

**Priority:** 🟠 MEDIUM  
**Effort:** 2-3 days

---

## 📊 Phase 4: Quality & Monitoring (1 semaine)

### 1. Structured Logging

Add `src/core/logging_structured.py`:
```python
# JSON logging for production
# Correlation IDs
# Structured context
```

Update all services to use:
```python
logger.info("recette_created", extra={
    "recipe_id": recette.id,
    "user_id": user_id,
    "timing_ms": elapsed_time
})
```

**Effort:** 2 days

### 2. Smart IA Cache

Enhance `src/core/ai/cache.py`:
- [ ] Similarity matching (cosine similarity)
- [ ] Version checking
- [ ] Compression for large responses
- [ ] Redis backend option

**Priority:** 🟠 MEDIUM  
**Effort:** 2-3 days

### 3. Monitoring with OpenTelemetry

Add `src/core/monitoring.py`:
- [ ] Tracing for all DB operations
- [ ] Timing metrics
- [ ] Error tracking
- [ ] Integration with Sentry/NewRelic

**Priority:** 🟡 LOW  
**Effort:** 2 days

### 4. API Documentation

- [ ] Docstrings Sphinx for all services
- [ ] Auto-generated API docs
- [ ] Integration with MkDocs

**Priority:** 🟡 LOW  
**Effort:** 1-2 days

---

## 📈 Progress Tracking

### Phase 2 Checklist

Services:
- [ ] `recettes.py` refactored (2-3 days)
- [ ] `inventaire.py` refactored (1-2 days)
- [ ] `planning.py` refactored (1-2 days)
- [ ] `courses.py` refactored (1 day)
- [ ] Modules updated (0.5-1 day)

**Total: 5-8 days** (plan 1 week)

### Phase 3 Checklist

Tests:
- [ ] conftest.py created (1 day)
- [ ] Unit tests written (3-4 days)
- [ ] Coverage >80% achieved
- [ ] Type hints completed (2-3 days)

**Total: 6-8 days** (plan 1 week)

### Phase 4 Checklist

Quality:
- [ ] Structured logging (2 days)
- [ ] Smart cache (2-3 days)
- [ ] OpenTelemetry (2 days)
- [ ] Documentation (1-2 days)

**Total: 7-9 days** (plan 1 week)

---

## 🎯 Success Criteria

By end of Phase 2:
- ✅ All services use new patterns
- ✅ All validation is Pydantic-based
- ✅ Type hints improved to 95%+

By end of Phase 3:
- ✅ >80% test coverage
- ✅ All type hints complete (strict mode)
- ✅ Tests for all critical paths

By end of Phase 4:
- ✅ Structured logging in place
- ✅ Performance monitoring active
- ✅ Documentation complete

---

## 🔄 File Refactoring Order

### Priority Order (Do in this order)

1. **`recettes.py`** (HIGHEST priority - most complex)
   - Tests first (easiest to test)
   - Then refactor
   - Then update modules

2. **`inventaire.py`** (HIGH priority - frequently used)

3. **`planning.py`** (MEDIUM priority)

4. **`courses.py`** (LOW priority - simple)

5. **Modules** (LOWER priority - UI code)

---

## 📚 Reference Templates

For Phase 2 refactoring, use these templates:

### Service Refactoring Template
```python
# Before refactoring: document in comments
# After refactoring: use new patterns

from src.core.decorators import with_db_session, with_cache
from src.core.validators_pydantic import MyInput
from src.core.errors_base import ErreurNonTrouve

class MyService(BaseService[MyModel]):
    @with_cache(ttl=3600)
    @with_db_session
    def read_operation(self, id: int, db: Session) -> MyModel | None:
        """Read with cache"""
        return db.query(MyModel).get(id)
    
    @with_db_session
    def write_operation(self, data: dict, db: Session) -> MyModel:
        """Write with validation"""
        validated = MyInput(**data)
        entity = MyModel(**validated.model_dump())
        db.add(entity)
        db.commit()
        self._invalider_cache()
        return entity
```

### Test Template
```python
import pytest
from src.services.my_service import MyService
from src.core.validators_pydantic import MyInput
from sqlalchemy.orm import Session

def test_read_operation(db: Session):
    service = MyService()
    result = service.read_operation(1, db=db)
    assert result is not None

def test_write_operation(db: Session):
    service = MyService()
    input_data = MyInput(...)
    result = service.write_operation(input_data.model_dump(), db=db)
    assert result.id is not None
```

---

## 💡 Tips for Smooth Refactoring

1. **Start with tests first**
   - Write tests for current behavior
   - Then refactor
   - Tests pass = refactoring successful

2. **Small commits**
   - One method at a time
   - Small, reviewable PRs
   - Easier to debug

3. **Keep old code temporarily**
   - Comment out old methods first
   - Replace gradually
   - Easier rollback if needed

4. **Document as you go**
   - Add docstrings
   - Update type hints
   - Update EXAMPLES_REFACTORING.md

---

## 🚀 Next Steps

1. **This week:** Start Phase 2 with `recettes.py`
2. **Next week:** Complete Phase 2 services
3. **Week 3:** Add tests (Phase 3)
4. **Week 4:** Quality improvements (Phase 4)

---

## 📞 Questions/Blockers?

Refer to:
- `REFACTORING_PHASE1.md` for patterns
- `EXAMPLES_REFACTORING.md` for code
- `src/services/base_service.py` for reference

Good luck with refactoring! 🎉
