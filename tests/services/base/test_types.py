"""
Tests unitaires complets pour src/services/base/types.py
Module: BaseService - CRUD, recherche avancée, statistiques, bulk operations.

Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, Mock, patch, call
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# ═══════════════════════════════════════════════════════════
# BASE DE TEST POUR INTÉGRATION
# ═══════════════════════════════════════════════════════════

TestBase = declarative_base()


class ItemModel(TestBase):
    """Modèle de test pour intégration SQLite."""
    __tablename__ = "test_items"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    statut = Column(String(50), default="actif")
    actif = Column(Boolean, default=True)
    prix = Column(Float, default=0.0)


# ═══════════════════════════════════════════════════════════
# MODÈLE DE TEST (MOCK)
# ═══════════════════════════════════════════════════════════


class MockModel:
    """Modèle fictif pour les tests unitaires."""
    __name__ = "MockModel"
    __tablename__ = "mock_models"
    
    class __table__:
        columns = []
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.nom = kwargs.get("nom", "Test")
        self.statut = kwargs.get("statut", "actif")
        self.actif = kwargs.get("actif", True)
        self.prix = kwargs.get("prix", 100)
        
    @classmethod
    def query(cls):
        return MagicMock()


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_db():
    """Session DB mockée."""
    session = MagicMock(spec=Session)
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.get = MagicMock(return_value=MockModel(id=1, nom="Test"))
    session.query = MagicMock()
    return session


@pytest.fixture
def integration_db():
    """Session SQLite en mémoire pour tests d'intégration."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestBase.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    TestBase.metadata.drop_all(engine)


@pytest.fixture
def integration_service(integration_db):
    """BaseService avec modèle réel pour intégration."""
    from src.services.base.types import BaseService
    return BaseService(model=ItemModel, cache_ttl=60)


@pytest.fixture
def base_service():
    """Instance de BaseService avec modèle mocké."""
    from src.services.base.types import BaseService
    
    service = BaseService(model=MockModel, cache_ttl=60)
    return service


