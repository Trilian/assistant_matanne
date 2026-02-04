# 📐 ORGANISATION CORRECTE DES TESTS - Alignement src/ ↔ tests/

## ❌ Problème Actuel

`tests/modules/` n'existe PAS en `src/`. C'est une mauvaise organisation.

---

## ✅ Bonne Structure (Respecter Arborescence src/)

### src/ vs tests/ - Alignement Correct

```
src/                              tests/
├── core/                    ↔    ├── core/
│   ├── ai/                        │   ├── test_ai_client.py
│   ├── models/                    │   ├── test_ai_cache.py
│   ├── database.py                │   ├── test_database.py
│   └── ...                        │   └── ...
│
├── services/                ↔    ├── services/
│   ├── recettes.py                │   ├── test_recettes_service.py
│   ├── courses.py                 │   ├── test_courses_service.py
│   ├── planning.py                │   ├── test_planning_service.py
│   └── ...                        │   └── ...
│
├── domains/                 ↔    ├── domains/
│   ├── cuisine/                   │   ├── test_cuisine.py
│   ├── famille/                   │   ├── test_famille.py
│   ├── planning/                  │   ├── test_planning_domain.py
│   └── jeux/                      │   └── test_jeux.py
│
├── ui/                      ↔    ├── ui/
│   ├── components/                │   ├── test_components.py
│   └── feedback/                  │   └── test_feedback.py
│
├── api/                     ↔    ├── api/
│   └── ...                        │   └── test_api.py
│
└── utils/                   ↔    └── utils/
    └── ...                            └── test_utils.py

Hors structure (pour tests transversaux):
                                  ├── e2e/          (tests bout-en-bout)
                                  ├── integration/  (tests multi-modules)
                                  ├── edge_cases/   (cas limites)
                                  └── benchmarks/   (performance)
```

---

## 📊 État Actuel vs Recommandation

| Domaine      | src/                                      | tests/            | Status           |
| ------------ | ----------------------------------------- | ----------------- | ---------------- |
| **core**     | ✓                                         | ✓ core/           | ✅ OK            |
| **services** | ✓                                         | ✓ services/       | ✅ OK            |
| **domains**  | ✓ domains/(cuisine/famille/planning/jeux) | ⚠️ domains/       | 🟡 À créer tests |
| **ui**       | ✓                                         | ✓ ui/             | ✅ OK            |
| **api**      | ✓                                         | ✓ api/            | ✅ OK            |
| **utils**    | ✓                                         | ✓ utils/          | ✅ OK            |
| **modules**  | ❌ N'existe pas                           | ⚠️ tests/modules/ | ❌ À supprimer   |

---

## 🔧 Actions à Faire

### 1. Supprimer `tests/modules/` (Mauvaise structure)

```bash
rm -r tests/modules/
# Récupérer les 70 tests de modules/ et les organiser correctement
```

### 2. Créer `tests/domains/` avec bonne structure

```
tests/domains/
├── test_cuisine.py           (tests du domaine cuisine)
├── test_famille.py           (tests du domaine famille)
├── test_planning_domain.py   (tests du domaine planning)
└── test_jeux.py             (tests du domaine jeux)
```

### 3. Vérifier couverture par domaine

```bash
# Core: ✓ 65%
pytest tests/core/ --cov=src.core

# Services: À mesurer
pytest tests/services/ --cov=src.services

# Domains: À créer
pytest tests/domains/ --cov=src.domains

# UI: À vérifier
pytest tests/ui/ --cov=src.ui

# API: À vérifier
pytest tests/api/ --cov=src.api

# Integration/E2E: Garder séparé
pytest tests/integration/ --cov=src
pytest tests/e2e/ --cov=src
```

---

## 📋 Recommandation Finale

### ✅ Garder Structure

```
tests/core/        ✓ Correspond à src/core/
tests/services/    ✓ Correspond à src/services/
tests/domains/     ✓ Correspond à src/domains/ (À vérifier/améliorer)
tests/ui/          ✓ Correspond à src/ui/
tests/api/         ✓ Correspond à src/api/
tests/utils/       ✓ Correspond à src/utils/
```

### ⚠️ Tests Transversaux (Garder Séparés)

```
tests/integration/ → Tests combinant plusieurs modules
tests/e2e/         → Tests bout-en-bout (scénarios complets)
tests/edge_cases/  → Tests de cas limites
tests/benchmarks/  → Tests de performance
```

### ❌ Supprimer

```
tests/modules/     → MAUVAISE ORGANISATION (pas de src/modules/)
```

---

## 🎯 Impact sur Phases 1-2

Les **232 tests générés (phases 1-2)** devraient être organisés AINSI:

```
Phase 1: Services coverage
├── tests/services/test_recettes_phase1.py      (141 tests)
├── tests/services/test_courses_phase1.py
├── tests/services/test_planning_phase1.py
├── tests/services/test_inventaire_phase1.py
└── tests/services/test_barcode_phase1.py

Phase 2: Domains coverage
├── tests/domains/test_cuisine_phase2.py         (91 tests)
├── tests/domains/test_famille_phase2.py
└── tests/domains/test_planning_phase2.py

E2E + Integration (Gardés séparés)
├── tests/e2e/test_scenarios_*.py
└── tests/integration/test_workflows_*.py
```

---

## 🚀 Prochaines Actions

### Immédiat

- [ ] Analyser les 70 tests de `tests/modules/`
- [ ] Les réorganiser vers `tests/domains/` ou `tests/services/`
- [ ] Supprimer `tests/modules/`
- [ ] Mesurer couverture par domaine correct

### Phases 1-2

- [ ] Générer tests phases 1-2 dans bonne structure
- [ ] Services: tests/services/
- [ ] Domains: tests/domains/
- [ ] E2E: tests/e2e/ (garder séparé)

### Résultat Final

```
✅ Couverture 80%+ avec bonne organisation
✅ Tests alignés avec src/ structure
✅ Facile à maintenir et étendre
```

---

**Verdict**: Réorganiser tests pour respecter src/ → couverture plus logique et maintenable 🎯
