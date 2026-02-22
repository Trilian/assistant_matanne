# Patterns d'Architecture — src/core

Ce document présente les patterns **actifs** utilisés dans le core de l'application avec exemples d'usage.

## Table des matières

1. [State Slices](#state-slices)
2. [Resilience Policies](#resilience-policies)
3. [Cache Multi-Niveaux](#cache-multi-niveaux)
4. [Circuit Breaker](#circuit-breaker)
5. [Service Factory Pattern](#service-factory-pattern)
6. [Event Bus](#event-bus)
7. [Best Practices](#best-practices)
8. [Test Patterns](#test-patterns)

---

## State Slices

**Fichiers**: `src/core/state/`

État applicatif découpé par domaine, découplé de Streamlit.

### Slices disponibles

```python
from src.core.state import EtatNavigation, EtatCuisine, EtatUI, EtatApp

# Navigation
etat.navigation.module_actuel  # "cuisine.recettes"
etat.navigation.historique_navigation  # ["accueil", "cuisine.recettes"]

# Cuisine
etat.cuisine.id_recette_visualisation  # 42
etat.cuisine.semaine_actuelle  # date(2024, 2, 19)

# UI
etat.ui.afficher_formulaire_ajout  # True
etat.ui.reinitialiser()  # Reset tous les flags
```

### Raccourcis

```python
from src.core.state import obtenir_etat, naviguer, revenir

etat = obtenir_etat()
naviguer("cuisine.recettes")  # + st.rerun() auto
revenir()  # Retour arrière
```

### Gestionnaire complet

```python
from src.core.state import GestionnaireEtat

GestionnaireEtat.definir_recette_visualisation(42)
GestionnaireEtat.nettoyer_etats_ui()
GestionnaireEtat.reset_complet()
```

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
|--------|-----------|--------|
| Services/métier | `@avec_cache` | Multi-niveaux, testable sans Streamlit |
| Composants UI (graphiques) | `@st.cache_data` | Retourne objets Streamlit/Plotly |
| Données UI (dict/list) | `@cache_ui` | Bridge `st.cache_data` + fallback tests |

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

### Lazy-load dans les modules

```python
# src/modules/cuisine/recettes/__init__.py
def app():
    """Point d'entrée module — imports dans la fonction pour lazy loading"""
    from src.services.cuisine.recettes import get_recette_service

    service = get_recette_service()
    suggestions = service.suggest_recipes("Dîner rapide")
```

> **Important**: Garder les imports des services DANS `app()`, pas au niveau du module.

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
# ❌ Mauvais (dans un service avec st.cache_data)
@st.cache_data(ttl=300)
def charger_donnees():
    return service.get_all()

# ✅ Bon (dans le service avec avec_cache)
@avec_cache(ttl=300)
def charger_donnees():
    return db.query(Recette).all()
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

### 4. Navigation via GestionnaireEtat

```python
# ❌ Mauvais — contourne le système de navigation
st.session_state.current_page = "cuisine.recettes"
st.rerun()

# ✅ Bon — utilise le raccourci
from src.core.state import naviguer
naviguer("cuisine.recettes")  # gère rerun automatiquement
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

Pour les modules UI qui utilisent `get_*_service()`:

```python
@patch("src.modules.cuisine.courses.get_courses_service")
def test_afficher_courses(mock_factory):
    mock_service = MagicMock()
    mock_service.lister_articles.return_value = [article]
    mock_factory.return_value = mock_service

    from src.modules.cuisine.courses import app
    app()

    mock_service.lister_articles.assert_called_once()
```

### Mock Streamlit

```python
@patch("src.modules.accueil.dashboard.st")
def test_dashboard(mock_st):
    mock_st.session_state = {}
    app()
    mock_st.title.assert_called()
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

Les patterns suivants ont été évalués et supprimés du codebase (dead code, inutiles pour une app Streamlit single-user):

| Pattern | Raison de suppression |
|---------|----------------------|
| **Result Monad** (`src/core/result/`) | Zero callers en production. Les exceptions Python standard suffisent. |
| **Repository Pattern** (`src/core/repository.py`) | Abstraction inutile au-dessus de SQLAlchemy ORM. |
| **Specification Pattern** (`src/core/specifications.py`) | Jamais utilisé. SQLAlchemy `.filter()` suffit. |
| **Unit of Work** (`src/core/unit_of_work.py`) | Zero callers. `@avec_session_db` gère les transactions. |
| **IoC Container** (`src/core/container.py`) | Zero callers en production. `@service_factory` + registre suffisent. |
| **Middleware Pipeline** (`src/core/middleware/`) | Zero callers. Le décorateur `@avec_resilience` remplace ce besoin. |
| **CQRS** (`src/services/core/cqrs/`) | Zero callers. Pas de séparation lecture/écriture pour une app single-user. |
| **UI v2.0** (DialogBuilder, FormBuilder, URL State) | Zero callers. Streamlit natif `st.dialog()`, `st.form()` suffisent. |

---

## Voir aussi

- [ARCHITECTURE.md](ARCHITECTURE.md) — Vue d'ensemble
- [API_REFERENCE.md](API_REFERENCE.md) — Référence API
- [MIGRATION_CORE_PACKAGES.md](MIGRATION_CORE_PACKAGES.md) — Guide de migration
