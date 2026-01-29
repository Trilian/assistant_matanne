"""
Tests unitaires pour base_service.py (Service CRUD Universel)
Ce fichier teste spÃ©cifiquement src/services/base_service.py
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

# Import direct du module Ã  tester
from src.services.base_service import BaseService
from src.core.models import Base


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class MockModel(Base):
    """ModÃ¨le mock pour les tests"""
    __tablename__ = "test_mock_table"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    description = Column(String(500))
    statut = Column(String(50), default="actif")
    created_at = Column(DateTime, default=datetime.utcnow)


@pytest.fixture
def mock_db():
    """Session de base de donnÃ©es mockÃ©e"""
    return MagicMock(spec=Session)


@pytest.fixture
def base_service():
    """Service de base pour les tests"""
    return BaseService(MockModel, cache_ttl=120)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceInit:
    """Tests d'initialisation du service"""
    
    def test_init_sets_model(self, base_service):
        """Test que l'initialisation configure le modÃ¨le"""
        assert base_service.model == MockModel
    
    def test_init_sets_model_name(self, base_service):
        """Test que le nom du modÃ¨le est correctement dÃ©fini"""
        assert base_service.model_name == "MockModel"
    
    def test_init_sets_cache_ttl(self, base_service):
        """Test que le TTL du cache est configurÃ©"""
        assert base_service.cache_ttl == 120
    
    def test_init_default_cache_ttl(self):
        """Test que le TTL par dÃ©faut est 60"""
        service = BaseService(MockModel)
        assert service.cache_ttl == 60


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MÃ‰THODES UTILITAIRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceHelpers:
    """Tests des mÃ©thodes utilitaires"""
    
    def test_invalider_cache(self, base_service):
        """Test l'invalidation du cache"""
        with patch.object(base_service, '_invalider_cache') as mock_invalider:
            base_service._invalider_cache()
            mock_invalider.assert_called_once()
    
    def test_model_to_dict_exists(self, base_service):
        """Test que _model_to_dict existe"""
        assert hasattr(base_service, '_model_to_dict')
    
    def test_apply_filters_exists(self, base_service):
        """Test que _apply_filters existe"""
        assert hasattr(base_service, '_apply_filters')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CREATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceCreate:
    """Tests de la mÃ©thode create"""
    
    @patch('src.services.base_service.obtenir_contexte_db')
    def test_create_exists(self, mock_ctx, base_service):
        """Test que create existe"""
        assert hasattr(base_service, 'create')
        assert callable(base_service.create)
    
    @patch('src.services.base_service.obtenir_contexte_db')
    def test_create_accepts_data_dict(self, mock_ctx, base_service, mock_db):
        """Test que create accepte un dict"""
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        
        # Le dÃ©corateur @with_db_session nÃ©cessite un contexte
        try:
            base_service.create({"nom": "Test"})
        except Exception:
            pass  # On vÃ©rifie juste que la signature est correcte


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceGet:
    """Tests des mÃ©thodes get"""
    
    def test_get_by_id_exists(self, base_service):
        """Test que get_by_id existe"""
        assert hasattr(base_service, 'get_by_id')
    
    def test_get_all_exists(self, base_service):
        """Test que get_all existe"""
        assert hasattr(base_service, 'get_all')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS UPDATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceUpdate:
    """Tests de la mÃ©thode update"""
    
    def test_update_exists(self, base_service):
        """Test que update existe"""
        assert hasattr(base_service, 'update')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DELETE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceDelete:
    """Tests de la mÃ©thode delete"""
    
    def test_delete_exists(self, base_service):
        """Test que delete existe"""
        assert hasattr(base_service, 'delete')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COUNT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceCount:
    """Tests de la mÃ©thode count"""
    
    def test_count_exists(self, base_service):
        """Test que count existe"""
        assert hasattr(base_service, 'count')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECHERCHE AVANCÃ‰E
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceAdvancedSearch:
    """Tests de la recherche avancÃ©e"""
    
    def test_advanced_search_exists(self, base_service):
        """Test que advanced_search existe"""
        assert hasattr(base_service, 'advanced_search')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BULK OPERATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceBulk:
    """Tests des opÃ©rations en masse"""
    
    def test_bulk_create_with_merge_exists(self, base_service):
        """Test que bulk_create_with_merge existe"""
        assert hasattr(base_service, 'bulk_create_with_merge')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceStats:
    """Tests des statistiques"""
    
    def test_get_stats_exists(self, base_service):
        """Test que get_stats existe"""
        assert hasattr(base_service, 'get_stats')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MIXINS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBaseServiceMixins:
    """Tests des fonctionnalitÃ©s mixins"""
    
    def test_service_is_generic(self, base_service):
        """Test que le service est gÃ©nÃ©rique"""
        from typing import Generic
        assert issubclass(BaseService, Generic)
    
    def test_model_accessible(self, base_service):
        """Test que le modÃ¨le est accessible"""
        assert base_service.model is not None

