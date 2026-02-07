"""
Tests couverture pour src/services/realtime_sync.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncEventType:
    """Tests pour SyncEventType enum."""

    def test_all_event_types_exist(self):
        """Test tous les types d'événements."""
        from src.services.realtime_sync import SyncEventType
        
        assert SyncEventType.ITEM_ADDED == "item_added"
        assert SyncEventType.ITEM_UPDATED == "item_updated"
        assert SyncEventType.ITEM_DELETED == "item_deleted"
        assert SyncEventType.ITEM_CHECKED == "item_checked"
        assert SyncEventType.ITEM_UNCHECKED == "item_unchecked"
        assert SyncEventType.LIST_CLEARED == "list_cleared"
        assert SyncEventType.USER_JOINED == "user_joined"
        assert SyncEventType.USER_LEFT == "user_left"
        assert SyncEventType.USER_TYPING == "user_typing"


# ═══════════════════════════════════════════════════════════
# TESTS PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncEventModel:
    """Tests pour SyncEvent model."""

    def test_sync_event_minimal(self):
        """Test création minimale."""
        from src.services.realtime_sync import SyncEvent, SyncEventType
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="user123",
            user_name="John"
        )
        
        assert event.event_type == SyncEventType.ITEM_ADDED
        assert event.liste_id == 1
        assert event.user_id == "user123"
        assert isinstance(event.timestamp, datetime)
        assert event.data == {}

    def test_sync_event_with_data(self):
        """Test création avec données."""
        from src.services.realtime_sync import SyncEvent, SyncEventType
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_CHECKED,
            liste_id=5,
            user_id="user456",
            user_name="Jane",
            data={"item_id": 123, "checked": True}
        )
        
        assert event.data["item_id"] == 123
        assert event.data["checked"] is True


@pytest.mark.unit
class TestPresenceInfoModel:
    """Tests pour PresenceInfo model."""

    def test_presence_info_minimal(self):
        """Test création minimale."""
        from src.services.realtime_sync import PresenceInfo
        
        presence = PresenceInfo(
            user_id="user123",
            user_name="Alice"
        )
        
        assert presence.user_id == "user123"
        assert presence.user_name == "Alice"
        assert presence.avatar_url is None
        assert presence.is_typing is False
        assert presence.current_item is None

    def test_presence_info_complete(self):
        """Test création complète."""
        from src.services.realtime_sync import PresenceInfo
        
        now = datetime.now()
        
        presence = PresenceInfo(
            user_id="user789",
            user_name="Bob",
            avatar_url="https://example.com/avatar.png",
            joined_at=now,
            last_seen=now,
            is_typing=True,
            current_item="Tomates"
        )
        
        assert presence.avatar_url == "https://example.com/avatar.png"
        assert presence.is_typing is True
        assert presence.current_item == "Tomates"


@pytest.mark.unit
class TestSyncStateDataclass:
    """Tests pour SyncState dataclass."""

    def test_sync_state_defaults(self):
        """Test valeurs par défaut."""
        from src.services.realtime_sync import SyncState
        
        state = SyncState()
        
        assert state.liste_id is None
        assert state.connected is False
        assert state.users_present == {}
        assert state.pending_events == []
        assert state.last_sync is None
        assert state.conflict_count == 0

    def test_sync_state_initialized(self):
        """Test état initialisé."""
        from src.services.realtime_sync import SyncState, PresenceInfo
        
        now = datetime.now()
        
        state = SyncState(
            liste_id=42,
            connected=True,
            last_sync=now,
            conflict_count=3
        )
        
        assert state.liste_id == 42
        assert state.connected is True
        assert state.conflict_count == 3


