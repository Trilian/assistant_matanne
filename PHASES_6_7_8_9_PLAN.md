# 🚀 PHASES 6-9: Plan Détaillé pour Atteindre 80% de Couverture

**Date**: Février 3, 2026  
**Couverture actuelle**: 55%  
**Couverture cible**: 80%  
**Gap**: 25 points de pourcentage  
**Effort estimé**: 17-21 heures  
**Timeline**: 2-3 jours de travail intensif

---

## 📊 Vue d'Ensemble des Phases

```
PHASE 6 (2-3h)   → Corriger erreurs collection       55% → 58-59%
PHASE 7 (4-5h)   → Couvrir fichiers UI massifs       59% → 64-66%
PHASE 8 (5-6h)   → Couvrir services critiques        66% → 71-74%
PHASE 9 (6-7h)   → Tests d'intégration cross-domain  74% → 80%+
────────────────────────────────────────────────────────────────────
TOTAL: ~17-21h pour +25% de couverture!
```

---

## ⚠️ PHASE 6: Corriger Erreurs de Collection (2-3h)

### Problème:

9 fichiers de test causent des erreurs de collection qui **bloquent pytest** complètement.

### Fichiers à corriger:

#### 1. `tests/test_parametres.py`

**Erreur**: Probablement import ou classe test mal nommée
**Action**:

- [ ] Vérifier imports (pytest, streamlit, models)
- [ ] Vérifier noms de classes (test\__ ou Test_)
- [ ] Vérifier pas de code exécuté au niveau module
      **Fichier**: ~250 lignes
      **Tests**: 15-20 tests

#### 2. `tests/test_rapports.py`

**Erreur**: Même problème que parametres
**Action**:

- [ ] Vérifier structure du fichier
- [ ] Corriger imports cassés
      **Fichier**: ~192 lignes
      **Tests**: 10-15 tests

#### 3. `tests/test_recettes_import.py`

**Erreur**: Import service non trouvé?
**Action**:

- [ ] Vérifier imports de services
- [ ] Corriger chemins de module
      **Fichier**: ~150 lignes
      **Tests**: 8-10 tests

#### 4. `tests/test_vue_ensemble.py`

**Erreur**: Module UI non trouvé?
**Action**:

- [ ] Vérifier import du module ui
- [ ] Corriger patch decorators
      **Fichier**: ~100 lignes
      **Tests**: 5-8 tests

#### 5-9. Tests dans `tests/domains/*/`

**Erreurs**: Multiples domaines (famille, maison, planning)
**Action**:

- [ ] Vérifier chaque fichier individuellement
- [ ] Corriger imports domaines
- [ ] Tester isolation entre domaines

### Vérification PHASE 6 - Avant/Après:

**AVANT**:

```bash
$ pytest --co -q
collected 2499 items / 9 errors  ❌
```

**APRÈS** (attendu):

```bash
$ pytest --co -q
collected 2500+ items            ✅
```

### Commandes de debug PHASE 6:

```bash
# Tester chaque fichier individuellement
pytest tests/test_parametres.py -v --tb=short
pytest tests/test_rapports.py -v --tb=short
pytest tests/test_recettes_import.py -v --tb=short
pytest tests/test_vue_ensemble.py -v --tb=short

# Une fois tous OK:
pytest --cov=src --cov-report=term-missing --tb=no -q
```

---

## 🎨 PHASE 7: Couvrir Fichiers UI Massifs (4-5h)

### Fichiers prioritaires (0% → 75%+):

#### 1. `src/domains/cuisine/ui/planificateur_repas.py` - **375 lignes** ⭐

**Couverture cible**: 0% → 75%  
**Gain**: +3.75%  
**Effort**: 2h (~50 tests)

**Ce qu'il faut tester**:

```python
- Affichage calendar de planification
- Sélection dates
- Composition planification (petit-déj, déj, dîner)
- Suggestions IA
- Modifications planification
- Exports/partage
- Filtres et recherche
- Interactions utilisateur (sliders, dropdowns, etc)
```

**Patterns testés** (avec @patch):

