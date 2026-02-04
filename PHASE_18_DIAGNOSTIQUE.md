# Phase 18 - Diagnostique des Erreurs Identifiées

## 🔍 PREMIER ERREUR IDENTIFIÉE

### Test Échoué:

```python
tests/api/test_api_endpoints_basic.py::TestRecetteDetailEndpoint::test_get_recette_not_found
```

### Comportement Observé:

- **Attendu**: Status code 404 (Not Found)
- **Reçu**: Status code 200 (OK)
- **Requête**: GET /api/v1/recettes/999999

### Cause Probable:

L'endpoint `/api/v1/recettes/{id}` retourne une entité vide ou un mock au lieu de lever une exception 404.

### Fichiers Concernés:

- Test: `tests/api/test_api_endpoints_basic.py` (ligne 195-198)
- Endpoint: Probablement `src/api/v1/endpoints/recettes.py`

### Solution:

Le endpoint doit avoir une validation:

```python
@router.get("/recettes/{recette_id}")
async def get_recette(recette_id: int, db: Session = Depends(get_db)):
    recette = db.query(Recette).filter(Recette.id == recette_id).first()
    if not recette:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    return recette
```

### Options de Correction:

1. **Option A** (Recommandée): Corriger le endpoint dans src/api/
2. **Option B**: Adapter le test si le comportement est intentionnel
3. **Option C**: Créer un middleware pour gérer les 404

---

## 🎯 NEXT STEPS POUR PHASE 18

### Étape 1: Diagnostique Complet (Déjà partiellement complété)

- ✅ Identifier le premier pattern d'erreur (404 mismatch)
- ⏳ Extraire tous les patterns d'erreur de l'exécution pytest
- ⏳ Classifier par catégorie et gravité

### Étape 2: Créer des Fixtures Améliorées

Créer: `tests/fixtures/service_factories.py`

```python
@pytest.fixture
def recette_service(test_db):
    return RecetteService(session=test_db)

@pytest.fixture
def planning_service(test_db):
    return PlanningService(session=test_db)
```

### Étape 3: Implémenter Mock Strategies

Créer: `tests/mocks/service_mocks.py`

```python
@pytest.fixture
def mock_ia_client():
    with patch('src.core.ai.ClientIA') as mock:
        mock.appel_complet.return_value = {...}
        yield mock
```

### Étape 4: Corriger les 319 Tests Échoués

Par catégorie:

1. **API Response Mismatch** (~50 tests) - Vérifier endpoints
2. **Service Init Errors** (~115 tests) - Améliorer fixtures
3. **Mock Issues** (~80 tests) - Stratégie de mock
4. **Assertion Failures** (~74 tests) - Vérifier attentes

### Étape 5: Ajouter Tests Avancés

- Edge cases (0, -1, max int, None, strings vides)
- Property-based testing (Hypothesis)
- Benchmarks de performance

### Étape 6: Valider Coverage

- Target: 50%+ coverage
- Check: `pytest --cov=src --cov-report=term`

---

## 📋 COMMANDS DE DEBUG RAPIDES

```bash
# Exécuter un seul test qui échoue
pytest tests/api/test_api_endpoints_basic.py::TestRecetteDetailEndpoint::test_get_recette_not_found -xvs

# Voir tous les tests d'un fichier avec status
pytest tests/api/test_api_endpoints_basic.py -v

# Exécuter avec traceback complet
pytest tests/api/test_api_endpoints_basic.py::TestRecetteDetailEndpoint::test_get_recette_not_found -vv --tb=short

# Mesurer coverage d'un module spécifique
pytest tests/api/ --cov=src.api --cov-report=term

# Lister tous les tests échoués (rapide)
pytest tests/ --tb=no -q 2>&1 | grep FAILED
```

---

## 🛠️ FICHIERS À CRÉER/MODIFIER

### À Créer:

- `tests/fixtures/service_factories.py` - Factory pattern pour services
- `tests/mocks/service_mocks.py` - Mock strategies
- `tests/property_tests/test_models_hypothesis.py` - Property-based tests
- `tests/benchmarks/test_perf.py` - Performance benchmarks
- `tests/edge_cases/test_edge_cases_models.py` - Edge case tests

### À Modifier:

- `tests/conftest.py` - Ajouter factories et fixtures avancées
- `tests/api/test_api_endpoints_basic.py` - Corriger les assertions
- `tests/services/test_*.py` - Améliorer les mocks

---

## 📊 MÉTRIQUES ACTUELLES (Après Phase 17)

| Métrique        | Valeur        |
| --------------- | ------------- |
| Coverage        | 31.24%        |
| Tests collectés | 3,302         |
| Tests passés    | 2,851 (86.4%) |
| Tests échoués   | 319           |
| Tests erreur    | 115           |
| Tests skippés   | 17            |

## 🎯 CIBLES PHASE 18

| Métrique      | Cible |
| ------------- | ----- |
| Tests échoués | <50   |
| Tests erreur  | 0     |
| Coverage      | 50%+  |
| Pass rate     | >95%  |

---

Status: Phase 18 Démarrée - Diagnostique en cours
Date: 2026-02-04
