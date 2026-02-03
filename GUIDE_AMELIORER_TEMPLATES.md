# 🎯 Guide: Améliorer les templates PHASE 1 → Tests réels

## État actuel

- **2/8 fichiers**: Complètement développés (image_generator, helpers_general)
- **6/8 fichiers**: Templates basiques, assertion `assert True` or `assert X or True`
- **Objectif**: Remplacer les assertions triviales par des tests réels

---

## 📋 Fichiers à développer

### 1. test_depenses.py (271 statements)

**Emplacement**: `tests/domains/maison/ui/test_depenses.py`

**État**: Template avec 3 classes (TestDepensesUIDisplay, TestDepensesUIInteractions, TestDepensesUIActions)

**À développer**:

#### Classe 1: TestDepensesUIDisplay

```python
@patch('streamlit.dataframe')
@patch('streamlit.write')
def test_afficher_tableau_depenses(self, mock_write, mock_dataframe):
    """Teste l'affichage du tableau de dépenses"""
    # CURRENT: assert mock_dataframe.called or True
    # IMPROVE:
    from src.domains.maison.ui.depenses import afficher_tableau_depenses

    # Arrange: créer des dépenses de test
    test_data = [
        {"nom": "Courses", "montant": 50.0, "categorie": "Alimentation"},
        {"nom": "Essence", "montant": 60.0, "categorie": "Transport"}
    ]

    # Act
    afficher_tableau_depenses(test_data)

    # Assert
    assert mock_dataframe.called
    # Vérifier que les bons arguments ont été passés
    call_args = mock_dataframe.call_args
    assert call_args is not None
    # Vérifier la structure du dataframe
    assert len(mock_dataframe.call_args[0][0]) == 2  # 2 dépenses
```

**Pattern similaire pour les 2-3 autres tests de display**

#### Classe 2: TestDepensesUIInteractions

```python
@patch('streamlit.form')
@patch('streamlit.number_input')
@patch('streamlit.text_input')
@patch('streamlit.selectbox')
@patch('streamlit.date_input')
def test_saisir_nouvelle_depense(self, mock_date, mock_select, mock_text, mock_number, mock_form):
    """Teste la saisie d'une nouvelle dépense"""
    # CURRENT: assert mock_form.called or True
    # IMPROVE:
    from src.domains.maison.ui.depenses import form_nouvelle_depense

    # Setup mocks pour retourner des valeurs de test
    mock_form.return_value.__enter__ = Mock(return_value=None)
    mock_form.return_value.__exit__ = Mock(return_value=None)
    mock_text.return_value = "Courses"
    mock_number.return_value = 50.0
    mock_select.return_value = "Alimentation"
    mock_date.return_value = "2024-01-15"

    # Act: appeler le formulaire
    result = form_nouvelle_depense()

    # Assert: vérifier que tous les widgets ont été appelés
    assert mock_form.called
    assert mock_text.called  # Nom dépense
    assert mock_number.called  # Montant
    assert mock_select.called  # Catégorie
    assert mock_date.called  # Date
```

#### Classe 3: TestDepensesUIActions

```python
def test_creer_depense(self, db_session: Session):
    """Teste la création d'une dépense en BD"""
    # CURRENT: assert True
    # IMPROVE:
    from src.domains.maison.models import Depense

    # Arrange
    data = {
        "nom": "Courses",
        "montant": 50.0,
        "categorie": "Alimentation"
    }

    # Act
    depense = Depense(**data)
    db_session.add(depense)
    db_session.commit()

    # Assert
    assert depense.id is not None
    assert depense.nom == "Courses"
    assert depense.montant == 50.0

    # Vérifier qu'elle est en BD
    found = db_session.query(Depense).filter_by(nom="Courses").first()
    assert found is not None
    assert found.id == depense.id
```

---

### 2. test_components_init.py (? statements)

**À développer similairement avec des imports réels et des assertions concrètes**

**Pattern**:

