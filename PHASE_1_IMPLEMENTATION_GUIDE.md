# PHASE 1: Guide d'Implémentation (8 fichiers 0%)

## 📋 Fichiers à couvrir (ordre prioritaire)

### 1. ✅ tests/utils/test_image_generator.py

- **Source**: `src/utils/image_generator.py` (312 statements, 0%)
- **Status**: COMPLÉTÉ (15 test methods)
- **Coverage actuelle**: ~5-8%
- **Classes**: `TestImageGeneratorAPIs`, `TestImageDownload`, `TestImageCache`
- **Topics couverts**:
  - Appels API (Unsplash, Pexels, Pixabay)
  - Gestion d'erreurs et timeouts
  - Cache et batch operations
  - Téléchargement d'images

### 2. ✅ tests/utils/test_helpers_general.py

- **Source**: `src/utils/helpers/helpers.py` (102 statements, 0%)
- **Status**: COMPLÉTÉ (18 test methods)
- **Coverage actuelle**: ~15-18%
- **Classes**: `TestHelpersDict`, `TestHelpersData`, `TestHelpersString`, `TestHelpersLogic`, `TestHelpersValidation`
- **Topics couverts**:
  - Opérations dictionnaires
  - Traitement données
  - Manipulation strings
  - Validation logique

### 3. 🔄 tests/domains/maison/ui/test_depenses.py

- **Source**: `src/domains/maison/ui/depenses.py` (271 statements, 0%)
- **Status**: PARTIELLEMENT COMPLÉTÉ (classe header changée)
- **Coverage cible**: +5-10%
- **Classes**: `TestDepensesUIDisplay`, `TestDepensesUIInteractions`, `TestDepensesUIActions`
- **À compléter**:
  - Test d'affichage tableau (mocking `st.dataframe`)
  - Test ajout dépense (mocking `st.form`, `st.number_input`)
  - Test suppression dépense
  - Test filtrage par catégorie
  - Test agrégations statistiques
  - Test export CSV

### 4. ⏳ tests/domains/planning/ui/components/test_components_init.py

- **Source**: `src/domains/planning/ui/components/__init__.py` (nécessite analyse)
- **Status**: À CRÉER
- **Coverage cible**: +1-2%
- **Classes suggérées**: `TestPlanningWidgets`, `TestEventComponents`, `TestCalendarComponents`
- **À implémenter**:
  - Tests d'import des composants
  - Tests d'initialisation des widgets
  - Tests de composition des événements
  - Tests des composants calendrier

### 5. ⏳ tests/domains/famille/ui/test_jules_planning.py

- **Source**: `src/domains/famille/ui/jules_planning.py` (nécessite analyse)
- **Status**: À CRÉER
- **Coverage cible**: +1-2%
- **Classes suggérées**: `TestJulesMilestones`, `TestJulesSchedule`, `TestJulesTracking`
- **À implémenter**:
  - Tests jalons du développement
  - Tests du planning Jules
  - Tests du suivi des activités

### 6. ⏳ tests/domains/cuisine/ui/test_planificateur_repas.py

- **Source**: `src/domains/cuisine/ui/planificateur_repas.py` (nécessite analyse)
- **Status**: À CRÉER
- **Coverage cible**: +1-2%
- **Classes suggérées**: `TestMealPlanning`, `TestMealSuggestions`, `TestMealSchedule`
- **À implémenter**:
  - Tests de planification de repas
  - Tests de suggestions IA
  - Tests du calendrier repas

### 7. ⏳ tests/domains/jeux/test_setup.py

- **Source**: `src/domains/jeux/setup.py` (nécessite analyse)
- **Status**: À CRÉER
- **Coverage cible**: +1%
- **Classes suggérées**: `TestGameSetup`, `TestGameInitialization`
- **À implémenter**:
  - Tests de configuration jeux
  - Tests d'initialisation BD
  - Tests de validation règles

### 8. ⏳ tests/domains/jeux/test_integration.py

- **Source**: `src/domains/jeux/integration.py` (nécessite analyse)
- **Status**: À CRÉER
- **Coverage cible**: +1%
- **Classes suggérées**: `TestGameAPIs`, `TestGameIntegration`
- **À implémenter**:
  - Tests d'intégration APIs jeux
  - Tests de synchronisation
  - Tests de gestion erreurs

---

## 🛠️ Patterns de test à utiliser

### Pattern 1: Mocking Streamlit

```python
@patch('streamlit.write')
@patch('streamlit.dataframe')
def test_afficher_depenses(self, mock_dataframe, mock_write):
    # Arrange
    mock_dataframe.return_value = None

    # Act
    afficher_depenses([...])

    # Assert
    mock_dataframe.assert_called_once()
```

### Pattern 2: Session DB (fixtures)

```python
@pytest.fixture
def db_session():
    from src.core.database import get_db_context
    with get_db_context() as session:
        yield session
        session.rollback()

def test_creer_depense(self, db_session):
    from src.domains.maison.models import Depense
    depense = Depense(nom="Test", montant=10.0)
    db_session.add(depense)
    db_session.commit()
    assert depense.id is not None
```

### Pattern 3: Tests formulaire

```python
@patch('streamlit.form')
@patch('streamlit.number_input')
@patch('streamlit.text_input')
def test_form_depense(self, mock_text, mock_number, mock_form):
    mock_form.return_value.__enter__ = Mock()
    mock_form.return_value.__exit__ = Mock()
    mock_number.return_value = 25.50
    mock_text.return_value = "Courses"

    # Test le formulaire
    result = creer_form_depense()
    assert result is not None
```

---

## 📊 Métriques de succès PHASE 1

| Metric                    | Target | Current |
| ------------------------- | ------ | ------- |
| Fichiers 0% couverts      | 8      | 2 ✅    |
| Lignes de code test       | 1000+  | ~500    |
| Couverture avg            | >30%   | ~18%    |
| Impact couverture globale | +3-5%  | pending |

---

## 🚀 Prochaine étape

1. **Compléter test_depenses.py** (3-5 heures)
   - Finaliser les 3 classes de test
   - Ajouter tests d'interactions UI
   - Ajouter tests d'actions (CRUD)

2. **Créer 5 nouveaux fichiers de test** (20-30 heures)
   - Analyser les sources
   - Identifier les paths critiques
   - Implémenter les tests

3. **Valider avec pytest**

   ```bash
   pytest tests/utils/test_image_generator.py -v
   pytest tests/utils/test_helpers_general.py -v
   pytest tests/domains/ -v --cov=src --cov-report=term-missing
   ```

4. **Passer à PHASE 2** (UI volumineux)
   - Recettes.py (825 statements)
   - Inventaire.py (825 statements)
   - Courses.py (659 statements)

---

## 📝 Notes importantes

- **Mocking obligatoire** pour tous les appels Streamlit (`@patch`)
- **Fixtures partagées** dans conftest.py pour éviter duplication
- **Tests isolés** (aucune dépendance entre tests)
- **Couverture ligne + branche** (branches conditionnelles critiques)
- **Nommage français** (respecter convention `test_fonction_cas_specific`)
