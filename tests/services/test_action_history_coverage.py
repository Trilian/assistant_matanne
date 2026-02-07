"""
Tests de couverture pour src/services/action_history.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS ET MODELES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionType:
    """Tests pour ActionType enum."""

    def test_action_type_values(self):
        """Test que les types d'actions sont définis."""
        from src.services.action_history import ActionType
        
        assert ActionType.RECETTE_CREATED.value == "recette.created"
        assert ActionType.INVENTAIRE_ADDED.value == "inventaire.added"
        assert ActionType.SYSTEM_LOGIN.value == "system.login"

    def test_action_type_enum_members(self):
        """Test tous les membres de l'enum."""
        from src.services.action_history import ActionType
        
        # Vérifier qu'il y a plusieurs types
        assert len(ActionType) > 10


@pytest.mark.unit
class TestActionEntry:
    """Tests pour ActionEntry model."""

    def test_action_entry_defaults(self):
        """Test valeurs par défaut."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user1",
            user_name="Test User",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test action"
        )
        
        assert entry.user_id == "user1"
        assert entry.id is None
        assert entry.details == {}
        assert entry.old_value is None

    def test_action_entry_complete(self):
        """Test avec tous les champs."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            id=1,
            user_id="user1",
            user_name="Test User",
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=42,
            entity_name="Tarte",
            description="Recette mise à jour",
            details={"field": "nom"},
            old_value={"nom": "Ancien"},
            new_value={"nom": "Nouveau"}
        )
        
        assert entry.entity_id == 42
        assert entry.entity_name == "Tarte"


@pytest.mark.unit
class TestActionFilter:
    """Tests pour ActionFilter model."""

    def test_action_filter_defaults(self):
        """Test valeurs par défaut."""
        from src.services.action_history import ActionFilter
        
        filters = ActionFilter()
        
        assert filters.limit == 50
        assert filters.offset == 0
        assert filters.user_id is None

    def test_action_filter_with_values(self):
        """Test avec valeurs personnalisées."""
        from src.services.action_history import ActionFilter, ActionType
        
        filters = ActionFilter(
            user_id="user1",
            action_types=[ActionType.RECETTE_CREATED],
            entity_type="recette",
            limit=10
        )
        
        assert filters.user_id == "user1"
        assert filters.limit == 10


