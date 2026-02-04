# Phase 18 - Plan d'Action Complet

**Objectif Global**: Augmenter la couverture de 31.24% à 50%+ en corrigeant les tests échoués et en améliorant la qualité des tests.

---

## 1️⃣ ANALYSE DES 319 TESTS ÉCHOUÉS

### Étape 1.1: Identifier les patterns d'erreur

- Créer script de classification des erreurs
- Catégoriser par type: assertion, mock, fixture, API response
- Grouper par module: api/, core/, services/, domains/, ui/

### Étape 1.2: Documenter les erreurs par catégorie

- **Erreurs d'assertion**: Différence entre résultat réel et attendu
- **Erreurs de mock**: Mauvaise configuration des mocks Streamlit/FastAPI
- **Erreurs de fixture**: Base de données, sessions, état initial incorrect
- **Erreurs d'API**: Réponses 200 au lieu de 404, validation incorrecte

### Étape 1.3: Corriger itérativement

- Corrections prioritaires: Erreurs communes (>5% des échecs)
- Corriger par lot par catégorie
- Valider après chaque correction

**Cible**: Réduire les 319 à <100 échoués

---

## 2️⃣ ADRESSER LES 115 ERREURS DE SERVICE

### Étape 2.1: Diagnostiquer les erreurs de constructeur

- Identifier quels services causent les TypeError
- Exemples potentiels:
  - `PlanningService(session)` vs `PlanningService(session, config)`
  - `InventaireService()` manque argument requis
  - `BudgetService` pas initialisé correctement

### Étape 2.2: Revoir les signatures de constructeur

- Vérifier [src/services/](../src/services/) pour les `__init__` réels
- Mettre à jour les fixtures dans [tests/conftest.py](../tests/conftest.py)
- Créer des factories pour chaque service

### Étape 2.3: Améliorer la stratégie de mock

- Implémenter `ServiceMockFactory` pour créer des services testables
- Utiliser `unittest.mock.MagicMock` pour les dépendances externes
- Pattern: Dependency Injection dans les fixtures

**Cible**: 0 erreurs de service init

---

## 3️⃣ STRATÉGIE DE MOCK AMÉLIORÉE

### Nouvelle architecture (tests/):

```
tests/
├── conftest.py                   # Base fixtures (UPDATED)
├── fixtures/
│   ├── service_factories.py      # NEW: Factories pour tous les services
│   ├── db_fixtures.py            # NEW: DB fixtures avancées
│   ├── api_fixtures.py           # NEW: FastAPI TestClient
│   └── streamlit_fixtures.py     # NEW: Streamlit mocks
├── mocks/
│   ├── service_mocks.py          # NEW: Mock strategies
│   ├── ai_client_mock.py         # NEW: ClientIA mock
│   └── database_mocks.py         # NEW: SQLAlchemy mocks
└── ...
```

### Patterns:

1. **Service Factory Pattern**:

   ```python
   @pytest.fixture
   def planning_service(test_db):
       return PlanningService(session=test_db)
   ```

2. **Mock Streamlit**:

   ```python
   @patch('streamlit.write')
   @patch('streamlit.session_state')
   def test_ui_component(mock_state, mock_write):
       ...
   ```

3. **Mock Mistral AI**:
   ```python
   @patch('src.core.ai.ClientIA.appel_complet')
   def test_with_ia(mock_ia):
       mock_ia.return_value = {"suggestions": [...]}
   ```

---

## 4️⃣ CRÉATION DE TESTS AVANCÉS

### 4.1: Tests d'Edge Cases

- Valeurs limites: 0, -1, max int, strings vides, None
- Fichiers: `tests/test_edge_cases_*.py`
- Exemple:
  ```python
  def test_recette_with_zero_portions(test_db):
      with pytest.raises(ValueError):
          recette = Recette(nom="", portions=0)
  ```

### 4.2: Property-Based Testing (Hypothesis)

- Installation: `pip install hypothesis`
- Stratégies pour modèles: `@given(strategies.recettes())`
- Fichiers: `tests/property_tests/`
- Exemple:
  ```python
  @given(st.text(), st.integers(min_value=1, max_value=20))
  def test_recette_creation(nom, portions):
      recette = Recette(nom=nom, portions=portions)
      assert recette.nom == nom
  ```

### 4.3: Benchmarks de Performance

