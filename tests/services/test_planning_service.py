"""
Tests pour PlanningService - Tests des méthodes réelles du service

NOTE: Tests marked skip because get_planning_service() uses production DB singleton.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.planning import PlanningService, get_planning_service
import importlib

# Skip all tests - service uses production DB singleton
pytestmark = pytest.mark.skip(reason="get_planning_service() uses production DB singleton")


def test_import_planning_module():
    """Vérifie que le module planning s'importe sans erreur."""
    module = importlib.import_module("src.services.planning")
    assert module is not None


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY ET INSTANCIATION
# ═══════════════════════════════════════════════════════════

class TestPlanningServiceFactory:
    """Tests pour la factory et l'instanciation."""
    
    def test_get_planning_service_returns_instance(self):
        """La factory retourne une instance de PlanningService."""
        service = get_planning_service()
        assert service is not None
        assert isinstance(service, PlanningService)
    
    def test_service_has_model(self):
        """Le service a le modèle Planning configuré."""
        service = get_planning_service()
        assert hasattr(service, 'model')
        assert service.model.__name__ == 'Planning'
    
    def test_service_inherits_base_service(self):
        """Le service hérite de BaseService."""
        service = get_planning_service()
        assert hasattr(service, 'create')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'get_all')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES CRUD (héritées de BaseService)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceCRUD:
    """Tests pour les méthodes CRUD héritées."""
    
    def test_get_all_returns_list(self, planning_service):
        """get_all retourne une liste."""
        with patch.object(planning_service, '_with_session') as mock_session:
            mock_session.return_value = []
            result = planning_service.get_all()
            assert isinstance(result, list)
    
    def test_get_by_id_with_mock(self, planning_service):
        """get_by_id utilise le cache."""
        with patch.object(planning_service, '_with_session') as mock_session:
            mock_session.return_value = None
            result = planning_service.get_by_id(99999)
            assert mock_session.called


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceSpecific:
    """Tests pour les méthodes spécifiques à PlanningService."""
    
    def test_get_planning_exists(self, planning_service):
        """La méthode get_planning existe."""
        assert hasattr(planning_service, 'get_planning')
        assert callable(planning_service.get_planning)
    
    def test_get_planning_complet_exists(self, planning_service):
        """La méthode get_planning_complet existe."""
        assert hasattr(planning_service, 'get_planning_complet')
        assert callable(planning_service.get_planning_complet)


# ═══════════════════════════════════════════════════════════
# TESTS BASEAISERVICE HÉRITÉ
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPlanningServiceAI:
    """Tests pour les méthodes IA héritées."""
    
    def test_has_build_json_prompt(self, planning_service):
        """Le service a la méthode build_json_prompt."""
        assert hasattr(planning_service, 'build_json_prompt')
    
    def test_has_build_system_prompt(self, planning_service):
        """Le service a la méthode build_system_prompt."""
        assert hasattr(planning_service, 'build_system_prompt')
    
    def test_service_name_is_planning(self, planning_service):
        """Le service_name est 'planning'."""
        assert planning_service.service_name == "planning"
