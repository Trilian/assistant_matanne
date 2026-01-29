# Organisation des Tests - Assistant Matanne

## Vue d'ensemble

L'application a **~2500+ tests** organisés sur **6 niveaux** :

### 1. **Tests Unitaires** (`tests/` et `tests/utils/`)
- **Utilité:** Tester les fonctions isolées et logique métier pure
- **Couverture:** Formatters, helpers, validators, utility functions
- **Fichiers:** ~90 fichiers
- **Statut:** ✅ Bien organisés

### 2. **Tests des Services** (`tests/services/`)
- **Utilité:** Tester les couches métier (CRUD, IA, API)
- **Fichiers:** ~40 fichiers
- **Services couverts:**
  - `test_recettes.py` - Services de recettes
  - `test_courses.py` - Services de courses
  - `test_planning.py` - Services de planification
  - `test_predictions.py` - Services de prédictions IA
  - `test_suggestions_ia_service.py` - Suggérations IA
  - `test_base_service.py` - Service de base
  - `test_notifications.py` - Notifications
  - `test_api.py` & `test_api_extended.py` - API REST
  - `test_auth.py` - Authentification
  - `test_backup.py` - Sauvegarde
  - `test_calendar_sync.py` - Synchronisation calendrier
  - `test_budget.py` - Gestion budget
  - `test_weather.py` - Services météo
  - `test_pwa.py` - Progressive Web App
  - Et 20+ autres services

### 3. **Tests d'Intégration** (`tests/integration/`)
- **Utilité:** Tester les interactions entre modules
- **Fichiers:** ~30 fichiers
- **Modules d'intégration:**
  - `test_cuisine.py` - Module cuisine intégré
  - `test_famille.py` - Module famille intégré
  - `test_planning.py` - Module planning intégré
  - `test_accueil.py` - Dashboard accueil
  - `test_offline.py` - Mode hors ligne
  - `test_planning_module.py` - Tests planning avancés
  - `test_rapports.py` - Génération de rapports
  - Et 10+ autres tests d'intégration

### 4. **Tests UI** (`tests/ui/`)
- **Utilité:** Tester les composants Streamlit
- **Fichiers:** ~12 fichiers
- **Couverture:**
  - `test_ui_atoms.py` - Composants atomiques
  - `test_ui_forms.py` - Formulaires
  - `test_ui_data.py` - Affichage de données
  - `test_ui_layouts.py` - Layouts
  - `test_ui_components.py` - Composants complexes
  - `test_ui_spinners.py` - Spinners et loaders
  - `test_ui_toasts.py` - Notifications visuelles
  - `test_ui_tablet_mode.py` - Mode tablette
  - `test_planning_components.py` - Composants planning
  - `test_dashboard_widgets.py` - Widgets tableau de bord
  - `test_ui_progress.py` - Barres de progression
  - `test_ui_base_form.py` - Formulaires de base

### 5. **Tests du Noyau** (`tests/core/`)
- **Utilité:** Tester les composants centraux
- **Fichiers:** ~15 fichiers
- **Couverture:**
  - `test_ai_parser.py` - Analyseur IA/JSON
  - `test_ai_cache.py` - Cache IA
  - `test_ai_agent_sync.py` - Agent IA synchrone
  - `test_cache.py` & `test_cache_multi.py` - Caching
  - `test_database.py` - Gestion base de données
  - `test_decorators.py` - Décorateurs
  - `test_lazy_loader.py` - Chargement différé
  - `test_state.py` - Gestion d'état
  - `test_performance.py` & `test_performance_optimizations.py` - Optimisations
  - `test_errors_base.py` - Gestion d'erreurs
  - `test_action_history.py` - Historique des actions

### 6. **Tests End-to-End** (`tests/e2e/`)
- **Utilité:** Tester les flux complets utilisateur
- **Fichiers:** 2-3 fichiers
- **Couverture:**
  - `test_e2e_streamlit.py` - Tests Streamlit complets
  - `test_e2e.py` - Scénarios utilisateur

### 7. **Tests Logique Métier** (`tests/logic/`)
- **Utilité:** Tester les modules logic (domaines)
- **Fichiers:** 4 fichiers
- **Couverture:**
  - `test_all_logic_modules.py` - Tous les modules logiques
  - `test_logic_modules_pure.py` - Fonctions pures
  - Et 2 autres

## Structure des Répertoires Source à Couvrir

