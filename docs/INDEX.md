# 📚 Documentation Index — MaTanne

> **Dernière mise à jour** : Mars 2026

## 🎯 Documents

| Fichier | Description |
|---|---|
| [README.md](../README.md) | Documentation principale du projet |
| [ROADMAP.md](../ROADMAP.md) | Roadmap et historique des sprints |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Architecture technique (FastAPI + Next.js) |
| [API_REFERENCE.md](./API_REFERENCE.md) | Référence complète de l'API REST |
| [SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md) | Documentation des services backend |
| [FONCTIONNALITES.md](./FONCTIONNALITES.md) | Fonctionnalités détaillées par module |
| [GUIDE_UTILISATEUR.md](./GUIDE_UTILISATEUR.md) | Guide utilisateur complet |
| [ERD_SCHEMA.md](./ERD_SCHEMA.md) | Schéma entité-relation de la DB |
| [SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md) | Guide sessions DB |
| [MIGRATION_CORE_PACKAGES.md](./MIGRATION_CORE_PACKAGES.md) | Guide migration imports core |
| [UI_COMPONENTS.md](./UI_COMPONENTS.md) | Composants UI Next.js / shadcn |
| [PATTERNS.md](./PATTERNS.md) | Patterns de code récurrents |
| [REDIS_SETUP.md](./REDIS_SETUP.md) | Configuration Redis (optionnel) |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Guide de déploiement (local, Docker, Railway, Vercel, Supabase) |

## 📁 Structure

```
docs/
├── INDEX.md                     ← Vous êtes ici
├── ARCHITECTURE.md              ← Architecture technique
├── API_REFERENCE.md             ← Documentation API REST
├── SERVICES_REFERENCE.md        ← Documentation Services
├── FONCTIONNALITES.md           ← Fonctionnalités
├── GUIDE_UTILISATEUR.md         ← Guide utilisateur
├── ERD_SCHEMA.md                ← Schéma ERD
├── SQLALCHEMY_SESSION_GUIDE.md  ← Guide sessions DB
├── MIGRATION_CORE_PACKAGES.md   ← Guide migration imports
├── UI_COMPONENTS.md             ← Composants UI Next.js
├── PATTERNS.md                  ← Patterns de code
├── REDIS_SETUP.md               ← Setup Redis
├── DEPLOYMENT.md                ← Guide déploiement
└── guides/                      ← Guides spécifiques
    ├── cuisine/batch_cooking.md
    ├── famille/README.md
    ├── jeux/README.md
    ├── maison/README.md
    ├── outils/README.md
    ├── planning/README.md
    └── utilitaires/
```

## 🚀 Démarrage rapide

```bash
# Backend FastAPI
python manage.py run              # http://localhost:8000

# Frontend Next.js
cd frontend && npm run dev        # http://localhost:3000

# Tests
python manage.py test_coverage    # Backend (pytest)
cd frontend && npm test           # Frontend (Vitest)
```

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
| `UI_COMPONENTS.md`            | Composants UI (Next.js / shadcn)                 |

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
