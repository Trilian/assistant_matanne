"""
conftest.py - Configuration pytest centralisée pour tests UI et Utils

Fournit des fixtures partagées pour tous les tests de UI et Utils.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os


# ═══════════════════════════════════════════════════════════
# MARKERS
# ═══════════════════════════════════════════════════════════

def pytest_configure(config):
    """Enregistrer les markers personnalisés."""
    config.addinivalue_line(
        "markers", "unit: marque les tests unitaires"
    )
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "ui: marque les tests UI (Streamlit)"
    )
    config.addinivalue_line(
        "markers", "utils: marque les tests Utils"
    )
    config.addinivalue_line(
        "markers", "performance: marque les tests de performance"
    )
    config.addinivalue_line(
        "markers", "endpoint: marque les tests d'endpoints"
    )


# ═══════════════════════════════════════════════════════════
# STREAMLIT MOCKS - Pour les tests UI
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state et fonctions."""
    with patch('streamlit') as mock_st:
        # Session state mock
        mock_session = MagicMock()
        mock_session.__setitem__ = Mock()
        mock_session.__getitem__ = Mock()
        mock_session.get = Mock(return_value=None)
        
        mock_st.session_state = mock_session
        
        # UI components mock
        mock_st.write = Mock()
        mock_st.title = Mock()
        mock_st.header = Mock()
        mock_st.subheader = Mock()
        mock_st.text = Mock()
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        mock_st.checkbox = Mock(return_value=False)
        mock_st.radio = Mock(return_value=None)
        mock_st.selectbox = Mock(return_value=None)
        mock_st.multiselect = Mock(return_value=[])
        mock_st.slider = Mock(return_value=0)
        mock_st.text_input = Mock(return_value="")
        mock_st.text_area = Mock(return_value="")
        mock_st.number_input = Mock(return_value=0)
        mock_st.date_input = Mock()
        mock_st.time_input = Mock()
        mock_st.file_uploader = Mock(return_value=None)
        
        # Layout mocks
        mock_st.container = MagicMock()
        mock_st.columns = Mock(return_value=[MagicMock(), MagicMock()])
        mock_st.tabs = Mock(return_value=[MagicMock(), MagicMock()])
        mock_st.expander = MagicMock()
        mock_st.sidebar = MagicMock()
        mock_st.form = MagicMock()
        
        # Data display
        mock_st.table = Mock()
        mock_st.dataframe = Mock()
        mock_st.chart = Mock()
        mock_st.metric = Mock()
        mock_st.progress = Mock()
        
        # Messages
        mock_st.success = Mock()
        mock_st.info = Mock()
        mock_st.warning = Mock()
        mock_st.error = Mock()
        
        # Spinner and status
        mock_st.spinner = MagicMock()
        mock_st.status = MagicMock()
        
        # Secrets
        mock_st.secrets = MagicMock()
        
        yield mock_st


# ═══════════════════════════════════════════════════════════
# DATABASE FIXTURES - Pour tous les tests
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def temp_db():
    """Fournir une base de données temporaire."""
    # En mémoire SQLite pour les tests
    from sqlalchemy import create_engine
    
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()


@pytest.fixture
def mock_session():
    """Mock de session SQLAlchemy."""
    session = MagicMock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.query = Mock()
    session.execute = Mock()
    session.close = Mock()
    
    yield session


# ═══════════════════════════════════════════════════════════
# DATETIME FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def current_date():
    """Date actuelle."""
    from datetime import date
    return date(2026, 1, 15)


@pytest.fixture
def current_datetime():
    """Datetime actuel."""
    from datetime import datetime
    return datetime(2026, 1, 15, 14, 30, 0)


@pytest.fixture
def past_date():
    """Date dans le passé."""
    from datetime import datetime, timedelta
    return (datetime.now() - timedelta(days=7)).date()


@pytest.fixture
def future_date():
    """Date dans le futur."""
    from datetime import datetime, timedelta
    return (datetime.now() + timedelta(days=7)).date()


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_recipe():
    """Recette exemple."""
    return {
        "name": "Tarte aux Pommes",
        "description": "Tarte classique",
        "servings": 4,
        "cooking_time": 45,
        "preparation_time": 15,
        "ingredients": [
            {"name": "Pommes", "quantity": 500, "unit": "g"},
            {"name": "Farine", "quantity": 200, "unit": "g"},
            {"name": "Sucre", "quantity": 100, "unit": "g"}
        ],
        "steps": [
            "Préparer la pâte",
            "Préparer les pommes",
            "Assembler la tarte",
            "Cuire 45 minutes"
        ]
    }