```
src/
├── app.py                  # ✅ Point d'entrée principal
├── api/                    # ✅ API REST (bien couverte)
│   ├── main.py
│   ├── rate_limiting.py
│   └── __init__.py
├── core/                   # ✅ Noyau (bien couvert)
│   ├── ai/                 # ✅ IA & Parsing
│   ├── cache.py            # ✅ Caching
│   ├── decorators.py       # ✅ Décorateurs
│   ├── database.py         # ✅ BD
│   ├── config.py           # ✅ Configuration
│   ├── models/             # ⚠️  Modèles (couverture moyenne)
│   ├── performance.py      # ✅ Optimisations
│   └── ...
├── domains/                # ⚠️  Domaines métier
│   ├── cuisine/            # ✅ Bien couvert
│   │   ├── ui/
│   │   └── logic/
│   ├── famille/            # ✅ Bien couvert
│   │   ├── ui/
│   │   └── logic/
│   ├── planning/           # ✅ Bien couvert
│   │   ├── ui/
│   │   └── logic/
│   ├── maison/             # ⚠️  Couverture insuffisante
│   │   ├── ui/
│   │   └── logic/
│   ├── shared/             # ✅ Bien couvert
│   └── ...
├── services/               # ✅ Services bien couverts
│   ├── recettes.py         # ✅
│   ├── courses.py          # ✅
│   ├── planning.py         # ✅
│   ├── base_service.py     # ✅
│   ├── base_ai_service.py  # ✅
│   └── ...
├── ui/                     # ✅ Composants UI
│   ├── components/         # ✅ Bien couverts
│   ├── feedback/           # ✅ Bien couverts
│   ├── core/               # ✅ Bien couverts
│   └── ...
└── utils/                  # ✅ Utilitaires (excellent)
    ├── formatters/         # ✅ Tous les formatters testés
    ├── validators/         # ✅ Tous les validators testés
    ├── helpers/            # ✅ Tous les helpers testés
    └── ...
```

## Statut de Couverture par Domaine

| Domaine | Couverture | État |
|---------|-----------|------|
| **Utils** | ~100% | ✅ Excellent |
| **Services** | ~95% | ✅ Excellent |
| **UI Components** | ~90% | ✅ Très bon |
| **Core (IA, Cache, BD)** | ~85% | ✅ Très bon |
| **API** | ~75% | ✅ Bon |
| **Domains (Métier)** | ~65% | ⚠️ À améliorer |
| **E2E** | ~20% | ⚠️ Insuffisant |
| **Maison (Domain)** | ~40% | ⚠️ À créer |
| **Logic Modules** | ~35% | ⚠️ À améliorer |

## Objectif: 40% de Couverture Globale

**État actuel estimé:** ~35-38%  
**Cible:** 40%+

### Actions pour atteindre 40%:

1. **Créer tests manquants:**
   - [ ] `tests/domains/maison/` - 5 nouveaux fichiers
   - [ ] `tests/domains/planning/` - 3 nouveaux fichiers
   - [ ] `tests/domains/cuisine/` - 2 nouveaux fichiers
   - [ ] `tests/domains/famille/` - 2 nouveaux fichiers
   - [ ] `tests/logic/` - Améliorer la couverture existing

2. **Améliorer tests existants:**
   - [ ] Ajouter plus de cas edge dans les tests logic
   - [ ] Augmenter la couverture E2E (3 → 8 fichiers)
   - [ ] Ajouter des tests pour `src/app.py`

3. **Fichiers à créer en priorité:**
   - [ ] `tests/test_domains_module_loader.py`
   - [ ] `tests/integration/test_domains_comprehensive.py`
   - [ ] `tests/domains/maison/test_jardin_module.py`
   - [ ] `tests/domains/maison/test_projets_module.py`
   - [ ] `tests/domains/maison/test_entretien_module.py`

## Exécution des Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Tests spécifiques
pytest tests/core/ -v          # Tests du noyau
pytest tests/services/ -v      # Tests des services
pytest tests/ui/ -v            # Tests UI
pytest tests/integration/ -v   # Tests d'intégration

# Tests par marqueur
pytest -m unit              # Tests unitaires
pytest -m integration       # Tests d'intégration
pytest -m e2e              # Tests end-to-end

# Mode watch (si pytest-watch installé)
ptw tests/ -- -v
```

## Organisation des Marqueurs Pytest

Fichier `pyproject.toml` (section `[tool.pytest.ini_options]`):

```ini
markers =
    unit: Tests unitaires (pas de BD)
    integration: Tests d'intégration (avec BD)
    e2e: Tests end-to-end (flux complets)
    services: Tests des services
    ui: Tests des composants UI
    core: Tests du noyau
    slow: Tests lents
    skip_in_ci: À ignorer en CI
```

## Conventions des Tests

### Nomenclature des Fichiers
- `test_*.py` pour les tests unitaires simples
- `test_*_service.py` pour les tests de service
- `test_*_integration.py` ou dans `tests/integration/`
- `test_*_module.py` ou `test_*_components.py` pour les modules

### Structure des Cas de Test

```python
class TestNomDuModule:
    """Tests pour NomDuModule."""
    
    def test_scenario_positif(self):
        """Cas nominal."""
        # Setup
        # Action
        # Assert
        
    def test_scenario_edge_case(self):
        """Cas limites."""
        # ...
        
    def test_scenario_erreur(self):
        """Gestion des erreurs."""
        # ...
        pytest.raises(Exception)
```

### Fixtures Courantes

```python
# Fournis par conftest.py
@pytest.fixture
def test_db():      # BD de test (SQLite en mémoire)
    pass

@pytest.fixture
def mock_streamlit():  # Mock Streamlit (évite l'UI)
    pass

@pytest.fixture  
def app_config():   # Configuration de test
    pass
```

## Prochaines Étapes

1. **Immédiat:** Exécuter `pytest --cov=src --cov-report=html` pour avoir la couverture exacte
2. **Court terme:** Créer 5-10 tests manquants dans les domaines insuffisants
3. **Moyen terme:** Atteindre 40% + améliorer qualité des tests E2E
4. **Long terme:** Viser 60-70% de couverture

---

**Dernière mise à jour:** 2026-01-29  
**Statut:** 📋 À améliorer