```python
st.title(), st.subheader()
st.calendar()
st.button(), st.selectbox()
st.columns()
st.session_state
StateManager operations
```

**Structure test recommandée**:

```
tests/domains/cuisine/ui/test_planificateur_repas.py
├─ TestPlanificateurDisplay (5-8 tests)
├─ TestPlanificateurInteraction (8-10 tests)
├─ TestPlanificateurData (10-15 tests)
├─ TestPlanificateurIntegration (5-8 tests)
└─ TestPlanificateurEdgeCases (3-5 tests)
```

#### 2. `src/domains/famille/ui/jules_planning.py` - **163 lignes**

**Couverture cible**: 0% → 75%  
**Gain**: +1.63%  
**Effort**: 1.5h (~30 tests)

**Ce qu'il faut tester**:

```python
- Affichage planning Jules (enfant)
- Jalons développement (17m-19m-24m, etc)
- Vaccins et suivi médical
- Activités et routines
- Croissance et poids
- Photos et mémorables
```

#### 3. `src/domains/planning/ui/components/__init__.py` - **110 lignes**

**Couverture cible**: 0% → 75%  
**Gain**: +1.10%  
**Effort**: 1h (~20 tests)

**Ce qu'il faut tester**:

```python
- Composants planning (calendrier, liste, kanban)
- Sélection périodes
- Filtrage événements
- Tri événements
```

### Structure commune pour PHASE 7:

```python
# tests/domains/[domain]/ui/test_[module].py

import pytest
from unittest.mock import patch, MagicMock

@patch('streamlit.title')
@patch('streamlit.subheader')
@patch('streamlit.columns')
def test_display_basic(self, mock_col, mock_sub, mock_title):
    """Test l'affichage basique du module"""
    mock_col.return_value = [MagicMock(), MagicMock()]
    mock_title.return_value = None
    mock_sub.return_value = None

    # Importer et exécuter la fonction principale
    from src.domains.[domain].ui.[module] import app
    app()

    # Vérifier que les éléments UI ont été appelés
    assert mock_title.called
    assert mock_sub.called
    assert mock_col.called
```

---

## 🔧 PHASE 8: Couvrir Services Critiques (5-6h)

### Services prioritaires (< 30% → 75%+):

#### 1. `src/services/planning.py` - **250+ lignes** ⭐⭐

**Couverture actuelle**: 23%  
**Couverture cible**: 75%  
**Gain**: +5.2%  
**Effort**: 2h (~60 tests)

**Fonctionnalités à tester**:

```python
- Créer événement
- Mettre à jour événement
- Supprimer événement
- Lister événements (avec filtres)
- Obtenir événement par ID
- Synchroniser calendriers
- Gérer récurrences
- Gérer notifications
- Export iCal
- Partage calendrier
```

**Structure test**:

```
tests/services/test_planning_extended.py
├─ TestPlanningCreate (5-8 tests)
├─ TestPlanningRead (5-8 tests)
├─ TestPlanningUpdate (5-8 tests)
├─ TestPlanningDelete (3-5 tests)
├─ TestPlanningFilter (8-10 tests)
├─ TestPlanningIntegration (10-15 tests)
└─ TestPlanningEdgeCases (5-8 tests)
```

#### 2. `src/services/inventaire.py` - **200+ lignes**

**Couverture actuelle**: 18%  
**Couverture cible**: 75%  
**Gain**: +5.7%  
**Effort**: 1.5h (~45 tests)

**Fonctionnalités**:

- CRUD stock
- Alertes stock bas
- Historique mouvements
- Catégorisation items
- Expiration produits
- Rapports stock

#### 3. `src/services/maison.py` - **300+ lignes**

**Couverture actuelle**: 12%  
**Couverture cible**: 70%  
**Gain**: +5.8%  
**Effort**: 1.5h (~50 tests)

**Fonctionnalités**:

- Gestion tâches maison
- Maintenance appliances
- Budget maison
- Stocks fournitures
- Nettoyage planning
- Réparations

### Patterns de test pour services:

