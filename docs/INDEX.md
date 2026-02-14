# 📚 Documentation Index - MaTanne v2

## 🎯 Documents Essentiels

| Fichier | Description |
|---------|-------------|
| **README.md** | Documentation principale du projet |
| **ROADMAP.md** | Plan de développement & roadmap |
| **[API_REFERENCE.md](./API_REFERENCE.md)** | **Référence complète de l'API REST** |
| **[SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md)** | **Documentation des services backend** |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Architecture technique |
| **[FONCTIONNALITES.md](./FONCTIONNALITES.md)** | Fonctionnalités détaillées |
| **[SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md)** | Guide sessions DB |

## 📁 Structure des Dossiers

### `/docs/` - Documentation Complète
```
docs/
├── INDEX.md                          ← Vous êtes ici
├── ARCHITECTURE.md                   ← Architecture technique
├── API_REFERENCE.md                  ← Documentation API REST (NEW!)
├── SERVICES_REFERENCE.md             ← Documentation Services (NEW!)
├── FONCTIONNALITES.md                ← Fonctionnalités
├── SQLALCHEMY_SESSION_GUIDE.md       ← Guide sessions DB
├── ERD_SCHEMA.md                     ← Schéma ERD
├── reports/                          ← Rapports d'analyse
│   ├── ANALYSIS_SUMMARY.json
│   ├── COVERAGE_REPORT.md
│   └── coverage.json
└── archive/                          ← Anciens documents (archivés)
```

### `/tools/` - Scripts & Outils
```
tools/
├── analyze_coverage.py               ← Analyser couverture
├── analyze_tests.py                  ← Analyser tests
├── measure_coverage.py               ← Mesurer couverture (ACTIF!)
├── deploy_supabase.py                ← Déployer Supabase
├── migrate_supabase.py               ← Migrer Supabase
├── seed_recettes.py                  ← Remplir BD recettes
└── *.ps1                             ← Scripts PowerShell
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
- ✅ Tests réorganisés dans `tests/phases/`
- ✅ Imports corrigés (3-level parent path)
- ✅ Documentation complète
- ✅ Outils centralisés
- ✅ Racine propre!

## 📌 Fichiers par Catégorie

### 🔧 Configuration (Racine)
- `pyproject.toml` - Dépendances Poetry
- `requirements.txt` - Dépendances pip
- `poetry.lock` - Lock file
- `alembic.ini` - Config migrations
- `.env.local` - Config locale
- `.env.example` - Template config
- `.gitignore` - Git ignore rules

### 🏗️ Infrastructure (Racine)
- `manage.py` - CLI manager
- `alembic/` - Migrations Alembic
- `src/` - Code source
- `tests/` - Tests (restructurés!)
- `scripts/` - Scripts utilities
- `backups/` - Backups BD

### 📚 Documentation (docs/)
- `ARCHITECTURE.md` - Architecture technique
- `reports/` - Rapports d'analyse
- `archive/` - Docs archivées

### 🔨 Outils (tools/)
- Scripts Python (11 fichiers)
- Scripts PowerShell (2 fichiers)
- Logs (*.log)

### 📊 Données (data/)
- `recettes_standard.json` - Recettes
- `TEMPLATE_IMPORT.csv` - Template
- `tests_new.txt` - Liste tests

## ✨ Nettoyage Effectué

✅ **Avant:** 70+ fichiers à la racine (bordel!)  
✅ **Après:** ~20 fichiers essentiels à la racine (PROPRE!)

### Déplacements:
- 11 scripts Python → `tools/`
- 2 scripts PowerShell → `tools/`
- 8 rapports/analyses → `docs/reports/`
- 13 docs anciennes → `docs/archive/`
- 2 templates/data → `data/`
- Logs → `tools/`
- PDFs → `docs/`

### Gains:
- 📁 Racine: **70 → 20 fichiers** (-71%)
- 🎯 Clarté: Structure logique & claire
- 🔍 Découverte: Facile de trouver ce qu'on cherche
- 📊 Maintenabilité: ++

## 🎯 Prochaines Étapes

### Immédiat
```bash
# 1. Mesurer couverture réelle
python tools/measure_coverage.py 40

# 2. Vérifier résultats
cat docs/reports/coverage.json
```

### Court Terme
```bash
# 3. Si <40%: Identifier gaps
grep -l "0%" docs/reports/coverage.json

# 4. Phase 4 si nécessaire
pytest tests/phases/ --cov=src -v
```

## 📞 Support

**Fichiers clés pour comprendre le projet:**
1. `/docs/ARCHITECTURE.md` - Architecture générale
2. `/README.md` - Documentation principale
3. `/ROADMAP.md` - Plan de développement
4. `/RESULTAT_FINAL_PHASE3.md` - Derniers résultats

**Pour exécuter des tests:**
- Voir `tools/measure_coverage.py` pour couverture
- Voir `README.md` pour commands pytest

**Pour trouver des rapports:**
- Tous dans `docs/reports/`
- Anciens docs dans `docs/archive/`

---

**Dernière mise à jour:** 29 Janvier 2026  
**État:** ✅ Structure complètement réorganisée et nettoyée!