- Tool: `pytest-benchmark`
- Fichiers: `tests/benchmarks/`
- Exemple:
  ```python
  def test_recette_creation_perf(benchmark):
      result = benchmark(create_recette, data)
      assert result.id > 0
  ```

---

## 5️⃣ AMÉLIORATION DE LA COUVERTURE UI

### Problème actuel: UI à <5% coverage

- Components Streamlit pas testées (st.write, st.button, etc.)
- Modales complexes pas validées
- Formulaires pas couverts

### Solution:

1. **Mock Streamlit correctement**:

   ```python
   @patch('streamlit.button', return_value=True)
   @patch('streamlit.text_input', return_value="test")
   def test_form_submission(mock_input, mock_button):
       from src.ui.components import button_component
       result = button_component()
       assert result is not None
   ```

2. **Tester les callbacks**:

   ```python
   def test_form_callback(test_db):
       # Initialiser st.session_state
       st.session_state.form_data = {...}
       # Exécuter le callback
       callback_function()
       # Vérifier l'état final
       assert st.session_state.saved
   ```

3. **Nouveaux fichiers test UI**:
   - `tests/ui/test_forms_extended.py`
   - `tests/ui/test_modals_extended.py`
   - `tests/ui/test_callbacks.py`

---

## 6️⃣ MAINTENIR LES CORRECTIONS

### Processus:

1. **Fixer un groupe d'erreurs** (par catégorie)
2. **Valider localement**: `pytest tests/api/ -v`
3. **Exécuter full suite**: `pytest tests/ -q`
4. **Mesurer coverage**: `pytest --cov=src --cov-report=term`
5. **Committer les progrès**: Documentation + fichiers
6. **Répéter** jusqu'à couverture 50%

### Checkpoints:

- ✅ 319 → 200 échoués
- ✅ 200 → 100 échoués
- ✅ 100 → 50 échoués
- ✅ 50 → <20 échoués
- ✅ Coverage: 35% → 40% → 50%

---

## 7️⃣ ARBORESCENCE RESPECTÉE

Tous les nouveaux fichiers respectent la structure existante:

```
src/
├── core/           # ← Tests pour errors, config, decorators
├── services/       # ← Tests pour CRUD, caching, IA
├── ui/             # ← Tests pour components, forms, modals
├── modules/        # ← Tests pour workflows, state
└── ...

tests/
├── conftest.py                          # ← MAJ: Factory patterns
├── fixtures/                            # ← NOUVEAU
│   ├── __init__.py
│   ├── service_factories.py
│   ├── db_fixtures.py
│   └── streamlit_fixtures.py
├── mocks/                               # ← NOUVEAU
│   ├── __init__.py
│   ├── service_mocks.py
│   └── ai_client_mock.py
├── property_tests/                      # ← NOUVEAU
│   ├── __init__.py
│   ├── test_models_hypothesis.py
│   └── test_services_hypothesis.py
├── benchmarks/                          # ← NOUVEAU
│   ├── __init__.py
│   └── test_perf_core_operations.py
├── edge_cases/                          # ← NOUVEAU
│   ├── __init__.py
│   ├── test_edge_cases_models.py
│   └── test_edge_cases_services.py
└── ... (existing)
```

---

## 📊 TIMELINE & JALONS

**Phase 18 Schedule** (Estimé: 2-3 jours de dev):

| Jour       | Tâche                                            | Cible                       |
| ---------- | ------------------------------------------------ | --------------------------- |
| **Jour 1** | Analyser 319 échoués + diagnostiquer 115 erreurs | 50% des patterns identifiés |
| **Jour 2** | Implémenter mock factories + corriger >100 tests | Coverage: 35%               |
| **Jour 3** | Ajouter edge cases + property-based tests        | Coverage: 40%               |
| **Jour 4** | Benchmarks + couvrir UI                          | Coverage: 45-50%            |

---

## ✅ DÉFINITION DE COMPLÉTÉ (Phase 18)

Phase 18 sera complétée quand:

1. ✅ 319 tests échoués réduits à <50
2. ✅ 115 erreurs service réduits à 0
3. ✅ Mock strategy améliorée (factories en place)
4. ✅ Tests edge cases créés (>20 tests)
5. ✅ Property-based tests intégrés (>15 tests)
6. ✅ Benchmarks créés (5+ benchmarks)
7. ✅ Coverage UI améliorée (>10%)
8. ✅ **Couverture globale ≥ 50%** ✅

---

Début Phase 18: 2026-02-04
Status: À commencer
