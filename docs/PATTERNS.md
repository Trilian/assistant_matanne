# Patterns d'Architecture â€” src/core

Ce document prÃ©sente les patterns **actifs** utilisÃ©s dans le core de l'application avec exemples d'usage.

## Table des matiÃ¨res

1. [Resilience Policies](#resilience-policies)
2. [Cache Multi-Niveaux](#cache-multi-niveaux)
3. [Circuit Breaker](#circuit-breaker)
4. [Service Factory Pattern](#service-factory-pattern)
5. [Event Bus](#event-bus)
6. [Best Practices](#best-practices)
7. [Test Patterns](#test-patterns)

---

## Resilience Policies

**Fichier**: `src/core/resilience/policies.py`

Politiques de rÃ©silience composables. `executer()` retourne `T` directement ou lÃ¨ve une exception.

### Politiques disponibles

```python
from src.core.resilience import (
    RetryPolicy,
    TimeoutPolicy,
    BulkheadPolicy,
    FallbackPolicy,
)

# Retry avec backoff exponentiel
retry = RetryPolicy(max_tentatives=3, delai_base=1.0, facteur_backoff=2.0)

# Timeout
timeout = TimeoutPolicy(timeout_secondes=30)

# Bulkhead (limite de concurrence)
bulkhead = BulkheadPolicy(max_concurrent=5)

# Fallback
fallback = FallbackPolicy(fallback_value=[])
```

### Composition

```python
# Combiner avec +
politique = RetryPolicy(3) + TimeoutPolicy(30) + BulkheadPolicy(5)

# Appliquer â€” retourne T ou lÃ¨ve une exception
result = politique.executer(lambda: appel_risque())
```

### PrÃ©-configurÃ©es

```python
from src.core.resilience import politique_ia, politique_base_de_donnees, politique_api_externe

result = politique_ia().executer(lambda: client.generer(...))
```

### DÃ©corateur @avec_resilience

```python
from src.core.decorators import avec_resilience

@avec_resilience(retry=2, timeout_s=30, fallback=None, circuit="api_externe")
def appel_api_externe():
    return httpx.get("https://api.example.com/data").json()
```

---

## Cache Multi-Niveaux

**Fichiers**: `src/core/caching/`

Cache L1 (mÃ©moire) â†’ L2 (session) â†’ L3 (fichier).

### DÃ©corateur unifiÃ©

```python
from src.core.decorators import avec_cache

@avec_cache(ttl=300, key_prefix="recettes")
def charger_recettes(page: int = 1) -> list[Recette]:
    return db.query(Recette).offset(page * 20).limit(20).all()

# Custom key
@avec_cache(ttl=3600, key_func=lambda self, id: f"recette_{id}")
def charger_recette(self, id: int) -> Recette:
    return db.get(Recette, id)
```

### API directe

```python
from src.core.caching import obtenir_cache, Cache

cache = obtenir_cache()

# Set/Get
cache.set("ma_cle", valeur, ttl=600, tags=["recettes"])
valeur = cache.get("ma_cle")

# Cache-aside pattern
valeur = cache.get_or_set("cle", compute_fn=lambda: calcul_couteux())

# Invalidation par tags ou pattern
cache.invalider_par_tag("recettes")
Cache.invalider(pattern="charger_")
```

### Politique de cache

| Couche | DÃ©corateur | Raison |
| -------- | ----------- | -------- |
| Services/mÃ©tier | `@avec_cache` | Multi-niveaux, testable indÃ©pendamment |
| Frontend | TanStack Query | Cache cÃ´tÃ© client (staleTime, gcTime) |
| HTTP | Middleware ETag | Cache navigateur automatique |

---

## Circuit Breaker

**Fichier**: `src/core/ai/circuit_breaker.py`

Protection contre les cascades d'Ã©checs.

### Ã‰tats

- **FERMÃ‰**: Fonctionnement normal
- **OUVERT**: Ã‰checs â†’ appels bloquÃ©s
- **SEMI-OUVERT**: Test de rÃ©cupÃ©ration

### Usage

```python
from src.core.ai import CircuitBreaker, obtenir_circuit

# Obtenir ou crÃ©er un circuit
circuit = obtenir_circuit("mistral_api")

# ExÃ©cuter avec protection
result = circuit.executer(lambda: api.call())

# VÃ©rifier l'Ã©tat
if circuit.est_disponible():
    # OK pour appeler
    pass
```

### DÃ©corateur

```python
from src.core.ai import avec_circuit_breaker

@avec_circuit_breaker(nom="external_api", fallback=lambda: [])
def appel_externe():
    return api.get_data()
```

---

## Service Factory Pattern

**Convention**: Chaque service exporte une fonction factory `get_{service_name}_service()`.

### Avec @service_factory (registre)

```python
from src.services.core.registry import service_factory

@service_factory("recettes", tags={"cuisine", "ia"})
def get_recette_service() -> RecetteService:
    """Factory singleton gÃ©rÃ© par le registre."""
    return RecetteService()

# AccÃ¨s direct (singleton)
service = get_recette_service()

# AccÃ¨s via le registre
from src.services.core.registry import obtenir_registre
service = obtenir_registre().obtenir("recettes")
```

### Lazy-load dans les routes

```python
# src/api/routes/recettes.py
from src.services.cuisine.recettes import get_recette_service

@router.get("")
async def lister_recettes(user: dict = Depends(require_auth)):
    service = get_recette_service()  # Singleton via @service_factory
    ...
```

> **Important**: Les services sont des singletons instanciÃ©s au premier appel via `@service_factory`.

---

## Event Bus

**Fichiers**: `src/services/core/events/`

### Bus d'Ã©vÃ©nements

```python
from src.services.core.events.bus import obtenir_bus

bus = obtenir_bus()

# S'abonner (support wildcards: *, **)
bus.on("recette.creee", lambda data: logger.info(f"Recette: {data['nom']}"))
bus.on("recette.*", lambda data: audit_log(data))

# Ã‰mettre
bus.emettre("recette.creee", {"nom": "Tarte", "id": 42})
```

---

## Best Practices

### 1. Utiliser @avec_resilience pour les appels externes

```python
# âŒ Mauvais â€” pas de retry, pas de timeout
def fetch_api():
    return httpx.get("https://api.foo.com").json()

# âœ… Bon â€” retry + timeout + fallback
@avec_resilience(retry=2, timeout_s=30, fallback=None)
def fetch_api():
    return httpx.get("https://api.foo.com").json()
```

### 2. Unifier la stratÃ©gie de cache

```python
# âœ… Bon (dans le service avec avec_cache)
@avec_cache(ttl=300)
def charger_donnees():
    return db.query(Recette).all()

# âœ… Invalider manuellement par tag
cache.invalider_par_tag("recettes")
```

### 3. Utiliser @service_factory pour les singletons

```python
# âŒ Mauvais â€” singleton manuel
_instance = None
def get_service():
    global _instance
    if _instance is None:
        _instance = MyService()
    return _instance

# âœ… Bon â€” singleton via registre
@service_factory("mon_service")
def get_service():
    return MyService()
```

---

## Test Patterns

### Mock DB via `db=` parameter

Le dÃ©corateur `@avec_session_db` injecte `db: Session`, mais peut Ãªtre contournÃ©:

```python
# Test unitaire â€” passer la session directement
def test_create_recipe(test_db: Session):
    service = RecetteService()
    result = service.creer_recette({"nom": "Tarte"}, db=test_db)
    assert result.nom == "Tarte"
```

### Mock service factory

Pour les routes FastAPI qui utilisent `get_*_service()` :

```python
@patch("src.api.routes.courses.get_courses_service")
async def test_lister_articles(mock_factory, client):
    mock_service = MagicMock()
    mock_service.lister_articles.return_value = [article]
    mock_factory.return_value = mock_service

    response = await client.get("/api/v1/courses")
    assert response.status_code == 200
    mock_service.lister_articles.assert_called_once()
```

### Fixtures DB (conftest.py)

```python
# conftest.py fournit des fixtures SQLite en mÃ©moire
@pytest.fixture
def test_db():
    """Session SQLAlchemy isolÃ©e â€” rollback automatique aprÃ¨s le test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

> **Important**: AprÃ¨s refactoring de tests, toujours supprimer les `__pycache__/` pour Ã©viter
> que Python charge d'anciens `.pyc` avec des patches obsolÃ¨tes.

---

## Patterns supprimÃ©s

Les patterns suivants ont Ã©tÃ© Ã©valuÃ©s et supprimÃ©s du codebase (dead code, inutiles pour cette application):

| Pattern | Raison de suppression |
| --------- | ---------------------- |
| **Result Monad** (`src/core/result/`) | Zero callers en production. Les exceptions Python standard suffisent. |
| **Repository Pattern** (`src/core/repository.py`) | Abstraction inutile au-dessus de SQLAlchemy ORM. |
| **Specification Pattern** (`src/core/specifications.py`) | Jamais utilisÃ©. SQLAlchemy `.filter()` suffit. |
| **Unit of Work** (`src/core/unit_of_work.py`) | Zero callers. `@avec_session_db` gÃ¨re les transactions. |
| **IoC Container** (`src/core/container.py`) | Zero callers en production. `@service_factory` + registre suffisent. |
| **Middleware Pipeline** (`src/core/middleware/`) | Zero callers. Le dÃ©corateur `@avec_resilience` remplace ce besoin. |
| **CQRS** (`src/services/core/cqrs/`) | Zero callers. Pas de sÃ©paration lecture/Ã©criture pour une app single-user. |
| **UI v2.0** (DialogBuilder, FormBuilder, URL State) | Zero callers. MigrÃ© vers Next.js + shadcn/ui. |

---

## Voir aussi
## SÃ©paration des schÃ©mas Pydantic (H.8)

Le projet dispose de **deux emplacements** pour les schÃ©mas Pydantic â€” chacun avec un rÃ´le prÃ©cis :

### `src/api/schemas/` â€” SchÃ©mas de sÃ©rialisation API

**RÃ´le** : Valider et sÃ©rialiser les donnÃ©es Ã  l'entrÃ©e/sortie de la couche HTTP.

```
src/api/schemas/
â”œâ”€â”€ base.py          â†’ BaseModel avec Config (alias_generator, populate_by_name)
â”œâ”€â”€ common.py        â†’ ErrorResponse, ReponsePaginee[T], MessageResponse
â”œâ”€â”€ errors.py        â†’ Constantes responses (REPONSES_CRUD_CREATION, etc.)
â”œâ”€â”€ recettes.py      â†’ RecetteCreate, RecetteUpdate, RecetteResponse
â”œâ”€â”€ jeux.py          â†’ AnalyseIARequest, GenererGrilleRequest, etc.
â””â”€â”€ ...
```

**RÃ¨gle** : Un schÃ©ma `*Response` ne doit pas contenir de logique mÃ©tier. Il expose exactement
ce que la route renvoie. Utiliser `model_validate(orm_obj)` (Pydantic v2) pour convertir depuis ORM.

### `src/core/validation/schemas/` â€” SchÃ©mas de validation mÃ©tier

**RÃ´le** : Valider les donnÃ©es de structure mÃ©tier *indÃ©pendamment de la couche HTTP*.  
Utiles dans les services, les imports de donnÃ©es, les scripts de seed.

```
src/core/validation/schemas/
â”œâ”€â”€ _helpers.py     â†’ Validators partagÃ©s (valider_date_future, etc.)
â”œâ”€â”€ recettes.py     â†’ Validation stricte des recettes (rÃ¨gles mÃ©tier)
â”œâ”€â”€ inventaire.py   â†’ Validation inventaire
â”œâ”€â”€ courses.py      â†’ Validation courses
â”œâ”€â”€ planning.py     â†’ Validation planning
â”œâ”€â”€ famille.py      â†’ Validation profils famille
â”œâ”€â”€ projets.py      â†’ Validation projets maison
â””â”€â”€ profils.py      â†’ Validation profils utilisateurs
```

**RÃ¨gle** : Les schÃ©mas ici ne dÃ©pendent PAS de FastAPI. Ils peuvent Ãªtre instanciÃ©s
depuis n'importe oÃ¹ (service, test, script). Utiliser `from src.core.validation.schemas.xxx import XxxSchema`.

### Guide de dÃ©cision â€” OÃ¹ mettre un nouveau schÃ©ma ?

```
Nouvelle validation de donnÃ©es ?
â”‚
â”œâ”€â”€ Elle est utilisÃ©e UNIQUEMENT dans une route FastAPI (request body/response)
â”‚   â†’ src/api/schemas/{domain}.py
â”‚
â”œâ”€â”€ Elle valide la logique mÃ©tier independamment du transport HTTP
â”‚   â†’ src/core/validation/schemas/{domain}.py
â”‚
â””â”€â”€ Elle est utilisÃ©e dans LES DEUX contextes
    â†’ DÃ©finir le schÃ©ma dans src/core/validation/schemas/{domain}.py
    â†’ Importer/hÃ©riter dans src/api/schemas/{domain}.py
    â†’ Ã‰viter la duplication
```

### Pattern â€” Relation schÃ©mas API â†” validation mÃ©tier

```python
# src/core/validation/schemas/recettes.py  (rÃ¨gles mÃ©tier rÃ©utilisables)
from pydantic import BaseModel, Field, field_validator

class RecetteBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    temps_preparation: int = Field(..., ge=1, le=480)

    @field_validator("nom")
    @classmethod
    def valider_nom(cls, v: str) -> str:
        return v.strip()

# src/api/schemas/recettes.py  (schÃ©mas HTTP â€” hÃ©rite de la validation mÃ©tier)
from src.core.validation.schemas.recettes import RecetteBase

class RecetteCreate(RecetteBase):
    """Body pour POST /api/v1/recettes"""
    ingredients: list[int] = []

class RecetteResponse(RecetteBase):
    """RÃ©ponse de GET /api/v1/recettes/{id}"""
    id: int
    cree_le: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## Voir aussi

- [ARCHITECTURE.md](ARCHITECTURE.md) â€” Vue d'ensemble
- [API_REFERENCE.md](API_REFERENCE.md) â€” RÃ©fÃ©rence API
- [SERVICES_REFERENCE.md](SERVICES_REFERENCE.md) â€” RÃ©fÃ©rence services backend