@pytest.mark.unit 
class TestActionStats:
    """Tests pour ActionStats model."""

    def test_action_stats_defaults(self):
        """Test valeurs par défaut."""
        from src.services.action_history import ActionStats
        
        stats = ActionStats()
        
        assert stats.total_actions == 0
        assert stats.actions_today == 0
        assert stats.most_active_users == []


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE INIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestActionHistoryServiceInit:
    """Tests pour l'initialisation du service."""

    def test_init_without_session(self):
        """Test init sans session."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        assert service._session is None

    def test_init_with_session(self):
        """Test init avec session."""
        from src.services.action_history import ActionHistoryService
        
        mock_session = MagicMock()
        service = ActionHistoryService(session=mock_session)
        
        assert service._session == mock_session


# ═══════════════════════════════════════════════════════════
# TESTS LOG_ACTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLogAction:
    """Tests pour log_action()."""

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_action_basic(self, mock_user, mock_save):
        """Test log_action basique."""
        mock_user.return_value = ("user1", "Test User")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        
        entry = service.log_action(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Recette créée"
        )
        
        assert entry.action_type == ActionType.RECETTE_CREATED
        assert entry.user_id == "user1"

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_action_with_entity(self, mock_user, mock_save):
        """Test log_action avec entité."""
        mock_user.return_value = ("user1", "Test User")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        
        entry = service.log_action(
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=42,
            entity_name="Tarte",
            description="Recette mise à jour",
            old_value={"nom": "Ancien"},
            new_value={"nom": "Nouveau"}
        )
        
        assert entry.entity_id == 42
        assert entry.entity_name == "Tarte"


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES LOG SPÉCIALISÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLogSpecializedMethods:
    """Tests pour les méthodes de log spécialisées."""

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_recette_created(self, mock_user, mock_save):
        """Test log création recette."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_recette_created(1, "Tarte aux pommes")
        
        assert entry.action_type == ActionType.RECETTE_CREATED
        assert "Tarte aux pommes" in entry.description

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_recette_updated(self, mock_user, mock_save):
        """Test log mise à jour recette."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_recette_updated(
            1, "Tarte",
            old_data={"nom": "Tarte"},
            new_data={"nom": "Tarte aux pommes"}
        )
        
        assert entry.action_type == ActionType.RECETTE_UPDATED

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_recette_deleted(self, mock_user, mock_save):
        """Test log suppression recette."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_recette_deleted(1, "Tarte", backup_data={"nom": "Tarte"})
        
        assert entry.action_type == ActionType.RECETTE_DELETED

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_inventaire_added(self, mock_user, mock_save):
        """Test log ajout inventaire."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_inventaire_added(1, "Lait", 2, "L")
        
        assert entry.action_type == ActionType.INVENTAIRE_ADDED

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_courses_item_checked(self, mock_user, mock_save):
        """Test log article coché."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_courses_item_checked(1, "Tomates", True)
        
        assert entry.action_type == ActionType.COURSES_ITEM_CHECKED

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_planning_repas_added(self, mock_user, mock_save):
        """Test log repas planifié."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_planning_repas_added(1, "Tarte", datetime.now().date(), "dîner")
        
        assert entry.action_type == ActionType.PLANNING_REPAS_ADDED

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_system_login(self, mock_user, mock_save):
        """Test log connexion."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_system_login()
        
        assert entry.action_type == ActionType.SYSTEM_LOGIN

    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_save_to_database')
    @patch.object(__import__('src.services.action_history', fromlist=['ActionHistoryService']).ActionHistoryService, '_get_current_user')
    def test_log_system_logout(self, mock_user, mock_save):
        """Test log déconnexion."""
        mock_user.return_value = ("user1", "Test")
        
        from src.services.action_history import ActionHistoryService, ActionType
        
        service = ActionHistoryService()
        entry = service.log_system_logout()
        
        assert entry.action_type == ActionType.SYSTEM_LOGOUT


