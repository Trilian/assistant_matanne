# Rapport d'Analyse de Couverture de Tests

**Date**: Février 3, 2026  
**Projet**: Assistant Matanne (Streamlit)  
**Objectif**: Atteindre >80% de couverture pour le dossier `src/`

---

## 📊 Résumé Exécutif

| Métrique                | Valeur     | Objectif |
| ----------------------- | ---------- | -------- |
| **Couverture actuelle** | 29.37%     | >80%     |
| **Fichiers analysés**   | 209        | -        |
| **Fichiers >80%**       | 60 (28.7%) | 100%     |
| **Fichiers <30%**       | 100        | 0%       |
| **Couverture moyenne**  | 46.6%      | >80%     |
| **Fichiers avec tests** | 66 (31.6%) | 100%     |

**🎯 Gap à couvrir: ~50% points de pourcentage**

---

## 🎯 Analyse par Niveau de Couverture

### ✅ Excellente (>90%) - 53 fichiers

Modules bien couverts:

- `src/core/models/` - Excellente couverture des modèles
- `src/core/__init__.py` - 100%
- `src/core/logging.py` - 98.32%
- `src/core/constants.py` - 97.20%
- `src/core/models/users.py` - 94.74%

### 🟢 Bonne (80-90%) - 7 fichiers

- `src/core/models/batch_cooking.py` - 87.59%
- `src/core/models/jeux.py` - 90.61%
- `src/core/state.py` - 86.55%
- `src/core/cache.py` - 83.09%

### 🟡 Acceptable (50-80%) - 31 fichiers

- `src/core/ai/parser.py` - 81.86%
- `src/core/validators_pydantic.py` - 79.13%
- `src/core/decorators.py` - 53.03%
- `src/core/config.py` - 50.62%

### 🔴 Faible (<50%) - 118 fichiers

**Beaucoup trop nombreux! Voir détails ci-dessous.**

---

## 🚨 Fichiers Critiques (<30%) - 100 fichiers

### Couverture 0% - 8 fichiers (Non testés du tout)

1. `src/domains/cuisine/ui/planificateur_repas.py` - 0/375 statements
2. `src/domains/famille/ui/jules_planning.py` - 0/163 statements
3. `src/domains/jeux/integration.py` - 0/15 statements
4. `src/domains/jeux/setup.py` - 0/76 statements
5. `src/domains/maison/ui/depenses.py` - 0/271 statements
6. `src/domains/planning/ui/components/__init__.py` - 0/110 statements
7. `src/utils/helpers/helpers.py` - 0/102 statements
8. `src/utils/image_generator.py` - 0/312 statements

### Couverture <5% - 12 fichiers (Quasi-aucune couverture)

- `src/domains/cuisine/ui/recettes.py` - 2.5%
- `src/domains/cuisine/ui/courses.py` - 3.1%
- `src/domains/cuisine/ui/inventaire.py` - 3.9%
- `src/domains/jeux/ui/paris.py` - 4.0%
- `src/utils/formatters/dates.py` - 4.4%
- `src/domains/planning/ui/vue_ensemble.py` - 4.4%
- Et 6 autres...

---

## 📦 Analyse par Module

| Module       | Couverture | Fichiers | Status        |
| ------------ | ---------- | -------- | ------------- |
| **core**     | 76.6%      | 42       | ✅ Bon        |
| **api**      | 66.3%      | 3        | 🟡 Acceptable |
| **utils**    | 51.5%      | 21       | 🔴 Faible     |
| **app.py**   | 50.9%      | 1        | 🔴 Faible     |
| **domains**  | 38.7%      | 83       | 🔴 Critique   |
| **ui**       | 37.5%      | 26       | 🔴 Critique   |
| **services** | 30.1%      | 33       | 🔴 Critique   |

### Détails par Module

#### 🟢 **core/** (76.6%) - Meilleur module

**Fichiers OK (>80%)**: Majority des models

- ✅ `models/famille.py` - 100%
- ✅ `models/maison.py` - 100%
- ✅ `models/sante.py` - 100%

**À améliorer (<80%)**:

- `database.py` - 65.14% (200 statements) → 35 lignes à couvrir
- `config.py` - 50.62% (193 statements) → 90 lignes à couvrir
- `decorators.py` - 53.03% (102 statements) → 47 lignes à couvrir
- `cache_multi.py` - 46.62% (337 statements) → 180 lignes à couvrir
- `offline.py` - 25.08% (269 statements) → 200+ lignes à couvrir
- `sql_optimizer.py` - 24.0% (245 statements) → 186 lignes à couvrir

