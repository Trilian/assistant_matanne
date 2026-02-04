# 📊 Rapport Détaillé de Couverture de Code

## Résumé Global

- **Couverture globale**: 8.34%
- **Tests créés**: 232 (Phase 1: 141, Phase 2: 91)
- **Tests validés**: 62 (Phase 1 modules + Phase 2 modules)
- **Statut**: En amélioration progressive

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Total fichiers analysés | 35 |
| Fichiers < 80% | 24 (68%) |
| Fichiers critiques (< 10%) | 3 |
| Couverture moyenne | 48.8% |

## 🔴 Fichiers Prioritaires (< 10% de couverture - CRITIQUE)

Priorité maximale - Ces fichiers nécessitent immédiatement des tests

| Fichier | Couverture | Gap | Tests estimés |
|---------|-----------|-----|---|
| [core\ai\parser.py](core\ai\parser.py) | 8.4% | 71.6pp | ~107 |
| [services\types.py](services\types.py) | 8.6% | 71.4pp | ~107 |
| [core\ai\client.py](core\ai\client.py) | 9.7% | 70.3pp | ~105 |

## 🟠 Couverture Très Faible (10-20%)

Priorité haute - Ces fichiers doivent être couverts rapidement

| Fichier | Couverture | Gap | Tests estimés |
|---------|-----------|-----|---|
| [services\base_ai_service.py](services\base_ai_service.py) | 11.8% | 68.2pp | ~102 |
| [core\errors.py](core\errors.py) | 13.6% | 66.4pp | ~99 |
| [services\io_service.py](services\io_service.py) | 15.1% | 64.9pp | ~97 |
| [services\inventaire.py](services\inventaire.py) | 19.7% | 60.3pp | ~90 |

## 🟡 Couverture Faible (20-40%)

Priorité moyenne - Amélioration nécessaire

| Fichier | Couverture | Gap | Tests estimés |
|---------|-----------|-----|---|
| [services\planning.py](services\planning.py) | 20.8% | 59.2pp | ~88 |
| [core\decorators.py](core\decorators.py) | 21.2% | 58.8pp | ~88 |
| [services\courses.py](services\courses.py) | 21.9% | 58.1pp | ~87 |
| [services\user_preferences.py](services\user_preferences.py) | 22.7% | 57.3pp | ~85 |
| [core\database.py](core\database.py) | 22.9% | 57.1pp | ~85 |
| [services\recettes.py](services\recettes.py) | 25.5% | 54.5pp | ~81 |
| [core\validation.py](core\validation.py) | 25.5% | 54.5pp | ~81 |
| [services\planning_unified.py](services\planning_unified.py) | 26.2% | 53.8pp | ~80 |
| [core\ai\rate_limit.py](core\ai\rate_limit.py) | 27.8% | 52.2pp | ~78 |
| [core\cache.py](core\cache.py) | 28.7% | 51.3pp | ~76 |
| [core\ai\cache.py](core\ai\cache.py) | 34.2% | 45.8pp | ~68 |
| [core\config.py](core\config.py) | 34.6% | 45.4pp | ~68 |

## 🟢 Bonne Couverture (60-80%)

| Fichier | Couverture | Gap | Tests estimés |
|---------|-----------|-----|---|
| [core\models\recettes.py](core\models\recettes.py) | 70.0% | 10.0pp | ~15 |

## ✅ Excellente Couverture (80%+)

**11 fichiers** avec couverture >= 80%

| Fichier | Couverture |
|---------|-----------|
| [core\models\nouveaux.py](core\models\nouveaux.py) | 99.4% ✅ |
| [core\constants.py](core\constants.py) | 97.2% ✅ |
| [core\models\courses.py](core\models\courses.py) | 96.8% ✅ |
| [core\models\base.py](core\models\base.py) | 96.4% ✅ |
| [core\models\user_preferences.py](core\models\user_preferences.py) | 96.3% ✅ |
| [core\models\planning.py](core\models\planning.py) | 95.6% ✅ |
| [core\models\users.py](core\models\users.py) | 94.7% ✅ |
| [core\models\inventaire.py](core\models\inventaire.py) | 92.2% ✅ |
| [core\models\schemas.py](core\models\schemas.py) | 90.9% ✅ |
| [core\models\jeux.py](core\models\jeux.py) | 90.6% ✅ |
| [core\models\batch_cooking.py](core\models\batch_cooking.py) | 87.6% ✅ |

## 📋 Plan d'Action Recommandé

### Phase 1 (Priorité - Cette semaine)
1. Couvrir les **fichiers critiques** (< 10%)
   - 3 fichiers identifiés
   - Estimation: ~319 tests

### Phase 2 (Haute priorité - Cette semaine)
1. Améliorer la **couverture très faible** (10-20%)
   - 4 fichiers identifiés
   - Estimation: ~388 tests

### Phase 3 (Prochaine semaine)
1. Couvrir les fichiers **40-60%**
2. Atteindre **80% de couverture globale**

## 🎯 Top 20 Fichiers à Améliorer en Priorité

| # | Fichier | Couverture | Gap | Tests |
|---|---------|-----------|-----|-------|
| 1 | [core\ai\parser.py](core\ai\parser.py) | 8.4% | 71.6pp | ~107 |
| 2 | [services\types.py](services\types.py) | 8.6% | 71.4pp | ~107 |
| 3 | [core\ai\client.py](core\ai\client.py) | 9.7% | 70.3pp | ~105 |
| 4 | [services\base_ai_service.py](services\base_ai_service.py) | 11.8% | 68.2pp | ~102 |
| 5 | [core\errors.py](core\errors.py) | 13.6% | 66.4pp | ~99 |
| 6 | [services\io_service.py](services\io_service.py) | 15.1% | 64.9pp | ~97 |
| 7 | [services\inventaire.py](services\inventaire.py) | 19.7% | 60.3pp | ~90 |
| 8 | [services\planning.py](services\planning.py) | 20.8% | 59.2pp | ~88 |
| 9 | [core\decorators.py](core\decorators.py) | 21.2% | 58.8pp | ~88 |
| 10 | [services\courses.py](services\courses.py) | 21.9% | 58.1pp | ~87 |
| 11 | [services\user_preferences.py](services\user_preferences.py) | 22.7% | 57.3pp | ~85 |
| 12 | [core\database.py](core\database.py) | 22.9% | 57.1pp | ~85 |
| 13 | [services\recettes.py](services\recettes.py) | 25.5% | 54.5pp | ~81 |
| 14 | [core\validation.py](core\validation.py) | 25.5% | 54.5pp | ~81 |
| 15 | [services\planning_unified.py](services\planning_unified.py) | 26.2% | 53.8pp | ~80 |
| 16 | [core\ai\rate_limit.py](core\ai\rate_limit.py) | 27.8% | 52.2pp | ~78 |
| 17 | [core\cache.py](core\cache.py) | 28.7% | 51.3pp | ~76 |
| 18 | [core\ai\cache.py](core\ai\cache.py) | 34.2% | 45.8pp | ~68 |
| 19 | [core\config.py](core\config.py) | 34.6% | 45.4pp | ~68 |
| 20 | [core\state.py](core\state.py) | 41.3% | 38.7pp | ~58 |
