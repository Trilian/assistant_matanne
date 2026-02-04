# 📋 PLAN PHASES 1-2 - Structure Alignée avec src/

**Respecter arborescence src/ dans tests/ - tests transversaux séparés**

---

## 🎯 Structure Correcte à Respecter

### src/ vs tests/

```
src/                          tests/
├── domains/                  ├── domains/
│   ├── cuisine/      ↔      │   ├── cuisine/
│   │   ├── __init__.py       │   │   ├── test_*.py
│   │   └── ...               │   │   ├── test_phase2_recipes.py (NEW)
│   │                         │   │   └── test_phase2_meals.py (NEW)
│   ├── famille/      ↔      │   ├── famille/
│   │   ├── __init__.py       │   │   ├── test_*.py
│   │   └── ...               │   │   ├── test_phase2_profiles.py (NEW)
│   │                         │   │   └── test_phase2_tracking.py (NEW)
│   ├── planning/     ↔      │   ├── planning/
│   │   ├── __init__.py       │   │   ├── test_*.py
│   │   └── ...               │   │   └── test_phase2_events.py (NEW)
│   ├── jeux/         ↔      │   ├── jeux/
│   ├── maison/       ↔      │   ├── maison/
│   └── utils/        ↔      │   └── utils/
│
├── services/                 ├── services/
│   ├── recettes.py   ↔      │   ├── test_recettes_service.py
│   ├── courses.py    ↔      │   ├── test_courses_service.py
│   ├── planning.py   ↔      │   ├── test_planning_service.py
│   ├── inventaire.py ↔      │   ├── test_inventaire_service.py
│   ├── barcode.py    ↔      │   ├── test_barcode_service.py
│   └── ...           ↔      │   ├── test_phase1_recettes.py (NEW)
│                            │   ├── test_phase1_courses.py (NEW)
│                            │   ├── test_phase1_planning.py (NEW)
│                            │   ├── test_phase1_inventaire.py (NEW)
│                            │   └── test_phase1_barcode.py (NEW)
│
├── ui/               ↔      ├── ui/
├── api/              ↔      ├── api/
└── utils/            ↔      └── utils/

Tests Transversaux (HORS STRUCTURE):
                             ├── integration/
                             ├── e2e/
                             ├── edge_cases/
                             └── benchmarks/
```

---

## 📊 Phases 1-2 - Placement Correct

### Phase 1: Services (141 tests)

```
Destination: tests/services/ (root level, pas dans sous-dossiers)

tests/services/
├── test_*.py (existants)
├── test_phase1_recettes.py       (35 tests)
├── test_phase1_courses.py        (28 tests)
├── test_phase1_planning.py       (24 tests)
├── test_phase1_inventaire.py     (18 tests)
└── test_phase1_barcode.py        (12 tests)
```

### Phase 2: Domains (91 tests)

```
Destination: tests/domains/ (dans sous-dossiers correspondants)

tests/domains/cuisine/
├── test_*.py (existants)
├── test_phase2_recipes.py        (15 tests)
└── test_phase2_meals.py          (15 tests)

tests/domains/famille/
├── test_*.py (existants)
├── test_phase2_profiles.py       (14 tests)
└── test_phase2_tracking.py       (14 tests)

tests/domains/planning/
├── test_*.py (existants)
└── test_phase2_events.py         (33 tests)
```

---

## ✅ Règles de Placement

| Fichiers           | Placement                          | Raison                                              |
| ------------------ | ---------------------------------- | --------------------------------------------------- |
| Phase 1 - Services | `tests/services/` (root)           | Services = fichiers directs en src/services/        |
| Phase 2 - Domains  | `tests/domains/{domaine}/`         | Domains = structure hiérarchique avec sous-dossiers |
| Tests transversaux | `tests/integration/`, `tests/e2e/` | Multi-modules, pas alignés 1-1 avec src/            |

---

## 📋 Actions Immédiates

### 1. Créer fichiers Phase 1

```bash
# Dans tests/services/
touch test_phase1_recettes.py       (35 tests)
touch test_phase1_courses.py        (28 tests)
touch test_phase1_planning.py       (24 tests)
touch test_phase1_inventaire.py     (18 tests)
touch test_phase1_barcode.py        (12 tests)
```

### 2. Créer fichiers Phase 2

```bash
# Dans tests/domains/cuisine/
touch test_phase2_recipes.py        (30 tests total)
touch test_phase2_meals.py

# Dans tests/domains/famille/
touch test_phase2_profiles.py       (28 tests total)
touch test_phase2_tracking.py

# Dans tests/domains/planning/
touch test_phase2_events.py         (33 tests)
```

### 3. Remplir les tests

```
Phase 1: Contenu tests services (141 tests)
Phase 2: Contenu tests domaines (91 tests)
```

### 4. Valider

```bash
pytest tests/services/test_phase1_*.py -q        # 141 tests
pytest tests/domains/*/test_phase2_*.py -q       # 91 tests
```

---

## 🎯 Résultat Final

```
✓ Phase 1 dans tests/services/ (141 tests)
✓ Phase 2 dans tests/domains/{domaine}/ (91 tests)
✓ Structure alignée 1-1 avec src/
✓ Tests transversaux séparés (e2e, integration)
✓ Total: 232 tests + 791 existants = 1023 tests
✓ Couverture estimée: 75-80% ✓
```

---

**Status**: ✅ Plan structuré correctement - Prêt pour implémentation 🚀
