# Patterns d'Architecture — src/core

Ce document présente les patterns utilisés dans le core de l'application avec exemples d'usage.

## Table des matières

1. [Result Monad](#result-monad)
2. [Repository Pattern](#repository-pattern)
3. [Specification Pattern](#specification-pattern)
4. [Unit of Work](#unit-of-work)
5. [IoC Container](#ioc-container)
6. [State Slices](#state-slices)
7. [Resilience Policies](#resilience-policies)
8. [Cache Multi-Niveaux](#cache-multi-niveaux)
9. [Circuit Breaker](#circuit-breaker)
10. [Middleware Pipeline](#middleware-pipeline)
11. [UI Patterns (v2.0)](#ui-patterns-v20)

---

## Result Monad

**Fichiers**: `src/core/result/`

Gestion explicite des erreurs style Rust — remplace les exceptions implicites.

### Usage basique

```python
from src.core.result import Ok, Err, Result

def diviser(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Err("Division par zéro")
    return Ok(a / b)

# Pattern matching (Python 3.10+)
match diviser(10, 2):
    case Ok(v): print(f"Résultat: {v}")
    case Err(e): print(f"Erreur: {e}")
```

### Chaînage fonctionnel

```python
result = (
    diviser(10, 2)
    .map(lambda x: x * 2)
    .map_err(lambda e: f"Erreur calcul: {e}")
    .unwrap_or(0.0)
)
```

### Erreurs structurées (production)

```python
from src.core.result import Ok, failure, ErrorCode, result_api

def charger_recette(id: int) -> Result[Recette, ErrorInfo]:
    recette = db.get(id)
    if not recette:
        return failure(ErrorCode.NOT_FOUND, f"Recette #{id} introuvable")
    return Ok(recette)

# Décorateur pour conversion automatique
@result_api(message_utilisateur="Impossible de charger les recettes")
def charger_recettes(categorie: str) -> list[Recette]:
    return db.query(Recette).filter_by(categorie=categorie).all()
```

### Side-effects

```python
result.on_success(lambda r: logger.info(f"Chargé: {r.nom}"))
result.on_failure(lambda e: logger.error(f"[{e.code}] {e.message}"))
```

---

## Repository Pattern

**Fichier**: `src/core/repository.py`

CRUD générique typé pour SQLAlchemy.

### Usage

```python
from src.core.repository import Repository
from src.core.models import Recette

class RecetteRepository(Repository[Recette]):
    pass

# Utilisation
with obtenir_contexte_db() as session:
    repo = RecetteRepository(session, Recette)

    # Lecture
    recette = repo.obtenir_par_id(42)
    toutes = repo.lister(filtre={"saison": "été"})

    # Écriture
    nouvelle = repo.creer(Recette(nom="Tarte"))
    repo.mettre_a_jour(recette)
    repo.supprimer(recette)

    # Batch operations
    repo.creer_en_masse([r1, r2, r3])
    repo.mettre_a_jour_en_masse(spec, actif=False)
```

### Avec Result

```python
result = repo.obtenir_result(42)  # Ok(Recette) | Err(ErrorInfo)
result = repo.creer_result(recette)
```

---

## Specification Pattern

**Fichier**: `src/core/specifications.py`

Critères de requête composables.

### Construction fluide

```python
from src.core.specifications import par_champ, contient, paginer, ordre_par

spec = (
    par_champ("actif", True)
    & contient("nom", "tarte")
    & ordre_par("created_at", desc=True)
    & paginer(page=1, taille=20)
)

recettes = repo.lister(spec=spec)
```

### Combinaison logique

```python
# AND (&)
spec = spec_actif & spec_saison_ete

# OR (|)
spec = spec_dessert | spec_gateau

# NOT (~)
spec = ~spec_archive
```

### Specs pré-définies

```python
from src.core.specifications import actif, recent, entre, par_date_range

# Entités actives
spec = actif()

# Créées dans les 7 derniers jours
spec = recent(jours=7)

# Plage de valeurs
spec = entre("prix", 10, 50)

# Plage de dates
spec = par_date_range("created_at", debut, fin)
```

---

## Unit of Work

**Fichier**: `src/core/unit_of_work.py`

Transaction atomique avec rollback automatique.

### Usage

```python
from src.core.unit_of_work import UnitOfWork

with UnitOfWork() as uow:
    # Repositories disponibles via uow
    recette = uow.recettes.creer(Recette(nom="Tarte"))
    ingredients = uow.ingredients.lister(spec=par_recette(recette.id))

    # Commit automatique en sortie, rollback sur exception
```

---

## IoC Container

**Fichier**: `src/core/container.py`

Injection de dépendances légère et typée.

### Enregistrement

```python
from src.core.container import conteneur

# Singleton (une instance pour tout le process)
conteneur.singleton(
    Parametres,
    factory=lambda: Parametres(),
    cleanup=lambda p: p.close(),  # Optionnel
)

# Transient (nouvelle instance à chaque appel)
conteneur.factory(
    RecetteService,
    factory=lambda c: RecetteService(c.resolve(ClientIA)),
)

# Instance existante
conteneur.instance(Engine, mon_engine)
```

### Résolution

```python
# Par type
params = conteneur.resolve(Parametres)

# Par alias
engine = conteneur.resolve("db_engine")

# Safe (retourne None si non trouvé)
service = conteneur.try_resolve(ServiceOptional)
```

### Lifecycle

```python
# Créer tous les singletons au démarrage
conteneur.initialiser()

# Cleanup propre à l'arrêt
conteneur.fermer()
```

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

Politiques de résilience composables.

### Politiques disponibles

```python
from src.core.resilience import (
    RetryPolicy,
    TimeoutPolicy,
    BulkheadPolicy,
    FallbackPolicy,
)

# Retry avec backoff exponentiel
retry = RetryPolicy(max_tentatives=3, delai_base=1.0, backoff=2.0)

# Timeout
timeout = TimeoutPolicy(secondes=30)

# Bulkhead (limite de concurrence)
bulkhead = BulkheadPolicy(max_concurrent=5)

# Fallback
fallback = FallbackPolicy(valeur_defaut=[])
```

### Composition

```python
# Combiner avec +
politique = RetryPolicy(3) + TimeoutPolicy(30) + BulkheadPolicy(5)

# Appliquer
result = politique.executer(lambda: appel_risque())
```

### Pré-configurées

```python
from src.core.resilience import politique_ia, politique_base_de_donnees

result = politique_ia().executer(lambda: client.generer(...))
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
from src.core.caching import obtenir_cache

cache = obtenir_cache()

# Set/Get
cache.set("ma_cle", valeur, ttl=600, tags=["recettes"])
valeur = cache.get("ma_cle")

# Cache-aside pattern
valeur = cache.get_or_set("cle", compute_fn=lambda: calcul_couteux())

# Invalidation par tags
cache.invalider_par_tag("recettes")
```

### Statistiques

```python
stats = cache.statistiques()
# {"hits": 150, "misses": 30, "hit_rate": 0.83, ...}
```

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

## Middleware Pipeline

**Fichiers**: `src/core/middleware/`

Chaîne de responsabilité composable.

### Construction

```python
from src.core.middleware import Pipeline

pipeline = (
    Pipeline()
    .utiliser(LogMiddleware())
    .utiliser(TimingMiddleware())
    .utiliser(RetryMiddleware(max_retries=3))
    .utiliser(ValidationMiddleware(schema=MonSchema))
)

result = pipeline.executer(lambda ctx: operation(ctx))
```

### Factories pré-configurées

```python
# Pour appels IA
pipeline = Pipeline.ia()

# Pour CRUD DB
pipeline = Pipeline.crud()

# Pour API externe
pipeline = Pipeline.api_externe()
```

### Middlewares disponibles

| Middleware                 | Description                 |
| -------------------------- | --------------------------- |
| `LogMiddleware`            | Logging entrée/sortie       |
| `TimingMiddleware`         | Mesure du temps d'exécution |
| `RetryMiddleware`          | Retry automatique           |
| `CacheMiddleware`          | Cache des résultats         |
| `ValidationMiddleware`     | Validation Pydantic         |
| `SessionMiddleware`        | Injection session DB        |
| `ErrorHandlerMiddleware`   | Conversion erreurs          |
| `RateLimitMiddleware`      | Limitation de débit         |
| `CircuitBreakerMiddleware` | Protection circuit          |

---

## Best Practices

### 1. Toujours utiliser Result pour les opérations risquées

```python
# ❌ Mauvais
def charger_recette(id: int) -> Recette:
    recette = db.get(id)
    if not recette:
        raise ValueError("Non trouvé")
    return recette

# ✅ Bon
def charger_recette(id: int) -> Result[Recette, ErrorInfo]:
    recette = db.get(id)
    if not recette:
        return failure(ErrorCode.NOT_FOUND, f"Recette #{id} introuvable")
    return Ok(recette)
```

### 2. Composer les Specifications

```python
# ❌ Mauvais
if actif:
    recettes = repo.lister(filtre={"actif": True})
if saison:
    recettes = [r for r in recettes if r.saison == saison]

# ✅ Bon
spec = par_champ("actif", actif) & par_champ("saison", saison)
recettes = repo.lister(spec=spec)
```

### 3. Utiliser le container pour les singletons

```python
# ❌ Mauvais
_engine = None
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(...)
    return _engine

# ✅ Bon
conteneur.singleton(Engine, factory=lambda: create_engine(...))
engine = conteneur.resolve(Engine)
```

### 4. Unifier la stratégie de cache

```python
# ❌ Mauvais (dans l'UI avec st.cache_data)
@st.cache_data(ttl=300)
def charger_donnees():
    return service.get_all()

# ✅ Bon (dans le service avec avec_cache)
@avec_cache(ttl=300)
def charger_donnees(self):
    return self.repo.lister()

# ✅ Bon (dans l'UI avec cache_ui - fallback pour tests)
@cache_ui(ttl=300, show_spinner=False)
def generer_graphique(data):
    return fig
```

**Politique de cache:**
| Couche | Décorateur | Raison |
|--------|-----------|--------|
| Services/métier | `@avec_cache` | Multi-niveaux, testable sans Streamlit |
| Composants UI | `@cache_ui` | Bridge `st.cache_data` + fallback tests |
| Singletons | IoC Container | Thread-safe, cleanup automatique |

---

## UI Patterns (v2.0)

**Fichiers**: `src/ui/dialogs.py`, `src/ui/fragments.py`, `src/ui/layouts/`, `src/ui/state/`, `src/ui/forms/`

Patterns modernes pour Streamlit 1.35+ avec fallbacks gracieux.

### DialogBuilder — Modales fluides

```python
from src.ui import DialogBuilder, confirm_dialog

# Simple confirmation
if confirm_dialog("Supprimer cet élément ?", "Confirmation"):
    delete_item()

# Builder pattern pour cas complexes
dialog = (
    DialogBuilder("edit_recipe", "Modifier la recette")
    .width("large")
    .content("Formulaire de modification...")
    .actions(
        {"label": "Sauvegarder", "type": "primary", "on_click": save},
        {"label": "Annuler", "type": "secondary"}
    )
    .build()
)
dialog.show()
```

### Fragments — Rerenders partiels

```python
from src.ui import ui_fragment, auto_refresh, FragmentGroup

# Fragment isolé (ne recharge que ce bloc)
@ui_fragment
def metrics_panel():
    data = fetch_metrics()
    for m in data:
        st.metric(m.label, m.value)

# Auto-refresh toutes les 30s
@auto_refresh(seconds=30)
def live_status():
    return get_system_status()

# Groupe coordonné
group = FragmentGroup("dashboard")

@group.register("charts")
def charts(): ...

@group.register("tables")
def tables(): ...

# Rafraîchir tout le groupe
group.refresh_all()
```

### Layouts Composables

```python
from src.ui import Row, Grid, Stack, Gap, two_columns

# Row avec proportions
with Row(gap="md") as row:
    with row.col(2):  # 2 parts sur 3
        st.write("Contenu principal")
    with row.col(1):  # 1 part sur 3
        st.write("Sidebar")

# Grid responsive
with Grid(cols=4, gap="lg") as grid:
    for item in items:
        with grid.cell():
            render_card(item)

# Stack vertical
with Stack(gap=Gap.MD, align="center"):
    st.title("Titre")
    st.button("Action")

# Helpers rapides
with two_columns() as (left, right):
    with left: st.write("Gauche")
    with right: st.write("Droite")
```

### URL State — Deep Linking

```python
from src.ui import url_state, selectbox_with_url, pagination_with_url

# Widget synchronisé avec URL
tab = selectbox_with_url("Section", ["Aperçu", "Détails", "Stats"], param="section")
# URL: ?section=Apr%C3%A9u

# Pagination persistante
page = pagination_with_url(total_pages=10, param="p")
# URL: ?p=3

# Décorateur pour toute la page
@url_state(namespace="recettes")
def page_recettes():
    # Tous les états synchronisés automatiquement
    pass
```

### FormBuilder — Formulaires déclaratifs

```python
from src.ui import FormBuilder

result = (
    FormBuilder("contact_form")
    .text("nom", "Nom", required=True, max_length=100)
    .email("email", "Email", required=True)
    .number("age", "Âge", min_value=0, max_value=120)
    .select("pays", "Pays", options=["France", "Belgique", "Suisse"])
    .textarea("message", "Message", max_length=500)
    .submit("Envoyer")
    .build()
)

if result.submitted:
    if result.is_valid:
        save_contact(**result.data)
        st.success("Contact enregistré")
    else:
        for error in result.errors:
            st.error(error)
```

### Quand utiliser quoi ?

| Pattern         | Cas d'usage                             |
| --------------- | --------------------------------------- |
| `@ui_fragment`  | Sections qui changent indépendamment    |
| `@auto_refresh` | Données temps réel (métriques, statuts) |
| `DialogBuilder` | Confirmations, formulaires modaux       |
| `Row`/`Grid`    | Layouts répétitifs, grilles de cartes   |
| `@url_state`    | Pages avec filtres, pagination, onglets |
| `FormBuilder`   | Formulaires avec validation côté client |

---

## Voir aussi

- [ARCHITECTURE.md](ARCHITECTURE.md) — Vue d'ensemble
- [API_REFERENCE.md](API_REFERENCE.md) — Référence API
- [MIGRATION_CORE_PACKAGES.md](MIGRATION_CORE_PACKAGES.md) — Guide de migration
- [MIGRATION_UI_V2.md](MIGRATION_UI_V2.md) — Guide de migration UI v2
