# 🔧 CORRECTION ORGANISATION - Consolidation Tests

## 📊 État Actuel

### ✅ Bonne Structure Existante

```
src/domains/                    tests/domains/
├── cuisine/          ↔        ├── cuisine/
├── famille/          ↔        ├── famille/
├── jeux/             ↔        ├── jeux/
├── maison/           ↔        ├── maison/
└── planning/         ↔        └── planning/

src/services/                   tests/services/
├── recettes.py       ↔        ├── test_recettes_service.py
├── courses.py        ↔        ├── test_courses_service.py
├── planning.py       ↔        ├── test_planning_service.py
├── inventaire.py     ↔        ├── test_inventaire_service.py
└── ...               ↔        └── ... (47 fichiers)
```

### ❌ Erreur d'Organisation

```
tests/modules/              ← MAUVAIS (pas de src/modules/)
├── test_85_coverage.py
├── test_extended_modules.py
└── test_simple_extended.py
  (70 tests au total)
```

---

## 🎯 Plan de Consolidation

### Étape 1: Analyser les 70 tests de `tests/modules/`

```python
# À vérifier:
# - test_85_coverage.py      : Tests de couverture - À mettre où?
# - test_extended_modules.py : Tests étendus - De quel domaine?
# - test_simple_extended.py  : Tests simples - De quel domaine?
```

### Étape 2: Réorganiser

**Option A**: Si tests = services génériques

```
tests/modules/ → tests/services/
├── test_services_coverage_85.py
├── test_services_extended.py
└── test_services_simple.py
```

**Option B**: Si tests = domaines (cuisine/famille/planning)

```
tests/modules/ → tests/domains/
├── test_domains_coverage_85.py
├── test_domains_extended.py
└── test_domains_simple.py
```

**Option C**: Si tests = mélange

```
tests/modules/
├── Services → tests/services/test_modules_services.py
├── Domains → tests/domains/test_modules_domains.py
└── E2E → tests/integration/test_modules_e2e.py
```

### Étape 3: Vérifier Couverture

Après réorganisation, mesurer par domaine:

```bash
# Services couverture
pytest tests/services/ --cov=src.services --cov-report=term-missing

# Domains couverture
pytest tests/domains/ --cov=src.domains --cov-report=term-missing

# UI couverture
pytest tests/ui/ --cov=src.ui --cov-report=term-missing

# API couverture
pytest tests/api/ --cov=src.api --cov-report=term-missing

# Global
pytest tests/ --cov=src --cov-report=term-missing (sans e2e/integration)
```

---

## 📋 Recommandation Immédiate

### ✅ CE QUE VOUS FAITES BIEN

```
✓ tests/core/        → src/core/     (65% couverture)
✓ tests/services/    → src/services/ (À mesurer)
✓ tests/domains/     → src/domains/  (À mesurer)
✓ tests/ui/          → src/ui/       (À mesurer)
✓ tests/api/         → src/api/      (À mesurer)
✓ tests/e2e/         → Tests bout-en-bout
✓ tests/integration/ → Tests multi-modules
```

### 🔧 À CORRIGER

```
tests/modules/ (70 tests)
  → À déplacer dans bonne structure
  → Probablement vers tests/services/ ou tests/domains/
```

### 🎯 STRUCTURE FINALE RECOMMANDÉE

```
tests/
├── core/                    ✅ Aligné src/core/
├── services/                ✅ Aligné src/services/
├── domains/                 ✅ Aligné src/domains/
│   ├── cuisine/
│   ├── famille/
│   ├── jeux/
│   ├── maison/
│   ├── planning/
│   └── test_*.py (fichiers domaines globaux)
├── ui/                      ✅ Aligné src/ui/
├── api/                     ✅ Aligné src/api/
├── utils/                   ✅ Aligné src/utils/
├── integration/             ✅ Tests multi-modules
├── e2e/                     ✅ Tests scénarios
├── edge_cases/              ✅ Cas limites
├── benchmarks/              ✅ Performance
├── conftest.py              ✅ Config shared
└── test_*.py (root tests)   ✅ Tests globaux app
```

---

## 🚀 Avant de Merger Phases 1-2

**URGENT**: Clarifier où aller les phases 1-2 tests

**Phases 1-2 = 232 tests**:

- Phase 1: 141 tests services (recettes, courses, planning, inventaire, barcode)
- Phase 2: 91 tests domains (cuisine, famille, planning)

**Donc**:

```
Phase 1 → tests/services/test_phase1_*.py
Phase 2 → tests/domains/test_phase2_*.py
```

**PAS** dans `tests/modules/` (mauvaise structure)

---

## ✅ Checklist

- [ ] Lire les 70 tests de `tests/modules/`
- [ ] Identifier leur destination correcte
- [ ] Déplacer vers `tests/services/` ou `tests/domains/`
- [ ] Supprimer `tests/modules/` vide
- [ ] Vérifier couverture par domaine
- [ ] Merger phases 1-2 dans bonne structure
- [ ] Mesurer couverture finale

---

**Suggestion**: Montrez-moi le contenu de `tests/modules/test_85_coverage.py` pour que je détermine la bonne destination! 📍