# ═══════════════════════════════════════════════════════════
# TESTS REALTIME SYNC SERVICE INIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRealtimeSyncServiceInit:
    """Tests pour l'initialisation du service."""

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_init_service(self, mock_init_client):
        """Test initialisation basique."""
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        
        assert service._client is None
        assert service._channel is None
        assert service._callbacks == {}
        mock_init_client.assert_called_once()

    @patch('src.services.realtime_sync.st')
    def test_init_client_with_config(self, mock_st):
        """Test initialisation client avec config - skip si supabase non dispo."""
        mock_st.session_state = {}
        
        # Mock le module supabase au niveau sys.modules avant l'import
        import sys
        mock_supabase = Mock()
        mock_client = Mock()
        mock_supabase.create_client = Mock(return_value=mock_client)
        sys.modules['supabase'] = mock_supabase
        
        try:
            with patch('src.core.config.obtenir_parametres') as mock_params:
                mock_settings = Mock()
                mock_settings.SUPABASE_URL = "https://test.supabase.co"
                mock_settings.SUPABASE_ANON_KEY = "anon_key_123"
                mock_params.return_value = mock_settings
                
                # Force reimport du module
                if 'src.services.realtime_sync' in sys.modules:
                    del sys.modules['src.services.realtime_sync']
                
                from src.services.realtime_sync import RealtimeSyncService
                
                service = RealtimeSyncService()
                
                # Vérifie que client est initialisé
                assert service._client is not None
        finally:
            # Nettoyer
            if 'supabase' in sys.modules:
                del sys.modules['supabase']

    @patch('src.services.realtime_sync.st')
    def test_init_client_missing_config(self, mock_st):
        """Test initialisation sans config."""
        mock_st.session_state = {}
        
        with patch('src.core.config.obtenir_parametres') as mock_params:
            mock_settings = Mock(spec=[])  # Pas d'attributs
            mock_params.return_value = mock_settings
            
            from src.services.realtime_sync import RealtimeSyncService
            
            service = RealtimeSyncService()
            
            # Client est None car pas de config
            assert service._client is None


# ═══════════════════════════════════════════════════════════
# TESTS IS_CONFIGURED PROPERTY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIsConfigured:
    """Tests pour is_configured property."""

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_is_configured_false(self, mock_init):
        """Test non configuré."""
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._client = None
        
        assert service.is_configured is False

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_is_configured_true(self, mock_init):
        """Test configuré."""
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._client = Mock()
        
        assert service.is_configured is True


# ═══════════════════════════════════════════════════════════
# TESTS JOIN LIST
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJoinList:
    """Tests pour join_list()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_join_list_not_configured(self, mock_init, mock_st):
        """Test join sans configuration."""
        mock_st.session_state = {}
        
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._client = None
        
        result = service.join_list(liste_id=1, user_id="u1", user_name="User 1")
        
        assert result is False

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_join_list_success(self, mock_init, mock_st):
        """Test join réussi."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: SyncState()}
        
        mock_channel = Mock()
        mock_client = Mock()
        mock_client.channel.return_value = mock_channel
        
        service = RealtimeSyncService()
        service._client = mock_client
        
        # Stub broadcast to prevent further issues
        service.broadcast_event = Mock()
        
        result = service.join_list(liste_id=42, user_id="user1", user_name="TestUser")
        
        assert result is True
        mock_client.channel.assert_called_once()
        mock_channel.subscribe.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS LEAVE LIST
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLeaveList:
    """Tests pour leave_list()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_leave_list_no_channel(self, mock_init, mock_st):
        """Test leave sans channel actif."""
        mock_st.session_state = {}
        
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._channel = None
        
        # Doit ne pas lever d'exception
        service.leave_list()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_leave_list_success(self, mock_init, mock_st):
        """Test leave réussi."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState(liste_id=42, connected=True)
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        mock_channel = Mock()
        
        service = RealtimeSyncService()
        service._channel = mock_channel
        service._get_current_user_id = Mock(return_value="user123")
        service._get_current_user_name = Mock(return_value="TestUser")
        service.broadcast_event = Mock()
        
        service.leave_list()
        
        mock_channel.unsubscribe.assert_called_once()
        assert service._channel is None
        assert state.connected is False


