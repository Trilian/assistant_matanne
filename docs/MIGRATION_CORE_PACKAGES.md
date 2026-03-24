# 🔄 Guide de Migration — Core Packages

> **⚠️ Référence historique** — Ce document retrace la migration des imports core. Le frontend est désormais Next.js.

> **Dernière mise à jour**: 19 Février 2026

## Résumé

Le module `src/core/` a été réorganisé en **7 sous-packages modulaires** pour améliorer la maintenabilité et la séparation des responsabilités. Les anciens fichiers shims de rétrocompatibilité (`database.py`, `cache_multi.py`, `performance.py`) ont été **supprimés** — tous les imports doivent utiliser les nouveaux sous-packages.

## Tableau de migration

| Ancien import (déprécié)                                        | Nouvel import (requis)                                                               |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `from src.core.config import obtenir_parametres`                | `from src.core.config import obtenir_parametres` _(inchangé)_                        |
| `from src.core.config import _get_mistral_api_key_from_secrets` | `from src.core.config.loader import _get_mistral_api_key_from_secrets`               |
| `from src.core.database import obtenir_moteur`                  | `from src.core.db import obtenir_moteur`                                             |
| `from src.core.database import obtenir_contexte_db`             | `from src.core.db import obtenir_contexte_db`                                        |
| `from src.core.database import obtenir_fabrique_session`        | `from src.core.db import obtenir_fabrique_session`                                   |
| `from src.core.database import GestionnaireMigrations`          | `from src.core.db import GestionnaireMigrations`                                     |
| `from src.core.database import verifier_connexion`              | `from src.core.db import verifier_connexion`                                         |
| `from src.core.cache_multi import CacheMultiNiveau`             | `from src.core.caching import CacheMultiNiveau`                                      |
| `from src.core.cache_multi import avec_cache_multi`             | `from src.core.caching import avec_cache_multi`                                      |
| `from src.core.cache_multi import obtenir_cache`                | `from src.core.caching import obtenir_cache`                                         |
| `from src.core.caching import clear_all`                        | _(supprimé — utiliser `cache.clear()` directement)_                                  |
| `from src.core.models.base import obtenir_valeurs_enum`         | _(supprimé — code mort)_                                                             |
| `from src.core.date_utils import ...` (fichier)                 | `from src.core.date_utils import ...` _(même API, package interne)_                  |
| `from src.core.validation.schemas import RecetteInput`          | `from src.core.validation.schemas import RecetteInput` _(même API, package interne)_ |

## Structure des nouveaux packages

### config/ — Configuration centralisée

```
src/core/config/
├── __init__.py     # Re-exports: obtenir_parametres, Parametres, charger_secrets_streamlit
├── settings.py     # Classe Parametres (Pydantic BaseSettings)
└── loader.py       # Chargement .env, secrets Streamlit, détection cloud
```

> **Note**: Les fonctions privées (`_get_mistral_api_key_from_secrets`, etc.) ne sont **pas** re-exportées
> depuis `__init__.py`. Pour les tests, importer depuis `src.core.config.loader` directement.

### db/ — Base de données

```
src/core/db/
├── __init__.py     # Re-exports
├── engine.py       # obtenir_moteur(), obtenir_moteur_securise(), QueuePool
├── session.py      # obtenir_fabrique_session(), obtenir_contexte_db()
├── migrations.py   # GestionnaireMigrations
└── utils.py        # verifier_connexion(), obtenir_infos_db(), vacuum_database()
```

### caching/ — Cache multi-niveaux

```
src/core/caching/
├── __init__.py      # Re-exports
├── base.py          # EntreeCache, StatistiquesCache (types)
├── cache.py         # Cache, cached() — décorateur typé avec ParamSpec
├── memory.py        # CacheMemoireN1 (L1: dict Python)
├── session.py       # CacheSessionN2 (L2: st.session_state)
├── file.py          # CacheFichierN3 (L3: pickle sur disque)
└── orchestrator.py  # CacheMultiNiveau, avec_cache_multi() — typé ParamSpec
```

> **Note**: `clear_all` a été supprimé. Utiliser `cache.clear()` directement sur l'instance.
> Les décorateurs `cached()` et `avec_cache_multi()` utilisent `ParamSpec`/`TypeVar` pour
> préserver les signatures de fonctions dans les outils de typage.

### date_utils/ — Utilitaires de dates (NOUVEAU package)

```
src/core/date_utils/
├── __init__.py     # Re-exports de toutes les fonctions publiques
├── semaines.py     # obtenir_debut_semaine, obtenir_fin_semaine, ...
├── periodes.py     # plage_dates, ajouter_jours_ouvres, obtenir_bornes_mois
├── formatage.py    # formater_date_fr, formater_jour_fr, format_week_label
└── helpers.py      # est_aujourd_hui, est_weekend, get_weekday_index
```

> **Migration**: Transparent — l'ancien `date_utils.py` (429 lignes) a été découpé en
> 4 modules thématiques. Le `__init__.py` ré-exporte tout, donc les imports existants
> (`from src.core.date_utils import ...`) fonctionnent sans changement.