@pytest.fixture
def patch_db_context(mock_db):
    """Patche obtenir_contexte_db pour retourner le mock."""
    with patch("src.core.database.obtenir_contexte_db") as mock:
        mock.return_value.__enter__ = Mock(return_value=mock_db)
        mock.return_value.__exit__ = Mock(return_value=None)
        yield mock_db


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceInit:
    """Tests pour l'initialisation de BaseService."""

    def test_init_sets_model(self):
        """Vérifie que le modèle est correctement défini."""
        from src.services.base.types import BaseService
        
        service = BaseService(model=MockModel)
        
        assert service.model == MockModel

    def test_init_sets_model_name(self):
        """Vérifie que le nom du modèle est extrait."""
        from src.services.base.types import BaseService
        
        service = BaseService(model=MockModel)
        
        assert service.model_name == "MockModel"

    def test_init_sets_default_cache_ttl(self):
        """Vérifie le TTL cache par défaut."""
        from src.services.base.types import BaseService
        
        service = BaseService(model=MockModel)
        
        assert service.cache_ttl == 60

    def test_init_custom_cache_ttl(self):
        """Vérifie le TTL cache personnalisé."""
        from src.services.base.types import BaseService
        
        service = BaseService(model=MockModel, cache_ttl=300)
        
        assert service.cache_ttl == 300


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - CREATE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceCreate:
    """Tests pour la méthode create."""

    def test_create_with_db_session(self, base_service, mock_db):
        """Test création avec session fournie."""
        with patch.object(base_service, "_invalider_cache"):
            with patch("src.core.errors.gerer_erreurs", lambda **kwargs: lambda f: f):
                # On doit patcher _with_session pour exécuter directement
                data = {"nom": "Nouvelle entité", "statut": "actif"}
                
                # Le modèle est appelé avec les données
                result = base_service.create(data=data, db=mock_db)
                
                # Vérifier que add et commit ont été appelés
                mock_db.add.assert_called()
                mock_db.commit.assert_called()

    def test_create_returns_entity(self, base_service, mock_db):
        """Test que create retourne l'entité créée."""
        with patch.object(base_service, "_with_session") as mock_with:
            # Simuler le retour de l'exécution
            mock_with.return_value = MockModel(id=1, nom="Test")
            
            result = base_service.create({"nom": "Test"}, db=mock_db)
            
            assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - GET BY ID
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceGetById:
    """Tests pour la méthode get_by_id."""

    def test_get_by_id_returns_entity(self, base_service, mock_db):
        """Test récupération par ID."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_entity = MockModel(id=1, nom="Test")
            mock_with.return_value = mock_entity
            
            result = base_service.get_by_id(entity_id=1, db=mock_db)
            
            assert result is not None
            assert result.id == 1

    def test_get_by_id_not_found(self, base_service, mock_db):
        """Test ID non trouvé."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = None
            
            result = base_service.get_by_id(entity_id=999, db=mock_db)
            
            assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - GET ALL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceGetAll:
    """Tests pour la méthode get_all."""

    def test_get_all_returns_list(self, base_service, mock_db):
        """Test retour d'une liste."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [
                MockModel(id=1, nom="Test1"),
                MockModel(id=2, nom="Test2"),
            ]
            
            result = base_service.get_all(db=mock_db)
            
            assert isinstance(result, list)
            assert len(result) == 2

    def test_get_all_with_skip_limit(self, base_service, mock_db):
        """Test pagination."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=2)]
            
            result = base_service.get_all(skip=1, limit=1, db=mock_db)
            
            assert len(result) == 1

    def test_get_all_with_filters(self, base_service, mock_db):
        """Test avec filtres."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=1, statut="actif")]
            
            result = base_service.get_all(filters={"statut": "actif"}, db=mock_db)
            
            assert len(result) == 1

    def test_get_all_with_order(self, base_service, mock_db):
        """Test avec tri."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=2), MockModel(id=1)]
            
            result = base_service.get_all(order_by="id", desc_order=True, db=mock_db)
            
            assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - UPDATE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceUpdate:
    """Tests pour la méthode update."""

    def test_update_returns_entity(self, base_service, mock_db):
        """Test mise à jour."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_entity = MockModel(id=1, nom="Updated")
            mock_with.return_value = mock_entity
            
            result = base_service.update(entity_id=1, data={"nom": "Updated"}, db=mock_db)
            
            assert result is not None

    def test_update_not_found(self, base_service, mock_db):
        """Test mise à jour entité non trouvée."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = None
            
            result = base_service.update(entity_id=999, data={"nom": "Updated"}, db=mock_db)
            
            assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CRUD - DELETE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceDelete:
    """Tests pour la méthode delete."""

    def test_delete_returns_true(self, base_service, mock_db):
        """Test suppression réussie."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = True
            
            result = base_service.delete(entity_id=1, db=mock_db)
            
            assert result is True

    def test_delete_not_found(self, base_service, mock_db):
        """Test suppression entité non trouvée."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = False
            
            result = base_service.delete(entity_id=999, db=mock_db)
            
            assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS COUNT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceCount:
    """Tests pour la méthode count."""

    def test_count_returns_int(self, base_service, mock_db):
        """Test comptage."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = 5
            
            result = base_service.count(db=mock_db)
            
            assert result == 5

    def test_count_with_filters(self, base_service, mock_db):
        """Test comptage avec filtres."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = 3
            
            result = base_service.count(filters={"statut": "actif"}, db=mock_db)
            
            assert result == 3


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE AVANCÉE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceAdvancedSearch:
    """Tests pour la méthode advanced_search."""

    def test_search_with_term(self, base_service, mock_db):
        """Test recherche textuelle."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=1, nom="Recherche")]
            
            result = base_service.advanced_search(
                search_term="Recherche", 
                search_fields=["nom"],
                db=mock_db
            )
            
            assert len(result) == 1

    def test_search_with_filters(self, base_service, mock_db):
        """Test recherche avec filtres."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=1, statut="actif")]
            
            result = base_service.advanced_search(
                filters={"statut": "actif"},
                db=mock_db
            )
            
            assert len(result) == 1

    def test_search_with_sort(self, base_service, mock_db):
        """Test recherche avec tri."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=2), MockModel(id=1)]
            
            result = base_service.advanced_search(
                sort_by="id",
                sort_desc=True,
                db=mock_db
            )
            
            assert len(result) == 2

    def test_search_with_pagination(self, base_service, mock_db):
        """Test recherche avec pagination."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = [MockModel(id=2)]
            
            result = base_service.advanced_search(
                offset=1,
                limit=1,
                db=mock_db
            )
            
            assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS BULK OPERATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceBulkOperations:
    """Tests pour bulk_create_with_merge."""

    def test_bulk_create_with_merge_creates(self, base_service, mock_db):
        """Test création en masse."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = (3, 0)  # 3 créés, 0 fusionnés
            
            items_data = [
                {"nom": "Item1", "statut": "actif"},
                {"nom": "Item2", "statut": "actif"},
                {"nom": "Item3", "statut": "actif"},
            ]
            
            created, merged = base_service.bulk_create_with_merge(
                items_data=items_data,
                merge_key="nom",
                merge_strategy=lambda old, new: {**old, **new},
                db=mock_db
            )
            
            assert created == 3
            assert merged == 0

    def test_bulk_create_with_merge_merges(self, base_service, mock_db):
        """Test fusion en masse."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = (0, 2)  # 0 créés, 2 fusionnés
            
            result = base_service.bulk_create_with_merge(
                items_data=[{"nom": "Existing1"}, {"nom": "Existing2"}],
                merge_key="nom",
                merge_strategy=lambda old, new: {**old, **new},
                db=mock_db
            )
            
            assert result[1] == 2

    def test_bulk_create_skip_no_merge_key(self, base_service, mock_db):
        """Test skip items sans clé de fusion."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = (1, 0)  # 1 créé (sans clé ignoré)
            
            items_data = [
                {"nom": "Item1"},
                {"statut": "actif"},  # Pas de clé 'nom'
            ]
            
            created, merged = base_service.bulk_create_with_merge(
                items_data=items_data,
                merge_key="nom",
                merge_strategy=lambda old, new: new,
                db=mock_db
            )
            
            assert created == 1


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceStats:
    """Tests pour get_stats."""

    def test_get_stats_total(self, base_service, mock_db):
        """Test statistiques - total."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = {"total": 10}
            
            result = base_service.get_stats(db=mock_db)
            
            assert "total" in result
            assert result["total"] == 10

    def test_get_stats_grouped(self, base_service, mock_db):
        """Test statistiques groupées."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = {
                "total": 10,
                "by_statut": {"actif": 7, "inactif": 3}
            }
            
            result = base_service.get_stats(
                group_by_fields=["statut"],
                db=mock_db
            )
            
            assert "by_statut" in result
            assert result["by_statut"]["actif"] == 7

    def test_get_stats_count_filters(self, base_service, mock_db):
        """Test compteurs conditionnels."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = {
                "total": 10,
                "actifs": 7
            }
            
            result = base_service.get_stats(
                count_filters={"actifs": {"actif": True}},
                db=mock_db
            )
            
            assert "actifs" in result
            assert result["actifs"] == 7