# ═══════════════════════════════════════════════════════════
# TESTS BROADCAST EVENT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBroadcastEvent:
    """Tests pour broadcast_event()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_event_no_channel(self, mock_init, mock_st):
        """Test broadcast sans channel."""
        mock_st.session_state = {}
        
        from src.services.realtime_sync import RealtimeSyncService, SyncEvent, SyncEventType
        
        service = RealtimeSyncService()
        service._channel = None
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="u1",
            user_name="User"
        )
        
        # Ne doit pas lever d'exception
        service.broadcast_event(event)


# ═══════════════════════════════════════════════════════════
# TESTS BROADCAST HELPERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBroadcastHelpers:
    """Tests pour les helpers de broadcast."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_item_added(self, mock_init, mock_st):
        """Test broadcast_item_added."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service.broadcast_event = Mock()
        service._get_current_user_id = Mock(return_value="user1")
        service._get_current_user_name = Mock(return_value="User")
        
        service.broadcast_item_added(liste_id=1, item_data={"nom": "Tomate"})
        
        service.broadcast_event.assert_called_once()
        call_args = service.broadcast_event.call_args[0][0]
        assert call_args.data["nom"] == "Tomate"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_item_checked(self, mock_init, mock_st):
        """Test broadcast_item_checked."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service.broadcast_event = Mock()
        service._get_current_user_id = Mock(return_value="user1")
        service._get_current_user_name = Mock(return_value="User")
        
        service.broadcast_item_checked(liste_id=1, item_id=42, checked=True)
        
        service.broadcast_event.assert_called_once()
        call_args = service.broadcast_event.call_args[0][0]
        assert call_args.event_type == SyncEventType.ITEM_CHECKED

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_item_deleted(self, mock_init, mock_st):
        """Test broadcast_item_deleted."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service.broadcast_event = Mock()
        service._get_current_user_id = Mock(return_value="user1")
        service._get_current_user_name = Mock(return_value="User")
        
        service.broadcast_item_deleted(liste_id=1, item_id=99)
        
        service.broadcast_event.assert_called_once()
        call_args = service.broadcast_event.call_args[0][0]
        assert call_args.event_type == SyncEventType.ITEM_DELETED

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_typing(self, mock_init, mock_st):
        """Test broadcast_typing."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service.broadcast_event = Mock()
        service._get_current_user_id = Mock(return_value="user1")
        service._get_current_user_name = Mock(return_value="User")
        
        service.broadcast_typing(liste_id=1, is_typing=True, item_name="Pomme")
        
        service.broadcast_event.assert_called_once()
        call_args = service.broadcast_event.call_args[0][0]
        assert call_args.event_type == SyncEventType.USER_TYPING


# ═══════════════════════════════════════════════════════════
# TESTS ON_EVENT CALLBACKS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOnEventCallbacks:
    """Tests pour l'enregistrement de callbacks."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_on_event(self, mock_init, mock_st):
        """Test enregistrement callback."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        callback = Mock()
        
        service.on_event(SyncEventType.ITEM_ADDED, callback)
        
        assert SyncEventType.ITEM_ADDED in service._callbacks
        assert callback in service._callbacks[SyncEventType.ITEM_ADDED]

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_on_item_added(self, mock_init, mock_st):
        """Test raccourci on_item_added."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        callback = Mock()
        
        service.on_item_added(callback)
        
        assert SyncEventType.ITEM_ADDED in service._callbacks

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_on_item_checked(self, mock_init, mock_st):
        """Test raccourci on_item_checked."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        callback = Mock()
        
        service.on_item_checked(callback)
        
        assert SyncEventType.ITEM_CHECKED in service._callbacks


