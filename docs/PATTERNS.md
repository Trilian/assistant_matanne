# Patterns d'Architecture — src/core

Ce document présente les patterns **actifs** utilisés dans le core de l'application avec exemples d'usage.

## Table des matières

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

Politiques de résilience composables. `executer()` retourne `T` directement ou lève une exception.

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

# Appliquer — retourne T ou lève une exception
result = politique.executer(lambda: appel_risque())
```

### Pré-configurées

```python
from src.core.resilience import politique_ia, politique_base_de_donnees, politique_api_externe

result = politique_ia().executer(lambda: client.generer(...))
```

### Décorateur @avec_resilience

```python
from src.core.decorators import avec_resilience

@avec_resilience(retry=2, timeout_s=30, fallback=None, circuit="api_externe")
def appel_api_externe():
    return httpx.get("https://api.example.com/data").json()
```

---

## Cache Multi-Niveaux

**Fichiers**: `src/core/caching/`

Cache L1 (mémoire) → L2 (session) → L3 (fichier).

### Décorateur unifié

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

| Couche | Décorateur | Raison |
| -------- | ----------- | -------- |
| Services/métier | `@avec_cache` | Multi-niveaux, testable indépendamment |
| Frontend | TanStack Query | Cache côté client (staleTime, gcTime) |
| HTTP | Middleware ETag | Cache navigateur automatique |

---

## Circuit Breaker

**Fichier**: `src/core/ai/circuit_breaker.py`

Protection contre les cascades d'échecs.

### États

- **FERMÉ**: Fonctionnement normal
- **OUVERT**: Échecs → appels bloqués
- **SEMI-OUVERT**: Test de récupération

### Usage

```python
from src.core.ai import CircuitBreaker, obtenir_circuit

# Obtenir ou créer un circuit
circuit = obtenir_circuit("mistral_api")

# Exécuter avec protection
result = circuit.executer(lambda: api.call())

# Vérifier l'état
if circuit.est_disponible():
    # OK pour appeler
    pass
```

### Décorateur

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
    """Factory singleton géré par le registre."""
    return RecetteService()

# Accès direct (singleton)
service = get_recette_service()

# Accès via le registre
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

> **Important**: Les services sont des singletons instanciés au premier appel via `@service_factory`.

---

## Event Bus

**Fichiers**: `src/services/core/events/`

### Bus d'événements

```python
from src.services.core.events.bus import obtenir_bus

bus = obtenir_bus()

# S'abonner (support wildcards: *, **)
bus.on("recette.creee", lambda data: logger.info(f"Recette: {data['nom']}"))
bus.on("recette.*", lambda data: audit_log(data))

# Émettre
bus.emettre("recette.creee", {"nom": "Tarte", "id": 42})
```

---

## Best Practices

### 1. Utiliser @avec_resilience pour les appels externes

```python
# ❌ Mauvais — pas de retry, pas de timeout
def fetch_api():
    return httpx.get("https://api.foo.com").json()

# ✅ Bon — retry + timeout + fallback
@avec_resilience(retry=2, timeout_s=30, fallback=None)
def fetch_api():
    return httpx.get("https://api.foo.com").json()
```

### 2. Unifier la stratégie de cache

```python
# ✅ Bon (dans le service avec avec_cache)
@avec_cache(ttl=300)
def charger_donnees():
    return db.query(Recette).all()

# ✅ Invalider manuellement par tag
cache.invalider_par_tag("recettes")
```

### 3. Utiliser @service_factory pour les singletons

```python
# ❌ Mauvais — singleton manuel
_instance = None
def get_service():
    global _instance
    if _instance is None:
        _instance = MyService()
    return _instance

# ✅ Bon — singleton via registre
@service_factory("mon_service")
def get_service():
    return MyService()
