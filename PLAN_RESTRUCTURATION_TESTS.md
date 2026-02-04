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

## État Actuel

### Fichiers Tests Existants

- **api/**: 4 fichiers tests
- **core/**: 32 fichiers tests
- **domains/**: 66 fichiers tests (7 modules)
- **services/**: 44 fichiers tests
- **ui/**: 32 fichiers tests
- **utils/**: 6 fichiers tests
- **e2e/**: 5 fichiers tests
- **integration/**: 5 fichiers tests (+ Phase 16-Extended avec 35 tests)

**Total**: 194 fichiers de test

### Phase 16-Extended Tests (35 tests)

Location actuelle: `tests/integration/test_phase16_extended.py`

Contient:

- TestRecettePhase16: 10 tests
- TestPlanningPhase16: 10 tests
- TestCoursesPhase16: 6 tests
- TestInventairePhase16: 6 tests
- TestBusinessLogicPhase16: 3 tests

## Plan d'Action

### 1. Intégrer Phase 16-Extended dans la structure

#### Option A: Garder en integration/ (Recommandé)

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