### validation/ — Validation & sanitization

```
src/core/validation/
├── __init__.py     # Re-exports complets
├── schemas/        # NOUVEAU package (remplace l'ancien schemas.py de 501 lignes)
│   ├── __init__.py # Re-exports de tous les schémas
│   ├── recettes.py # RecetteInput, IngredientInput, EtapeInput, SCHEMA_RECETTE
│   ├── inventaire.py # ArticleInventaireInput, IngredientStockInput, SCHEMA_INVENTAIRE
│   ├── courses.py    # ArticleCoursesInput, SCHEMA_COURSES
│   ├── planning.py   # RepasInput
│   ├── famille.py    # EntreeJournalInput, RoutineInput, TacheRoutineInput
│   ├── projets.py    # ProjetInput
│   └── _helpers.py   # nettoyer_texte (utilitaire partagé)
├── sanitizer.py    # NettoyeurEntrees (anti-XSS/injection SQL)
└── validators.py   # valider_modele(), valider_entree(), afficher_erreurs_validation()
```

> **Migration**: Transparent — le `__init__.py` de `schemas/` ré-exporte tout.
> Les imports existants (`from src.core.validation.schemas import RecetteInput`)
> fonctionnent sans changement.

## Rate Limiting — Source de vérité unifiée

`RateLimitIA` dans `src/core/ai/rate_limit.py` est la **source de vérité unique** pour la limitation de débit des appels IA.

```python
from src.core.ai import RateLimitIA

RateLimitIA.peut_appeler()
```

## Fichiers shims (supprimés)

Les fichiers shims suivants ont été **supprimés**. Tous les imports doivent utiliser les sous-packages directement :

| Ancien shim (supprimé)    | Remplacé par           |
| ------------------------- | ---------------------- |
| `src/core/database.py`    | `src/core/db/`         |
| `src/core/cache_multi.py` | `src/core/caching/`    |
| `src/core/performance.py` | `src/core/monitoring/` |

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

| Ancien mock path                                    | Nouveau mock path                                          |
| --------------------------------------------------- | ---------------------------------------------------------- |
| `src.core.database.obtenir_moteur`                  | `src.core.db.engine.obtenir_moteur`                        |
| `src.core.database.obtenir_fabrique_session`        | `src.core.db.session.obtenir_fabrique_session`             |
| `src.core.database.obtenir_contexte_db`             | `src.core.db.session.obtenir_contexte_db`                  |
| `src.core.database.GestionnaireMigrations`          | `src.core.db.migrations.GestionnaireMigrations`            |
| `src.core.database.create_engine`                   | `src.core.db.engine.create_engine`                         |
| `src.core.database.st`                              | `src.core.db.engine.st` ou `src.core.db.utils.st`          |
| `src.core.config._get_mistral_api_key_from_secrets` | `src.core.config.loader._get_mistral_api_key_from_secrets` |
| `src.core.config._read_st_secret`                   | `src.core.config.settings._read_st_secret`                 |
| `src.core.config._reload_env_files`                 | `src.core.config.settings._reload_env_files`               |
| `src.core.config.charger_secrets_streamlit`         | `src.core.config.settings.charger_secrets_streamlit`       |
| `src.core.config.configure_logging`                 | `src.core.logging.configure_logging`                       |
| `src.core.performance.ProfileurFonction`            | `src.core.monitoring.profiler.ProfileurFonction`           |
| `src.core.performance.st`                           | `src.core.monitoring.{profiler,memory,sql,dashboard}.st`   |

## Symboles supprimés

| Symbole                                      | Ancien emplacement         | Raison                                         |
| -------------------------------------------- | -------------------------- | ---------------------------------------------- |
| `clear_all`                                  | `src.core.caching`         | Alias inutilisé — utiliser `cache.clear()`     |
| `obtenir_valeurs_enum`                       | `src.core.models.base`     | Code mort, jamais appelé                       |
| `_get_mistral_api_key_from_secrets` (export) | `src.core.config.__init__` | Fonction privée, importer depuis `loader.py`   |
| `_read_st_secret` (export)                   | `src.core.config.__init__` | Fonction privée, importer depuis `settings.py` |
| `_reload_env_files` (export)                 | `src.core.config.__init__` | Fonction privée, importer depuis `settings.py` |
| `_charger_configuration` (export)            | `src.core.config.__init__` | Fonction privée, importer depuis `settings.py` |

## Notes de migration

1. **Migration terminée** — les anciens shims ont été supprimés, tous les imports utilisent les sous-packages
2. **Imports** : utiliser `src.core.db`, `src.core.caching`, `src.core.monitoring`, etc.
3. **Tests** : les mock paths doivent cibler les sous-modules (voir tableau ci-dessus)
4. **date_utils** et **validation/schemas** : migration transparente via re-exports dans `__init__.py`
5. **py.typed** : marqueur PEP 561 ajouté pour compatibilité avec mypy/pyright
6. **Typage décorateurs** : `cached()` et `avec_cache_multi()` préservent les signatures via `ParamSpec`