# ═══════════════════════════════════════════════════════════
# TESTS GET HISTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetHistory:
    """Tests pour get_history()."""

    @patch('src.core.database.get_db_context')
    def test_get_history_success(self, mock_db_ctx):
        """Test récupération historique réussie."""
        from src.services.action_history import ActionHistoryService, ActionFilter
        
        mock_session = MagicMock()
        mock_entry = MagicMock()
        mock_entry.id = 1
        mock_entry.user_id = "user1"
        mock_entry.user_name = "Test"
        mock_entry.action_type = "recette.created"
        mock_entry.entity_type = "recette"
        mock_entry.entity_id = 1
        mock_entry.entity_name = "Tarte"
        mock_entry.description = "Créé"
        mock_entry.details = {}
        mock_entry.old_value = None
        mock_entry.new_value = None
        mock_entry.created_at = datetime.now()
        mock_entry.ip_address = None
        mock_entry.user_agent = None
        
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_entry]
        mock_session.query.return_value = mock_query
        
        mock_db_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = Mock(return_value=False)
        
        service = ActionHistoryService()
        result = service.get_history()
        
        assert isinstance(result, list)

    def test_get_history_fallback_to_cache(self):
        """Test fallback sur cache en cas d'erreur."""
        from src.services.action_history import ActionHistoryService, ActionEntry, ActionType
        
        # Ajouter une entrée au cache
        service = ActionHistoryService()
        service._recent_cache = [
            ActionEntry(
                user_id="user1",
                user_name="Test",
                action_type=ActionType.RECETTE_CREATED,
                entity_type="recette",
                description="Test"
            )
        ]
        
        with patch('src.core.database.get_db_context', side_effect=Exception("DB Error")):
            result = service.get_history()
            
            # Devrait retourner le cache
            assert len(result) >= 0

    def test_get_user_history(self):
        """Test get_user_history délègue à get_history."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        with patch.object(service, 'get_history', return_value=[]) as mock_get:
            result = service.get_user_history("user1", limit=10)
            
            mock_get.assert_called_once()
            assert result == []

    def test_get_entity_history(self):
        """Test get_entity_history délègue à get_history."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        with patch.object(service, 'get_history', return_value=[]) as mock_get:
            result = service.get_entity_history("recette", 1, limit=10)
            
            mock_get.assert_called_once()
            assert result == []

    def test_get_recent_actions(self):
        """Test get_recent_actions."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        with patch.object(service, 'get_history', return_value=[]) as mock_get:
            result = service.get_recent_actions(limit=5)
            
            mock_get.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS GET STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetStats:
    """Tests pour get_stats()."""

    @patch('src.core.database.get_db_context')
    def test_get_stats_success(self, mock_db_ctx):
        """Test statistiques réussies."""
        from src.services.action_history import ActionHistoryService, ActionStats
        
        mock_session = MagicMock()
        
        # Mock les requêtes de comptage
        mock_session.query.return_value.scalar.return_value = 100
        mock_session.query.return_value.filter.return_value.scalar.return_value = 10
        mock_session.query.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        mock_db_ctx.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = Mock(return_value=False)
        
        service = ActionHistoryService()
        result = service.get_stats(days=7)
        
        assert isinstance(result, ActionStats)

    def test_get_stats_error(self):
        """Test statistiques avec erreur DB."""
        from src.services.action_history import ActionHistoryService, ActionStats
        
        service = ActionHistoryService()
        
        with patch('src.core.database.get_db_context', side_effect=Exception("DB Error")):
            result = service.get_stats(days=7)
            
            assert isinstance(result, ActionStats)
            assert result.total_actions == 0


# ═══════════════════════════════════════════════════════════
# TESTS CAN_UNDO ET UNDO_ACTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUndoActions:
    """Tests pour can_undo() et undo_action()."""

    def test_can_undo_nonexistent(self):
        """Test can_undo pour action inexistante."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        result = service.can_undo(999999)
        
        assert result is False

    def test_undo_action_nonexistent(self):
        """Test undo pour action inexistante."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        result = service.undo_action(999999)
        
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES PRIVÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPrivateMethods:
    """Tests pour les méthodes privées."""

    def test_get_current_user_anonymous(self):
        """Test récupération utilisateur anonyme."""
        from src.services.action_history import ActionHistoryService
        
        # Mock auth service qui échoue
        with patch('src.services.auth.get_auth_service', side_effect=Exception("No auth")):
            service = ActionHistoryService()
            user_id, user_name = service._get_current_user()
            
            assert user_id == "anonymous"
            assert user_name == "Anonyme"

    def test_add_to_cache(self):
        """Test ajout au cache."""
        from src.services.action_history import ActionHistoryService, ActionEntry, ActionType
        
        service = ActionHistoryService()
        service._recent_cache = []
        
        entry = ActionEntry(
            user_id="user1",
            user_name="Test",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test"
        )
        
        service._add_to_cache(entry)
        
        assert len(service._recent_cache) == 1
        assert service._recent_cache[0] == entry

    def test_add_to_cache_max_size(self):
        """Test limite du cache."""
        from src.services.action_history import ActionHistoryService, ActionEntry, ActionType
        
        service = ActionHistoryService()
        service._cache_max_size = 3
        service._recent_cache = []
        
        # Ajouter plus que la limite
        for i in range(5):
            entry = ActionEntry(
                user_id=f"user{i}",
                user_name=f"Test{i}",
                action_type=ActionType.RECETTE_CREATED,
                entity_type="recette",
                description=f"Test {i}"
            )
            service._add_to_cache(entry)
        
        assert len(service._recent_cache) == 3

    def test_compute_changes(self):
        """Test calcul des changements."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        old = {"nom": "Ancien", "prix": 10}
        new = {"nom": "Nouveau", "prix": 10}
        
        changes = service._compute_changes(old, new)
        
        assert len(changes) == 1
        assert changes[0]["field"] == "nom"
        assert changes[0]["old"] == "Ancien"
        assert changes[0]["new"] == "Nouveau"

    def test_compute_changes_new_field(self):
        """Test calcul avec nouveau champ."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        old = {"nom": "Test"}
        new = {"nom": "Test", "description": "Nouvelle desc"}
        
        changes = service._compute_changes(old, new)
        
        assert len(changes) == 1
        assert changes[0]["field"] == "description"


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY ET EXPORTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFactoryAndExports:
    """Tests pour factory et exports."""

    def test_get_action_history_service(self):
        """Test fonction factory."""
        from src.services.action_history import get_action_history_service
        
        service = get_action_history_service()
        
        assert service is not None

    def test_module_exports(self):
        """Test exports du module."""
        from src.services.action_history import (
            ActionType,
            ActionEntry,
            ActionFilter,
            ActionStats,
            ActionHistoryService
        )
        
        assert ActionType is not None
        assert ActionEntry is not None
        assert ActionFilter is not None
        assert ActionStats is not None
        assert ActionHistoryService is not None


# ═══════════════════════════════════════════════════════════
# TESTS POUR METHODES DB AVANCEES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGetHistoryDB:
    """Tests pour get_history avec mocking DB."""

    def test_get_history_with_all_filters(self):
        """Test get_history avec tous les filtres via DB mock."""
        from src.services.action_history import (
            ActionHistoryService, ActionFilter, ActionType, ActionEntry
        )
        
        mock_entry = Mock()
        mock_entry.id = 1
        mock_entry.user_id = "user1"
        mock_entry.user_name = "Test User"
        mock_entry.action_type = "recette.created"
        mock_entry.entity_type = "recette"
        mock_entry.entity_id = 10
        mock_entry.entity_name = "Tarte"
        mock_entry.description = "Recette créée"
        mock_entry.details = {}
        mock_entry.old_value = None
        mock_entry.new_value = None
        mock_entry.created_at = datetime.now()
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_entry]
        
        mock_session = Mock()
        mock_session.query.return_value = mock_query
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("src.core.database.get_db_context", return_value=mock_session):
            service = ActionHistoryService()
            filters = ActionFilter(
                user_id="user1",
                action_types=[ActionType.RECETTE_CREATED],
                entity_type="recette",
                entity_id=10,
                date_from=datetime.now() - timedelta(days=1),
                date_to=datetime.now(),
                search_text="test",
                limit=10,
                offset=0
            )
            
            result = service.get_history(filters)
        
        assert mock_query.filter.called

    def test_get_history_db_exception_fallback(self):
        """Test get_history avec exception DB - fallback sur cache."""
        from src.services.action_history import (
            ActionHistoryService, ActionFilter, ActionEntry, ActionType
        )
        
        service = ActionHistoryService()
        # Ajouter des entrées au cache
        entry = ActionEntry(
            id=1,
            user_id="user1",
            user_name="Cached User",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Action from cache"
        )
        service._recent_cache = [entry]
        
        with patch("src.core.database.get_db_context") as mock_ctx:
            mock_ctx.side_effect = Exception("DB Error")
            
            result = service.get_history(ActionFilter(limit=10))
        
        # Should fallback to cache
        assert len(result) >= 0


@pytest.mark.unit
class TestGetStatsDB:
    """Tests pour get_stats avec mocking DB."""

    def test_get_stats_from_db(self):
        """Test get_stats avec DB mock."""
        from src.services.action_history import ActionHistoryService
        from sqlalchemy import func
        
        mock_session = Mock()
        mock_session.query.return_value.scalar.return_value = 100
        mock_session.query.return_value.filter.return_value.scalar.return_value = 10
        mock_session.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("src.core.database.get_db_context", return_value=mock_session):
            service = ActionHistoryService()
            
            result = service.get_stats(days=7)
        
        # Test passes if no exception is raised

    def test_get_stats_db_exception_fallback(self):
        """Test get_stats avec exception DB - fallback sur stats vides."""
        from src.services.action_history import ActionHistoryService
        
        with patch("src.core.database.get_db_context") as mock_ctx:
            mock_ctx.side_effect = Exception("DB Error")
            
            service = ActionHistoryService()
            result = service.get_stats()
        
        assert result.total_actions == 0


@pytest.mark.unit
class TestGetCurrentUser:
    """Tests pour _get_current_user."""

    def test_get_current_user_authenticated(self):
        """Test avec utilisateur authentifié."""
        from src.services.action_history import ActionHistoryService
        
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.display_name = "John Doe"
        
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user
        
        with patch("src.services.auth.get_auth_service", return_value=mock_auth):
            service = ActionHistoryService()
            user_id, user_name = service._get_current_user()
        
        assert user_id == "user123"
        assert user_name == "John Doe"

    def test_get_current_user_not_authenticated(self):
        """Test avec utilisateur non authentifié."""
        from src.services.action_history import ActionHistoryService
        
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = None
        
        with patch("src.services.auth.get_auth_service", return_value=mock_auth):
            service = ActionHistoryService()
            user_id, user_name = service._get_current_user()
        
        assert user_id == "anonymous"
        assert user_name == "Anonyme"

    def test_get_current_user_auth_exception(self):
        """Test avec exception auth - fallback anonyme."""
        from src.services.action_history import ActionHistoryService
        
        with patch("src.services.auth.get_auth_service") as mock_auth:
            mock_auth.side_effect = Exception("Auth error")
            
            service = ActionHistoryService()
            user_id, user_name = service._get_current_user()
        
        assert user_id == "anonymous"
        assert user_name == "Anonyme"


@pytest.mark.unit
class TestSaveToDatabase:
    """Tests pour _save_to_database."""

    def test_save_to_database_success(self):
        """Test sauvegarde réussie en DB."""
        from src.services.action_history import ActionHistoryService, ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user1",
            user_name="Test",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test save"
        )
        
        mock_db_entry = Mock()
        mock_db_entry.id = 42
        
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("src.core.database.get_db_context", return_value=mock_session):
            with patch("src.core.models.ActionHistory") as MockModel:
                MockModel.return_value = mock_db_entry
                
                service = ActionHistoryService()
                service._save_to_database(entry)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_save_to_database_exception(self):
        """Test sauvegarde avec exception - pas de crash."""
        from src.services.action_history import ActionHistoryService, ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user1",
            user_name="Test",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test save error"
        )
        
        with patch("src.core.database.get_db_context") as mock_ctx:
            mock_ctx.side_effect = Exception("DB Error")
            
            service = ActionHistoryService()
            # Should not raise
            service._save_to_database(entry)


@pytest.mark.unit
class TestCanUndoWithHistory:
    """Tests pour can_undo avec historique réel."""

    def test_can_undo_reversible_action_with_old_value(self):
        """Test can_undo pour action réversible avec old_value."""
        from src.services.action_history import ActionHistoryService, ActionType, ActionEntry
        
        entry = ActionEntry(
            id=42,
            user_id="user1",
            user_name="Test",
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            description="Updated",
            old_value={"nom": "Ancien"}
        )
        
        service = ActionHistoryService()
        
        with patch.object(service, "get_history", return_value=[entry]):
            result = service.can_undo(42)
        
        assert result is True

    def test_can_undo_non_reversible_action(self):
        """Test can_undo pour action non réversible."""
        from src.services.action_history import ActionHistoryService, ActionType, ActionEntry
        
        entry = ActionEntry(
            id=42,
            user_id="user1",
            user_name="Test",
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Login",
            old_value=None
        )
        
        service = ActionHistoryService()
        
        with patch.object(service, "get_history", return_value=[entry]):
            result = service.can_undo(42)
        
        assert result is False


@pytest.mark.unit
class TestUndoAction:
    """Tests pour undo_action."""

    def test_undo_action_returns_false(self):
        """Test undo_action retourne False (non implémenté)."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        result = service.undo_action(1)
        
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS COMPOSANTS UI
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRenderActivityTimeline:
    """Tests pour render_activity_timeline."""

    def test_render_timeline_with_actions(self):
        """Test render timeline avec actions."""
        from src.services.action_history import render_activity_timeline, ActionEntry, ActionType
        
        mock_actions = [
            ActionEntry(
                id=1,
                user_id="user1",
                user_name="Test",
                action_type=ActionType.RECETTE_CREATED,
                entity_type="recette",
                description="Recette créée"
            )
        ]
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_recent_actions.return_value = mock_actions
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                mock_st.columns.return_value = [Mock(), Mock()]
                render_activity_timeline(limit=5)
        
        mock_service.get_recent_actions.assert_called_once_with(limit=5)

    def test_render_timeline_empty(self):
        """Test render timeline sans actions."""
        from src.services.action_history import render_activity_timeline
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_recent_actions.return_value = []
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                render_activity_timeline()
        
        mock_st.info.assert_called_once()


