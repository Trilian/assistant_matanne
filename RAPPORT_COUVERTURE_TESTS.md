# Rapport d'Analyse de Couverture de Tests

Date: 4 Février 2026

## Résumé Exécutif

- **Fichiers src/**: 175
- **Fichiers tests/**: 225
- **Fichiers manquant tests**: 89
- **Couverture structure**: 127.8% (tests supplémentaires détectés)
- **Objectif**: 80% couverture + 95% pass rate

## 1. Fichiers Manquant Correspondants

### Par Module (Priorité Décroissante)

#### 🔴 HIGH PRIORITY - core/ (17 fichiers manquants)

Tests manquants:

- `test_ai_client.py` - src/core/ai/client.py
- `test_ai_parser.py` - src/core/ai/parser.py
- `test_ai_rate_limit.py` - src/core/ai/rate_limit.py
- `test_base_models.py` - src/core/models/base.py
- `test_models_batch_cooking.py` - src/core/models/batch_cooking.py
- `test_models_courses.py` - src/core/models/courses.py
- `test_models_famille.py` - src/core/models/famille.py
- `test_models_inventaire.py` - src/core/models/inventaire.py
- `test_models_jeux.py` - src/core/models/jeux.py
- `test_models_maison.py` - src/core/models/maison.py
- `test_models_maison_extended.py` - src/core/models/maison_extended.py
- `test_models_nouveaux.py` - src/core/models/nouveaux.py
- `test_models_planning.py` - src/core/models/planning.py
- `test_models_recettes.py` - src/core/models/recettes.py
- `test_models_sante.py` - src/core/models/sante.py
- `test_models_user_preferences.py` - src/core/models/user_preferences.py
- `test_models_users.py` - src/core/models/users.py

#### 🟠 MEDIUM PRIORITY - services/ (27 fichiers manquants)

#### 🟡 MEDIUM PRIORITY - ui/ (20 fichiers manquants)

#### 🟡 MEDIUM PRIORITY - domains/ (9 fichiers manquants)

#### 🟡 LOW PRIORITY - utils/ (16 fichiers manquants)

## 2. État de la Structure Actuelle

| Dossier  | Fichiers src/ | Tests | Couverture | Statut          |
| -------- | ------------- | ----- | ---------- | --------------- |
| api      | 2             | 7     | 350.0%     | ✓ Excellent     |
| core     | 39            | 36    | 92.3%      | ✓ Bon           |
| domains  | 63            | 73    | 115.9%     | ✓ Excellent     |
| services | 32            | 45    | 140.6%     | ✓ Excellent     |
| ui       | 21            | 27    | 128.6%     | ✓ Excellent     |
| utils    | 17            | 9     | 52.9%      | ⚠️ **CRITIQUE** |
| root     | 1             | 14    | 1400.0%    | ✓ Excellent     |

## 3. Plan d'Action Immédiat

### Étape 1: Fixer les tests échoués

- 5 tests échoués en api/test_api_endpoints_basic.py (inventaire)

### Étape 2: Créer tests pour modules critiques (core/)

- [ ] test_ai_client.py
- [ ] test_ai_parser.py
- [ ] test_ai_rate_limit.py
- [ ] 14 tests pour modèles

### Étape 3: Compléter services/

- [ ] 27 fichiers manquants

### Étape 4: Compléter ui/

- [ ] 20 fichiers manquants

### Étape 5: Compléter utils/

- [ ] 16 fichiers manquants

## Métriques Cibles

- ✅ 80% couverture globale
- ✅ 95% pass rate
- ✅ 0 fichiers sans tests correspondants
