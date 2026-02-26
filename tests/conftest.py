"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database setup and cleanup
- Service instances
- Test data factories
- Mock clients (IA, cache)
"""

import os
import sys
import warnings
from pathlib import Path

# DÉSACTIVER LE RATE LIMITING POUR TOUS LES TESTS
os.environ["RATE_LIMITING_DISABLED"] = "true"

# Suppress Streamlit warnings when running tests outside Streamlit context
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*Session state does not function.*")
warnings.filterwarnings("ignore", message=".*No runtime found.*")

# Configurer le chemin pour les imports
workspace_root = Path(__file__).parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from src.core.models import (  # noqa: E402
    Base,
    Ingredient,
    Planning,
    Recette,
    RetourRecette,  # Nécessaire pour résoudre la relation Recette.feedbacks
)
from src.services.cuisine.courses import ServiceCourses  # noqa: E402
from src.services.cuisine.planning import ServicePlanning  # noqa: E402
from src.services.cuisine.recettes import ServiceRecettes  # noqa: E402
from src.services.inventaire import ServiceInventaire  # noqa: E402

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


# ═══════════════════════════════════════════════════════════
# SERVICE FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def recette_service():
    """ServiceRecettes instance for testing."""
    return ServiceRecettes()


@pytest.fixture
def inventaire_service():
    """ServiceInventaire instance for testing."""
    return ServiceInventaire()


@pytest.fixture
def planning_service(patch_db_context):
    """ServicePlanning instance for testing with test DB."""
    return ServicePlanning()


@pytest.fixture
def courses_service(patch_db_context):
    """ServiceCourses instance for testing with test DB."""
    return ServiceCourses()


# ═══════════════════════════════════════════════════════════
# FACTORY FIXTURES (Test Data)
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA FIXTURES
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# COURSES FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def sample_articles():
    """Sample articles for courses tests"""
    return [
        {
            "id": 1,
            "ingredient_id": 1,
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 2.0,
            "unite": "kg",
            "priorite": "haute",
            "achete": False,
            "rayon_magasin": "Fruits & Légumes",
            "notes": None,
            "suggere_par_ia": False,
        },
        {
            "id": 2,
            "ingredient_id": 2,
            "ingredient_nom": "Oeufs",
            "quantite_necessaire": 6.0,
            "unite": "pièce",
            "priorite": "moyenne",
            "achete": False,
            "rayon_magasin": "Laitier",
            "notes": "Bio si possible",
            "suggere_par_ia": False,
        },
    ]


@pytest.fixture
def sample_suggestions():
    """Sample IA suggestions for courses"""
    from unittest.mock import Mock

    mock_suggestions = [
        Mock(nom="Tomates", quantite=2.0, unite="kg", priorite="haute", rayon="Fruits & Légumes"),
        Mock(nom="Oeufs", quantite=6.0, unite="pièce", priorite="moyenne", rayon="Laitier"),
        Mock(nom="Pain", quantite=1.0, unite="pièce", priorite="moyenne", rayon="Boulangerie"),
    ]
    return mock_suggestions


@pytest.fixture
def courses_service_instance(db_session):
    """Get or create ServiceCourses instance for tests"""
    return ServiceCourses()


# ═══════════════════════════════════════════════════════════
# PYTEST CONFIGURATION
# ═══════════════════════════════════════════════════════════


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "courses: mark test as courses module test")


# ═══════════════════════════════════════════════════════════
# HELPER FIXTURES
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# STREAMLIT MOCK UTILITIES
# ═══════════════════════════════════════════════════════════


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
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            ) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            ) from None


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
    mock_st.columns = MagicMock(
        side_effect=lambda *args, **kwargs: [
            create_context_mock()
            for _ in range(args[0] if args and isinstance(args[0], int) else 2)
        ]
    )

    # Default tabs behavior
    mock_st.tabs = MagicMock(side_effect=lambda labels: [create_context_mock() for _ in labels])

    return mock_st


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before/after each test.

    Clears all levels (L1, L2 session_state, L3 file) then destroys the singleton
    so the next test starts with a completely fresh cache.
    """

    def _clear_all():
        try:
            from src.core.caching.orchestrator import (
                CacheMultiNiveau,
                obtenir_cache,
                reinitialiser_cache,
            )

            # First, clear all levels on the existing instance (clears L2 session_state)
            try:
                cache = obtenir_cache()
                cache.clear("all")
            except Exception:
                pass

            # Then destroy the singleton so next test gets a fresh instance
            reinitialiser_cache()
        except Exception:
            pass

    _clear_all()
    yield
    _clear_all()


@pytest.fixture
def patch_db_context(db):
    """
    Fixture that patches obtenir_contexte_db and obtenir_contexte_db to use test session.

    This allows services that use @avec_session_db to work with the test database
    instead of the production database.

    Usage:
        def test_service_method(patch_db_context, recette_service):
            # recette_service methods will now use test DB
            result = recette_service.lister_recettes()
            assert result is not None
    """
    from contextlib import contextmanager
    from unittest.mock import patch

    @contextmanager
    def mock_db_context():
        """Returns the test session instead of production."""
        yield db

    # Patch both French and English function names
    with patch("src.core.db.obtenir_contexte_db", mock_db_context):
        with patch("src.core.db.obtenir_contexte_db", mock_db_context):
            yield db


@pytest.fixture(autouse=True)
def mock_mistral_api(monkeypatch):
    """Mock Mistral AI API for all tests."""

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
