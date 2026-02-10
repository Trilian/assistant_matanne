"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database setup and cleanup
- Service instances
- Test data factories
- Mock clients (IA, cache)
"""

import sys
import os
import warnings
from pathlib import Path

# Suppress Streamlit warnings when running tests outside Streamlit context
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*Session state does not function.*")
warnings.filterwarnings("ignore", message=".*No runtime found.*")

# Configurer le chemin pour les imports
workspace_root = Path(__file__).parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.core.models import (
    Base,
    Recette,
    Ingredient,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    ArticleInventaire,
    Planning,
    Repas,
    ArticleCourses,
    ListeCourses,
    ChildProfile,
    WellbeingEntry,
    Milestone,
    FamilyActivity,
    CalendarEvent,
    HealthRoutine,
    HealthObjective,
    HealthEntry,
    BatchMeal,
)
from src.services.recettes import RecetteService
from src.services.inventaire import InventaireService
from src.services.planning import PlanningService
from src.services.courses import CoursesService


# ==================== DATABASE SETUP - SQLite JSON compatibility ====================

def adapt_jsonb_for_sqlite(connection, record):
    """Adapt JSONB types for SQLite compatibility."""
    # This is handled at DDL creation time with the event listener
    pass


@pytest.fixture(scope="session")
def test_db_url():
    """Test database URL (SQLite in-memory)."""
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Create test database engine with SQLite JSON support."""
    
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=StaticPool,
    )
    
    # Monkey patch JSONB compiler for SQLite
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
    from sqlalchemy.sql import sqltypes
    
    original_process = SQLiteTypeCompiler.process
    
    def patched_process(self, type_, **kw):
        """Patch JSONB to JSON for SQLite."""
        # Import here to avoid circular imports
        from sqlalchemy.dialects.postgresql import JSONB
        
        if isinstance(type_, JSONB):
            return "JSON"
        return original_process(self, type_, **kw)
    
    SQLiteTypeCompiler.process = patched_process
    
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        """Enable JSON1 extension and foreign keys for SQLite."""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        cursor.close()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(engine):
    """Create fresh database session for each test with proper isolation."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    # Ensure clean state
    for table in reversed(Base.metadata.sorted_tables):
        try:
            session.execute(table.delete())
        except Exception:
            pass
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_db(db):
    """Alias for db fixture - backwards compatibility."""
    return db


@pytest.fixture
def mock_session(db):
    """Alias for db fixture - backwards compatibility with older tests."""
    return db


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SERVICE FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture
def recette_service():
    """RecetteService instance for testing."""
    return RecetteService()


@pytest.fixture
def inventaire_service():
    """InventaireService instance for testing."""
    return InventaireService()


@pytest.fixture
def planning_service(patch_db_context):
    """PlanningService instance for testing with test DB."""
    return PlanningService()


@pytest.fixture
def courses_service(patch_db_context):
    """CoursesService instance for testing with test DB."""
    return CoursesService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTORY FIXTURES (Test Data)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class RecetteFactory:
    """Factory for creating test recipes."""
    
    def __init__(self, db: Session):
        self.db = db
        self.counter = 0
    
    def create(
        self,
        nom: str = None,
        description: str = None,
        temps_preparation: int = 30,
        temps_cuisson: int = 20,
        portions: int = 4,
        difficulte: str = "moyen",
        type_repas: str = "dîner",
        saison: str = "toute_année",
    ) -> Recette:
        """Create and save a test recipe."""
        self.counter += 1
        
        if nom is None:
            nom = f"Recette Test {self.counter}"
        if description is None:
            description = f"Description for {nom}"
        
        recette = Recette(
            nom=nom,
            description=description,
            temps_preparation=temps_preparation,
            temps_cuisson=temps_cuisson,
            portions=portions,
            difficulte=difficulte,
            type_repas=type_repas,
            saison=saison,
        )
        self.db.add(recette)
        self.db.commit()
        self.db.refresh(recette)
        return recette


class IngredientFactory:
    """Factory for creating test ingredients."""
    
    def __init__(self, db: Session):
        self.db = db
        self.counter = 0
    
    def create(
        self,
        nom: str = None,
        unite: str = "g",
        categorie: str = "Légumes",
    ) -> Ingredient:
        """Create and save a test ingredient."""
        self.counter += 1
        
        if nom is None:
            nom = f"Ingredient {self.counter}"
        
        ingredient = Ingredient(
            nom=nom,
            unite=unite,
            categorie=categorie,
        )
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient


class PlanningFactory:
    """Factory for creating test planning."""
    
    def __init__(self, db: Session):
        self.db = db
        self.counter = 0
    
    def create(
        self,
        nom: str = None,
        semaine_debut: date = None,
        genere_par_ia: bool = False,
    ) -> Planning:
        """Create and save a test planning."""
        self.counter += 1
        
        if nom is None:
            nom = f"Planning {self.counter}"
        if semaine_debut is None:
            semaine_debut = date.today()
        
        planning = Planning(
            nom=nom,
            semaine_debut=semaine_debut,
            semaine_fin=semaine_debut + timedelta(days=6),
            actif=True,
            genere_par_ia=genere_par_ia,
        )
        self.db.add(planning)
        self.db.commit()
        self.db.refresh(planning)
        return planning


@pytest.fixture
def recette_factory(db: Session) -> RecetteFactory:
    """Recipe factory fixture."""
    return RecetteFactory(db)


@pytest.fixture
def ingredient_factory(db: Session) -> IngredientFactory:
    """Ingredient factory fixture."""
    return IngredientFactory(db)


@pytest.fixture
def planning_factory(db: Session) -> PlanningFactory:
    """Planning factory fixture."""
    return PlanningFactory(db)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SAMPLE DATA FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture
def sample_recipe(recette_factory):
    """Create a sample recipe for testing."""
    return recette_factory.create(
        nom="Poulet Rôti",
        description="Poulet rôti aux herbes",
        temps_preparation=15,
        temps_cuisson=60,
        portions=6,
        difficulte="facile",
    )


@pytest.fixture
def sample_ingredients(ingredient_factory):
    """Create sample ingredients for testing."""
    return {
        "poulet": ingredient_factory.create("Poulet", "kg", "Protéines"),
        "citron": ingredient_factory.create("Citron", "pcs", "Fruits"),
        "thym": ingredient_factory.create("Thym", "g", "Epices & Condiments"),
    }


@pytest.fixture
def sample_planning(planning_factory):
    """Create a sample planning for testing."""
    return planning_factory.create(
        nom="Semaine du 13 janvier",
        semaine_debut=date(2026, 1, 13),
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# COURSES FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@pytest.fixture
def sample_articles():
    """Sample articles for courses tests"""
    return [
        {
            'id': 1,
            'ingredient_id': 1,
            'ingredient_nom': 'Tomates',
            'quantite_necessaire': 2.0,
            'unite': 'kg',
            'priorite': 'haute',
            'achete': False,
            'rayon_magasin': 'Fruits & Légumes',
            'notes': None,
            'suggere_par_ia': False
        },
        {
            'id': 2,
            'ingredient_id': 2,
            'ingredient_nom': 'Oeufs',
            'quantite_necessaire': 6.0,
            'unite': 'pièce',
            'priorite': 'moyenne',
            'achete': False,
            'rayon_magasin': 'Laitier',
            'notes': 'Bio si possible',
            'suggere_par_ia': False
        },
    ]


@pytest.fixture
def sample_suggestions():
    """Sample IA suggestions for courses"""
    from unittest.mock import Mock
    
    mock_suggestions = [
        Mock(nom='Tomates', quantite=2.0, unite='kg', priorite='haute', rayon='Fruits & Légumes'),
        Mock(nom='Oeufs', quantite=6.0, unite='pièce', priorite='moyenne', rayon='Laitier'),
        Mock(nom='Pain', quantite=1.0, unite='pièce', priorite='moyenne', rayon='Boulangerie')
    ]
    return mock_suggestions


@pytest.fixture
def courses_service_instance(db_session):
    """Get or create CoursesService instance for tests"""
    return CoursesService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PYTEST CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "courses: mark test as courses module test"
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPER FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STREAMLIT MOCK UTILITIES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class SessionStateMock(dict):
    """
    Mock for Streamlit's session_state that supports both
    attribute access (st.session_state.key) and 
    dict access (st.session_state["key"]).
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


