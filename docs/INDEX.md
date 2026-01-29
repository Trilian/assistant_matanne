# 📚 Documentation Index - MaTanne v2

## 🎯 Documents Essentiels (Racine)

| Fichier | Description |
|---------|-------------|
| **README.md** | Documentation principale du projet |
| **ROADMAP.md** | Plan de développement & roadmap |
| **CHECKLIST_FINAL.md** | Checklist finale Phase 3 |
| **RESULTAT_FINAL_PHASE3.md** | Résultats complets Phase 3 ✅ |
| **RESTRUCTURATION_TESTS.md** | Guide de restructuration des tests |
| **PHASE3_COMPLETE_REORGANIZED.md** | Phase 3 + réorganisation détails |

## 📁 Structure des Dossiers

### `/docs/` - Documentation Complète
```
docs/
├── INDEX.md                          ← Vous êtes ici
├── ARCHITECTURE.md                   ← Architecture technique
├── reports/                          ← Rapports d'analyse
│   ├── ANALYSIS_SUMMARY.json
│   ├── COVERAGE_REPORT.md
│   ├── FINAL_COVERAGE_ANALYSIS.md
│   ├── TEST_ANALYSIS_DETAILED.md
│   ├── TEST_ANALYSIS_REPORT.json
│   └── coverage.json
└── archive/                          ← Anciens documents (archivés)
    ├── PHASE1_RESULTS.md
    ├── PHASE2_SUITE_COMPLETE.md
    ├── DASHBOARD_FINAL_PHASE12.md
    ├── TESTING_GUIDE.md
    ├── QUICK_COMMANDS.md
    └── ... (13+ fichiers)
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
├── reorganize_tests.py               ← Réorganiser tests
├── run_tests_planning.py             ← Runner planning tests
├── test_manager.py                   ← Manager tests
├── fix_encoding*.py                  ← Fixes encoding
└── *.ps1                             ← Scripts PowerShell
```

### `/data/` - Données & Templates
```
data/
├── recettes_standard.json            ← Recettes standard
├── TEMPLATE_IMPORT.csv               ← Template import
└── tests_new.txt                     ← Test liste
```

## 🚀 Commandes Principales

### Mesurer Couverture (Actif)
```bash
# Depuis la racine
python tools/measure_coverage.py 40

# Via manage.py
python manage.py test_coverage
```

### Exécuter Tests
```bash
# Tous les tests
pytest tests/ -v

# Phases seulement
pytest tests/phases/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

### Outils Disponibles
```bash
# Analyser couverture
python tools/analyze_coverage.py

# Analyser tests
python tools/analyze_tests.py

# Déployer migrations
python tools/migrate_supabase.py

# Seed recettes
python tools/seed_recettes.py
```

## 📊 Derniers Résultats

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
