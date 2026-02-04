# 📋 PLAN MERGER PHASES 1-2 - Structure Organisée

**Après réorganisation tests/modules/ → tests/domains/**

---

## 🎯 Phases 1-2: Structure d'Intégration

### Phase 1: Services Coverage (141 tests)

```
Destination: tests/services/

Fichiers à créer:
├── test_phase1_recettes.py          (35 tests - recettes service)
├── test_phase1_courses.py           (28 tests - courses service)
├── test_phase1_planning.py          (24 tests - planning service)
├── test_phase1_inventaire.py        (18 tests - inventaire service)
└── test_phase1_barcode.py           (12 tests - barcode service)

Total: 141 tests
Impact: Améliorer couverture services (actuellement ~40-60%)
```

### Phase 2: Domains Coverage (91 tests)

```
Destination: tests/domains/

Fichiers à créer:
├── test_phase2_cuisine.py           (30 tests - domain cuisine)
├── test_phase2_famille.py           (28 tests - domain famille)
└── test_phase2_planning_domain.py   (33 tests - domain planning)

Total: 91 tests
Impact: Améliorer couverture domains (actuellement ~30-40%)
```

### Total: 232 tests

```
- Phase 1 (141) → tests/services/
- Phase 2 (91) → tests/domains/
- Tous 100% PASSED ✓
```

---

## 📊 Couverture Estimée Après Merger

### Avant Phases 1-2

```
Core:      65%    (1800/6026)
Services:  ~40%   (À mesurer avec phases)
Domains:   ~30%   (67 tests réorganisés)
Global:    ~50%   (Estimé)
```

### Après Phases 1-2

```
Core:      65%    (stable - no changes)
Services:  ~65%   (+141 tests = +20-25%)
Domains:   ~70%   (67 existing + 91 new = +30-40%)
Global:    ~75-80% (OBJECTIF ATTEINT ✓)
```

---

## 🚀 Action Immédiate

### Étape 1: Créer fichiers phases 1-2 dans bonne structure

```bash
# Phase 1 → tests/services/
touch tests/services/test_phase1_recettes.py
touch tests/services/test_phase1_courses.py
touch tests/services/test_phase1_planning.py
touch tests/services/test_phase1_inventaire.py
touch tests/services/test_phase1_barcode.py

# Phase 2 → tests/domains/
touch tests/domains/test_phase2_cuisine.py
touch tests/domains/test_phase2_famille.py
touch tests/domains/test_phase2_planning_domain.py
```

### Étape 2: Copier contenu tests (141 + 91 tests)

```
Récupérer tests générés phases 1-2
Les placer dans les fichiers ci-dessus
Respecter structure pytest (classes TestXXX, fonctions test_xxx)
```

### Étape 3: Valider tous les tests

```bash
pytest tests/services/test_phase1_*.py -q --tb=no
pytest tests/domains/test_phase2_*.py -q --tb=no
# Vérifier: 141 + 91 = 232 PASSED ✓
```

### Étape 4: Mesurer couverture complète

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
# Vérifier: global >= 80% ✓
```

---

## ✅ Structure Finale Après Merger

```
tests/
├── core/
│   ├── test_*.py              (791 PASSED)
│   └── ...
├── services/
│   ├── test_*.py              (existants)
│   ├── test_phase1_recettes.py    (35 NEW)
│   ├── test_phase1_courses.py     (28 NEW)
│   ├── test_phase1_planning.py    (24 NEW)
│   ├── test_phase1_inventaire.py  (18 NEW)
│   └── test_phase1_barcode.py     (12 NEW)
├── domains/
│   ├── cuisine/
│   │   └── test_*.py          (existants)
│   ├── famille/
│   │   └── test_*.py          (existants)
│   ├── planning/
│   │   └── test_*.py          (existants)
│   ├── test_modules_*.py      (67 réorganisés ✓)
│   ├── test_phase2_cuisine.py     (30 NEW)
│   ├── test_phase2_famille.py     (28 NEW)
│   └── test_phase2_planning_domain.py (33 NEW)
├── ui/
├── api/
├── integration/
├── e2e/
└── ...
```

---

## 🎯 Commandes Finales

```bash
# Après avoir créé les fichiers phases 1-2:

# 1. Valider phases 1-2 seuls
pytest tests/services/test_phase1_*.py tests/domains/test_phase2_*.py -q

# 2. Mesurer couverture complète
pytest tests/ --cov=src --cov-report=term-missing -q

# 3. Vérifier objectif
# Expected: >= 80% coverage
```

---

## 📋 Checklist

- [ ] Créer fichiers phases 1-2 dans bonne structure
- [ ] Copier/coller contenu tests (232 tests)
- [ ] Valider: 232 tests PASSED
- [ ] Mesurer couverture: >= 80%
- [ ] Générer rapport final
- [ ] Documenter décision structure

---

**Status**: ✅ Plan prêt - Attend tests contenus phases 1-2 🚀