#### 🔴 **services/** (30.1%) - Module CRITIQUE

**33 fichiers, couverture très basse**

Priorités:

1. `base_ai_service.py` - 13.54% (222 statements)
2. `base_service.py` - 16.94% (168 statements)
3. `auth.py` - 19.27% (381 statements) - Services critiques!
4. `backup.py` - 18.32% (319 statements)
5. `calendar_sync.py` - 16.97% (481 statements)

#### 🔴 **domains/** (38.7%) - Module CRITIQUE

**83 fichiers, très hétérogène**

**Sous-modules**:

- **cuisine**: Couverture très basse pour les UI
  - `logic/courses_logic.py` - 98.64% ✅ (très bon!)
  - `logic/batch_cooking_logic.py` - 69.03%
  - `ui/planificateur_repas.py` - 0.0% ❌ (375 statements!)
  - `ui/recettes.py` - 2.48% (825 statements!)

- **famille**: Logique bonne, UI faible
  - `logic/activites_logic.py` - 99.38% ✅ (excellent!)
  - `logic/routines_logic.py` - 93.78% ✅ (très bon!)
  - `ui/achats_famille.py` - 6.62% (234 statements)
  - `ui/routines.py` - 4.71% (271 statements)

- **maison**: Très faible
  - `logic/entretien_logic.py` - 97.62% ✅ (excellent!)
  - `logic/jardin_logic.py` - 78.26%
  - `ui/depenses.py` - 0.0% (271 statements!)
  - `ui/*` - Tous <10%

- **planning**: Très faible
  - `logic/calendrier_unifie_logic.py` - 33.64%
  - `ui/calendrier_unifie.py` - 5.31% (247 statements)
  - `ui/components/__init__.py` - 0.0% (110 statements!)

#### 🔴 **ui/** (37.5%) - Module CRITIQUE

**26 fichiers de composants UI, très peu couverts**

- `components/camera_scanner.py` - 6.56% (182 statements)
- `components/layouts.py` - 8.54% (56 statements)
- `core/base_form.py` - 13.67% (101 statements)
- `core/base_module.py` - 17.56% (192 statements)
- `layout/sidebar.py` - 10.45% (47 statements)

---

## ⚠️ Fichiers sans Tests Correspondants (115 fichiers)

### Structure de tests actuelle

```
tests/
├── core/          (43 fichiers de test)
├── domains/
│   ├── cuisine/   (13 fichiers de test)
│   ├── famille/   (9 fichiers de test)
│   ├── maison/    (9 fichiers de test)
│   └── ...
├── services/      (20 fichiers de test)
├── ui/            (21 fichiers de test)
├── utils/         (6 fichiers de test)
└── e2e/           (1 fichier - insuffisant!)
```

### Fichiers orphelins prioritaires

**Sans tests du tout** (couverture 0%):

```
- src/domains/cuisine/ui/planificateur_repas.py
- src/domains/famille/ui/jules_planning.py
- src/domains/jeux/integration.py
- src/domains/jeux/setup.py
- src/domains/maison/ui/depenses.py
- src/domains/planning/ui/components/__init__.py
- src/utils/helpers/helpers.py
- src/utils/image_generator.py
```

**Avec tests minimalistes** (<5%):

```
- src/domains/cuisine/ui/recettes.py (2.48%) - 825 statements!
- src/domains/cuisine/ui/courses.py (3.06%) - 659 statements!
- src/domains/cuisine/ui/inventaire.py (3.86%) - 825 statements!
- src/domains/jeux/ui/paris.py (4.03%) - 622 statements!
- Et beaucoup d'autres...
```

---

## 📋 Plan d'Action Détaillé

### Phase 1: Fichiers Critiques (0% - 30%)

**Nombre de fichiers**: 100  
**Effort estimé**: 150-200 heures  
**Impact sur couverture**: +20-30%

#### 1.1 Groupe 1: 0% (8 fichiers) - 15 jours

- `src/utils/image_generator.py` (312 statements)
- `src/domains/maison/ui/depenses.py` (271 statements)
- `src/domains/planning/ui/components/__init__.py` (110 statements)
- `src/utils/helpers/helpers.py` (102 statements)
- `src/domains/famille/ui/jules_planning.py` (163 statements)
- `src/domains/cuisine/ui/planificateur_repas.py` (375 statements)
- `src/domains/jeux/setup.py` (76 statements)
- `src/domains/jeux/integration.py` (15 statements)

**Recommandation**: Créer tests/utils/test_image_generator.py, tests/utils/test_helpers.py, etc.