```

---

## Test Patterns

### Mock DB via `db=` parameter

Le décorateur `@avec_session_db` injecte `db: Session`, mais peut être contourné:

```python
# Test unitaire — passer la session directement
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
# conftest.py fournit des fixtures SQLite en mémoire
@pytest.fixture
def test_db():
    """Session SQLAlchemy isolée — rollback automatique après le test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

> **Important**: Après refactoring de tests, toujours supprimer les `__pycache__/` pour éviter
> que Python charge d'anciens `.pyc` avec des patches obsolètes.

---

## Patterns supprimés

Les patterns suivants ont été évalués et supprimés du codebase (dead code, inutiles pour cette application):

| Pattern | Raison de suppression |
| --------- | ---------------------- |
| **Result Monad** (`src/core/result/`) | Zero callers en production. Les exceptions Python standard suffisent. |
| **Repository Pattern** (`src/core/repository.py`) | Abstraction inutile au-dessus de SQLAlchemy ORM. |
| **Specification Pattern** (`src/core/specifications.py`) | Jamais utilisé. SQLAlchemy `.filter()` suffit. |
| **Unit of Work** (`src/core/unit_of_work.py`) | Zero callers. `@avec_session_db` gère les transactions. |
| **IoC Container** (`src/core/container.py`) | Zero callers en production. `@service_factory` + registre suffisent. |
| **Middleware Pipeline** (`src/core/middleware/`) | Zero callers. Le décorateur `@avec_resilience` remplace ce besoin. |
| **CQRS** (`src/services/core/cqrs/`) | Zero callers. Pas de séparation lecture/écriture pour une app single-user. |
| **UI v2.0** (DialogBuilder, FormBuilder, URL State) | Zero callers. Migré vers Next.js + shadcn/ui. |

---

## Voir aussi
## Séparation des schémas Pydantic (H.8)

Le projet dispose de **deux emplacements** pour les schémas Pydantic — chacun avec un rôle précis :

### `src/api/schemas/` — Schémas de sérialisation API

**Rôle** : Valider et sérialiser les données à l'entrée/sortie de la couche HTTP.

```
src/api/schemas/
├── base.py          → BaseModel avec Config (alias_generator, populate_by_name)
├── common.py        → ErrorResponse, ReponsePaginee[T], MessageResponse
├── errors.py        → Constantes responses (REPONSES_CRUD_CREATION, etc.)
├── recettes.py      → RecetteCreate, RecetteUpdate, RecetteResponse
├── jeux.py          → AnalyseIARequest, GenererGrilleRequest, etc.
└── ...
```

**Règle** : Un schéma `*Response` ne doit pas contenir de logique métier. Il expose exactement
ce que la route renvoie. Utiliser `model_validate(orm_obj)` (Pydantic v2) pour convertir depuis ORM.

### `src/core/validation/schemas/` — Schémas de validation métier

**Rôle** : Valider les données de structure métier *indépendamment de la couche HTTP*.  
Utiles dans les services, les imports de données, les scripts de seed.

```
src/core/validation/schemas/
├── _helpers.py     → Validators partagés (valider_date_future, etc.)
├── recettes.py     → Validation stricte des recettes (règles métier)
├── inventaire.py   → Validation inventaire
├── courses.py      → Validation courses
├── planning.py     → Validation planning
├── famille.py      → Validation profils famille
├── projets.py      → Validation projets maison
└── profils.py      → Validation profils utilisateurs
```

**Règle** : Les schémas ici ne dépendent PAS de FastAPI. Ils peuvent être instanciés
depuis n'importe où (service, test, script). Utiliser `from src.core.validation.schemas.xxx import XxxSchema`.

### Guide de décision — Où mettre un nouveau schéma ?

```
Nouvelle validation de données ?
│
├── Elle est utilisée UNIQUEMENT dans une route FastAPI (request body/response)
│   → src/api/schemas/{domain}.py
│
├── Elle valide la logique métier independamment du transport HTTP
│   → src/core/validation/schemas/{domain}.py
│
└── Elle est utilisée dans LES DEUX contextes
    → Définir le schéma dans src/core/validation/schemas/{domain}.py
    → Importer/hériter dans src/api/schemas/{domain}.py
    → Éviter la duplication
```

### Pattern — Relation schémas API ↔ validation métier

```python
# src/core/validation/schemas/recettes.py  (règles métier réutilisables)
from pydantic import BaseModel, Field, field_validator

class RecetteBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    temps_preparation: int = Field(..., ge=1, le=480)

    @field_validator("nom")
    @classmethod
    def valider_nom(cls, v: str) -> str:
        return v.strip()

# src/api/schemas/recettes.py  (schémas HTTP — hérite de la validation métier)
from src.core.validation.schemas.recettes import RecetteBase

class RecetteCreate(RecetteBase):
    """Body pour POST /api/v1/recettes"""
    ingredients: list[int] = []

class RecetteResponse(RecetteBase):
    """Réponse de GET /api/v1/recettes/{id}"""
    id: int
    cree_le: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## Voir aussi

- [ARCHITECTURE.md](ARCHITECTURE.md) — Vue d'ensemble
- [API_REFERENCE.md](API_REFERENCE.md) — Référence API
- [SERVICES_REFERENCE.md](SERVICES_REFERENCE.md) — Référence services backend