# ═══════════════════════════════════════════════════════════
# TESTS RESOLVE CONFLICT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestResolveConflict:
    """Tests pour resolve_conflict()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_resolve_conflict_remote_newer(self, mock_init, mock_st):
        """Test résolution conflit - remote plus récent."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        local = {"updated_at": "2024-01-01T10:00:00", "nom": "Tomate locale"}
        remote = {"updated_at": "2024-01-01T12:00:00", "nom": "Tomate distante"}
        
        result = service.resolve_conflict(local, remote)
        
        assert result["nom"] == "Tomate distante"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_resolve_conflict_local_newer(self, mock_init, mock_st):
        """Test résolution conflit - local plus récent."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        local = {"updated_at": "2024-01-01T14:00:00", "nom": "Tomate locale"}
        remote = {"updated_at": "2024-01-01T10:00:00", "nom": "Tomate distante"}
        
        result = service.resolve_conflict(local, remote)
        
        assert result["nom"] == "Tomate locale"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_resolve_conflict_increments_counter(self, mock_init, mock_st):
        """Test que le compteur de conflits est incrémenté."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState(conflict_count=5)
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        local = {"updated_at": "2024-01-01T10:00:00"}
        remote = {"updated_at": "2024-01-01T12:00:00"}
        
        service.resolve_conflict(local, remote)
        
        assert state.conflict_count == 6


