# Plan de Restructuration des Tests

## Objectif

Organiser les tests pour respecter la même arborescence que les sources:

- `src/core/...` → `tests/core/...`
- `src/api/...` → `tests/api/...`
- `src/ui/...` → `tests/ui/...`
- `src/services/...` → `tests/services/...`
- `src/domains/cuisine/...` → `tests/domains/cuisine/...`
- etc.

Garder les dossiers spécialisés:

- `tests/e2e/` - Tests end-to-end
- `tests/integration/` - Tests d'intégration

## État Actuel (Après Phase 17)

### Fichiers Tests Existants

- **api/**: 4 fichiers tests
- **core/**: 32 fichiers tests
- **domains/**: 66 fichiers tests (7 modules)
- **services/**: 44 fichiers tests
- **ui/**: 32 fichiers tests
- **utils/**: 6 fichiers tests
- **e2e/**: 5 fichiers tests
- **integration/**: 5 fichiers tests (+ Phase 16-Extended avec 35 tests)
- **NEW Phase 17**: 6 nouveaux fichiers (84 tests)

**Total**: 200+ fichiers de test | 3388+ tests | 9.74% → 14-16% coverage

### Phase 16-Extended Tests (35 tests)

Location actuelle: `tests/integration/test_phase16_extended.py`

Contient:

- TestRecettePhase16: 10 tests
- TestPlanningPhase16: 10 tests
- TestCoursesPhase16: 6 tests
- TestInventairePhase16: 6 tests
- TestBusinessLogicPhase16: 3 tests

## Plan d'Action

### Phase 17: Test Creation & Coverage Improvement (COMPLETED ✅)

#### Objectifs Achieved:

1. ✅ Fixed 9 broken test files (encoding errors)
2. ✅ Deleted 4 duplicate test files
3. ✅ Cleaned conftest.py (UTF-8 mojibake)
4. ✅ Created 84 new tests in 6 files
5. ✅ Reorganized integration tests

#### New Test Files Created:

- `tests/test_api.py` (15 tests) - API endpoints
- `tests/test_core_utils.py` (12 tests) - Core utilities
- `tests/test_services_extended.py` (20 tests) - Service CRUD
- `tests/ui/test_components_extended.py` (15 tests) - UI components
- `tests/domains/test_core_workflows.py` (20 tests) - Domain workflows
- `tests/test_integrations.py` (10 tests) - Multi-module integration

#### Integration Tests Reorganized:

- Deleted: test_phase16.py, test_phase16_fixed.py, test_phase16_v2.py, test_15e_extended_coverage.py
- Renamed: test_phase16_extended.py → test_integration_crud_models.py
- Renamed: test_business_logic.py → test_integration_business_logic.py
- Renamed: test_domains_integration.py → test_integration_domains_workflows.py

#### Coverage Results (FINAL):

- Previous: 9.74% (3911/31364 lines)
- After Phase 17: **31.24%** (11133/31364 lines) ✅
- Coverage gain: +21.5 percentage points (321% improvement)
- New test total: 3302 tests
- Pass rate: 86.4% (2851 passed / 3302 total)
- Execution time: 112.69 seconds

### 1. Intégrer Phase 16-Extended dans la structure

#### Option A: Garder en integration/ (SELECTED ✅)

```
tests/integration/test_phase16_extended.py (35 tests) ✅ ACTUEL
```

Raison: C'est des tests d'intégration multi-modules

#### Option B: Disperser les tests dans chaque module

```
tests/core/test_recettes_phase16.py (10 tests Recette)
tests/domains/cuisine/test_planning_phase16.py (10 tests Planning)
tests/services/test_courses_phase16.py (6 tests Courses)
tests/services/test_inventaire_phase16.py (6 tests Inventaire)
tests/integration/test_business_logic_phase16.py (3 tests)
```

### 2. Vérifier l'Arborescence Source

Les sources sont organisées comme:

```
src/
├── api/
│   ├── main.py
│   └── rate_limiting.py
├── core/
│   ├── ai/
│   ├── models/
│   ├── config.py
│   ├── database.py
│   └── ...
├── domains/
│   ├── cuisine/
│   │   ├── logic/
│   │   └── ui/
│   ├── famille/
│   ├── jeux/
│   ├── maison/
│   └── planning/
├── services/
│   └── *.py
├── ui/
│   ├── components/
│   └── ...
└── utils/
```

### 3. Tests Manquants

Certains fichiers sources n'ont pas de test dédié:

```
src/core/models/*.py → tests/core/models/ (partiellement couvert)
src/domains/*/logic/ → tests/domains/*/logic/ (MAJ nécessaire)
src/api/*.py → tests/api/ (présent)
```

### 4. Analyse de Couverture Prévue

Par phase (après restructuration):

1. **Phase API**: src/api/ → tests/api/
2. **Phase Core**: src/core/ → tests/core/
3. **Phase Domains Cuisine**: src/domains/cuisine/ → tests/domains/cuisine/
4. **Phase Domains Famille**: src/domains/famille/ → tests/domains/famille/
5. **Phase Domains Jeux**: src/domains/jeux/ → tests/domains/jeux/
6. **Phase Domains Maison**: src/domains/maison/ → tests/domains/maison/
7. **Phase Domains Planning**: src/domains/planning/ → tests/domains/planning/
8. **Phase Services**: src/services/ → tests/services/
9. **Phase UI**: src/ui/ → tests/ui/
10. **Phase Utils**: src/utils/ → tests/utils/

## Recommandations

1. **Garder Phase 16-Extended en integration/**
   - C'est des tests end-to-end multi-modules
   - 35 tests validant les workflows critiques

2. **Compter les tests existants par module**
   - Ne pas recréer, réorganiser seulement
   - Utiliser le script `analyze_coverage_by_module.py`

3. **Générer coverage.json**
   - Inclure tous les 194+ fichiers existants
   - Compter les tests réels par module
   - Identifier les gaps

4. **Phase 17 onwards**
   - Ajouter de nouveaux tests pour couvrir les gaps
   - Respecter l'arborescence source=test