#### 1.2 Groupe 2: <5% (12 fichiers) - 20 jours

- `src/domains/cuisine/ui/recettes.py` (825 statements) ⚠️ TRÈS GROS
- `src/domains/cuisine/ui/inventaire.py` (825 statements) ⚠️ TRÈS GROS
- `src/domains/cuisine/ui/courses.py` (659 statements) ⚠️ TRÈS GROS
- `src/domains/jeux/ui/paris.py` (622 statements) ⚠️ TRÈS GROS
- Et autres...

**Recommandation**: Créer tests/domains/cuisine/ui/test_recettes.py amélioration majeure

#### 1.3 Groupe 3: 5-30% (80 fichiers) - 40 jours

- Services: auth.py, backup.py, etc.
- UI components: layouts, forms, data, etc.
- Formatters: dates, numbers, text, units

### Phase 2: Modules Faibles (30-80%)

**Nombre de fichiers**: 60  
**Effort estimé**: 80-100 heures  
**Impact sur couverture**: +15-20%

Focus:

- `src/services/` (30.1%) → 60%
- `src/ui/` (37.5%) → 70%
- `src/domains/` (38.7%) → 70%

### Phase 3: Tests d'Intégration (E2E)

**Répertoire**: `tests/e2e/`  
**Fichiers**: À créer (actuellement 1 seul fichier)  
**Effort estimé**: 30-40 heures

Scénarios critiques à couvrir:

- Flux de création de recette (cuisine)
- Flux de création d'événement (planning)
- Flux d'ajout d'enfant (famille)
- Synchronisation multi-tenant

---

## 🛠️ Actions Recommandées

### 1. Restructuration de tests/ (URGENT)

```
tests/
├── e2e/                          # ← À CRÉER
│   ├── test_cuisine_flow.py      # Flux recette complet
│   ├── test_planning_flow.py     # Flux événement complet
│   ├── test_famille_flow.py      # Flux famille complet
│   ├── test_auth_flow.py         # Flux authentification
│   └── test_multitenancy.py      # Flux multi-tenant
├── core/
│   ├── test_database.py          # Améliorer
│   ├── test_config.py            # Améliorer
│   ├── test_decorators.py        # Améliorer
│   └── ...
├── domains/
│   ├── cuisine/
│   │   ├── logic/
│   │   │   ├── test_batch_cooking_logic.py   # OK
│   │   │   ├── test_courses_logic.py         # OK
│   │   │   ├── test_inventaire_logic.py      # À améliorer
│   │   │   ├── test_planificateur_repas_logic.py  # À améliorer
│   │   │   └── test_recettes_logic.py        # À améliorer
│   │   └── ui/
│   │       ├── test_recettes.py              # À RÉÉCRIRE (825 lines!)
│   │       ├── test_courses.py               # À améliorer (659 lines!)
│   │       ├── test_inventaire.py            # À améliorer (825 lines!)
│   │       └── ...
│   ├── maison/
│   │   └── ui/
│   │       ├── test_depenses.py              # ← À CRÉER (271 lines!)
│   │       └── ...
│   └── ...
├── services/
│   ├── test_auth_service.py      # À améliorer (auth.py: 19.27%)
│   ├── test_base_ai_service.py   # À améliorer (13.54%)
│   ├── test_base_service.py      # À améliorer (16.94%)
│   └── ...
└── ui/
    ├── test_camera_scanner.py    # À améliorer
    └── ...
```

### 2. Créer Fichiers de Test Prioritaires

**Top 10 fichiers à couvrir** (par impact):

1. `src/domains/cuisine/ui/recettes.py` - 825 statements, 2.48%
2. `src/domains/cuisine/ui/inventaire.py` - 825 statements, 3.86%
3. `src/domains/cuisine/ui/courses.py` - 659 statements, 3.06%
4. `src/domains/jeux/ui/paris.py` - 622 statements, 4.03%
5. `src/services/auth.py` - 381 statements, 19.27%
6. `src/domains/planning/ui/calendrier_unifie.py` - 247 statements, 5.31%
7. `src/services/weather.py` - 371 statements, 18.76%
8. `src/domains/maison/ui/entretien.py` - 253 statements, 8.26%
9. `src/core/decorators.py` - 102 statements, 53.03%
10. `src/utils/image_generator.py` - 312 statements, 0.0%

### 3. Améliorer Tests Existants

Fichiers avec tests **insuffisants** (<30%):