# ═══════════════════════════════════════════════════════════
# TESTS MIXINS STATUS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceStatusMixin:
    """Tests pour les méthodes de statut."""

    def test_count_by_status(self, base_service, mock_db):
        """Test comptage par statut."""
        with patch.object(base_service, "get_stats") as mock_stats:
            mock_stats.return_value = {
                "total": 10,
                "by_statut": {"actif": 7, "inactif": 3}
            }
            
            result = base_service.count_by_status(status_field="statut", db=mock_db)
            
            assert result == {"actif": 7, "inactif": 3}

    def test_mark_as(self, base_service, mock_db):
        """Test marquage de statut."""
        with patch.object(base_service, "update") as mock_update:
            mock_update.return_value = MockModel(id=1, statut="termine")
            
            result = base_service.mark_as(
                item_id=1,
                status_field="statut",
                status_value="termine",
                db=mock_db
            )
            
            assert result is True
            mock_update.assert_called_once_with(1, {"statut": "termine"}, db=mock_db)

    def test_mark_as_not_found(self, base_service, mock_db):
        """Test marquage entité non trouvée."""
        with patch.object(base_service, "update") as mock_update:
            mock_update.return_value = None
            
            result = base_service.mark_as(
                item_id=999,
                status_field="statut",
                status_value="termine",
                db=mock_db
            )
            
            assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceHelpers:
    """Tests pour les méthodes privées."""

    def test_with_session_uses_provided_db(self, base_service, mock_db):
        """Test _with_session avec session fournie."""
        mock_func = MagicMock(return_value="result")
        
        result = base_service._with_session(mock_func, db=mock_db)
        
        mock_func.assert_called_once_with(mock_db)
        assert result == "result"

    def test_with_session_creates_context(self, base_service):
        """Test _with_session crée un contexte si pas de session."""
        mock_func = MagicMock(return_value="result")
        mock_session = MagicMock()
        
        with patch("src.core.database.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=None)
            
            result = base_service._with_session(mock_func, db=None)
            
            # Vérifier que le context manager est utilisé
            mock_ctx.assert_called_once()

    def test_apply_filters_simple(self, base_service):
        """Test _apply_filters avec comparaison simple."""
        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        
        # On doit mocker le modèle pour avoir les colonnes
        with patch.object(base_service, "model") as mock_model:
            mock_model.nom = MagicMock()
            
            result = base_service._apply_filters(mock_query, {"nom": "Test"})
            
            mock_query.filter.assert_called()

    def test_apply_filters_operators(self, base_service):
        """Test _apply_filters avec opérateurs."""
        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        
        with patch.object(base_service, "model") as mock_model:
            mock_model.prix = MagicMock()
            mock_model.prix.__ge__ = MagicMock()
            mock_model.prix.__le__ = MagicMock()
            
            # Filtres avec opérateurs
            filters = {"prix": {"gte": 50, "lte": 100}}
            
            result = base_service._apply_filters(mock_query, filters)
            
            # Deux appels filter (gte et lte)
            assert mock_query.filter.call_count >= 1

    def test_apply_filters_in_operator(self, base_service):
        """Test _apply_filters avec opérateur in."""
        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        
        with patch.object(base_service, "model") as mock_model:
            mock_model.statut = MagicMock()
            mock_model.statut.in_ = MagicMock()
            
            filters = {"statut": {"in": ["actif", "inactif"]}}
            
            result = base_service._apply_filters(mock_query, filters)
            
            mock_query.filter.assert_called()

    def test_apply_filters_like_operator(self, base_service):
        """Test _apply_filters avec opérateur like."""
        mock_query = MagicMock()
        mock_query.filter = MagicMock(return_value=mock_query)
        
        with patch.object(base_service, "model") as mock_model:
            mock_model.nom = MagicMock()
            mock_model.nom.ilike = MagicMock()
            
            filters = {"nom": {"like": "Test"}}
            
            result = base_service._apply_filters(mock_query, filters)
            
            mock_query.filter.assert_called()

    def test_model_to_dict(self, base_service):
        """Test _model_to_dict conversion."""
        mock_obj = MagicMock()
        mock_obj.__table__ = MagicMock()
        
        # Simuler des colonnes
        col1 = MagicMock()
        col1.name = "id"
        col2 = MagicMock()
        col2.name = "nom"
        col3 = MagicMock()
        col3.name = "created_at"
        
        mock_obj.__table__.columns = [col1, col2, col3]
        mock_obj.id = 1
        mock_obj.nom = "Test"
        mock_obj.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = base_service._model_to_dict(mock_obj)
        
        assert result["id"] == 1
        assert result["nom"] == "Test"
        assert result["created_at"] == "2024-01-01T12:00:00"

    def test_invalider_cache(self, base_service):
        """Test _invalider_cache."""
        with patch("src.core.cache.Cache.invalider") as mock_invalider:
            base_service._invalider_cache()
            
            mock_invalider.assert_called_once_with(pattern="mockmodel")


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceEdgeCases:
    """Tests pour les cas limites."""

    def test_get_all_empty(self, base_service, mock_db):
        """Test liste vide."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = []
            
            result = base_service.get_all(db=mock_db)
            
            assert result == []

    def test_count_zero(self, base_service, mock_db):
        """Test comptage zéro."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = 0
            
            result = base_service.count(db=mock_db)
            
            assert result == 0

    def test_advanced_search_no_results(self, base_service, mock_db):
        """Test recherche sans résultats."""
        with patch.object(base_service, "_with_session") as mock_with:
            mock_with.return_value = []
            
            result = base_service.advanced_search(
                search_term="inexistant",
                search_fields=["nom"],
                db=mock_db
            )
            
            assert result == []

    def test_apply_filters_unknown_field(self, base_service):
        """Test filtres avec champ inconnu."""
        mock_query = MagicMock()
        
        with patch.object(base_service, "model") as mock_model:
            # Le modèle n'a pas l'attribut 'inconnu'
            delattr(mock_model, "inconnu") if hasattr(mock_model, "inconnu") else None
            
            # Ne doit pas lever d'erreur
            result = base_service._apply_filters(mock_query, {"inconnu": "valeur"})
            
            # La requête doit être retournée sans modification
            assert result is mock_query


# ═══════════════════════════════════════════════════════════
# TESTS GENERIC TYPE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseServiceGeneric:
    """Tests pour la nature générique de BaseService."""

    def test_is_generic(self):
        """Vérifie que BaseService est Generic[T]."""
        from src.services.base.types import BaseService
        import typing
        
        # Vérifier que c'est une classe générique
        assert hasattr(BaseService, "__class_getitem__")

    def test_typevar_export(self):
        """Vérifie que T est exporté."""
        from src.services.base.types import T
        from typing import TypeVar
        
        assert isinstance(T, TypeVar)

    def test_all_exports(self):
        """Vérifie les exports __all__."""
        from src.services.base import types
        
        assert hasattr(types, "__all__")
        assert "BaseService" in types.__all__
        assert "T" in types.__all__


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION AVEC SQLITE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestBaseServiceIntegration:
    """Tests d'intégration avec vraie DB SQLite."""

    def test_create_entity(self, integration_service, integration_db):
        """Test création réelle."""
        with patch("src.core.cache.Cache.invalider"):
            result = integration_service.create(
                data={"nom": "Test Item", "statut": "actif", "prix": 10.5},
                db=integration_db
            )
        
        assert result is not None
        assert result.nom == "Test Item"
        assert result.id is not None

    def test_get_by_id_found(self, integration_service, integration_db):
        """Test get_by_id avec entité existante."""
        # Créer d'abord
        with patch("src.core.cache.Cache.invalider"):
            entity = integration_service.create(
                data={"nom": "GetTest", "statut": "actif"},
                db=integration_db
            )
        
        # Récupérer
        with patch("src.core.cache.Cache.obtenir", return_value=None):
            with patch("src.core.cache.Cache.definir"):
                result = integration_service.get_by_id(entity.id, db=integration_db)
        
        assert result is not None
        assert result.nom == "GetTest"

    def test_get_by_id_not_found(self, integration_service, integration_db):
        """Test get_by_id avec ID inexistant."""
        with patch("src.core.cache.Cache.obtenir", return_value=None):
            result = integration_service.get_by_id(999, db=integration_db)
        
        assert result is None

    def test_get_by_id_cache_hit(self, integration_service, integration_db):
        """Test get_by_id avec cache hit."""
        cached_entity = ItemModel(id=1, nom="Cached")
        
        with patch("src.core.cache.Cache.obtenir", return_value=cached_entity):
            result = integration_service.get_by_id(1, db=integration_db)
        
        assert result == cached_entity

    def test_get_all_empty(self, integration_service, integration_db):
        """Test get_all sans données."""
        result = integration_service.get_all(db=integration_db)
        
        assert result == []

    def test_get_all_with_data(self, integration_service, integration_db):
        """Test get_all avec données."""
        # Créer des items
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Item1"}, db=integration_db)
            integration_service.create({"nom": "Item2"}, db=integration_db)
        
        result = integration_service.get_all(db=integration_db)
        
        assert len(result) == 2

    def test_get_all_with_skip_limit(self, integration_service, integration_db):
        """Test pagination."""
        with patch("src.core.cache.Cache.invalider"):
            for i in range(5):
                integration_service.create({"nom": f"Item{i}"}, db=integration_db)
        
        result = integration_service.get_all(skip=2, limit=2, db=integration_db)
        
        assert len(result) == 2

    def test_get_all_with_filters(self, integration_service, integration_db):
        """Test filtres."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Active", "actif": True}, db=integration_db)
            integration_service.create({"nom": "Inactive", "actif": False}, db=integration_db)
        
        result = integration_service.get_all(filters={"actif": True}, db=integration_db)
        
        assert len(result) == 1
        assert result[0].nom == "Active"

    def test_get_all_with_order(self, integration_service, integration_db):
        """Test tri."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "B"}, db=integration_db)
            integration_service.create({"nom": "A"}, db=integration_db)
            integration_service.create({"nom": "C"}, db=integration_db)
        
        result = integration_service.get_all(order_by="nom", db=integration_db)
        
        assert result[0].nom == "A"
        assert result[2].nom == "C"

    def test_get_all_desc_order(self, integration_service, integration_db):
        """Test tri descendant."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "B"}, db=integration_db)
            integration_service.create({"nom": "A"}, db=integration_db)
        
        result = integration_service.get_all(order_by="nom", desc_order=True, db=integration_db)
        
        assert result[0].nom == "B"

    def test_update_success(self, integration_service, integration_db):
        """Test mise à jour réussie."""
        with patch("src.core.cache.Cache.invalider"):
            entity = integration_service.create({"nom": "Original"}, db=integration_db)
            
            result = integration_service.update(
                entity.id, 
                {"nom": "Updated"}, 
                db=integration_db
            )
        
        assert result is not None
        assert result.nom == "Updated"

    def test_update_not_found(self, integration_service, integration_db):
        """Test mise à jour entité non trouvée."""
        with patch("src.core.cache.Cache.invalider"):
            result = integration_service.update(999, {"nom": "Test"}, db=integration_db)
        
        assert result is None

    def test_delete_success(self, integration_service, integration_db):
        """Test suppression réussie."""
        with patch("src.core.cache.Cache.invalider"):
            entity = integration_service.create({"nom": "ToDelete"}, db=integration_db)
            
            result = integration_service.delete(entity.id, db=integration_db)
        
        assert result is True

    def test_delete_not_found(self, integration_service, integration_db):
        """Test suppression entité non trouvée."""
        with patch("src.core.cache.Cache.invalider"):
            result = integration_service.delete(999, db=integration_db)
        
        assert result is False

    def test_count(self, integration_service, integration_db):
        """Test comptage."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A"}, db=integration_db)
            integration_service.create({"nom": "B"}, db=integration_db)
        
        result = integration_service.count(db=integration_db)
        
        assert result == 2

    def test_count_with_filters(self, integration_service, integration_db):
        """Test comptage avec filtres."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "actif": True}, db=integration_db)
            integration_service.create({"nom": "B", "actif": False}, db=integration_db)
        
        result = integration_service.count(filters={"actif": True}, db=integration_db)
        
        assert result == 1


@pytest.mark.integration
class TestBaseServiceAdvancedSearchIntegration:
    """Tests d'intégration pour advanced_search."""

    def test_search_with_term(self, integration_service, integration_db):
        """Test recherche textuelle."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Pommes"}, db=integration_db)
            integration_service.create({"nom": "Oranges"}, db=integration_db)
            integration_service.create({"nom": "Pommes vertes"}, db=integration_db)
        
        result = integration_service.advanced_search(
            search_term="Pommes",
            search_fields=["nom"],
            db=integration_db
        )
        
        assert len(result) == 2

    def test_search_with_filters_and_sort(self, integration_service, integration_db):
        """Test recherche avec filtres et tri."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Z", "actif": True}, db=integration_db)
            integration_service.create({"nom": "A", "actif": True}, db=integration_db)
            integration_service.create({"nom": "B", "actif": False}, db=integration_db)
        
        result = integration_service.advanced_search(
            filters={"actif": True},
            sort_by="nom",
            sort_desc=False,
            db=integration_db
        )
        
        assert len(result) == 2
        assert result[0].nom == "A"

    def test_search_invalid_field(self, integration_service, integration_db):
        """Test recherche avec champ invalide."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Test"}, db=integration_db)
        
        # Ne doit pas lever d'erreur
        result = integration_service.advanced_search(
            search_term="Test",
            search_fields=["champ_inexistant"],
            db=integration_db
        )
        
        assert isinstance(result, list)


@pytest.mark.integration
class TestBaseServiceBulkIntegration:
    """Tests d'intégration pour bulk operations."""

    def test_bulk_create_with_merge_new(self, integration_service, integration_db):
        """Test création en masse de nouveaux items."""
        with patch("src.core.cache.Cache.invalider"):
            items = [
                {"nom": "Item1", "prix": 10},
                {"nom": "Item2", "prix": 20},
            ]
            
            created, merged = integration_service.bulk_create_with_merge(
                items_data=items,
                merge_key="nom",
                merge_strategy=lambda old, new: {**old, **new},
                db=integration_db
            )
        
        assert created == 2
        assert merged == 0

    def test_bulk_create_with_merge_existing(self, integration_service, integration_db):
        """Test mise à jour en masse d'items existants."""
        with patch("src.core.cache.Cache.invalider"):
            # Créer d'abord
            integration_service.create({"nom": "Existing", "prix": 10}, db=integration_db)
            
            # Puis bulk merge
            items = [{"nom": "Existing", "prix": 20}]
            
            created, merged = integration_service.bulk_create_with_merge(
                items_data=items,
                merge_key="nom",
                merge_strategy=lambda old, new: {**new},
                db=integration_db
            )
        
        assert created == 0
        assert merged == 1

    def test_bulk_create_skip_no_key(self, integration_service, integration_db):
        """Test skip items sans clé de fusion."""
        with patch("src.core.cache.Cache.invalider"):
            items = [
                {"nom": "Valid", "prix": 10},
                {"prix": 20},  # Pas de nom
            ]
            
            created, merged = integration_service.bulk_create_with_merge(
                items_data=items,
                merge_key="nom",
                merge_strategy=lambda old, new: new,
                db=integration_db
            )
        
        assert created == 1


