"""Mocks pour services Phase 18."""
from unittest.mock import MagicMock, patch
import pytest


class ServiceMockFactory:
    """Factory pour créer des mocks de services standardisés."""
    
    @staticmethod
    def mock_recette_service():
        """Mock RecetteService avec méthodes standard."""
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
        mock.appel_complet = MagicMock(
            return_value={"suggestions": [], "status": "success"}
        )
        mock.appel_streaming = MagicMock()
        return mock


@pytest.fixture
def mock_services():
    """Fixture fournissant tous les service mocks."""
    return {
        "recette": ServiceMockFactory.mock_recette_service(),
        "planning": ServiceMockFactory.mock_planning_service(),
        "courses": ServiceMockFactory.mock_courses_service(),
        "ai": ServiceMockFactory.mock_ai_client()
    }
