"""Fixtures pour services Phase 18."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

# Import des services réels
try:
    from src.services.cuisine.courses import CoursesService
    from src.services.cuisine.planning import PlanningService
    from src.services.cuisine.recettes import ServiceRecettes
except ImportError:
    pass


# =============================================================================
# ServiceMockFactory - Factories pour créer des mocks de services standardisés
# =============================================================================


class ServiceMockFactory:
    """Factory pour créer des mocks de services standardisés."""

    @staticmethod
    def mock_recette_service():
        """Mock ServiceRecettes avec méthodes standard."""
        mock = MagicMock()
        mock.obtenir_recettes = MagicMock(return_value=[])
        mock.obtenir_recette = MagicMock(return_value=None)
        mock.creer_recette = MagicMock(return_value=MagicMock(id=1))
        mock.modifier_recette = MagicMock(return_value=MagicMock(id=1))
        mock.supprimer_recette = MagicMock(return_value=True)
        return mock

    @staticmethod
    def mock_planning_service():
        """Mock PlanningService avec méthodes standard."""
        mock = MagicMock()
        mock.obtenir_plannings = MagicMock(return_value=[])
        mock.obtenir_planning = MagicMock(return_value=None)
        mock.creer_planning = MagicMock(return_value=MagicMock(id=1))
        return mock

    @staticmethod
    def mock_courses_service():
        """Mock CoursesService avec méthodes standard."""
        mock = MagicMock()
        mock.obtenir_courses = MagicMock(return_value=[])
        mock.obtenir_course = MagicMock(return_value=None)
        mock.creer_course = MagicMock(return_value=MagicMock(id=1))
        return mock

    @staticmethod
    def mock_ai_client():
        """Mock ClientIA avec réponses standard."""
        mock = MagicMock()
        mock.appel_complet = MagicMock(return_value={"suggestions": [], "status": "success"})
        mock.appel_streaming = MagicMock()
        return mock


# =============================================================================
# Fixtures principales
# =============================================================================


@pytest.fixture
def mock_services():
    """Fixture fournissant tous les service mocks via ServiceMockFactory."""
    return {
        "recette": ServiceMockFactory.mock_recette_service(),
        "planning": ServiceMockFactory.mock_planning_service(),
        "courses": ServiceMockFactory.mock_courses_service(),
        "ai": ServiceMockFactory.mock_ai_client(),
    }


@pytest.fixture
def recette_service(test_db: Session) -> ServiceRecettes:
    """Factory pour ServiceRecettes avec DB de test."""
    try:
        return ServiceRecettes(session=test_db)
    except TypeError:
        # Si signature différente, adapter ici
        return MagicMock(spec=ServiceRecettes)


@pytest.fixture
def planning_service(test_db: Session) -> PlanningService:
    """Factory pour PlanningService avec DB de test."""
    try:
        return PlanningService(session=test_db)
    except TypeError:
        # Si signature différente, adapter ici
        return MagicMock(spec=PlanningService)


@pytest.fixture
def courses_service(test_db: Session) -> CoursesService:
    """Factory pour CoursesService avec DB de test."""
    try:
        return CoursesService(session=test_db)
    except TypeError:
        # Si signature différente, adapter ici
        return MagicMock(spec=CoursesService)


@pytest.fixture
def mock_ia_service():
    """Mock pour service IA avec cache."""
    with patch("src.core.ai.ClientIA") as mock:
        mock.appel_complet = MagicMock(return_value={"suggestions": [], "status": "success"})
        mock.appel_streaming = MagicMock()
        yield mock


@pytest.fixture
def mock_streamlit_state():
    """Mock pour st.session_state."""
    with patch("streamlit.session_state") as mock:
        mock.__setitem__ = MagicMock()
        mock.__getitem__ = MagicMock(return_value=None)
        mock.get = MagicMock(return_value=None)
        yield mock
