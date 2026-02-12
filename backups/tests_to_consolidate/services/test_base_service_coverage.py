"""
Tests complets pour src/services/base_service.py
Approche simplifiÃ©e sans dÃ©pendance DB
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES ET MODÃˆLES FACTICES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class FakeColumn:
    """Colonne factice pour tests."""
    def __init__(self, name):
        self.name = name


class FakeTable:
    """Table factice pour tests."""
    columns = [FakeColumn("id"), FakeColumn("nom"), FakeColumn("statut"), FakeColumn("created_at")]


class SimpleFakeModel:
    """ModÃ¨le simple pour tests basiques."""
    __name__ = "SimpleFakeModel"
    __table__ = FakeTable()
    id = None
    nom = None
    statut = None
    code = None
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def mock_session():
    """Session DB mockÃ©e."""
    session = Mock()
    query = Mock()
    session.query.return_value = query
    query.get.return_value = None
    query.all.return_value = []
    query.first.return_value = None
    query.count.return_value = 0
    query.filter.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.order_by.return_value = query
    query.delete.return_value = 0
    query.group_by.return_value = query
    return session


@pytest.fixture
def base_service():
    """Instance BaseService."""
    from src.services.base_service import BaseService
    return BaseService(SimpleFakeModel, cache_ttl=60)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceInitialization:
    """Tests d'initialisation."""

    def test_init_model(self):
        """Test initialisation avec modÃ¨le."""
        from src.services.base_service import BaseService
        
        service = BaseService(SimpleFakeModel)
        
        assert service.model == SimpleFakeModel
        assert service.model_name == "SimpleFakeModel"

    def test_init_cache_ttl_custom(self):
        """Test TTL cache personnalisÃ©."""
        from src.services.base_service import BaseService
        
        service = BaseService(SimpleFakeModel, cache_ttl=300)
        
        assert service.cache_ttl == 300

    def test_init_cache_ttl_default(self):
        """Test TTL cache par dÃ©faut = 60."""
        from src.services.base_service import BaseService
        
        service = BaseService(SimpleFakeModel)
        
        assert service.cache_ttl == 60


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MÃ‰THODES CRUD (vÃ©rification existence)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceCRUDInterface:
    """Tests interface CRUD."""

    def test_create_method_exists(self, base_service):
        """VÃ©rifie que create existe."""
        assert hasattr(base_service, 'create')
        assert callable(base_service.create)

    def test_get_by_id_method_exists(self, base_service):
        """VÃ©rifie que get_by_id existe."""
        assert hasattr(base_service, 'get_by_id')
        assert callable(base_service.get_by_id)

    def test_get_all_method_exists(self, base_service):
        """VÃ©rifie que get_all existe."""
        assert hasattr(base_service, 'get_all')
        assert callable(base_service.get_all)

    def test_update_method_exists(self, base_service):
        """VÃ©rifie que update existe."""
        assert hasattr(base_service, 'update')
        assert callable(base_service.update)

    def test_delete_method_exists(self, base_service):
        """VÃ©rifie que delete existe."""
        assert hasattr(base_service, 'delete')
        assert callable(base_service.delete)

    def test_count_method_exists(self, base_service):
        """VÃ©rifie que count existe."""
        assert hasattr(base_service, 'count')
        assert callable(base_service.count)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECHERCHE AVANCÃ‰E (interface)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceAdvancedSearchInterface:
    """Tests interface recherche avancÃ©e."""

    def test_advanced_search_method_exists(self, base_service):
        """VÃ©rifie que advanced_search existe."""
        assert hasattr(base_service, 'advanced_search')
        assert callable(base_service.advanced_search)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BULK OPERATIONS (interface)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceBulkInterface:
    """Tests interface bulk operations."""

    def test_bulk_create_with_merge_method_exists(self, base_service):
        """VÃ©rifie que bulk_create_with_merge existe."""
        assert hasattr(base_service, 'bulk_create_with_merge')
        assert callable(base_service.bulk_create_with_merge)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STATISTIQUES (interface)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceStatsInterface:
    """Tests interface statistiques."""

    def test_get_stats_method_exists(self, base_service):
        """VÃ©rifie que get_stats existe."""
        assert hasattr(base_service, 'get_stats')
        assert callable(base_service.get_stats)

    def test_count_by_status_method_exists(self, base_service):
        """VÃ©rifie que count_by_status existe."""
        assert hasattr(base_service, 'count_by_status')
        assert callable(base_service.count_by_status)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MIXINS (interface)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceMixinsInterface:
    """Tests interface mixins."""

    def test_mark_as_method_exists(self, base_service):
        """VÃ©rifie que mark_as existe."""
        assert hasattr(base_service, 'mark_as')
        assert callable(base_service.mark_as)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _apply_filters (helper privÃ© testable directement)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestApplyFilters:
    """Tests pour _apply_filters()."""

    def test_apply_filters_empty(self, base_service):
        """Test avec filtres vides."""
        mock_query = Mock()
        
        result = base_service._apply_filters(mock_query, {})
        
        assert result == mock_query

    def test_apply_filters_simple_equality(self, base_service):
        """Test filtre Ã©galitÃ© simple."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        # Mock l'attribut du modÃ¨le
        SimpleFakeModel.statut = Mock()
        
        result = base_service._apply_filters(mock_query, {"statut": "actif"})
        
        mock_query.filter.assert_called()

    def test_apply_filters_unknown_field_ignored(self, base_service):
        """Test filtre sur champ inexistant ignorÃ©."""
        mock_query = Mock()
        
        # Supprimer l'attribut inexistant
        if hasattr(SimpleFakeModel, 'champ_inexistant'):
            delattr(SimpleFakeModel, 'champ_inexistant')
        
        result = base_service._apply_filters(mock_query, {"champ_inexistant": "valeur"})
        
        # Query non modifiÃ©e (filter pas appelÃ©)
        assert result == mock_query

    def test_apply_filters_gte_operator(self, base_service):
        """Test opÃ©rateur gte (>=)."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.id = Mock()
        SimpleFakeModel.id.__ge__ = Mock(return_value="condition")
        
        result = base_service._apply_filters(mock_query, {"id": {"gte": 10}})
        
        mock_query.filter.assert_called()

    def test_apply_filters_lte_operator(self, base_service):
        """Test opÃ©rateur lte (<=)."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.id = Mock()
        SimpleFakeModel.id.__le__ = Mock(return_value="condition")
        
        result = base_service._apply_filters(mock_query, {"id": {"lte": 100}})
        
        mock_query.filter.assert_called()

    def test_apply_filters_in_operator(self, base_service):
        """Test opÃ©rateur in."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.statut = Mock()
        SimpleFakeModel.statut.in_ = Mock(return_value="condition")
        
        result = base_service._apply_filters(
            mock_query, 
            {"statut": {"in": ["actif", "pending"]}}
        )
        
        mock_query.filter.assert_called()

    def test_apply_filters_like_operator(self, base_service):
        """Test opÃ©rateur like."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.nom = Mock()
        SimpleFakeModel.nom.ilike = Mock(return_value="condition")
        
        result = base_service._apply_filters(
            mock_query, 
            {"nom": {"like": "test"}}
        )
        
        mock_query.filter.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _model_to_dict (helper privÃ© testable directement)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModelToDict:
    """Tests pour _model_to_dict()."""

    def test_model_to_dict_basic(self):
        """Test conversion modÃ¨le en dict."""
        from src.services.base_service import BaseService
        
        class MockColumn:
            def __init__(self, name):
                self.name = name
        
        class MockTable:
            columns = [MockColumn("id"), MockColumn("nom")]
        
        class MockModel:
            __name__ = "MockModel"
            __table__ = MockTable()
            
            def __init__(self):
                self.id = 1
                self.nom = "Test"
        
        service = BaseService(MockModel)
        obj = MockModel()
        
        result = service._model_to_dict(obj)
        
        assert result["id"] == 1
        assert result["nom"] == "Test"

    def test_model_to_dict_with_datetime(self):
        """Test conversion datetime en ISO string."""
        from src.services.base_service import BaseService
        
        class MockColumn:
            def __init__(self, name):
                self.name = name
        
        class MockTable:
            columns = [MockColumn("id"), MockColumn("created_at")]
        
        class MockModel:
            __name__ = "MockModel"
            __table__ = MockTable()
            
            def __init__(self):
                self.id = 1
                self.created_at = datetime(2024, 1, 15, 10, 30, 0)
        
        service = BaseService(MockModel)
        obj = MockModel()
        
        result = service._model_to_dict(obj)
        
        assert result["id"] == 1
        assert result["created_at"] == "2024-01-15T10:30:00"

    def test_model_to_dict_with_none_values(self):
        """Test conversion avec valeurs None."""
        from src.services.base_service import BaseService
        
        class MockColumn:
            def __init__(self, name):
                self.name = name
        
        class MockTable:
            columns = [MockColumn("id"), MockColumn("nom")]
        
        class MockModel:
            __name__ = "MockModel"
            __table__ = MockTable()
            
            def __init__(self):
                self.id = 1
                self.nom = None
        
        service = BaseService(MockModel)
        obj = MockModel()
        
        result = service._model_to_dict(obj)
        
        assert result["id"] == 1
        assert result["nom"] is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _with_session (helper privÃ© testable directement)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestWithSession:
    """Tests pour _with_session()."""

    def test_with_session_uses_provided_db(self, base_service):
        """Test utilisation session fournie."""
        mock_session = Mock()
        test_func = Mock(return_value="result")
        
        result = base_service._with_session(test_func, mock_session)
        
        test_func.assert_called_once_with(mock_session)
        assert result == "result"

    @patch('src.services.base_service.obtenir_contexte_db')
    def test_with_session_creates_session_if_none(self, mock_ctx, base_service):
        """Test crÃ©ation session si non fournie."""
        mock_session = Mock()
        mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = Mock(return_value=False)
        
        test_func = Mock(return_value="result")
        
        result = base_service._with_session(test_func, None)
        
        test_func.assert_called_once_with(mock_session)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _invalider_cache (helper privÃ© testable directement)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestInvaliderCache:
    """Tests pour _invalider_cache()."""

    @patch('src.services.base_service.Cache')
    def test_invalider_cache_calls_invalider(self, mock_cache, base_service):
        """Test appel Ã  Cache.invalider."""
        base_service._invalider_cache()
        
        mock_cache.invalider.assert_called()

    @patch('src.services.base_service.Cache')
    def test_invalider_cache_uses_model_name(self, mock_cache, base_service):
        """Test utilisation du nom de modÃ¨le."""
        base_service._invalider_cache()
        
        # Doit utiliser le nom du modÃ¨le en minuscules
        mock_cache.invalider.assert_called_with(pattern="simplefakemodel")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_base_service_exported(self):
        """Test BaseService est exportÃ©."""
        from src.services.base_service import BaseService
        
        assert BaseService is not None

    def test_base_service_is_generic(self):
        """Test BaseService hÃ©rite de Generic."""
        from src.services.base_service import BaseService
        from typing import Generic
        
        assert hasattr(BaseService, '__orig_bases__')

    def test_type_var_t_exists(self):
        """Test TypeVar T dÃ©fini."""
        from src.services.base_service import T
        
        assert T is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SIGNATURE DES MÃ‰THODES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestMethodSignatures:
    """Tests des signatures de mÃ©thodes."""

    def test_advanced_search_parameters(self, base_service):
        """Test paramÃ¨tres de advanced_search."""
        import inspect
        
        sig = inspect.signature(base_service.advanced_search)
        params = list(sig.parameters.keys())
        
        assert 'search_term' in params
        assert 'search_fields' in params
        assert 'filters' in params
        assert 'sort_by' in params
        assert 'limit' in params
        assert 'offset' in params

    def test_get_all_parameters(self, base_service):
        """Test paramÃ¨tres de get_all."""
        import inspect
        
        sig = inspect.signature(base_service.get_all)
        params = list(sig.parameters.keys())
        
        assert 'skip' in params
        assert 'limit' in params
        assert 'filters' in params
        assert 'order_by' in params
        assert 'desc_order' in params

    def test_bulk_create_with_merge_parameters(self, base_service):
        """Test paramÃ¨tres de bulk_create_with_merge."""
        import inspect
        
        sig = inspect.signature(base_service.bulk_create_with_merge)
        params = list(sig.parameters.keys())
        
        assert 'items_data' in params
        assert 'merge_key' in params
        assert 'merge_strategy' in params

    def test_get_stats_parameters(self, base_service):
        """Test paramÃ¨tres de get_stats."""
        import inspect
        
        sig = inspect.signature(base_service.get_stats)
        params = list(sig.parameters.keys())
        
        assert 'group_by_fields' in params
        assert 'count_filters' in params
        assert 'additional_filters' in params


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COUVERTURE SUPPLÃ‰MENTAIRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceAdditionalCoverage:
    """Tests supplÃ©mentaires pour la couverture."""

    def test_model_name_is_class_name(self, base_service):
        """Test model_name = __name__ du modÃ¨le."""
        assert base_service.model_name == SimpleFakeModel.__name__

    def test_apply_filters_with_multiple_filters(self, base_service):
        """Test plusieurs filtres appliquÃ©s."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.id = Mock()
        SimpleFakeModel.nom = Mock()
        SimpleFakeModel.nom.ilike = Mock(return_value="cond")
        
        result = base_service._apply_filters(mock_query, {
            "id": 1,
            "nom": {"like": "test"}
        })
        
        # filter appelÃ©
        assert mock_query.filter.call_count >= 1

    def test_apply_filters_gte_and_lte_combined(self, base_service):
        """Test filtres gte et lte combinÃ©s."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        SimpleFakeModel.id = Mock()
        SimpleFakeModel.id.__ge__ = Mock(return_value="cond1")
        SimpleFakeModel.id.__le__ = Mock(return_value="cond2")
        
        result = base_service._apply_filters(mock_query, {
            "id": {"gte": 10, "lte": 100}
        })
        
        assert mock_query.filter.call_count >= 1

    def test_model_to_dict_handles_all_columns(self):
        """Test _model_to_dict parcourt toutes les colonnes."""
        from src.services.base_service import BaseService
        
        class MockColumn:
            def __init__(self, name):
                self.name = name
        
        class MockTable:
            columns = [MockColumn("a"), MockColumn("b"), MockColumn("c")]
        
        class MockModel:
            __name__ = "MockModel"
            __table__ = MockTable()
            
            def __init__(self):
                self.a = 1
                self.b = 2
                self.c = 3
        
        service = BaseService(MockModel)
        obj = MockModel()
        
        result = service._model_to_dict(obj)
        
        assert len(result) == 3
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LOGGING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceLogging:
    """Tests du logging."""

    def test_logger_exists(self):
        """Test logger dÃ©fini dans le module."""
        from src.services import base_service
        
        assert hasattr(base_service, 'logger')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CRUD AVEC SESSION MOCKÃ‰E (db= passÃ© directement)
# Le dÃ©corateur @with_db_session utilise db= si fourni
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceCRUDWithMockedDb:
    """Tests CRUD en passant db= directement (bypass du decorator)."""

    @patch('src.services.base_service.Cache')
    def test_create_success(self, mock_cache, base_service, mock_session):
        """Test crÃ©ation rÃ©ussie."""
        # Configure mock session
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh = Mock(side_effect=lambda e: setattr(e, 'id', 1))
        
        result = base_service.create({"nom": "Test"}, db=mock_session)
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('src.services.base_service.Cache')
    def test_get_by_id_cache_hit(self, mock_cache, base_service, mock_session):
        """Test rÃ©cupÃ©ration depuis le cache."""
        cached = SimpleFakeModel(id=1, nom="Cached")
        mock_cache.obtenir.return_value = cached
        
        result = base_service.get_by_id(1, db=mock_session)
        
        mock_cache.obtenir.assert_called()

    @patch('src.services.base_service.Cache')
    def test_get_by_id_cache_miss_db_hit(self, mock_cache, base_service, mock_session):
        """Test rÃ©cupÃ©ration depuis DB quand pas en cache."""
        mock_cache.obtenir.return_value = None
        
        db_entity = SimpleFakeModel(id=1, nom="FromDB")
        mock_session.query.return_value.get.return_value = db_entity
        
        result = base_service.get_by_id(1, db=mock_session)
        
        mock_session.query.assert_called_with(SimpleFakeModel)

    @patch('src.services.base_service.Cache')
    def test_get_by_id_not_found(self, mock_cache, base_service, mock_session):
        """Test ID non trouvÃ© retourne None."""
        mock_cache.obtenir.return_value = None
        mock_session.query.return_value.get.return_value = None
        
        result = base_service.get_by_id(999, db=mock_session)
        
        assert result is None

    def test_get_all_basic(self, base_service, mock_session):
        """Test liste basique."""
        entities = [SimpleFakeModel(id=1), SimpleFakeModel(id=2)]
        mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = entities
        
        result = base_service.get_all(db=mock_session)
        
        assert len(result) == 2


    def test_get_all_with_filters(self, base_service, mock_session):
        """Test get_all avec filtres."""
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        
        SimpleFakeModel.statut = Mock()
        
        result = base_service.get_all(filters={"statut": "actif"}, db=mock_session)

    @patch('src.services.base_service.Cache')
    def test_update_success(self, mock_cache, base_service, mock_session):
        """Test mise Ã  jour rÃ©ussie."""
        existing = SimpleFakeModel(id=1, nom="Old")
        mock_session.query.return_value.get.return_value = existing
        
        result = base_service.update(1, {"nom": "New"}, db=mock_session)
        
        assert existing.nom == "New"
        mock_session.commit.assert_called()

    def test_update_not_found(self, base_service, mock_session):
        """Test update entitÃ© non trouvÃ©e."""
        from src.core.errors_base import ErreurNonTrouve
        
        mock_session.query.return_value.get.return_value = None
        
        with pytest.raises(ErreurNonTrouve):
            base_service.update(999, {"nom": "New"}, db=mock_session)

    @patch('src.services.base_service.Cache')
    def test_delete_success(self, mock_cache, base_service, mock_session):
        """Test suppression rÃ©ussie."""
        mock_session.query.return_value.filter.return_value.delete.return_value = 1
        
        result = base_service.delete(1, db=mock_session)
        
        assert result is True
        mock_session.commit.assert_called()

    def test_delete_not_found(self, base_service, mock_session):
        """Test suppression ID non trouvÃ©."""
        mock_session.query.return_value.filter.return_value.delete.return_value = 0
        
        result = base_service.delete(999, db=mock_session)
        
        assert result is False

    def test_count_basic(self, base_service, mock_session):
        """Test comptage simple."""
        mock_session.query.return_value.count.return_value = 42
        
        result = base_service.count(db=mock_session)
        
        assert result == 42

    def test_count_with_filters(self, base_service, mock_session):
        """Test comptage avec filtres."""
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        
        SimpleFakeModel.statut = Mock()
        
        result = base_service.count(filters={"statut": "actif"}, db=mock_session)
        
        assert result == 10


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECHERCHE AVANCÃ‰E AVEC SESSION MOCKÃ‰E
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestAdvancedSearchWithMockedDb:
    """Tests advanced_search avec session mockÃ©e."""

    def test_advanced_search_basic(self, base_service, mock_session):
        """Test recherche basique."""
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        result = base_service.advanced_search(db=mock_session)
        
        assert isinstance(result, list)


    def test_advanced_search_with_filters(self, base_service, mock_session):
        """Test recherche avec filtres."""
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        SimpleFakeModel.statut = Mock()
        
        result = base_service.advanced_search(
            filters={"statut": "actif"},
            db=mock_session
        )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BULK ET STATS AVEC SESSION MOCKÃ‰E (via _with_session)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBulkAndStatsWithMockedDb:
    """Tests bulk et stats qui utilisent _with_session."""

    @patch('src.services.base_service.Cache')
    def test_bulk_create_new_items(self, mock_cache, base_service, mock_session):
        """Test crÃ©ation en masse de nouveaux items."""
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        def merge_strategy(existing, new):
            return {**existing, **new}
        
        items = [
            {"nom": "Item1", "code": "A"},
            {"nom": "Item2", "code": "B"}
        ]
        
        # Ajouter attribut code au modÃ¨le
        SimpleFakeModel.code = Mock()
        
        result = base_service.bulk_create_with_merge(
            items, "code", merge_strategy, db=mock_session
        )
        
        # RÃ©sultat est (created, merged)
        assert isinstance(result, tuple)

    @patch('src.services.base_service.Cache')
    def test_bulk_create_merge_existing(self, mock_cache, base_service, mock_session):
        """Test fusion avec items existants."""
        existing = SimpleFakeModel(id=1, nom="Existing", code="A")
        existing.__table__ = SimpleFakeModel.__table__
        
        # Premier item existe, second non
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            existing, None
        ]
        
        def merge_strategy(existing, new):
            return {**existing, **new}
        
        items = [
            {"nom": "Updated1", "code": "A"},
            {"nom": "New2", "code": "B"}
        ]
        
        SimpleFakeModel.code = Mock()
        
        result = base_service.bulk_create_with_merge(
            items, "code", merge_strategy, db=mock_session
        )

    def test_get_stats_basic(self, base_service, mock_session):
        """Test stats basiques."""
        mock_session.query.return_value.count.return_value = 100
        
        result = base_service.get_stats(db=mock_session)
        
        assert "total" in result
        assert result["total"] == 100


    def test_get_stats_with_count_filters(self, base_service, mock_session):
        """Test stats avec compteurs conditionnels."""
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 25
        
        SimpleFakeModel.statut = Mock()
        
        result = base_service.get_stats(
            count_filters={"actifs": {"statut": "actif"}},
            db=mock_session
        )


    @patch('src.services.base_service.Cache')
    def test_mark_as(self, mock_cache, base_service, mock_session):
        """Test marquage de statut."""
        existing = SimpleFakeModel(id=1, statut="ancien")
        mock_session.query.return_value.get.return_value = existing
        
        result = base_service.mark_as(1, "statut", "nouveau", db=mock_session)
        
        assert result is True
        assert existing.statut == "nouveau"