```python
def test_importer_composants_planning(self):
    """Teste l'import des composants planning"""
    # Vérifier que les imports fonctionnent
    from src.domains.planning.ui.components import (
        widget_event, widget_calendar, widget_schedule
    )
    # Vérifier que ce sont des fonctions
    assert callable(widget_event)
    assert callable(widget_calendar)
    assert callable(widget_schedule)
```

---

### 3. test_jules_planning.py (? statements)

**Focus**: Tests des jalons et du suivi de Jules

**Pattern**:

```python
def test_ajouter_jalon(self, db_session: Session):
    """Teste l'ajout d'un jalon du développement"""
    from src.domains.famille.models import JalonsJules

    # Arrange
    jalon_data = {
        "nom": "Premier sourire",
        "age_mois": 2,
        "date": datetime.now()
    }

    # Act
    jalon = JalonsJules(**jalon_data)
    db_session.add(jalon)
    db_session.commit()

    # Assert
    assert jalon.id is not None
    found = db_session.query(JalonsJules).filter_by(nom="Premier sourire").first()
    assert found is not None
```

---

### 4. test_planificateur_repas.py (? statements)

**Focus**: Planning de repas et suggestions IA

**Pattern**:

```python
def test_creer_planning_repas(self, db_session: Session):
    """Teste la création d'un planning de repas"""
    from src.domains.cuisine.models import PlanningRepas

    planning = PlanningRepas(
        semaine_debut="2024-01-15",
        description="Planning semaine 1"
    )
    db_session.add(planning)
    db_session.commit()

    assert planning.id is not None
    assert planning.semaine_debut == "2024-01-15"
```

---

### 5. test_setup.py (? statements)

**Focus**: Initialisation jeux

**Simple pattern**:

```python
def test_initialiser_bd_jeux(self, db_session: Session):
    """Teste l'initialisation de la BD jeux"""
    from src.domains.jeux.setup import initialiser_bd

    # Act
    initialiser_bd(db_session)

    # Assert
    # Vérifier que les tables de jeux sont créées
    # (utiliser des imports de modèles pour valider)
    from src.domains.jeux.models import Jeu, Partie
    assert db_session.query(Jeu).count() >= 0  # Pas d'erreur
```

---

### 6. test_integration.py (? statements)

**Focus**: Intégration APIs

**Pattern with mocking APIs**:

```python
@patch('requests.get')
def test_connexion_api_externe(self, mock_get):
    """Teste la connexion à une API externe"""
    from src.domains.jeux.integration import sync_external_data

    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "data": []}
    mock_get.return_value = mock_response

    # Act
    result = sync_external_data()

    # Assert
    assert mock_get.called
    assert result is not None
    assert mock_response.json.called
```

---

## 🔄 Processus de développement

### Pour chaque fichier:

1. **Lire le fichier source** (3-5 min)

   ```bash
   # Voir le contenu du fichier source
   cat src/domains/maison/ui/depenses.py | head -100
   ```

2. **Identifier les functions critiques** (5 min)
   - Imports principaux
   - Fonctions CRUD
   - Fonctions UI
   - Appels externes (APIs, BD)

3. **Écrire les tests** (15-30 min par fichier)
   - Remplacer `assert X or True` par de vraies assertions
   - Ajouter des `Arrange-Act-Assert` réels
   - Tester les cas d'erreur

4. **Tester localement** (5 min)

   ```bash
   pytest tests/domains/maison/ui/test_depenses.py -v
   ```

5. **Valider la couverture** (2 min)
   ```bash
   pytest tests/domains/maison/ui/test_depenses.py --cov=src.domains.maison.ui.depenses
   ```

---

## 📊 Métriques de succès par fichier

