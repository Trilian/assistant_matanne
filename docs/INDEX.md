# 📚 Documentation Index - MaTanne v2

> **Dernière mise à jour**: 26 Février 2026

## 🎯 Documents Essentiels

| Fichier                                                          | Description                            |
| ---------------------------------------------------------------- | -------------------------------------- |
| **README.md**                                                    | Documentation principale du projet     |
| **[GUIDE_UTILISATEUR.md](./GUIDE_UTILISATEUR.md)**               | **Guide utilisateur complet**          |
| **ROADMAP.md**                                                   | Plan de développement & roadmap        |
| **[API_REFERENCE.md](./API_REFERENCE.md)**                       | **Référence complète de l'API REST**   |
| **[SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md)**             | **Documentation des services backend** |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)**                         | Architecture technique                 |
| **[MIGRATION_CORE_PACKAGES.md](./MIGRATION_CORE_PACKAGES.md)**   | **Guide migration imports core**       |
| **[FONCTIONNALITES.md](./FONCTIONNALITES.md)**                   | Fonctionnalités détaillées             |
| **[SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md)** | Guide sessions DB                      |
| **[ERD_SCHEMA.md](./ERD_SCHEMA.md)**                             | Schéma entité-relation                 |
| **[UI_COMPONENTS.md](./UI_COMPONENTS.md)**                       | Composants UI Streamlit                |

## 📁 Structure des Dossiers

### `/docs/` - Documentation Complète

```text
docs/
├── INDEX.md                          ← Vous êtes ici
├── GUIDE_UTILISATEUR.md              ← Guide utilisateur complet
├── ARCHITECTURE.md                   ← Architecture technique
├── API_REFERENCE.md                  ← Documentation API REST
├── SERVICES_REFERENCE.md             ← Documentation Services
├── MIGRATION_CORE_PACKAGES.md        ← Guide migration imports core
├── FONCTIONNALITES.md                ← Fonctionnalités
├── SQLALCHEMY_SESSION_GUIDE.md       ← Guide sessions DB
├── ERD_SCHEMA.md                     ← Schéma ERD
├── UI_COMPONENTS.md                  ← Composants UI
├── PLAN_DIVISION_FICHIERS.md         ← Plan de découpage
└── SERVICES_RESTRUCTURATION.md       ← Historique restructuration services
```

### `/scripts/` - Scripts & Outils

```text
scripts/
├── __init__.py                       ← Package Python
├── db/                               ← Opérations base de données
│   ├── deploy_supabase.py           ← Déployer schéma SQL
│   ├── import_recettes.py           ← Import recettes JSON
│   ├── init_db.py                   ← Initialisation BD
│   ├── reset_supabase.py            ← Reset complet Supabase
│   └── seed_data.py                 ← Données démo
├── test/                            ← Outils de test
│   ├── audit_tests.py               ← Audit couverture
│   ├── audit_tests_fast.py          ← Audit rapide
│   ├── generate_skeletons.py        ← Générer tests
│   ├── summary_tests.py             ← Résumé couverture
│   └── test_manager.py              ← Gestionnaire tests
├── analysis/                        ← Analyse de code
│   └── analyze_api.py               ← Analyser API
├── setup/                           ← Configuration
│   ├── convert_utf8.py              ← Fix encodage
│   ├── generate_vapid.py            ← Clés VAPID
│   ├── setup_api_key.py             ← Config API Football
│   └── setup_jeux.py                ← Setup module Jeux
├── fix_encoding.py                  ← Script fix encoding (pre-commit hook)
├── convert_to_utf8.py               ← Conversion batch UTF-8
└── run_api.py                       ← Lancer l'API FastAPI
```

## 🚀 Démarrage rapide

### Lancer l'application

```bash
streamlit run src/app.py
```

### Lancer l'API REST

```bash
uvicorn src.api.main:app --reload --port 8000
# Documentation: http://localhost:8000/docs
```

### Tests

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

### Phase 3 (Complète ✅)

- **Tests créés:** 170 (P1: 51, P2: 36, P3: 83)
- **Tests passants:** 158/164 (96.3%)
- **Couverture phase:** 11.06%
- **Couverture estimée:** 33-35%
- **Direction:** 40% ✅