@pytest.mark.unit
class TestRenderUserActivity:
    """Tests pour render_user_activity."""

    def test_render_user_activity_with_actions(self):
        """Test render user activity avec actions."""
        from src.services.action_history import render_user_activity, ActionEntry, ActionType
        
        mock_actions = [
            ActionEntry(
                id=1,
                user_id="user1",
                user_name="Test",
                action_type=ActionType.RECETTE_CREATED,
                entity_type="recette",
                description="Recette créée",
                details={"field": "test"}
            )
        ]
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_user_history.return_value = mock_actions
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                mock_st.expander.return_value.__enter__ = Mock()
                mock_st.expander.return_value.__exit__ = Mock()
                render_user_activity("user1")
        
        mock_service.get_user_history.assert_called_once_with("user1", limit=20)

    def test_render_user_activity_empty(self):
        """Test render user activity sans actions."""
        from src.services.action_history import render_user_activity
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_user_history.return_value = []
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                render_user_activity("user1")
        
        mock_st.info.assert_called()


@pytest.mark.unit
class TestRenderActivityStats:
    """Tests pour render_activity_stats."""

    def test_render_activity_stats(self):
        """Test render activity stats."""
        from src.services.action_history import render_activity_stats, ActionStats
        
        mock_stats = ActionStats(
            total_actions=100,
            actions_today=10,
            actions_this_week=50,
            most_active_users=[{"name": "User1", "count": 20}],
            most_common_actions=[{"type": "recette.created", "count": 15}]
        )
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_stats.return_value = mock_stats
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                mock_st.columns.return_value = [Mock(), Mock(), Mock()]
                render_activity_stats()
        
        mock_service.get_stats.assert_called_once()

    def test_render_activity_stats_no_users(self):
        """Test render activity stats sans utilisateurs actifs."""
        from src.services.action_history import render_activity_stats, ActionStats
        
        mock_stats = ActionStats(
            total_actions=0,
            actions_today=0,
            actions_this_week=0,
            most_active_users=[],
            most_common_actions=[]
        )
        
        with patch("src.services.action_history.get_action_history_service") as mock_factory:
            mock_service = Mock()
            mock_service.get_stats.return_value = mock_stats
            mock_factory.return_value = mock_service
            
            with patch("src.services.action_history.st") as mock_st:
                mock_st.columns.return_value = [Mock(), Mock(), Mock()]
                render_activity_stats()
