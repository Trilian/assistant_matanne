# Plan de Restructuration des Tests d'Intégration

## Objectif

Renommer les fichiers `tests/integration/` avec des noms clairs qui indiquent leur CONTENU, pas juste un numéro de phase.

## État Actuel (Confus)

```
tests/integration/
├── test_15e_extended_coverage.py    ❓ Phase 15? Quoi?
├── test_business_logic.py            ✓ Clair
├── test_domains_integration.py       ✓ Clair
├── test_phase16.py                   ❓ Ancien? Cassé?
├── test_phase16_extended.py          ✓ 35 tests Phase 16-Extended (KEEPER)
├── test_phase16_fixed.py             ❓ Ancien/cassé?
└── test_phase16_v2.py                ❓ Ancien?
```

## Nommage Recommandé (Clair et Maintenable)

### 1. Garder et Clarifier

```
test_business_logic.py              →  test_integration_business_logic.py
test_domains_integration.py         →  test_integration_domains_workflows.py
test_phase16_extended.py            →  test_integration_crud_models.py
                                       (Tests CRUD pour Recette, Planning, Courses, Inventaire)
```

### 2. À Supprimer (Anciens/Cassés)

- `test_phase16.py` - ancien
- `test_phase16_fixed.py` - ancien
- `test_phase16_v2.py` - ancien
- `test_15e_extended_coverage.py` - phase 15, pas clair

## Convention de Nommage pour `tests/integration/`

**Format**: `test_integration_[domaine]_[type].py`

Exemples:

- `test_integration_crud_models.py` - Tests CRUD basiques (Recette, Planning, etc.)
- `test_integration_business_logic.py` - Logique métier complexe multi-modules
- `test_integration_domains_workflows.py` - Workflows domaines (cuisine, famille, etc.)
- `test_integration_e2e_shopping.py` - E2E workflow complet shopping
- `test_integration_e2e_planning.py` - E2E workflow complet planning

## Tests à Conserver

### `test_integration_crud_models.py` (ancien: test_phase16_extended.py)

**35 tests** - Tous PASSING ✅

- TestRecettePhase16 (10 tests)
- TestPlanningPhase16 (10 tests)
- TestCoursesPhase16 (6 tests)
- TestInventairePhase16 (6 tests)
- TestBusinessLogicPhase16 (3 tests)

### `test_integration_business_logic.py`

Tests logique métier complexe (existant)

### `test_integration_domains_workflows.py`

Tests workflows domaines (existant)

## Action Plan

1. ✅ Supprimer anciens fichiers (phase16.py, phase16_fixed.py, phase16_v2.py, 15e_extended_coverage.py)
2. ✅ Renommer test_phase16_extended.py → test_integration_crud_models.py
3. ✅ Renommer test_business_logic.py → test_integration_business_logic.py
4. ✅ Renommer test_domains_integration.py → test_integration_domains_workflows.py
5. ✅ Mettre à jour la structure

**Résultat final:**

```
tests/integration/
├── test_integration_crud_models.py         (35 tests, tous PASSING)
├── test_integration_business_logic.py      (tests logique métier)
└── test_integration_domains_workflows.py   (tests workflows)
```

Puis garder `tests/e2e/` pour les vrais tests end-to-end.