| Fichier                     | Statements | Target Coverage | Success =                         |
| --------------------------- | ---------- | --------------- | --------------------------------- |
| test_depenses.py            | 271        | >30%            | ~80 lines de vraies logiques test |
| test_components_init.py     | ?          | >30%            | ~50 lines vrais tests             |
| test_jules_planning.py      | ?          | >30%            | ~60 lines vrais tests             |
| test_planificateur_repas.py | ?          | >30%            | ~60 lines vrais tests             |
| test_setup.py               | ?          | >20%            | ~35 lines vrais tests             |
| test_integration.py         | ?          | >20%            | ~35 lines vrais tests             |

---

## ✅ Checklist pour chaque fichier

- [ ] Lire le fichier source
- [ ] Identifier 3-5 fonctions critiques
- [ ] Écrire 3-5 tests par classe
- [ ] Remplacer les `assert True` par de vrais assertions
- [ ] Ajouter du mocking (streamlit, requests, etc.)
- [ ] Ajouter des fixtures DB si nécessaire
- [ ] Tester localement: `pytest test_X.py -v`
- [ ] Vérifier pas d'erreurs de syntax
- [ ] Vérifier coverage >20-30%

---

## 🎯 Exemple complet: test_depenses.py

```python
# AVANT (Template)
def test_afficher_tableau_depenses(self, mock_write, mock_dataframe):
    assert mock_dataframe.called or True

# APRÈS (Réel)
def test_afficher_tableau_depenses(self, mock_write, mock_dataframe):
    """Teste l'affichage d'un tableau de dépenses"""
    from src.domains.maison.ui.depenses import afficher_tableau_depenses

    # Arrange: créer des données de test
    test_depenses = [
        {"id": 1, "nom": "Courses", "montant": 50.0, "categorie": "Alimentation"},
        {"id": 2, "nom": "Carburant", "montant": 60.0, "categorie": "Transport"}
    ]

    # Act: appeler la fonction
    afficher_tableau_depenses(test_depenses)

    # Assert: vérifier que les mocks ont été appelés correctement
    assert mock_dataframe.called

    # Vérifier que les bonnes données ont été passées
    call_args = mock_dataframe.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0]["nom"] == "Courses"
    assert call_args[1]["montant"] == 60.0

    # Vérifier que write a été appelé pour les titres
    assert mock_write.called
```

---

## ⏱️ Timeline

```
Day 1:      Lire guides, comprendre structure
Day 2-3:    Développer test_depenses.py
Day 4:      Développer test_components_init.py
Day 5:      Développer test_jules_planning.py
Day 6:      Développer test_planificateur_repas.py
Day 7:      Développer test_setup.py + test_integration.py
Week 2:     Validation complète PHASE 1, mesurer coverage
```

---

## 🚀 START NOW

1. **Lire cette doc**: ✅ DONE
2. **Ouvrir test_depenses.py**: `code tests/domains/maison/ui/test_depenses.py`
3. **Lire le source**: `cat src/domains/maison/ui/depenses.py | head -50`
4. **Écrire le 1er test réel** (copy-paste from examples ci-dessus)
5. **Tester**: `pytest tests/domains/maison/ui/test_depenses.py -v`
6. **Valider pas d'erreurs**: Doit passer ou échouer avec messages clairs
7. **Continuer** avec les 5 autres fichiers

---

## 💡 Tips & Tricks

**Trouver les imports corrects**:

```bash
grep -n "def " src/domains/maison/ui/depenses.py | head -20
```

**Tester un test unique**:

```bash
pytest tests/domains/maison/ui/test_depenses.py::TestDepensesUIDisplay::test_afficher_tableau_depenses -v
```

**Voir le détail des mocks**:

```python
@patch('streamlit.dataframe')
def test_something(self, mock_dataframe):
    # Après l'appel:
    print(mock_dataframe.call_args)  # Voir exactement ce qui a été appelé
    print(mock_dataframe.call_count)  # Nombre d'appels
```

**Vérifier les imports**:

```bash
python -c "from src.domains.maison.ui.depenses import afficher_tableau_depenses; print('OK')"
```

---

**C'est parti! 🚀 À vous de développer les vrais tests!**