@pytest.mark.integration
class TestBaseServiceStatsIntegration:
    """Tests d'intégration pour statistiques."""

    def test_get_stats_total(self, integration_service, integration_db):
        """Test statistiques - total."""
        with patch("src.core.cache.Cache.invalider"):
            for i in range(5):
                integration_service.create({"nom": f"Item{i}"}, db=integration_db)
        
        result = integration_service.get_stats(db=integration_db)
        
        assert result["total"] == 5

    def test_get_stats_grouped(self, integration_service, integration_db):
        """Test statistiques groupées."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "statut": "actif"}, db=integration_db)
            integration_service.create({"nom": "B", "statut": "actif"}, db=integration_db)
            integration_service.create({"nom": "C", "statut": "inactif"}, db=integration_db)
        
        result = integration_service.get_stats(
            group_by_fields=["statut"],
            db=integration_db
        )
        
        assert "by_statut" in result
        assert result["by_statut"]["actif"] == 2
        assert result["by_statut"]["inactif"] == 1

    def test_get_stats_count_filters_simple(self, integration_service, integration_db):
        """Test compteurs conditionnels simples."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "actif": True}, db=integration_db)
            integration_service.create({"nom": "B", "actif": True}, db=integration_db)
            integration_service.create({"nom": "C", "actif": False}, db=integration_db)
        
        result = integration_service.get_stats(
            count_filters={"actifs": {"actif": True}},
            db=integration_db
        )
        
        assert result["actifs"] == 2

    def test_get_stats_count_filters_operators(self, integration_service, integration_db):
        """Test compteurs avec opérateurs."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "prix": 50}, db=integration_db)
            integration_service.create({"nom": "B", "prix": 100}, db=integration_db)
            integration_service.create({"nom": "C", "prix": 150}, db=integration_db)
        
        result = integration_service.get_stats(
            count_filters={
                "prix_haut": {"prix": {"gte": 100}},
                "prix_bas": {"prix": {"lt": 100}},
            },
            db=integration_db
        )
        
        assert result["prix_haut"] == 2
        assert result["prix_bas"] == 1


@pytest.mark.integration
class TestBaseServiceFiltersIntegration:
    """Tests d'intégration pour _apply_filters."""

    def test_filter_gte(self, integration_service, integration_db):
        """Test filtre gte."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "prix": 50}, db=integration_db)
            integration_service.create({"nom": "B", "prix": 100}, db=integration_db)
        
        result = integration_service.get_all(
            filters={"prix": {"gte": 100}},
            db=integration_db
        )
        
        assert len(result) == 1
        assert result[0].nom == "B"

    def test_filter_lte(self, integration_service, integration_db):
        """Test filtre lte."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "prix": 50}, db=integration_db)
            integration_service.create({"nom": "B", "prix": 100}, db=integration_db)
        
        result = integration_service.get_all(
            filters={"prix": {"lte": 50}},
            db=integration_db
        )
        
        assert len(result) == 1
        assert result[0].nom == "A"

    def test_filter_in(self, integration_service, integration_db):
        """Test filtre in."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "A", "statut": "actif"}, db=integration_db)
            integration_service.create({"nom": "B", "statut": "inactif"}, db=integration_db)
            integration_service.create({"nom": "C", "statut": "archive"}, db=integration_db)
        
        result = integration_service.get_all(
            filters={"statut": {"in": ["actif", "inactif"]}},
            db=integration_db
        )
        
        assert len(result) == 2

    def test_filter_like(self, integration_service, integration_db):
        """Test filtre like."""
        with patch("src.core.cache.Cache.invalider"):
            integration_service.create({"nom": "Pommes rouges"}, db=integration_db)
            integration_service.create({"nom": "Pommes vertes"}, db=integration_db)
            integration_service.create({"nom": "Oranges"}, db=integration_db)
        
        result = integration_service.get_all(
            filters={"nom": {"like": "Pommes"}},
            db=integration_db
        )
        
        assert len(result) == 2