```python
# tests/services/test_[service]_extended.py

import pytest
from sqlalchemy.orm import Session
from src.services.[service] import [ServiceClass]
from src.core.models import [Model]
from unittest.mock import patch, MagicMock

@pytest.fixture
def service(test_db: Session):
    """Fixture service avec DB de test"""
    return [ServiceClass](test_db)

def test_create_item_basic(service):
    """Test création d'item simple"""
    data = {"nom": "Test", "description": "Test"}
    result = service.creer([Model](**data))

    assert result.nom == "Test"
    assert result.id is not None

def test_list_with_filters(service, test_db):
    """Test listing avec filtres"""
    # Setup
    for i in range(5):
        service.creer([Model](nom=f"Item {i}"))

    # Test
    results = service.lister(filtre="Item 1")
    assert len(results) == 1
    assert results[0].nom == "Item 1"
```

---

## 🔗 PHASE 9: Tests d'Intégration Cross-Domain (6-7h)

### Objectif:

Tester les **workflows complets** qui traversent plusieurs domaines:

#### 1. Workflow Cuisine → Courses → Maison (~15 tests)

**Scénario**:

```
1. User crée une recette (cuisine)
   → Suggère ingrédients manquants
2. Ajoute ingrédients à la liste de courses (courses)
   → Crée article dans inventaire
3. Après courses, met à jour stock (maison/inventaire)
   → Notifie si item expira bientôt
4. Planning utilise stock pour suggestions (planning)
```

**Tests à créer**:

```
tests/e2e/test_kitchen_shopping_workflow.py
├─ test_recipe_to_shopping_list
├─ test_shopping_to_inventory
├─ test_inventory_to_meal_planning
├─ test_expiry_notifications
├─ test_complete_cooking_cycle
└─ test_error_handling_workflow
```

#### 2. Workflow Famille Jules (~10 tests)

**Scénario**:

```
1. Enregistrer jalons Jules (famille/jules)
2. Ajouter vaccin (suivi santé)
3. Planifier activité d'apprentissage (planning)
4. Notifier milestones atteints
5. Générer rapport développement
```

#### 3. Data Consistency Tests (~8 tests)

**Vérifier**:

```python
- Contraintes d'intégrité
- Cascade deletes
- Transaction rollbacks
- Concurrency handling
- Cache invalidation
- State synchronization
```

#### 4. Performance & Scale Tests (~5 tests)

**Tester**:

```python
- Listing 1000+ items
- Filtering large datasets
- Report generation avec gros volumes
- Concurrent operations
- Memory usage
```

#### 5. Error Recovery Tests (~8 tests)

**Vérifier**:

```python
- API errors → user-friendly messages
- DB connection issues
- Timeout handling
- Partial failures
- Retry mechanisms
- Data cleanup after errors
```

### Structure PHASE 9:

```
tests/e2e/
├─ test_kitchen_shopping_workflow.py (15 tests)
├─ test_famille_jules_workflow.py (10 tests)
├─ test_data_consistency.py (8 tests)
├─ test_performance_scale.py (5 tests)
├─ test_error_recovery.py (8 tests)
└─ test_advanced_scenarios.py (8 tests)
```

---

## 📈 Progression Estimée par Phase

### PHASE 6 (Correction erreurs)

```
Tests à ajouter: ~50-80 (correction + tests des fichiers fixés)
Gain couverture: +3-4%
Résultat: 55% → 58-59%
Pass rate: 99%+
```

### PHASE 7 (UI Massifs)

```
Tests à ajouter: ~100-120
Gain couverture: +5-7%
Résultat: 59% → 64-66%
Pass rate: 98%+
```

### PHASE 8 (Services)

```
Tests à ajouter: ~150-180
Gain couverture: +5-8%
Résultat: 66% → 71-74%
Pass rate: 97%+
```

### PHASE 9 (Intégration)

```
Tests à ajouter: ~50-60
Gain couverture: +6-8%
Résultat: 74% → 80%+
Pass rate: 96%+
```

### TOTAL Phases 6-9:

```
Tests créés: ~350-440
Gain total: +25%
Résultat final: 55% → 80%+
Temps: 17-21 heures
Pass rate global: 96%+
```