# ═══════════════════════════════════════════════════════════
# TESTS PRIVATE HELPERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPrivateHelpers:
    """Tests pour les méthodes privées."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_get_current_user_id(self, mock_get_auth, mock_init, mock_st):
        """Test récupération user_id depuis auth service."""
        mock_st.session_state = {}
        
        mock_user = Mock()
        mock_user.id = "session_user_123"
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_auth
        
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        
        result = service._get_current_user_id()
        
        assert result == "session_user_123"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_get_current_user_id_default(self, mock_get_auth, mock_init, mock_st):
        """Test user_id par défaut."""
        mock_st.session_state = {}
        
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = None
        mock_get_auth.return_value = mock_auth
        
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        
        result = service._get_current_user_id()
        
        assert result == "anonymous"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_get_current_user_name(self, mock_get_auth, mock_init, mock_st):
        """Test récupération user_name depuis auth service."""
        mock_st.session_state = {}
        
        mock_user = Mock()
        mock_user.display_name = "Alice"
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_auth
        
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        
        result = service._get_current_user_name()
        
        assert result == "Alice"


# ═══════════════════════════════════════════════════════════
# TESTS MODULE EXPORTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_sync_event_type_exported(self):
        """Test SyncEventType exporté."""
        from src.services.realtime_sync import SyncEventType
        assert SyncEventType is not None

    def test_sync_event_exported(self):
        """Test SyncEvent exporté."""
        from src.services.realtime_sync import SyncEvent
        assert SyncEvent is not None

    def test_presence_info_exported(self):
        """Test PresenceInfo exporté."""
        from src.services.realtime_sync import PresenceInfo
        assert PresenceInfo is not None

    def test_sync_state_exported(self):
        """Test SyncState exporté."""
        from src.services.realtime_sync import SyncState
        assert SyncState is not None

    def test_service_exported(self):
        """Test RealtimeSyncService exporté."""
        from src.services.realtime_sync import RealtimeSyncService
        assert RealtimeSyncService is not None


# ═══════════════════════════════════════════════════════════
# TESTS HANDLERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestHandlers:
    """Tests pour les handlers d'événements."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_handle_broadcast_own_event(self, mock_get_auth, mock_init, mock_st):
        """Test ignorer nos propres événements."""
        mock_st.session_state = {}
        
        mock_user = Mock()
        mock_user.id = "user123"
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_auth
        
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        service = RealtimeSyncService()
        
        payload = {
            "event_type": "item_added",
            "liste_id": 1,
            "user_id": "user123",  # Notre propre user
            "user_name": "Moi",
            "data": {}
        }
        
        # Ne devrait pas déclencher st.rerun
        service._handle_broadcast(payload)
        mock_st.rerun.assert_not_called()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_handle_broadcast_with_callback(self, mock_get_auth, mock_init, mock_st):
        """Test traitement avec callback."""
        mock_st.session_state = {}
        
        mock_user = Mock()
        mock_user.id = "my_user"
        mock_auth = Mock()
        mock_auth.get_current_user.return_value = mock_user
        mock_get_auth.return_value = mock_auth
        
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        service = RealtimeSyncService()
        
        callback = Mock()
        service.on_event(SyncEventType.ITEM_ADDED, callback)
        
        payload = {
            "event_type": "item_added",
            "liste_id": 1,
            "user_id": "other_user",  # Autre utilisateur
            "user_name": "Other",
            "data": {"nom": "Tomate"}
        }
        
        service._handle_broadcast(payload)
        
        callback.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_sync(self, mock_init, mock_st):
        """Test synchronisation des présences."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        payload = {
            "presences": {
                "user1": [{"user_name": "Alice"}],
                "user2": {"user_name": "Bob"}
            }
        }
        
        service._handle_presence_sync(payload)
        
        assert len(state.users_present) == 2
        assert "user1" in state.users_present
        assert "user2" in state.users_present

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_join(self, mock_init, mock_st):
        """Test arrivée d'un utilisateur."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        payload = {
            "key": "new_user",
            "newPresences": [{"user_id": "new_user", "user_name": "NewUser"}]
        }
        
        service._handle_presence_join(payload)
        
        assert "new_user" in state.users_present
        assert state.users_present["new_user"].user_name == "NewUser"

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_leave(self, mock_init, mock_st):
        """Test départ d'un utilisateur."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, PresenceInfo
        
        state = SyncState()
        state.users_present["leaving_user"] = PresenceInfo(
            user_id="leaving_user",
            user_name="Leaving"
        )
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        payload = {"key": "leaving_user"}
        
        service._handle_presence_leave(payload)
        
        assert "leaving_user" not in state.users_present


# ═══════════════════════════════════════════════════════════
# TESTS CONNECTED USERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConnectedUsers:
    """Tests pour get_connected_users()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_get_connected_users(self, mock_init, mock_st):
        """Test récupération utilisateurs connectés."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, PresenceInfo
        
        state = SyncState()
        state.users_present["user1"] = PresenceInfo(user_id="user1", user_name="User 1")
        state.users_present["user2"] = PresenceInfo(user_id="user2", user_name="User 2")
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        result = service.get_connected_users()
        
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS SYNC PENDING EVENTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncPendingEvents:
    """Tests pour sync_pending_events()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_sync_pending_events_no_channel(self, mock_init, mock_st):
        """Test sync sans channel."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service._channel = None
        
        # Ne doit pas lever d'exception
        service.sync_pending_events()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_sync_pending_events_no_events(self, mock_init, mock_st):
        """Test sync sans événements."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        service._channel = Mock()
        
        # Ne doit pas lever d'exception
        service.sync_pending_events()


# ═══════════════════════════════════════════════════════════
# TESTS BROADCAST ITEM UNCHECKED
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBroadcastItemUnchecked:
    """Tests pour broadcast avec unchecked."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_item_unchecked(self, mock_init, mock_st):
        """Test broadcast_item_checked avec checked=False."""
        from src.services.realtime_sync import RealtimeSyncService, SyncEventType
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        service.broadcast_event = Mock()
        service._get_current_user_id = Mock(return_value="user1")
        service._get_current_user_name = Mock(return_value="User")
        
        service.broadcast_item_checked(liste_id=1, item_id=42, checked=False)
        
        service.broadcast_event.assert_called_once()
        call_args = service.broadcast_event.call_args[0][0]
        assert call_args.event_type == SyncEventType.ITEM_UNCHECKED


# ═══════════════════════════════════════════════════════════
# TESTS STATE PROPERTY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestStateProperty:
    """Tests pour la propriété state."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_state_creates_default(self, mock_init, mock_st):
        """Test création état par défaut."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        # Accéder à state devrait créer un SyncState par défaut
        state = service.state
        
        assert state is not None
        assert mock_st.session_state[RealtimeSyncService.STATE_KEY] is not None
