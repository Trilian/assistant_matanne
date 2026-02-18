# 🔄 Guide de Migration — Core Packages

## Résumé

Le module `src/core/` a été réorganisé en **5 sous-packages modulaires** pour améliorer la maintenabilité et la séparation des responsabilités. Les anciens fichiers monolithiques sont conservés comme **shims de rétrocompatibilité** — aucun changement n'est requis immédiatement.

## Tableau de migration

| Ancien import (déprécié, toujours supporté) | Nouvel import (recommandé) |
|---------------------------------------------|----------------------------|
| `from src.core.config import obtenir_parametres` | `from src.core.config import obtenir_parametres` *(inchangé)* |
| `from src.core.database import obtenir_moteur` | `from src.core.db import obtenir_moteur` |
| `from src.core.database import get_db_context` | `from src.core.db import obtenir_contexte_db` |
| `from src.core.database import obtenir_fabrique_session` | `from src.core.db import obtenir_fabrique_session` |
| `from src.core.database import GestionnaireMigrations` | `from src.core.db import GestionnaireMigrations` |
| `from src.core.database import verifier_connexion` | `from src.core.db import verifier_connexion` |
| `from src.core.cache_multi import CacheMultiNiveau` | `from src.core.caching import CacheMultiNiveau` |
| `from src.core.cache_multi import avec_cache_multi` | `from src.core.caching import avec_cache_multi` |
| `from src.core.cache_multi import obtenir_cache` | `from src.core.caching import obtenir_cache` |
| `from src.core.performance import ProfileurFonction` | `from src.core.monitoring import ProfileurFonction` |
| `from src.core.performance import MoniteurMemoire` | `from src.core.monitoring import MoniteurMemoire` |
| `from src.core.performance import OptimiseurSQL` | `from src.core.monitoring import OptimiseurSQL` |
| `from src.core.performance import profiler` | `from src.core.monitoring import profiler` |
| *(pas de changement)* `from src.core.validation import ...` | `from src.core.validation import ...` |

## Structure des nouveaux packages

### config/ — Configuration centralisée
```
src/core/config/
├── __init__.py     # Re-exports: obtenir_parametres, Parametres, ...
├── settings.py     # Classe Parametres (Pydantic BaseSettings)
└── loader.py       # Chargement .env, secrets Streamlit, détection cloud
```

### db/ — Base de données
```
src/core/db/
├── __init__.py     # Re-exports + alias get_db_context
├── engine.py       # obtenir_moteur(), obtenir_moteur_securise(), QueuePool
├── session.py      # obtenir_fabrique_session(), obtenir_contexte_db()
├── migrations.py   # GestionnaireMigrations
└── utils.py        # verifier_connexion(), obtenir_infos_db(), vacuum_database()
```

### caching/ — Cache multi-niveaux
```
src/core/caching/
├── __init__.py      # Re-exports + alias: cache, cached, get_cache
├── base.py          # EntreeCache, StatistiquesCache (types)
├── memory.py        # CacheMemoireN1 (L1: dict Python)
├── session.py       # CacheSessionN2 (L2: st.session_state)
├── file.py          # CacheFichierN3 (L3: pickle sur disque)
└── orchestrator.py  # CacheMultiNiveau, avec_cache_multi(), obtenir_cache()
```

### validation/ — Validation & sanitization
```
src/core/validation/
├── __init__.py     # Re-exports complets
├── schemas.py      # Modèles Pydantic (RecetteInput, IngredientInput, etc.)
├── sanitizer.py    # NettoyeurEntrees, InputSanitizer (anti-XSS/injection SQL)
└── validators.py   # valider_modele(), valider_entree(), afficher_erreurs_validation()
```

### monitoring/ — Métriques & performance
```
src/core/monitoring/
├── __init__.py     # Re-exports complets
├── profiler.py     # ProfileurFonction, @profiler, @mesurer_temps, @antirrebond
├── memory.py       # MoniteurMemoire (suivi RAM, objets, garbage collector)
├── sql.py          # OptimiseurSQL, suivre_requete (tracking requêtes lentes)
└── dashboard.py    # TableauBordPerformance (UI Streamlit de métriques)
```

## Rate Limiting — Source de vérité unifiée

Avant : deux implémentations coexistaient (`LimiteDebit` dans `cache.py` et `RateLimitIA` dans `ai/rate_limit.py`).

**Maintenant** : `RateLimitIA` est la **source de vérité unique**. `LimiteDebit` dans `cache.py` est un wrapper léger qui délègue à `RateLimitIA` via lazy import.

```python
# Source de vérité
from src.core.ai import RateLimitIA

# Alias (délègue à RateLimitIA)
from src.core.cache import LimiteDebit
from src.core import LimiteDebit  # Aussi disponible

# Les deux fonctionnent de manière identique
RateLimitIA.peut_appeler()
LimiteDebit.peut_appeler()
```

## Fichiers shims (rétrocompatibilité)

| Shim | Redirige vers | Note |
|------|---------------|------|
| `src/core/database.py` | `src/core/db/` | Inclut `import streamlit as st` pour les mocks de test |
| `src/core/cache_multi.py` | `src/core/caching/` | Re-export complet + alias `cached` |
| `src/core/performance.py` | `src/core/monitoring/` | Re-export complet |
| `src/core/config.py` → package | `src/core/config/` | Devenu un package (pas de shim nécessaire) |

## Impacts sur les tests

### Mocking avec `unittest.mock.patch`

**Important** : quand un test mocke un symbole `src.core.*`, le chemin de patch doit pointer vers le **sous-module où le symbole est utilisé**, pas le shim.

```python
# ❌ Ne fonctionne pas (patch le shim, pas le module réel)
@patch("src.core.database.obtenir_moteur")

# ✅ Correct (patch le sous-module source)
@patch("src.core.db.engine.obtenir_moteur")

# ❌ Ne fonctionne pas
@patch("src.core.performance.st")

# ✅ Correct
@patch("src.core.monitoring.profiler.st")
```

### Correspondances de mock paths

| Ancien mock path | Nouveau mock path |
|------------------|-------------------|
| `src.core.database.obtenir_moteur` | `src.core.db.engine.obtenir_moteur` |
| `src.core.database.obtenir_fabrique_session` | `src.core.db.session.obtenir_fabrique_session` |
| `src.core.database.obtenir_contexte_db` | `src.core.db.session.obtenir_contexte_db` |
| `src.core.database.GestionnaireMigrations` | `src.core.db.migrations.GestionnaireMigrations` |
| `src.core.database.create_engine` | `src.core.db.engine.create_engine` |
| `src.core.database.st` | `src.core.db.engine.st` ou `src.core.db.utils.st` |
| `src.core.config._read_st_secret` | `src.core.config.settings._read_st_secret` |
| `src.core.config._reload_env_files` | `src.core.config.settings._reload_env_files` |
| `src.core.config.configure_logging` | `src.core.logging.configure_logging` |
| `src.core.performance.ProfileurFonction` | `src.core.monitoring.profiler.ProfileurFonction` |
| `src.core.performance.st` | `src.core.monitoring.{profiler,memory,sql,dashboard}.st` |

## Notes de migration progressive

1. **Aucun changement requis** immédiatement — les shims garantissent la rétrocompatibilité
2. **Nouveaux fichiers/modules** : préférer les imports depuis les sous-packages (`src.core.db`, `src.core.caching`, etc.)
3. **Tests** : les mock paths doivent cibler les sous-modules (voir tableau ci-dessus)
4. **Migration optionnelle** : remplacer les anciens imports au fur et à mesure des modifications de fichiers
