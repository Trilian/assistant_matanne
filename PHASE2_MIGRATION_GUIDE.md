# Phase 2: Migration Guide

## What Changed?

### Before (Old Pattern)
```python
from src.core.errors import gerer_erreurs
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db

@gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
def get_recettes(self, term: str | None = None) -> list[dict]:
    """Récupère des recettes."""
    cache_key = f"recettes_{term}"
    cached = Cache.obtenir(cache_key, ttl=3600)
    if cached:
        return cached

    with obtenir_contexte_db() as db:
        query = db.query(Recette)
        if term:
            query = query.filter(Recette.nom.like(f"%{term}%"))
        
        recettes = query.all()
        
        result = [{"id": r.id, "nom": r.nom} for r in recettes]
        
        Cache.definir(cache_key, result, ttl=3600)
        return result
```

### After (Phase 2 Pattern)
```python
from src.core.decorators import with_db_session, with_cache, with_error_handling

@with_cache(ttl=3600, key_func=lambda self, term: f"recettes_{term}")
@with_error_handling(fallback=[])
@with_db_session
def get_recettes(
    self,
    term: str | None = None,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Récupère des recettes.
    
    Args:
        term: Terme de recherche optionnel
        db: Session DB injectée par @with_db_session
        
    Returns:
        Liste des recettes trouvées
    """
    query = db.query(Recette)
    if term:
        query = query.filter(Recette.nom.like(f"%{term}%"))
    
    recettes = query.all()
    
    return [{"id": r.id, "nom": r.nom} for r in recettes]
```

## Key Differences

### 1. Imports Change
```python
# Old
from src.core.errors import gerer_erreurs
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db

# New
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurNonTrouve, ErreurValidation
```

### 2. Decorator Stack (Bottom-to-Top)
```python
@with_cache(...)        # Apply caching first (outermost)
@with_error_handling(...) # Then error handling
@with_db_session        # Finally DB session injection
def method(self, ..., db: Session | None = None):
    # db is automatically injected
    pass
```

### 3. Database Session Injection
```python
# Old: Manual context manager
with obtenir_contexte_db() as db:
    result = db.query(Model).filter(...).first()

# New: Automatic injection
@with_db_session
def method(self, ..., db: Session | None = None):
    result = db.query(Model).filter(...).first()
```

### 4. Cache Management
```python
# Old: Manual cache key & operations
cache_key = f"key_{id}"
cached = Cache.obtenir(cache_key, ttl=3600)
if cached:
    return cached
# ... do work ...
Cache.definir(cache_key, result, ttl=3600)

# New: Declarative via decorator
@with_cache(ttl=3600, key_func=lambda self, id: f"key_{id}")
def method(self, id: int) -> Model:
    # ... do work ...
    return result  # Caching automatic
```

### 5. Error Handling
```python
# Old: Decorator handles everything
@gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
def method(self) -> list:
    # Exceptions caught, fallback returned

# New: Selective error handling
@with_error_handling(
    fallback=[],
    catch=(ValueError, KeyError),  # Only catch specific errors
    log_level="warning",            # Control logging
)
def method(self) -> list:
    # ValueError and KeyError return fallback=[]
    # Other exceptions propagate
```

## Migration Checklist

### For Each Service File

- [ ] Update imports:
  ```python
  from src.core.decorators import with_db_session, with_cache, with_error_handling
  from src.core.errors_base import ErreurNonTrouve, ErreurValidation
  ```

- [ ] Remove `@gerer_erreurs` decorator, replace with `@with_error_handling`

- [ ] Add `@with_db_session` to methods using `obtenir_contexte_db()`

- [ ] Add `@with_cache` to read operations with appropriate TTL

- [ ] Remove manual cache operations:
  ```python
  # Remove these lines:
  Cache.obtenir(...)
  Cache.definir(...)
  ```

- [ ] Add `db: Session | None = None` parameter to methods

- [ ] Remove `with obtenir_contexte_db() as db:` context managers

- [ ] Add type hints to all parameters and returns

- [ ] Add comprehensive docstrings with Args/Returns sections

- [ ] Add logging for operations (info, warning, error)

- [ ] Test that all imports work

## Common Patterns

