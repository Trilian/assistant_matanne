# 🏠 MaTanne v2 - Quick Navigation

**Bienvenue! Voici ce qu'il faut savoir:**

## 📖 Lire D'Abord

| Document | Quand le lire |
|----------|---------------|
| **[README.md](README.md)** | Pour comprendre le projet |
| **[ROADMAP.md](ROADMAP.md)** | Pour voir le plan |
| **[RESULTAT_FINAL_PHASE3.md](RESULTAT_FINAL_PHASE3.md)** | Pour les derniers résultats ✅ |

## 🎯 Actions Rapides

### Lancer l'App
```bash
streamlit run src/app.py
```

### Exécuter Tests
```bash
# Tous
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html

# Phases seulement
pytest tests/phases/ -v
```

### Mesurer Couverture
```bash
# MAIN TOOL - Mesurer vers 40%
python tools/measure_coverage.py 40

# Via CLI
python manage.py test_coverage
```

## 📁 Structure

```
.
├── README.md                      ← Lire d'abord!
├── ROADMAP.md                     ← Plan projet
├── RESULTAT_FINAL_PHASE3.md       ← Résultats ✅
├── CHECKLIST_FINAL.md             ← Checklist
├── RESTRUCTURATION_TESTS.md       ← Tests structure
├── PHASE3_COMPLETE_REORGANIZED.md ← Phase 3 détails
│
├── manage.py                      ← CLI (run, test, etc)
├── pyproject.toml                 ← Dépendances
├── requirements.txt               ← Pip requirements
│
├── src/                           ← Code source
├── tests/                         ← Tests (réorganisés!)
│   └── phases/                    ← Phase 1, 2, 3 ✨
├── tools/                         ← Scripts & outils (11+)
├── docs/                          ← Documentation
│   ├── ARCHITECTURE.md
│   ├── reports/                   ← Rapports analyses
│   └── archive/                   ← Docs anciennes
├── data/                          ← Données & templates
├── scripts/                       ← Scripts utilitaires
└── ...
```

## 🔨 Outils Disponibles

Tous dans `tools/`:

```bash
# Mesurer couverture (PRINCIPAL)
python tools/measure_coverage.py 40

# Analyser
python tools/analyze_coverage.py
python tools/analyze_tests.py

# Migrations
python tools/migrate_supabase.py
python tools/deploy_supabase.py

# Data
python tools/seed_recettes.py

# Fix issues
python tools/fix_encoding_and_imports.py
```

## 📊 État Couverture

| Métrique | Valeur |
|----------|--------|
| Baseline | 30.18% |
| Phase 1+2+3 | 11.06% (phases only) |
| Estimé final | 33-35% |
| **Cible** | **40%** 🎯 |

## 📚 Documentation Complète

**Voir [docs/INDEX.md](docs/INDEX.md)** pour la navigation complète.

## ✨ Récemment Fait

✅ **Phase 3 créée** - 83 tests edge cases  
✅ **Tests réorganisés** - Structure propre dans `tests/phases/`  
✅ **Imports corrigés** - 3-level parent path  
✅ **Outils centralisés** - Tous dans `tools/`  
✅ **Docs archivées** - Nettoyage racine  
✅ **Reports structurés** - Dans `docs/reports/`  

**Total: 70 fichiers racine → 20 essentiels (-71%!)**

## 🎯 Prochaines Étapes

### 1️⃣ Mesurer Couverture Réelle
```bash
python tools/measure_coverage.py 40
```

### 2️⃣ Vérifier Résultats
```bash
# Voir rapport HTML
start htmlcov/index.html

# Ou JSON
cat docs/reports/coverage.json
```

### 3️⃣ Si <40%: Phase 4
```bash
pytest tests/phases/ --cov=src -v
```

## ❓ Questions Fréquentes

**Où sont les rapports de couverture?**  
→ `docs/reports/` (FINAL_COVERAGE_ANALYSIS.md, coverage.json, etc)

**Où sont les anciens documents?**  
→ `docs/archive/` (archivés mais disponibles)

**Comment utiliser les outils?**  
→ Chaque script a `--help` ou voir inline docstrings

**Où lancer l'app?**  
→ `streamlit run src/app.py` ou `python manage.py run`

**Comment ajouter des tests?**  
→ Ajouter dans `tests/phases/` ou `tests/{domaine}/`

## 📞 Navigation

- 🚀 **Pour démarrer** → [README.md](README.md)
- 📋 **Pour le plan** → [ROADMAP.md](ROADMAP.md)
- ✅ **Résultats finaux** → [RESULTAT_FINAL_PHASE3.md](RESULTAT_FINAL_PHASE3.md)
- 📚 **Docs complètes** → [docs/INDEX.md](docs/INDEX.md)
- 🏗️ **Architecture** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Dernière update:** 29 Jan 2026  
**Phase 3 Status:** ✅ COMPLÈTE  
**Tests:** 170 créés, 158 passants (96.3%)  
**Couverture:** ~33-35% (vers 40% 🎯)
