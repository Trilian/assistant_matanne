"""Fixtures pour services Phase 18."""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

# Import des services réels
try:
    from src.services.recettes import RecetteService
    from src.services.planning import PlanningService
    from src.services.courses import CoursesService
except ImportError:
    pass


@pytest.fixture
def recette_service(test_db: Session) -> RecetteService:
    """Factory pour RecetteService avec DB de test."""
    try:
        return RecetteService(session=test_db)
    except TypeError:
        # Si signature différente, adapter ici
        return MagicMock(spec=RecetteService)


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
    with patch('src.core.ai.ClientIA') as mock:
        mock.appel_complet = MagicMock(
            return_value={"suggestions": [], "status": "success"}
        )
        mock.appel_streaming = MagicMock()
        yield mock


@pytest.fixture
def mock_streamlit_state():
    """Mock pour st.session_state."""
    with patch('streamlit.session_state') as mock:
        mock.__setitem__ = MagicMock()
        mock.__getitem__ = MagicMock(return_value=None)
        mock.get = MagicMock(return_value=None)
        yield mock