---

## 🎯 Commandes Clés par Phase

### PHASE 6 - Validation:

```bash
# Tester chaque fichier individuellement
pytest tests/test_parametres.py -v
pytest tests/test_rapports.py -v
pytest tests/test_recettes_import.py -v
pytest tests/test_vue_ensemble.py -v
pytest tests/domains/famille/ui/test_routines.py -v
pytest tests/domains/maison/services/test_inventaire.py -v
pytest tests/domains/maison/ui/test_courses.py -v
pytest tests/domains/maison/ui/test_paris.py -v
pytest tests/domains/planning/ui/components/test_init.py -v

# Une fois tous OK - couverture complète:
python manage.py test_coverage
```

### PHASE 7 - UI Tests:

```bash
# Ajouter fichiers
pytest tests/domains/cuisine/ui/test_planificateur_repas.py -v --cov
pytest tests/domains/famille/ui/test_jules_planning.py -v --cov
pytest tests/domains/planning/ui/components/test_components_init_extended.py -v --cov
```

### PHASE 8 - Services:

```bash
# Tester services spécifiques
pytest tests/services/test_planning_extended.py -v --cov=src/services/planning.py
pytest tests/services/test_inventaire_extended.py -v --cov=src/services/inventaire.py
pytest tests/services/test_maison_extended.py -v --cov=src/services/maison.py
```

### PHASE 9 - E2E:

```bash
# Tous les E2E tests
pytest tests/e2e/ -v --cov
```

### Final - Rapport complet:

```bash
python manage.py test_coverage
# Vérifier: 80%+
```

---

## 📝 Template Général pour Chaque Test

```python
"""
Tests pour [module/service].
Objectif: Atteindre 75%+ de couverture pour [description].
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

# Fixtures
@pytest.fixture
def db_session(test_db: Session):
    """Fixture DB pour tests"""
    return test_db

@pytest.fixture
def mock_streamlit():
    """Mock tous les éléments streamlit"""
    with patch('streamlit.title'), \
         patch('streamlit.subheader'), \
         patch('streamlit.write'), \
         patch('streamlit.button') as m_btn:
        m_btn.return_value = False
        yield

# Tests
class TestModuleBasic:
    """Tests basiques de fonctionnalité"""

    def test_afficher_interface(self, mock_streamlit):
        """Tester affichage interface"""
        # Setup
        # Action
        # Assert

class TestModuleInteraction:
    """Tests interactions utilisateur"""

    def test_interaction_button_click(self):
        """Tester clic bouton"""
        pass

class TestModuleData:
    """Tests données/persistence"""

    def test_create_and_retrieve(self, db_session):
        """Tester CRUD"""
        pass

class TestModuleIntegration:
    """Tests intégration avec autres modules"""

    def test_workflow_complet(self, db_session):
        """Tester workflow complet"""
        pass

class TestModuleEdgeCases:
    """Tests cas limites"""

    def test_error_handling(self):
        """Tester gestion erreurs"""
        pass
```

---

## 🚀 Prochaines Étapes

### Immédiatement:

1. Exécuter PHASE 6 - corriger les 9 fichiers cassés
2. Valider avec `pytest --co -q` (pas d'erreurs)
3. Réexécuter couverture globale

### Puis:

4. Exécuter PHASE 7 - tester UI massifs (3 fichiers)
5. Exécuter PHASE 8 - tester services (3 services)
6. Exécuter PHASE 9 - tests E2E cross-domain

### Final:

7. Couverture globale: 80%+ ✅
8. Pass rate: 95%+ ✅
9. Commit: "Phases 6-9: Reach 80% test coverage"

---

## 📌 Notes Importantes

- ✅ Patterns de test sont déjà établis (voir PHASE 1-5)
- ✅ Création sera RAPIDE (44x plus rapide que estimé)
- ⚠️ PHASE 6 est **BLOQUANTE** - corriger d'abord!
- ✅ Chaque phase peut être exécutée indépendamment
- ✅ Total 17-21 heures pour +25% = très faisable
