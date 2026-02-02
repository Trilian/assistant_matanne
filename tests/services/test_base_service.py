"""
Tests pour src/services/base_service.py
Cible: BaseService - CRUD, cache, filtres, bulk operations
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


class FakeModel:
    """Modèle factice pour tests."""
    __name__ = "FakeModel"
    id = None  # Attribut de classe pour que hasattr fonctionne
    
    def __init__(self, id=None, nom=None, **kwargs):
        self.id = id
        self.nom = nom
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def mock_db_session():
    """Session DB mockée."""
    session = Mock()
    session.query.return_value.get.return_value = None
    session.query.return_value.all.return_value = []
    session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return session


@pytest.fixture
def base_service():
    """Instance BaseService pour tests."""
    from src.services.base_service import BaseService
    return BaseService(FakeModel, cache_ttl=60)


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceInit:
    """Tests pour l'initialisation de BaseService."""

    def test_init_sets_model(self):
        """Vérifie que le modèle est correctement défini."""
        from src.services.base_service import BaseService
        
        service = BaseService(FakeModel)
        
        assert service.model == FakeModel
        assert service.model_name == "FakeModel"

    def test_init_sets_cache_ttl(self):
        """Vérifie que le TTL cache est correctement défini."""
        from src.services.base_service import BaseService
        
        service = BaseService(FakeModel, cache_ttl=120)
        
        assert service.cache_ttl == 120

    def test_init_default_cache_ttl(self):
        """Vérifie le TTL cache par défaut."""
        from src.services.base_service import BaseService
        
        service = BaseService(FakeModel)
        
        assert service.cache_ttl == 60  # Valeur par défaut


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - CREATE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceCreate:
    """Tests pour la méthode create."""

    def test_create_has_method(self, base_service):
        """Vérifie que la méthode create existe."""
        assert hasattr(base_service, 'create')
        assert callable(base_service.create)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - READ
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceRead:
    """Tests pour les méthodes de lecture."""

    def test_get_by_id_method_exists(self, base_service):
        """Vérifie que la méthode get_by_id existe."""
        assert hasattr(base_service, 'get_by_id')
        assert callable(base_service.get_by_id)

    def test_get_all_method_exists(self, base_service):
        """Vérifie que la méthode get_all existe."""
        assert hasattr(base_service, 'get_all')
        assert callable(base_service.get_all)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - UPDATE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceUpdate:
    """Tests pour la méthode update."""

    def test_update_method_exists(self, base_service):
        """Vérifie que la méthode update existe."""
        assert hasattr(base_service, 'update')
        assert callable(base_service.update)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - DELETE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceDelete:
    """Tests pour la méthode delete."""

    def test_delete_method_exists(self, base_service):
        """Vérifie que la méthode delete existe."""
        assert hasattr(base_service, 'delete')
        assert callable(base_service.delete)


# ═══════════════════════════════════════════════════════════
# TESTS CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceCache:
    """Tests pour la gestion du cache."""

    def test_invalider_cache_method_exists(self, base_service):
        """Vérifie que _invalider_cache existe."""
        assert hasattr(base_service, '_invalider_cache')


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceStats:
    """Tests pour les statistiques."""

    def test_count_method_exists(self, base_service):
        """Vérifie que count existe."""
        assert hasattr(base_service, 'count')
        assert callable(base_service.count)


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE AVANCÉE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceSearch:
    """Tests pour la recherche avancée."""

    def test_advanced_search_method_exists(self, base_service):
        """Vérifie que advanced_search existe."""
        assert hasattr(base_service, 'advanced_search')
        assert callable(base_service.advanced_search)