@pytest.fixture
def sample_recipes():
    """Plusieurs recettes exemple."""
    return [
        {
            "name": "Tarte aux Pommes",
            "cooking_time": 45
        },
        {
            "name": "Gâteau au Chocolat",
            "cooking_time": 40
        },
        {
            "name": "Salade Verte",
            "cooking_time": 10
        }
    ]


@pytest.fixture
def sample_ingredient():
    """Ingrédient exemple."""
    return {
        "name": "Tomate",
        "quantity": 200,
        "unit": "g",
        "category": "Légume"
    }


@pytest.fixture
def sample_form_data():
    """Données de formulaire exemple."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "category": "admin"
    }


# ═══════════════════════════════════════════════════════════
# MOCK DECORATORS FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_db_decorator():
    """Mock le décorateur @with_db_session."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs['db'] = MagicMock()
            return func(*args, **kwargs)
        return wrapper
    
    return decorator


@pytest.fixture
def mock_cache_decorator():
    """Mock le décorateur @with_cache."""
    def decorator(func):
        return func
    
    return decorator


# ═══════════════════════════════════════════════════════════
# MOCK BUILDERS - Pour construire des objets de test
# ═══════════════════════════════════════════════════════════

class FormBuilder:
    """Builder pour construire des formulaires de test."""
    
    def __init__(self):
        self.fields = []
        self.validators = {}
        self.title = "Test Form"
    
    def add_field(self, name, field_type, required=False):
        self.fields.append({
            "name": name,
            "type": field_type,
            "required": required
        })
        return self
    
    def add_validator(self, field_name, validator_func):
        self.validators[field_name] = validator_func
        return self
    
    def build(self):
        return {
            "title": self.title,
            "fields": self.fields,
            "validators": self.validators
        }


@pytest.fixture
def form_builder():
    """Builder pour formulaires."""
    return FormBuilder()


class DataGridBuilder:
    """Builder pour DataGrid."""
    
    def __init__(self):
        self.data = []
        self.columns = []
        self.sortable = False
        self.filterable = False
    
    def add_row(self, **kwargs):
        self.data.append(kwargs)
        return self
    
    def add_column(self, key, label):
        self.columns.append({"key": key, "label": label})
        return self
    
    def sortable_enabled(self):
        self.sortable = True
        return self
    
    def filterable_enabled(self):
        self.filterable = True
        return self
    
    def build(self):
        return {
            "data": self.data,
            "columns": self.columns,
            "sortable": self.sortable,
            "filterable": self.filterable
        }


@pytest.fixture
def data_grid_builder():
    """Builder pour DataGrid."""
    return DataGridBuilder()


# ═══════════════════════════════════════════════════════════
# ASSERTION HELPERS
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def assert_valid_recipe():
    """Assertion helper pour recettes."""
    def _assert(recipe):
        assert isinstance(recipe, dict)
        assert "name" in recipe
        assert "ingredients" in recipe
        assert "steps" in recipe
        assert isinstance(recipe["ingredients"], list)
        assert isinstance(recipe["steps"], list)
    
    return _assert


@pytest.fixture
def assert_valid_form_data():
    """Assertion helper pour données de formulaire."""
    def _assert(data, required_fields):
        assert isinstance(data, dict)
        for field in required_fields:
            assert field in data
    
    return _assert


@pytest.fixture
def assert_valid_response():
    """Assertion helper pour réponses API."""
    def _assert(response, expected_status=200):
        if hasattr(response, 'status_code'):
            assert response.status_code == expected_status
        
        if hasattr(response, 'json'):
            data = response.json()
            assert isinstance(data, (dict, list))
    
    return _assert


# ═══════════════════════════════════════════════════════════
# HOOKS PYTEST
# ═══════════════════════════════════════════════════════════

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook pour les rapports de test."""
    outcome = yield
    rep = outcome.get_result()
    
    # Peut être utilisé pour logging personnalisé
    if rep.failed:
        # Log failed tests
        pass


# ═══════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════

def pytest_unconfigure(config):
    """Nettoyage après les tests."""
    pass


# ═══════════════════════════════════════════════════════════
# PARAMETRIZATION FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture(params=["email", "url", "phone", "password"])
def validation_type(request):
    """Paramétriser les types de validation."""
    return request.param


@pytest.fixture(params=["grams", "kg", "ml", "liters"])
def unit_type(request):
    """Paramétriser les types d'unités."""
    return request.param


@pytest.fixture(params=["success", "info", "warning", "error"])
def notification_type(request):
    """Paramétriser les types de notifications."""
    return request.param