### Structure Finale

- ✅ Tests organisés dans `tests/` (core, modules, services, api, e2e)
- ✅ Documentation maintenue à jour dans `docs/`
- ✅ Outils centralisés dans `scripts/`
- ✅ Racine propre

## 📌 Fichiers par Catégorie

### 🔧 Configuration (Racine)

- `pyproject.toml` - Dépendances Poetry
- `requirements.txt` - Dépendances pip
- `alembic.ini` - Config migrations
- `pytest.ini` - Config pytest
- `.env.local` - Config locale
- `.gitignore` - Git ignore rules
- `.pre-commit-config.yaml` - Hooks pre-commit

### 🏗️ Infrastructure (Racine)

- `manage.py` - CLI manager
- `alembic/` - Migrations Alembic
- `src/` - Code source
- `tests/` - Tests
- `scripts/` - Scripts utilitaires
- `backups/` - Backups BD

### 📚 Documentation (docs/)

| Fichier                       | Contenu                                          |
| ----------------------------- | ------------------------------------------------ |
| `GUIDE_UTILISATEUR.md`        | Guide utilisateur complet (tous les modules)     |
| `ARCHITECTURE.md`             | Architecture technique (core, services, modules) |
| `API_REFERENCE.md`            | Référence API REST FastAPI                       |
| `SERVICES_REFERENCE.md`       | Documentation services backend                   |
| `MIGRATION_CORE_PACKAGES.md`  | Guide migration imports core                     |
| `FONCTIONNALITES.md`          | Fonctionnalités détaillées                       |
| `SQLALCHEMY_SESSION_GUIDE.md` | Guide sessions DB                                |
| `ERD_SCHEMA.md`               | Schéma entité-relation                           |
| `UI_COMPONENTS.md`            | Composants UI Streamlit                          |

### 📊 Données (data/)

- `recettes_standard.json` - Recettes de base
- `entretien_catalogue.json` - Catalogue entretien maison
- `plantes_catalogue.json` - Catalogue plantes jardin
- `TEMPLATE_IMPORT.csv` - Template import
- `parisSportifs - Recapitulatif.csv` - Données paris

## ✨ Nettoyage Effectué

✅ **Avant:** 70+ fichiers à la racine (bordel!)  
✅ **Après:** ~20 fichiers essentiels à la racine (PROPRE!)

### Déplacements

- 11 scripts Python → `tools/`
- 2 scripts PowerShell → `tools/`
- 8 rapports/analyses → `docs/reports/`
- 13 docs anciennes → `docs/archive/`
- 2 templates/data → `data/`
- Logs → `tools/`
- PDFs → `docs/`

### Gains

- 📁 Racine: **70 → 20 fichiers** (-71%)
- 🎯 Clarté: Structure logique & claire
- 🔍 Découverte: Facile de trouver ce qu'on cherche
- 📊 Maintenabilité: ++

## 🎯 Prochaines Étapes

### Tests

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html

# Tests core uniquement
pytest tests/core/ -v

# Tests modules
pytest tests/modules/ -v
```

## 📞 Support

**Fichiers clés pour comprendre le projet:**

1. `/docs/ARCHITECTURE.md` - Architecture générale (core, services, modules)
2. `/docs/MIGRATION_CORE_PACKAGES.md` - Guide de migration des imports core
3. `/README.md` - Documentation principale
4. `/.github/copilot-instructions.md` - Instructions Copilot (workflow, conventions)
5. `/ROADMAP.md` - Plan de développement

**Structure du core (`src/core/`):**

- 7 sous-packages: `ai/`, `caching/`, `config/`, `date_utils/`, `db/`, `models/`, `validation/`
- Fichiers utilitaires: `constants.py`, `decorators.py`, `errors.py`, `state.py`, `logging.py`
- Marqueur typing: `py.typed` (PEP 561)

---

**Dernière mise à jour:** 19 Février 2026  
**État:** ✅ Documentation à jour après refactoring core (date_utils, schemas, caching)