def create_streamlit_mock(session_state_data: dict = None):
    """
    Creates a configured Streamlit mock with SessionStateMock.
    
    Args:
        session_state_data: Initial data for session_state
        
    Returns:
        MagicMock configured for Streamlit testing
    """
    from unittest.mock import MagicMock
    
    mock_st = MagicMock()
    mock_st.session_state = SessionStateMock(session_state_data or {})
    
    # Configure context managers for columns/tabs
    def create_context_mock():
        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=ctx)
        ctx.__exit__ = MagicMock(return_value=False)
        return ctx
    
    # Default columns behavior
    mock_st.columns = MagicMock(side_effect=lambda *args, **kwargs: 
        [create_context_mock() for _ in range(args[0] if args and isinstance(args[0], int) else 2)])
    
    # Default tabs behavior  
    mock_st.tabs = MagicMock(side_effect=lambda labels: 
        [create_context_mock() for _ in labels])
    
    return mock_st


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before/after each test."""
    try:
        from src.core.cache import Cache
        # Clear before test - catch errors when st.session_state is unavailable
        try:
            Cache.clear()
        except Exception:
            pass  # Ignore errors when running outside Streamlit context
        yield
        # Clear after test
        try:
            Cache.clear()
        except Exception:
            pass  # Ignore errors when running outside Streamlit context
    except ImportError:
        yield


@pytest.fixture
def patch_db_context(db):
    """
    Fixture that patches get_db_context and obtenir_contexte_db to use test session.
    
    This allows services that use @with_db_session to work with the test database
    instead of the production database.
    
    Usage:
        def test_service_method(patch_db_context, recette_service):
            # recette_service methods will now use test DB
            result = recette_service.lister_recettes()
            assert result is not None
    """
    from unittest.mock import patch
    from contextlib import contextmanager
    
    @contextmanager
    def mock_db_context():
        """Returns the test session instead of production."""
        yield db
    
    # Patch both French and English function names
    with patch("src.core.database.get_db_context", mock_db_context):
        with patch("src.core.database.obtenir_contexte_db", mock_db_context):
            yield db


@pytest.fixture(autouse=True)
def mock_mistral_api(monkeypatch):
    """Mock Mistral AI API for all tests."""
    import os
    
    # Set fake API key to prevent initialization errors
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key-12345")
    
    # Mock the ClientIA class to avoid actual API calls
    from unittest.mock import MagicMock, patch
    
    mock_client = MagicMock()
    mock_client.generer_recettes = MagicMock(return_value=[])
    mock_client.generer_planning = MagicMock(return_value=None)
    mock_client.generer_suggestions_courses = MagicMock(return_value=[])
    
    with patch("src.core.ai.client.ClientIA", return_value=mock_client):
        with patch("src.core.ai.client.obtenir_client_ia", return_value=mock_client):
            yield mock_client
