# Analyse Exhaustive de `src/core/` — Rapport Technique

**Projet** : Assistant MaTanne (Application Streamlit de gestion familiale)  
**Scope** : 89 fichiers Python, ~14 500 lignes de code, 13 packages  
**Date** : Janvier 2025

---

## Table des Matières

1. [Vue d'ensemble de l'architecture](#1-vue-densemble-de-larchitecture)
2. [Qualité du code](#2-qualité-du-code)
3. [Design Patterns identifiés](#3-design-patterns-identifiés)
4. [Anti-patterns & Code Smells](#4-anti-patterns--code-smells)
5. [Problèmes de performance](#5-problèmes-de-performance)
6. [Préoccupations de sécurité](#6-préoccupations-de-sécurité)
7. [Problèmes spécifiques par fichier](#7-problèmes-spécifiques-par-fichier)
8. [Lacunes de couverture de test](#8-lacunes-de-couverture-de-test)
9. [Résumé des métriques](#9-résumé-des-métriques)

---

## 1. Vue d'ensemble de l'architecture

### 1.1 Organisation des packages

```
src/core/                          # 17 fichiers racine (~3 200 LoC)
├── ai/                            # 6 fichiers  (~1 270 LoC) — Client IA Mistral, parsing, cache, rate limit, circuit breaker
├── caching/                       # 7 fichiers  (~820 LoC)  — Cache multi-niveaux L1/L2/L3
├── config/                        # 4 fichiers  (~770 LoC)  — Pydantic BaseSettings, .env loading, validation
├── date_utils/                    # 5 fichiers  (~370 LoC)  — Dates, semaines, formatage FR
├── db/                            # 5 fichiers  (~760 LoC)  — Engine, sessions, migrations SQL-file
├── middleware/                    # 4 fichiers  (~750 LoC)  — Pipeline middleware (onion model)
├── models/                        # 20 fichiers (~4 600 LoC) — SQLAlchemy ORM (le plus gros package)
├── monitoring/                    # 4 fichiers  (~760 LoC)  — Métriques, health checks, chronomètre
├── observability/                 # 2 fichiers  (~280 LoC)  — Correlation ID, contexte d'exécution
├── query/                         # 2 fichiers  (~475 LoC)  — Query builder fluent
├── resilience/                    # 2 fichiers  (~370 LoC)  — Retry, Timeout, Bulkhead, Fallback
├── validation/                    # 3 fichiers  (~580 LoC)  — Sanitizer, validators
│   └── schemas/                   # 8 fichiers  (~430 LoC)  — Schémas Pydantic par domaine
```

### 1.2 Architecture en couches

Le `core` implémente une architecture en couches bien structurée :

| Couche | Packages | Rôle |
|--------|----------|------|
| **Infrastructure** | `db/`, `caching/`, `ai/`, `config/` | Accès aux ressources externes |
| **Cross-cutting** | `logging`, `monitoring/`, `observability/`, `resilience/`, `middleware/` | Aspects transverses |
| **Domain Support** | `models/`, `repository`, `unit_of_work`, `specifications`, `query/` | Accès aux données typé |
| **Validation** | `validation/`, `errors_base`, `result` | Intégrité des données |
| **Composition** | `container`, `bootstrap`, `decorators`, `lazy_loader` | Assemblage DI + démarrage |
| **UI Bridge** | `state`, `storage`, `session_keys`, `events` | Interface avec Streamlit |

### 1.3 Flux de démarrage

```
bootstrap.demarrer_application()
  ├── config/loader._reload_env_files()
  ├── config/settings.obtenir_parametres()
  ├── container.enregistrer(Parametres, Engine, CacheMultiNiveau, ClientIA, CollecteurMetriques)
  ├── container.initialiser()  [eager singletons]
  └── atexit(arreter_application)
```

### 1.4 Points positifs architecturaux

- **Modularité excellente** : Chaque package a une responsabilité unique et claire.
- **Lazy loading systématique** : PEP 562 utilisé dans `__init__.py`, `models/__init__.py` et `lazy_loader.py` — ~60% d'accélération au démarrage revendiquée.
- **Conventions de nommage SQL** : `MetaData(naming_convention=)` dans `models/base.py` — nommage cohérent des contraintes FK, PK, UQ, CK.
- **Abstraction SessionStorage** : Protocol-based pour découpler de `st.session_state` (testable avec `MemorySessionStorage`).
- **Result monad** : Pattern fonctionnel (`Ok`/`Err`) pour la gestion d'erreurs sans exceptions dans `resilience/`.

---

## 2. Qualité du code

### 2.1 Points forts

| Critère | Évaluation | Détails |
|---------|------------|---------|
| **Typage** | ★★★★★ | `Mapped[T]` + `mapped_column()` partout (SQLAlchemy 2.0), generics TypeVar, PEP 604 unions |
| **Documentation** | ★★★★☆ | Docstrings françaises complètes avec `Args`, `Returns`, `Examples` dans la plupart des fichiers |
| **Séparation UI/domain** | ★★★★☆ | `errors_base.py` pur vs `errors.py` avec Streamlit ; `storage.py` Protocol ; lazy imports de `st` |
| **Cohérence interne** | ★★★☆☆ | Certaines dualités (voir anti-patterns) |
| **Tests unitaires** | ★★★☆☆ | Fixtures fournies mais couverture incomplète sur les packages récents |

### 2.2 Conventions de nommage

- **Langue** : Français systématique (`obtenir_parametres`, `avec_session_db`, `GestionnaireMigrations`)
- **Style** : Cohérent — `snake_case` pour fonctions/variables, `PascalCase` pour classes, `SCREAMING_SNAKE` pour constantes
- **Exception notable** : Modèles SQLAlchemy mélangent EN et FR (`ChildProfile`, `FamilyActivity` vs `Recette`, `Repas`) — héritage historique du domaine famille initialement codé en anglais

### 2.3 Distribution du code

| Package | Fichiers | LoC | LoC moyen/fichier |
|---------|----------|-----|-------------------|
| models/ | 20 | ~4 600 | 230 |
| ai/ | 6 | ~1 270 | 212 |
| root files | 17 | ~3 200 | 188 |
| caching/ | 7 | ~820 | 117 |
| config/ | 4 | ~770 | 193 |
| middleware/ | 4 | ~750 | 188 |
| db/ | 5 | ~760 | 152 |
| monitoring/ | 4 | ~760 | 190 |
| validation/ (+ schemas/) | 11 | ~1 010 | 92 |
| query/ | 2 | ~475 | 238 |
| resilience/ | 2 | ~370 | 185 |
| date_utils/ | 5 | ~370 | 74 |
| observability/ | 2 | ~280 | 140 |

---

## 3. Design Patterns identifiés

### 3.1 Patterns structurels

| Pattern | Fichier(s) | Implémentation |
|---------|-----------|----------------|
| **IoC Container** | `container.py` | `Conteneur` avec scopes SINGLETON/TRANSIENT/SESSION, thread-safe (RLock), factory detection via `inspect.signature` |
| **Repository** | `repository.py` | Generic `Repository[T]` avec `lister()`, `creer()`, `mettre_a_jour()`, support Specification |
| **Unit of Work** | `unit_of_work.py` | Context manager avec repository cache par type de modèle, auto-commit/rollback |
| **Singleton** | Multiples | `obtenir_parametres()`, `obtenir_moteur()`, `CacheMultiNiveau.__new__()`, `conteneur` global |
| **Facade** | `caching/cache.py` | `Cache` static class delegate vers `CacheMultiNiveau` |
| **Strategy** | `ai/parser.py` | 5 stratégies de parsing JSON en cascade |
| **Pipeline/Middleware** | `middleware/` | Onion model avec `Pipeline.utiliser()` fluent API |

### 3.2 Patterns comportementaux

| Pattern | Fichier(s) | Implémentation |
|---------|-----------|----------------|
| **Specification** | `specifications.py` | Composable avec `&`, `|`, `~` operators, intégré dans Repository |
| **Circuit Breaker** | `ai/circuit_breaker.py` | 3 états (FERME/OUVERT/SEMI_OUVERT), registre global, décorateur |
| **Result Monad** | `result.py` | `Ok[T]`/`Err[E]` frozen dataclasses avec `map()`, `and_then()`, `combiner()` |
| **Observer/Pub-Sub** | `events.py` | Bus d'événements avec wildcards |
| **Decorator** | `decorators.py` | `@avec_session_db`, `@avec_cache`, `@avec_gestion_erreurs`, `@avec_validation` |
| **Builder** | `query/builder.py` | `Requete[T]` fluent API (`.et()`, `.contient()`, `.trier_par()`, `.paginer()`) |

### 3.3 Patterns d'infrastructure

| Pattern | Fichier(s) | Implémentation |
|---------|-----------|----------------|
| **Multi-level Cache** | `caching/` | L1 mémoire (OrderedDict LRU) → L2 session (st.session_state) → L3 fichier (pickle) |
| **Correlation ID** | `observability/context.py` | `contextvars.ContextVar` (thread-safe + async-safe) avec propagation hiérarchique |
| **Resilience Policies** | `resilience/policies.py` | Composables via `+` operator : `RetryPolicy + TimeoutPolicy + BulkheadPolicy` |
| **Lazy Loading** | `__init__.py`, `models/__init__.py` | PEP 562 `__getattr__` avec cache dans `globals()` |

### 3.4 Qualité des implémentations

- **Container** : Bien implémenté avec thread-safety, scopes multiples, introspection. Manque : interface déclarative (annotations) et auto-wiring.
- **Repository** : Générique et utile, bien intégré avec Specification. La méthode `lister()` accepte à la fois des dicts et des Specifications — flexible.
- **Result monad** : Très complète (19 méthodes), frozen dataclasses, bien typée avec generics.
- **Resilience policies** : Composition élégante via `__add__`, factories pré-configurées (`politique_ia()`, `politique_base_de_donnees()`). Le `TimeoutPolicy` utilise `ThreadPoolExecutor` (1 worker) ce qui est correct mais crée un thread pool par appel.

---

## 4. Anti-patterns & Code Smells

### 4.1 Duplication de responsabilité

#### 4.1.1 Double système de gestion d'erreurs

**`decorators.py:@avec_gestion_erreurs`** vs **`errors.py:@gerer_erreurs`** — deux décorateurs avec la même finalité (attraper les exceptions et afficher dans Streamlit), mais avec des implémentations différentes.

- `@avec_gestion_erreurs` (L213-256) : Catch générique + `st.error()` + log + return None
- `@gerer_erreurs` (L30-95 dans errors.py) : Catch par type d'exception avec icônes Streamlit spécifiques (⚠️ pour validation, 🔍 pour non trouvé, 💾 pour DB, 🤖 pour IA, ⏱️ pour rate limit)

**Impact** : Confusion pour les développeurs sur quel décorateur utiliser. Le second est plus riche mais le premier est dans le module "officiel" des décorateurs.

**Recommandation** : Conserver uniquement `@gerer_erreurs` (le plus complet) et le déplacer vers `decorators.py`.

#### 4.1.2 Double circuit breaker

**`ai/circuit_breaker.py`** implémente un circuit breaker complet (291 lignes), puis une note indique qu'il est "déprécié en faveur de `resilience.policies`". Mais le `CircuitBreakerMiddleware` dans `middleware/builtin.py` réimplémente le même concept une troisième fois.

**Recommandation** : Retirer `ai/circuit_breaker.py`, utiliser `resilience/policies.py` + middleware pour le circuit breaker.

#### 4.1.3 Logique async dupliquée

**`ai/client.py:generer_json()`** (L376-400) contient une implémentation inline d'async-to-sync avec `ThreadPoolExecutor`, alors que **`async_utils.py:executer_async()`** fait exactement cela.

```python
# client.py — dupliqué
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(asyncio.run, coro)
    return future.result(timeout=120)

# async_utils.py — existant
def executer_async(coro):
    # même chose mais avec détection event loop
```

### 4.2 Couplage au framework Streamlit

#### 4.2.1 Couplage direct dans des modules "purs"

Plusieurs fichiers censés être indépendants du framework importent directement `streamlit` :

| Fichier | Ligne | Nature du couplage |
|---------|-------|--------------------|
| `ai/cache.py` | `obtenir_statistiques()` | Accès direct à `st.session_state` au lieu de `SessionStorage` |
| `caching/session.py` | Import global | `import streamlit as st` au top level |
| `lazy_loader.py` | `afficher_stats_chargement_differe()` | Crée des widgets `st.button`, `st.rerun`, `st.metric` |
| `errors.py` | `afficher_erreur_streamlit()` | Import lazy (acceptable car c'est la couche UI des erreurs) |
| `validation/validators.py` | `afficher_erreurs_validation()` | Import lazy avec fallback logging (bon pattern) |

**Recommandation** :
- `ai/cache.py` : Utiliser `SessionStorage` protocol au lieu d'accès direct à `st.session_state`
- `caching/session.py` : Utiliser l'abstraction `obtenir_session_state()` de `storage.py`
- `lazy_loader.py` : Séparer les fonctions d'affichage dans un module UI dédié

#### 4.2.2 SessionStorage partiellement adopté

Le Protocol `SessionStorage` est défini dans `storage.py` et utilisé par `state.py` et `ai/rate_limit.py`, mais **pas** par :
- `caching/session.py` (accès direct à `st.session_state`)
- `ai/cache.py` (accès direct à `st.session_state`)
- `session_keys.py` (constantes seulement, acceptable)

### 4.3 God-like files

| Fichier | LoC | Problème |
|---------|-----|----------|
| `models/temps_entretien.py` | 615 | 14 classes+enums dans un seul fichier — devrait être splitté |
| `models/users.py` | 570 | 9 classes (UserProfile + Garmin + Purchases + FoodLog + Weekend) — responsabilités mélangées |
| `models/jeux.py` | 564 | 16 classes+enums — Paris sportifs + Loto dans le même fichier |
| `ai/client.py` | 452 | Client HTTP + retry + cache check + vision + sync wrapper dans une classe |

### 4.4 Classes à méthodes statiques uniquement

Plusieurs classes n'ont que des méthodes statiques (pas d'état d'instance) :

| Classe | Fichier |
|--------|---------|
| `NettoyeurEntrees` | `validation/sanitizer.py` |
| `CacheIA` | `ai/cache.py` |
| `RateLimitIA` | `ai/rate_limit.py` |
| `GestionnaireEtat` | `state.py` (toutes les méthodes sont `@staticmethod`) |
| `GestionnaireLog` | `logging.py` |
| `GestionnaireMigrations` | `db/migrations.py` |

**Impact** : Ne bénéficient pas de l'injection de dépendances via le container IoC. Impossible de remplacer par un mock dans les tests sans monkey-patching.

**Recommandation** : Convertir en instances (même singletons) enregistrées dans le container.

### 4.5 Mutable class-level state

`ChargeurModuleDiffere` dans `lazy_loader.py` utilise un dict de classe `_cache = {}` pour le cache des modules chargés. Ce dict est partagé entre toutes les instances (et même les appels statiques) mais n'est pas protégé par un lock.

```python
class ChargeurModuleDiffere:
    _cache: dict[str, types.ModuleType] = {}  # Partagé !

    @staticmethod
    def charger(chemin):
        if chemin in ChargeurModuleDiffere._cache:
            return ChargeurModuleDiffere._cache[chemin]  # Race condition possible
```

### 4.6 Nommage EN/FR incohérent dans les modèles

Les modèles SQLAlchemy mélangent les deux langues :

- **Français** : `Recette`, `Repas`, `Planning`, `ArticleCourses`, `ListeCourses`, `ArticleInventaire`
- **Anglais** : `ChildProfile`, `FamilyActivity`, `FamilyBudget`, `ShoppingItem`, `HealthRoutine`, `HealthEntry`, `Project`, `ProjectTask`, `Furniture`, `HouseStock`, `MaintenanceTask`, `EcoAction`, `GardenItem`, `UserProfile`, `GarminActivity`, `Backup`, `ActionHistory`

Plus de la moitié des modèles sont en anglais, contrairement à la convention du projet (français partout).

---

## 5. Problèmes de performance

### 5.1 TimeoutPolicy crée un ThreadPoolExecutor par appel

```python
# resilience/policies.py — TimeoutPolicy.executer()
def executer(self, fn):
    with ThreadPoolExecutor(max_workers=1) as executor:  # Nouveau pool à chaque appel !
        future = executor.submit(fn)
```

**Impact** : Création + destruction d'un thread pool à chaque invocation. En usage intensif (ex: boucle de retry), cela crée beaucoup d'overhead OS.

**Recommandation** : Réutiliser un pool partagé ou créer le pool à l'__init__ du policy.

### 5.2 Cache L3 fichier utilise pickle

`caching/file.py` sérialise avec `pickle.dump()` et désérialise avec `pickle.load()`. Pickle est lent comparé à JSON/msgpack pour les données simples.

**Impact** : Latence supplémentaire pour le cache L3. Acceptable car le L3 est le fallback (L1/L2 absorbent la majorité des hits).

### 5.3 `Requete.supprimer()` charge toutes les entités en mémoire

```python
# query/builder.py — Requete.supprimer()
def supprimer(self, session):
    entites = self.executer(session)  # SELECT * FROM ...
    for entite in entites:
        session.delete(entite)  # DELETE one by one
    return len(entites)
```

**Impact** : Pour une suppression en masse (ex: purge de 10 000 entrées), cela charge tout en mémoire puis émet N requêtes DELETE au lieu d'un seul `DELETE ... WHERE`.

**Recommandation** : Utiliser `session.execute(delete(Model).where(...))` pour la suppression bulk.

### 5.4 `Requete.compter()` ne bénéficie pas du `_limit`/`_offset`

La méthode `compter()` ignore la pagination (ce qui est correct pour un "total count") mais reconstruit les conditions manuellement au lieu de réutiliser `construire()`. Duplication mineure.

### 5.5 Repository.lister() avec filtres dict

```python
# repository.py
for champ, valeur in filtres.items():
    colonne = getattr(self.modele, champ, None)  # getattr par itération
```

Pas de validation que le champ existe sur le modèle — un champ invalide est silencieusement ignoré (retourne tous les résultats au lieu d'un filtrage).

### 5.6 Equipe.forme_recente charge toutes les relations

```python
# models/jeux.py — Equipe.forme_recente property
tous_matchs = [
    *[(m, "dom") for m in self.matchs_domicile if m.joue],  # Lazy load!
    *[(m, "ext") for m in self.matchs_exterieur if m.joue],  # Lazy load!
]
```

Accéder à `self.matchs_domicile` déclenche un lazy load SQLAlchemy. Si cette propriété est appelée sur une liste de 20 équipes, cela génère 40 requêtes SQL (N+1 problem).

---

## 6. Préoccupations de sécurité

### 6.1 Cache fichier avec pickle (désérialisation arbitraire)

```python
# caching/file.py
data = pickle.load(f)  # Risque d'exécution de code arbitraire
```

**Risque** : Si un attaquant peut écrire dans le dossier `.cache/`, il peut injecter du code Python via un objet pickle malveillant.

**Mitigation existante** : Le cache est en écriture locale uniquement (pas exposé sur le réseau). Risque faible en contexte Streamlit single-user.

**Recommandation** : Remplacer par `json` + `marshal` ou `msgpack` pour les données simples. Garder pickle uniquement pour les objets complexes non-sérialisables autrement.

### 6.2 Sanitizer SQL : détection sans blocage

```python
# validation/sanitizer.py
for pattern in NettoyeurEntrees.PATTERNS_SQL:
    if re.search(pattern, valeur, re.IGNORECASE):
        logger.warning(f"[!] Tentative injection SQL détectée: {valeur[:50]}")
        # On laisse passer mais on log (pour ne pas bloquer faux positifs)
```

**Risque** : Les patterns SQL sont détectés mais pas bloqués. La stratégie "log only" est consciente (commentaire explicite) mais laisse passer les injections si l'ORM est bypassé.

**Mitigation existante** : SQLAlchemy ORM paramétrise toutes les requêtes — le risque d'injection est quasi nul via l'ORM. Le risque existe uniquement si des requêtes brutes (`text()`) sont utilisées avec des entrées non-sanitizées.

### 6.3 OAuth tokens stockés en clair

```python
# models/users.py — GarminToken
oauth_token: Mapped[str] = mapped_column(String(500), nullable=False)
oauth_token_secret: Mapped[str] = mapped_column(String(500), nullable=False)

# models/calendrier.py — CalendrierExterne
credentials: Mapped[dict | None] = mapped_column(JSONB)  # Tokens OAuth
```

**Risque** : Les tokens OAuth 1.0a Garmin et les credentials calendrier sont stockés en clair dans PostgreSQL.

**Recommandation** : Chiffrer via `pgcrypto` ou chiffrement applicatif (Fernet/AES) avant stockage.

### 6.4 Logging de secrets

`logging.py` implémente un `FiltreSecrets` qui masque les patterns sensibles dans les logs :

```python
PATTERNS_SECRETS = [
    (r'(postgresql://[^\s]+)', r'postgresql://***'),
    (r'(Bearer\s+[^\s]+)', r'Bearer ***'),
    (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)[^\s"\']+', r'\1***'),
    (r'(password["\']?\s*[:=]\s*["\']?)[^\s"\']+', r'\1***'),
]
```

**Point positif** : Bonne pratique. Mais le regex `api[_-]?key` est trop large — il pourrait masquer des chaînes légitimes comme "api_key_name" dans du code debug.

### 6.5 Données personnelles hardcodées

```python
# constants.py
JULES_NAISSANCE = date(2024, 6, 22)  # Date de naissance d'un enfant
```

**Risque** : PII hardcodé dans le code source. Acceptable pour une application familiale privée. Problématique si le repo devient public.

---

## 7. Problèmes spécifiques par fichier

### 7.1 Fichiers racine

#### `__init__.py` (212 lignes)
- **Pattern** : PEP 562 lazy loading avec 100+ symboles mappés
- **Issue** : `_LAZY_IMPORTS` dict est énorme et doit être maintenu manuellement en sync avec les modules réels
- **Issue L30-90** : Certains imports sont commentés/supprimés mais les entrées dans `_LAZY_IMPORTS` restent — risque de `ImportError` silencieux

#### `constants.py` (228 lignes)
- **Issue L126** : `JULES_NAISSANCE = date(2024, 6, 22)` — PII hardcodé
- **Issue** : Constantes de cache (`CACHE_TTL_*`, `CACHE_MAX_SIZE`) dupliquées entre ici et `config/settings.py` — double source de vérité

#### `container.py` (366 lignes)
- **Pattern** : IoC Container bien implémenté
- **Issue L240-260** : `_creer_instance()` utilise `inspect.signature` à chaque résolution (pas caché) — léger overhead pour des types TRANSIENT fréquents
- **Issue** : Pas de support pour l'auto-wiring (injection basée sur les types de paramètres)

#### `decorators.py` (329 lignes)
- **Issue L85-100** : `@avec_cache` — La logique de génération de clé cache est complexe (50+ lignes) avec 3 fallbacks imbriqués. Difficile à maintenir et à déboguer
- **Issue L26** : `_SENTINELLE = object()` pour distinguer None d'une valeur absente dans le cache — correct mais ajoute de la complexité

#### `errors.py` (330 lignes)
- **Issue** : Dualité avec `decorators.py:@avec_gestion_erreurs` (voir §4.1.1)
- **Point positif** : `GestionnaireErreurs` context manager est utile pour les blocs try/except sans décorateur

#### `errors_base.py` (410 lignes)
- **Issue L320-340** : `valider_plage()` est marquée comme dépréciée mais toujours présente
- **Point positif** : Hiérarchie d'exceptions propre avec `code_erreur`, `message_utilisateur`, `to_dict()`

#### `lazy_loader.py` (372 lignes)
- **Issue L12** : `_cache: dict = {}` mutable class-level (voir §4.5)
- **Issue L200+** : `RouteurOptimise` couple navigation + chargement + affichage Streamlit — trop de responsabilités
- **Issue** : `precharger()` utilise des daemon threads sans gestion d'erreur

#### `logging.py` (266 lignes)
- **Point positif** : `FiltreSecrets` avec masquage regex — bonne pratique
- **Issue** : `_initialise` flag n'est pas thread-safe (pas de lock)

#### `repository.py` (~250 lignes)
- **Issue** : Filtres dict ignorés silencieusement si le champ n'existe pas sur le modèle
- **Point positif** : Intégration Specification bien typée avec generics

#### `result.py` (315 lignes)
- **Point positif** : Implémentation complète et idiomatique du pattern Result
- **Issue L180** : `combiner()` convertit les résultats via tuple unpacking — pourrait utiliser `dataclasses.fields`

#### `session_keys.py` (211 lignes)
- **Pattern** : Namespace de constantes avec `__slots__ = ()`
- **Issue** : 80+ constantes de clés — risque de collision non détecté (valeurs dupliquées possibles)

#### `specifications.py` (~300 lignes)
- **Point positif** : Operators `&`, `|`, `~` bien typés, intégration SQLAlchemy propre
- **Issue** : `Spec` accepte un lambda — pas sérialisable, pas inspectable pour debug

#### `state.py` (~400 lignes)
- **Issue** : `GestionnaireEtat` — toutes les méthodes sont `@staticmethod` (voir §4.4)
- **Issue** : `EtatApp` dataclass contient ~30 champs — God Object
- **Issue** : Historique de navigation limité à 50 entrées sans cleanup des anciennes

#### `storage.py` (210 lignes)
- **Point positif** : Protocol-based `SessionStorage` — bon découplage
- **Point positif** : `MemorySessionStorage` pour les tests

#### `unit_of_work.py` (~155 lignes)
- **Point positif** : Lazy session creation, repository cache
- **Issue** : `repository()` retourne toujours un nouveau `Repository` sauf si le type est déjà dans le cache — pas de lifetime management

#### `bootstrap.py` (268 lignes)
- **Point positif** : Orchestration claire du démarrage
- **Issue** : `_deja_demarre` flag global — ne supporte pas le rechargement à chaud de Streamlit si le state est partagé

#### `async_utils.py` (57 lignes)
- **Issue** : `timeout=120` hardcodé dans le `ThreadPoolExecutor.submit()` — devrait être paramétrable

### 7.2 Package AI

#### `ai/client.py` (452 lignes)
- **Issue L376-400** : `generer_json()` duplique la logique async-to-sync de `async_utils.py`
- **Issue L150-200** : `_effectuer_appel()` crée un nouveau `httpx.AsyncClient` à chaque appel — pas de session réutilisée
- **Issue** : Retry avec `asyncio.sleep()` dans `appeler()` + retry séparé dans `generer_json()` — double retry possible
- **Point positif** : Vision/OCR support avec `chat_with_vision()` pour modèle pixtral

#### `ai/parser.py` (~300 lignes)
- **Point positif** : 5 stratégies de parsing en cascade — très robuste face aux réponses IA malformées
- **Issue** : La stratégie 3 (repair) modifie les chaînes en place avec des regex — fragile pour de gros blocs JSON

#### `ai/cache.py` (~290 lignes)
- **Issue** : Accès direct à `st.session_state` dans `obtenir_statistiques()` — bypass du `SessionStorage` protocol
- **Issue** : Clé SHA-256 inclut le modèle dans le hash — un changement de modèle invalide tout le cache

#### `ai/rate_limit.py` (~200 lignes)
- **Point positif** : Utilise `SessionStorage` (bon découplage)
- **Issue** : Historique des 100 derniers appels stocké dans le session state — peut devenir volumineux

#### `ai/circuit_breaker.py` (~290 lignes)
- **Issue** : Marqué comme déprécié mais toujours importé dans `ai/__init__.py` et probablement utilisé

### 7.3 Package Caching

#### `caching/memory.py` (~130 lignes)
- **Point positif** : LRU O(1) via `OrderedDict.move_to_end` + `popitem`
- **Point positif** : Thread-safe avec RLock

#### `caching/session.py` (~130 lignes)
- **Issue** : Import direct de `streamlit` au top level — couplage fort

#### `caching/file.py` (~180 lignes)
- **Issue** : Utilise `pickle` (risque sécurité + performance)
- **Issue** : `invalidate()` par tags only — impossible d'invalider par pattern/clé car les noms de fichiers sont hashés en MD5
- **Point positif** : Écriture atomique (tmp + rename)

#### `caching/orchestrator.py` (~250 lignes)
- **Point positif** : Singleton thread-safe via `__new__` + lock
- **Issue** : `obtenir_ou_calculer()` n'est pas atomique — deux threads peuvent calculer en parallèle la même valeur

### 7.4 Package Config

#### `config/settings.py` (431 lignes)
- **Issue** : `DATABASE_URL` property tente 3 stratégies (st.secrets → env vars → field) — complexe mais nécessaire en multi-env
- **Issue** : Constantes de cache importées depuis `constants.py` puis redéfinies comme fields — double source de vérité

#### `config/loader.py` (~175 lignes)
- **Issue** : `_reload_env_files()` parse manuellement les .env comme `key=value` — devrait utiliser `python-dotenv`
- **Issue** : `_is_streamlit_cloud()` vérifie des heuristiques (présence de `st.secrets`) — fragile

#### `config/validator.py` (~320 lignes)
- **Point positif** : API fluent avec `NiveauValidation` (CRITIQUE/AVERTISSEMENT/INFO)
- **Point positif** : Test de connexion DB comme validation

### 7.5 Package DB

#### `db/engine.py` (~145 lignes)
- **Point positif** : Double-check locking singleton, pool pre-ping, SSL required
- **Issue** : `pool_size=5, max_overflow=10` hardcodé — devrait être configurable via `Parametres`

#### `db/session.py` (~130 lignes)
- **Point positif** : Context managers propres avec rollback automatique
- **Issue** : `obtenir_db_securise()` retourne `None` en cas d'erreur — peut masquer des problèmes

#### `db/migrations.py` (314 lignes)
- **Point positif** : SHA-256 checksums pour vérifier l'intégrité des migrations
- **Issue** : Migrations exécutées séquentiellement sans transaction — une erreur laisse la DB dans un état partiel

#### `db/utils.py` (228 lignes)
- **Issue** : `vacuum_database()` ouvre une connexion avec `AUTOCOMMIT` — pas de timeout configuré

### 7.6 Package Middleware

#### `middleware/builtin.py` (391 lignes)
- **Point positif** : 5 middlewares (Log, Timing, Retry, Validation, Cache, CircuitBreaker)
- **Issue** : `CircuitBreakerMiddleware` — les variables d'état (`_erreurs`, `_etat`, `_dernier_echec`) ne sont pas thread-safe (pas de lock)
- **Issue** : `CacheMiddleware` utilise `f"{ctx.operation}:{sorted(ctx.params.items())}"` comme clé — les valeurs non-hashables dans params casseront

### 7.7 Package Monitoring

#### `monitoring/collector.py` (301 lignes)
- **Point positif** : Thread-safe avec RLock
- **Point positif** : Sliding window à 500 points avec percentiles (p50, p95, p99)
- **Issue** : `Deque(maxlen=500)` — hardcodé, pas configurable

#### `monitoring/health.py` (264 lignes)
- **Point positif** : Pattern registry pour les health checks avec `enregistrer_verification()`
- **Issue** : Les health checks sont synchrones — `_verifier_db()` peut bloquer longtemps

### 7.8 Package Models (20 fichiers, ~4 600 LoC)

#### Points positifs globaux
- `Mapped[T]` + `mapped_column()` SQLAlchemy 2.0 partout
- `CheckConstraint` systématiques (quantités positives, notes valides, dates cohérentes)
- `CASCADE` / `SET NULL` sur les `ForeignKey` selon la sémantique
- `index=True` sur les colonnes fréquemment filtrées
- `__repr__` défini sur tous les modèles

#### Issues globales
- **Nommage EN/FR** incohérent (voir §4.6)
- **Pas de `__table_args__` systématique** — certains modèles n'ont pas de contraintes CHECK même quand c'est pertinent (ex: `HealthEntry.note_energie` a une contrainte, mais `WellbeingEntry.sleep_hours` non)
- **Properties avec lazy load** — `Equipe.forme_recente`, `UserProfile.streak_jours` déclenchent des SELECT implicites
- **Modèles "jardin" dupliqués** — `GardenItem`/`GardenLog` dans `maison.py` et `ZoneJardin`/`PlanteJardin` dans `temps_entretien.py` couvrent le même domaine

### 7.9 Packages Validation, Observability, Resilience, Query, Date Utils

#### `validation/sanitizer.py` (~230 lignes)
- **Point positif** : `nettoyer_dictionnaire()` selon un schéma — flexible
- **Issue** : Patterns XSS et SQL sont des listes de chaînes compilées à chaque appel — devrait utiliser `re.compile()`

#### `observability/context.py` (243 lignes)
- **Point positif** : `contextvars.ContextVar` — thread-safe ET async-safe
- **Point positif** : Propagation hiérarchique avec `creer_enfant()`

#### `resilience/policies.py` (~340 lignes)
- **Point positif** : Composition élégante via `+`
- **Issue** : `TimeoutPolicy` crée un thread pool par appel (voir §5.1)

#### `query/builder.py` (444 lignes)
- **Point positif** : API fluent très expressive (`.et()`, `.contient()`, `.entre()`, `.paginer()`)
- **Issue** : `supprimer()` charge toutes les entités en mémoire (voir §5.3)
- **Issue** : Les attributs de colonnes invalides sont ignorés silencieusement (`getattr(self.model, col_name, None)`)

#### `date_utils/` (5 fichiers, ~370 lignes)
- **Point positif** : Fonctions pures, bien testables, pas de dépendances externes
- **Issue** : `formatage.py` importe depuis `src.core.constants` (import absolu) — devrait être relatif pour cohérence

---

## 8. Lacunes de couverture de test

### 8.1 Packages insuffisamment testés (estimation)

| Package | Estimation couverture | Raison |
|---------|----------------------|--------|
| `resilience/` | Faible | Package récent, patterns complexes (timeout, bulkhead) difficiles à tester |
| `middleware/` | Faible | Pipeline + middlewares composés, pas de tests visibles dans test_output |
| `observability/` | Faible | `contextvars` testing nécessite des setups spécifiques |
| `query/` | Faible | Query builder nécessite une DB de test avec des fixtures |
| `monitoring/` | Moyenne | Metrics collectées en mémoire — testable mais nécessite timing assertions |

### 8.2 Scénarios de test manquants identifiés

1. **Circuit breaker state transitions** : FERME → OUVERT → SEMI_OUVERT → FERME avec timing
2. **Cache multi-niveaux cascade** : L1 miss → L2 miss → L3 hit → promotion vers L1
3. **Container scope lifecycle** : SESSION scope cleanup à la fin de request
4. **Resilience policy composition** : `RetryPolicy(3) + TimeoutPolicy(5)` avec timeout pendant un retry
5. **Concurrent cache access** : Deux threads écrivent la même clé simultanément (race condition dans `CacheMultiNiveau.obtenir_ou_calculer`)
6. **Migration checksum mismatch** : Que se passe-t-il si un fichier SQL est modifié après application ?
7. **Query builder edge cases** : Colonnes inexistantes, types incompatibles dans `.entre()`, pagination page 0
8. **Sanitizer bypass** : Tests de contournement XSS (double encoding, unicode normalization)
9. **Result monad error propagation** : `and_then()` chain avec erreurs intermédiaires
10. **Health check timeouts** : `_verifier_db()` quand la DB est injoignable (timeout handling)

### 8.3 Patterns testables mais non-testés

- `UnitOfWork` avec rollback automatique sur exception
- `Requete[T].supprimer()` bulk vs unitaire
- `RouteurOptimise.charger_module()` avec module manquant
- `ValidateurConfiguration` avec config partielle
- `FiltreSecrets` avec patterns edge cases (URL sans mot de passe, Bearer sans espace)

---

## 9. Résumé des métriques

### 9.1 Statistiques générales

| Métrique | Valeur |
|----------|--------|
| Fichiers Python | 89 |
| Lignes de code totales | ~14 500 |
| Packages | 13 |
| Classes | ~120+ |
| Enums | ~25 |
| Fonctions/méthodes publiques | ~400+ |
| Design patterns implémentés | 14 |

### 9.2 Top 10 issues par impact

| # | Issue | Impact | Effort fix |
|---|-------|--------|------------|
| 1 | Double gestion d'erreurs (decorators vs errors) | Confusion développeur | Moyen |
| 2 | Couplage Streamlit dans modules purs | Testabilité réduite | Faible |
| 3 | `Requete.supprimer()` charge tout en mémoire | Performance critique sur gros volumes | Faible |
| 4 | Pickle cache L3 (sécurité) | Exécution de code si .cache exposé | Moyen |
| 5 | OAuth tokens en clair en DB | Sécurité | Élevé |
| 6 | N+1 queries sur `Equipe.forme_recente` | Performance DB | Moyen |
| 7 | TimeoutPolicy crée un pool par appel | Performance threads | Faible |
| 8 | Nommage EN/FR incohérent dans models | Maintenabilité | Élevé (migration) |
| 9 | Classes static-only non-injectables | Testabilité | Moyen |
| 10 | Regex XSS/SQL non-compilées | Performance validation | Très faible |

### 9.3 Santé architecturale

```
Architecture      : ████████░░ 8/10  — Excellente modularité, bons abstractions
Code Quality      : ███████░░░ 7/10  — Bon typage, documentation FR, quelques dualités
Design Patterns   : █████████░ 9/10  — Riche et bien implémentés
Performance       : ██████░░░░ 6/10  — N+1 queries, bulk delete, thread pool wastage
Security          : ██████░░░░ 6/10  — XSS/SQL log-only, pickle cache, tokens en clair
Testability       : ██████░░░░ 6/10  — Storage protocol OK, mais static classes problématiques
Maintainability   : ███████░░░ 7/10  — Lazy loading excellent, quelques god files
```

---

*Rapport généré par analyse statique exhaustive des 89 fichiers Python de `src/core/`.  
Prochaines étapes recommandées : Prioriser les issues #1-#4 du tableau §9.2 pour un impact maximum avec effort minimal.*