### Read Operation (with cache)
```python
@with_cache(ttl=3600, key_func=lambda self, id: f"item_{id}")
@with_error_handling(fallback=None)
@with_db_session
def get_by_id(self, id: int, db: Session | None = None) -> Model | None:
    """Get item by ID."""
    return db.query(Model).filter(Model.id == id).first()
```

### Create Operation (with validation)
```python
@with_error_handling(catch=(ErreurValidation,), fallback=None)
@with_db_session
def create(self, data: dict, db: Session | None = None) -> Model:
    """Create new item."""
    validated = ModelInput(**data)  # Pydantic validation
    model = Model(**validated.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    Cache.invalider(pattern="items")  # Invalidate related caches
    return model
```

### Search Operation (complex queries)
```python
@with_cache(ttl=1800, key_func=lambda self, filters: f"search_{hash(str(filters))}")
@with_error_handling(fallback=[])
@with_db_session
def search(self, filters: dict, db: Session | None = None) -> list[Model]:
    """Search with filters."""
    query = db.query(Model)
    for key, value in filters.items():
        if hasattr(Model, key) and value is not None:
            query = query.filter(getattr(Model, key) == value)
    return query.all()
```

### IA Operation (with caching & error handling)
```python
@with_cache(ttl=21600, key_func=lambda self, context: f"ai_{hash(context)}")
@with_error_handling(fallback=[])
def generate_with_ai(self, context: str) -> list[Result]:
    """Generate results with AI."""
    prompt = self.build_prompt(context)
    response = self.ia_client.generer(prompt)
    results = self.parse_response(response)
    return results
```

## Type Hints Standards

### Function Signatures
```python
from typing import Any
from sqlalchemy.orm import Session

def method(
    self,
    param1: str,
    param2: int | None = None,
    db: Session | None = None,
) -> dict[str, Any] | None:
    """Comprehensive docstring."""
    pass
```

### Return Types
```python
# Single model
def get_by_id(self, id: int, db: Session) -> Model | None:
    pass

# List of models
def get_all(self, db: Session) -> list[Model]:
    pass

# Dict with metadata
def get_complex(self, db: Session) -> dict[str, Any]:
    pass

# Union of types
def flexible(self, id: int, db: Session) -> Model | dict[str, Any] | None:
    pass
```

## Testing Services with Phase 2 Patterns

### Before (Streamlit imports everywhere)
```python
from src.core.errors import gerer_erreurs  # UI imports
from src.ui.feedback import toast           # Streamlit-specific
```

### After (Pure business logic)
```python
from src.core.decorators import with_db_session  # Pure Python
from src.core.errors_base import ErreurValidation  # No UI deps
```

### Test Example
```python
import pytest
from src.services.recettes import RecetteService

@pytest.fixture
def service():
    return RecetteService()

@pytest.fixture
def session(db):
    return db

def test_get_by_id(service, session, recette_factory):
    recette = recette_factory()
    # Direct call, no Streamlit needed
    result = service.get_by_id_full(recette.id, db=session)
    assert result.id == recette.id
```

## FAQ

**Q: Do I need to change my function calls?**
A: No! The decorators handle everything. Just add `db=` parameter when calling.

```python
# Old
result = service.get_by_id(123)

# New (still works, decorator injects db)
result = service.get_by_id(123)

# Or explicit (for tests)
result = service.get_by_id(123, db=test_session)
```

**Q: Can I use @with_cache on write operations?**
A: No. Only use @with_cache on read operations. Write operations should invalidate cache:
```python
@with_error_handling(...)
@with_db_session
def create(self, data: dict, db: Session) -> Model:
    # ... create ...
    Cache.invalider(pattern="items")  # Invalidate caches
    return result
```

**Q: What if I need custom error handling?**
A: Use the `catch` parameter to specify which errors to handle:
```python
@with_error_handling(
    fallback=None,
    catch=(ValueError, KeyError),  # Only these
)
def method(self):
    pass
```

**Q: How do I log operations?**
A: Add logging calls in methods:
```python
logger = logging.getLogger(__name__)

def method(self, id: int):
    logger.info(f"Fetching item {id}")
    result = ...
    logger.info(f"✅ Got item {id}")
    return result
```

**Q: Can I still use raw SQL?**
A: Yes, the session is normal SQLAlchemy:
```python
@with_db_session
def raw_query(self, db: Session) -> list:
    result = db.execute(text("SELECT * FROM ...")).fetchall()
    return result
```

