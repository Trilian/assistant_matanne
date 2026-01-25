# 🚀 Quick Start Tests Planning Module

## Installation (une fois)

```bash
cd d:\Projet_streamlit\assistant_matanne
pip install pytest pytest-cov
```

## Lancer les Tests

### Option 1: Script Python (Plus facile)

```bash
# Tous les tests
python run_tests_planning.py

# Seulement unitaires (rapides)
python run_tests_planning.py --unit

# Avec rapport couverture
python run_tests_planning.py --coverage

# Mode watch (réexécute à chaque sauvegarde)
python run_tests_planning.py --watch
```

### Option 2: pytest Direct

```bash
# Tous les tests planning
pytest tests/test_planning_unified.py tests/test_planning_schemas.py tests/test_planning_components.py tests/integration/test_planning_full.py -v

# Un fichier spécifique
pytest tests/test_planning_unified.py -v

# Une classe spécifique
pytest tests/test_planning_unified.py::TestCalculCharge -v

# Une méthode spécifique
pytest tests/test_planning_unified.py::TestCalculCharge::test_charge_intense_multiple -v

# Avec couverture
pytest tests/test_planning_*.py tests/integration/test_planning_*.py --cov=src/services/planning_unified --cov-report=html
```

### Option 3: Via manage.py

```bash
python manage.py test_coverage
```

## Fichiers de Tests

| Fichier | Tests | Description |
|---------|-------|-------------|
| **test_planning_unified.py** | 35 | Service PlanningAIService |
| **test_planning_schemas.py** | 37 | Validation schémas Pydantic |
| **test_planning_components.py** | 34 | Composants UI |
| **integration/test_planning_full.py** | 27 | Flux complet E2E |
| **TOTAL** | **133** | |

## Résultats Attendus

✅ PASSED: ~130 tests
✅ FAILED: 0
✅ Duration: 15-20 secondes
✅ Success Rate: 100%

## Exploration des Tests

```bash
# Voir les tests sans les exécuter
pytest tests/test_planning_unified.py --collect-only

# Voir les 5 tests les plus lents
pytest tests/test_planning_unified.py --durations=5

# Stop au premier erreur
pytest tests/test_planning_unified.py -x

# Afficher les print() statements
pytest tests/test_planning_unified.py -v -s

# Verbose mode
pytest tests/test_planning_unified.py -v -s --capture=no
```

## Exemples de Tests

### Test Unitaire Simple
```python
def test_badge_charge_intense():
    """Badge charge intense"""
    result = afficher_badge_charge(85)
    assert "intense" in result.lower() or "🔴" in result
```

### Test Calcul Charge
```python
def test_charge_intense_multiple(service: PlanningAIService):
    """Charge intense - beaucoup d'événements"""
    repas = [{"temps_total": 90}, {"temps_total": 60}]
    activites = [{}, {}, {}]
    projets = [{"priorite": "haute"}, {"priorite": "haute"}]
    
    score = service._calculer_charge(repas, activites, projets, [])
    assert score > 70
```

### Test Intégration Complète
```python
def test_semaine_avec_donnees_completes(
    service_integration: PlanningAIService,
    famille_complete_setup: dict,
):
    """Semaine avec données complètes"""
    data = famille_complete_setup
    semaine = service_integration.get_semaine_complete(data["semaine_debut"])
    
    assert semaine is not None
    assert semaine.stats_semaine["total_repas"] == 2
    assert semaine.stats_semaine["total_activites"] == 2
```

## Dépannage

❌ "ImportError: cannot import name 'PlanningAIService'"
✅ Vérifier que `src/services/planning_unified.py` existe

❌ "No such table: planning"
✅ Les tables sont créées automatiquement par conftest.py

❌ "fixture 'db' not found"
✅ Lancer depuis la racine du projet (où conftest.py existe)

❌ Erreur Streamlit dans composants
✅ Les mocks Streamlit sont configurés automatiquement

## Documentation Complète

- **TESTING_PLANNING_GUIDE.md** - Guide complet avec 10 commandes
- **TESTS_PLANNING_SUMMARY.md** - Résumé statistiques et couverture
- **TESTS_PLANNING_IMPLEMENTATION.md** - Implémentation détaillée

## Suite de Tests

✅ **133 tests** couvrant:
- Service (35 tests)
- Schémas (37 tests)
- Composants (34 tests)
- Intégration (27 tests)

Couverture: **~90% du code** planification

## Questions?

Consulter:
1. TESTING_PLANNING_GUIDE.md - Commandes détaillées
2. TESTS_PLANNING_SUMMARY.md - Statistiques complètes
3. Code des tests - Exemple d'utilisation

---

🎉 **Prêt à tester!** Lancez: `python run_tests_planning.py`
