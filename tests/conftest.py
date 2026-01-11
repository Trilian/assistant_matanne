"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database setup and cleanup
- Service instances
- Test data factories
- Mock clients (IA, cache)
"""

import os
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
)
from src.services.recettes import RecetteService
from src.services.inventaire import InventaireService
from src.services.planning import PlanningService
from src.services.courses import CoursesService

# ═══════════════════════════════════════════════════════════
# DATABASE SETUP - SQLite JSON compatibility
# ═══════════════════════════════════════════════════════════

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


@pytest.fixture
def db(engine):
    """Create fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# ═══════════════════════════════════════════════════════════
# SERVICE FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def recette_service():
    """RecetteService instance for testing."""
    return RecetteService()


@pytest.fixture
def inventaire_service():
    """InventaireService instance for testing."""
    return InventaireService()


@pytest.fixture
def planning_service():
    """PlanningService instance for testing."""
    return PlanningService()


@pytest.fixture
def courses_service():
    """CoursesService instance for testing."""
    return CoursesService()


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
        "thym": ingredient_factory.create("Thym", "g", "Épices & Condiments"),
    }


@pytest.fixture
def sample_planning(planning_factory):
    """Create a sample planning for testing."""
    return planning_factory.create(
        nom="Semaine du 13 janvier",
        semaine_debut=date(2026, 1, 13),
    )


# ═══════════════════════════════════════════════════════════
# PYTEST CONFIGURATION
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# HELPER FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def clear_cache():
    """Clear cache before/after each test."""
    from src.core.cache import Cache
    # Cache doesn't expose a clear method, so we just yield
    # The tests use in-memory SQLite which is ephemeral anyway
    yield


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