- `src/core/offline.py` - 25.08%
- `src/core/sql_optimizer.py` - 24.0%
- `src/api/rate_limiting.py` - 24.2%
- `src/services/budget.py` - 24.0%
- `src/services/planning.py` - 23.42%

### 4. Mise en Place de Bonnes Pratiques

#### Convention de nommage

✅ Format recommandé (respecté):

```
src/domains/cuisine/ui/recettes.py
tests/domains/cuisine/ui/test_recettes.py
```

#### Fixtures réutilisables

Créer `tests/conftest.py` amélioré avec:

- Fixtures pour les modèles principaux
- Fixtures pour les services
- Fixtures pour les contexts Streamlit

#### Mock pour Streamlit

```python
# Exemple pour tester UI
import streamlit as st
import unittest.mock as mock

def test_recipe_form():
    with mock.patch('streamlit.form'):
        result = recipe_form()
        assert result is not None
```

### 5. CI/CD Integration

Ajouter à GitHub Actions:

```yaml
- name: Coverage Report
  run: pytest --cov=src --cov-report=term-missing --cov-report=html

- name: Check Coverage
  run: |
    coverage report --fail-under=80
```

---

## 📈 Objectifs Progressifs

| Phase        | Couverture | Délai          | Fichiers testés    |
| ------------ | ---------- | -------------- | ------------------ |
| **Actuelle** | 29.37%     | -              | 66/209             |
| **Phase 1**  | 45-50%     | 2 semaines     | +50 fichiers       |
| **Phase 2**  | 60-70%     | 4 semaines     | +40 fichiers       |
| **Phase 3**  | 75-80%     | 2 semaines     | +20 fichiers + E2E |
| **Cible**    | **>80%**   | **8 semaines** | 180+/209           |

---

## 🎯 Checklist d'Implémentation

- [ ] Créer dossier `tests/e2e/`
- [ ] Réorganiser tests selon arborescence src/
- [ ] Créer test_image_generator.py (312 statements)
- [ ] Créer test_depenses.py (271 statements)
- [ ] Améliorer test_recettes.py (825 statements → 500+ lignes de test)
- [ ] Améliorer test_inventaire.py (825 statements)
- [ ] Améliorer test_courses.py (659 statements)
- [ ] Ajouter tests pour auth.py (381 statements)
- [ ] Améliorer decorators.py tests
- [ ] Améliorer offline.py tests
- [ ] Créer fixtures conftest.py
- [ ] Mettre en place CI/CD coverage check

---

## 💡 Recommandations Stratégiques

### Court terme (1-2 semaines)

1. **Créer les 8 fichiers 0%** → +3-5% couverture
2. **Améliorer les 12 fichiers <5%** → +5-8% couverture
3. **Restructurer tests/** pour éviter doublons

### Moyen terme (3-4 semaines)

1. **Couvrir services/** (30.1% → 60%) → +10-15% couverture
2. **Couvrir domains/** (38.7% → 70%) → +15-20% couverture
3. **Couvrir ui/** (37.5% → 70%) → +10-15% couverture

### Long terme (5-8 semaines)

1. **Tests E2E** pour flux critiques
2. **Atteindre >80%** de couverture globale
3. **Maintenir** avec CI/CD stricte (fail <80%)

---

## Annexe: Fichiers par Module et Priorité

### 📌 URGENT (0-5% couverture, >100 statements)

```
1. src/domains/cuisine/ui/recettes.py (825) - 2.48%
2. src/domains/cuisine/ui/inventaire.py (825) - 3.86%
3. src/domains/cuisine/ui/courses.py (659) - 3.06%
4. src/domains/jeux/ui/paris.py (622) - 4.03%
5. src/services/recipe_import.py (483) - 9.45%
6. src/services/auth.py (381) - 19.27%
7. src/domains/planning/ui/calendrier_unifie.py (247) - 5.31%
8. src/services/weather.py (371) - 18.76%
9. src/utils/image_generator.py (312) - 0.0%
10. src/domains/maison/ui/depenses.py (271) - 0.0%
```

### 📌 IMPORTANT (5-30%, >50 statements)

```
11. src/domains/maison/ui/entretien.py (253) - 8.26%
12. src/core/sql_optimizer.py (245) - 24.0%
13. src/services/budget.py (470) - 23.96%
14. src/domains/cuisine/ui/planificateur_repas.py (375) - 0.0%
15. src/services/backup.py (319) - 18.32%
... et 50 autres
```

---

**Généré par**: `analyze_coverage.py`  
**Date**: 2026-02-03  
**Prochaine actualisation**: À chaque commit majeur
