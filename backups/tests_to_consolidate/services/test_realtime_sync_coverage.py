"""
Tests couverture pour src/services/realtime_sync.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSyncEventType:
    """Tests pour SyncEventType enum."""

    def test_all_event_types_exist(self):
        """Test tous les types d'Ã©vÃ©nements."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PYDANTIC MODELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSyncEventModel:
    """Tests pour SyncEvent model."""

    def test_sync_event_minimal(self):
        """Test crÃ©ation minimale."""
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
        """Test crÃ©ation avec donnÃ©es."""
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
        """Test crÃ©ation minimale."""
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
        """Test crÃ©ation complÃ¨te."""
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
        """Test valeurs par dÃ©faut."""
        from src.services.realtime_sync import SyncState
        
        state = SyncState()
        
        assert state.liste_id is None
        assert state.connected is False
        assert state.users_present == {}
        assert state.pending_events == []
        assert state.last_sync is None
        assert state.conflict_count == 0

    def test_sync_state_initialized(self):
        """Test Ã©tat initialisÃ©."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS REALTIME SYNC SERVICE INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
                
                # VÃ©rifie que client est initialisÃ©
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IS_CONFIGURED PROPERTY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestIsConfigured:
    """Tests pour is_configured property."""

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_is_configured_false(self, mock_init):
        """Test non configurÃ©."""
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._client = None
        
        assert service.is_configured is False

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_is_configured_true(self, mock_init):
        """Test configurÃ©."""
        from src.services.realtime_sync import RealtimeSyncService
        
        service = RealtimeSyncService()
        service._client = Mock()
        
        assert service.is_configured is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS JOIN LIST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
        """Test join rÃ©ussi."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LEAVE LIST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
        """Test leave rÃ©ussi."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BROADCAST EVENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BROADCAST HELPERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ON_EVENT CALLBACKS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RESOLVE CONFLICT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestResolveConflict:
    """Tests pour resolve_conflict()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_resolve_conflict_remote_newer(self, mock_init, mock_st):
        """Test rÃ©solution conflit - remote plus rÃ©cent."""
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
        """Test rÃ©solution conflit - local plus rÃ©cent."""
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
        """Test que le compteur de conflits est incrÃ©mentÃ©."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState(conflict_count=5)
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        local = {"updated_at": "2024-01-01T10:00:00"}
        remote = {"updated_at": "2024-01-01T12:00:00"}
        
        service.resolve_conflict(local, remote)
        
        assert state.conflict_count == 6


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PRIVATE HELPERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestPrivateHelpers:
    """Tests pour les mÃ©thodes privÃ©es."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_get_current_user_id(self, mock_get_auth, mock_init, mock_st):
        """Test rÃ©cupÃ©ration user_id depuis auth service."""
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
        """Test user_id par dÃ©faut."""
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
        """Test rÃ©cupÃ©ration user_name depuis auth service."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_sync_event_type_exported(self):
        """Test SyncEventType exportÃ©."""
        from src.services.realtime_sync import SyncEventType
        assert SyncEventType is not None

    def test_sync_event_exported(self):
        """Test SyncEvent exportÃ©."""
        from src.services.realtime_sync import SyncEvent
        assert SyncEvent is not None

    def test_presence_info_exported(self):
        """Test PresenceInfo exportÃ©."""
        from src.services.realtime_sync import PresenceInfo
        assert PresenceInfo is not None

    def test_sync_state_exported(self):
        """Test SyncState exportÃ©."""
        from src.services.realtime_sync import SyncState
        assert SyncState is not None

    def test_service_exported(self):
        """Test RealtimeSyncService exportÃ©."""
        from src.services.realtime_sync import RealtimeSyncService
        assert RealtimeSyncService is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HANDLERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestHandlers:
    """Tests pour les handlers d'Ã©vÃ©nements."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    @patch('src.services.auth.get_auth_service')
    def test_handle_broadcast_own_event(self, mock_get_auth, mock_init, mock_st):
        """Test ignorer nos propres Ã©vÃ©nements."""
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
        
        # Ne devrait pas dÃ©clencher st.rerun
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
        """Test synchronisation des prÃ©sences."""
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
        """Test arrivÃ©e d'un utilisateur."""
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
        """Test dÃ©part d'un utilisateur."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONNECTED USERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestConnectedUsers:
    """Tests pour get_connected_users()."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_get_connected_users(self, mock_init, mock_st):
        """Test rÃ©cupÃ©ration utilisateurs connectÃ©s."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, PresenceInfo
        
        state = SyncState()
        state.users_present["user1"] = PresenceInfo(user_id="user1", user_name="User 1")
        state.users_present["user2"] = PresenceInfo(user_id="user2", user_name="User 2")
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        result = service.get_connected_users()
        
        assert len(result) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SYNC PENDING EVENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
        """Test sync sans Ã©vÃ©nements."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        service._channel = Mock()
        
        # Ne doit pas lever d'exception
        service.sync_pending_events()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BROADCAST ITEM UNCHECKED
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STATE PROPERTY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestStateProperty:
    """Tests pour la propriÃ©tÃ© state."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_state_creates_default(self, mock_init, mock_st):
        """Test crÃ©ation Ã©tat par dÃ©faut."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        # AccÃ©der Ã  state devrait crÃ©er un SyncState par dÃ©faut
        state = service.state
        
        assert state is not None
        assert mock_st.session_state[RealtimeSyncService.STATE_KEY] is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INIT CLIENT EXCEPTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestInitClientExceptions:
    """Tests pour les exceptions lors de l'initialisation du client."""

    @patch('src.services.realtime_sync.st')
    def test_init_client_import_error(self, mock_st):
        """Test initialisation avec ImportError."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        # Simuler l'erreur d'import en patchant create_client
        with patch.dict('sys.modules', {'supabase': None}):
            # CrÃ©er le service - _init_client sera appelÃ©
            service = RealtimeSyncService()
            
            # Doit Ã©chouer gracieusement
            assert service._client is None

    @patch('src.services.realtime_sync.st')
    @patch('src.core.config.obtenir_parametres')
    def test_init_client_generic_exception(self, mock_params, mock_st):
        """Test initialisation avec exception gÃ©nÃ©rique."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        mock_params.side_effect = Exception("Unknown error")
        
        service = RealtimeSyncService()
        
        assert service._client is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LEAVE LIST EXCEPTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestLeaveListException:
    """Tests pour les exceptions lors de leave_list."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_leave_list_with_exception(self, mock_init, mock_st):
        """Test leave_list gÃ¨re les exceptions."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState(liste_id=1)
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        mock_channel = MagicMock()
        mock_channel.unsubscribe.side_effect = Exception("Unsubscribe failed")
        service._channel = mock_channel
        
        # Mock _get_current_user_id et _get_current_user_name
        service._get_current_user_id = Mock(return_value="u")
        service._get_current_user_name = Mock(return_value="U")
        
        # Ne doit pas lever d'exception
        service.leave_list()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SYNC PENDING EVENTS SUCCESS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSyncPendingEventsSuccess:
    """Tests pour sync_pending_events avec succÃ¨s."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_sync_pending_events_success(self, mock_init, mock_st):
        """Test sync avec Ã©vÃ©nements."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, SyncEvent, SyncEventType
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="u",
            user_name="U"
        )
        
        state = SyncState()
        state.pending_events = [event]
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        mock_channel = MagicMock()
        service._channel = mock_channel
        
        service.sync_pending_events()
        
        mock_channel.send_broadcast.assert_called_once()
        assert len(state.pending_events) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RENDER PRESENCE INDICATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRenderPresenceIndicatorUI:
    """Tests pour render_presence_indicator."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_presence_no_users(self, mock_service, mock_st):
        """Test render_presence_indicator sans utilisateurs."""
        from src.services.realtime_sync import render_presence_indicator
        
        mock_service.return_value.get_connected_users.return_value = []
        
        render_presence_indicator()
        
        # st.markdown ne doit pas Ãªtre appelÃ© avec "ConnectÃ©s"
        mock_st.markdown.assert_not_called()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_presence_with_users(self, mock_service, mock_st):
        """Test render_presence_indicator avec utilisateurs."""
        from src.services.realtime_sync import render_presence_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id="u1", user_name="Alice"),
            PresenceInfo(user_id="u2", user_name="Bob")
        ]
        mock_service.return_value.get_connected_users.return_value = users
        
        mock_cols = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_cols
        
        render_presence_indicator()
        
        mock_st.markdown.assert_called()
        mock_st.columns.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_presence_more_than_5_users(self, mock_service, mock_st):
        """Test render_presence_indicator avec plus de 5 utilisateurs."""
        from src.services.realtime_sync import render_presence_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id=f"u{i}", user_name=f"User {i}")
            for i in range(7)
        ]
        mock_service.return_value.get_connected_users.return_value = users
        
        mock_cols = [MagicMock() for _ in range(5)]
        mock_st.columns.return_value = mock_cols
        
        render_presence_indicator()
        
        # Doit afficher le caption "... et X autre(s)"
        mock_st.caption.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RENDER TYPING INDICATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRenderTypingIndicatorUI:
    """Tests pour render_typing_indicator."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_typing_no_typing(self, mock_service, mock_st):
        """Test render_typing_indicator sans utilisateurs qui tapent."""
        from src.services.realtime_sync import render_typing_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id="u1", user_name="Alice", is_typing=False)
        ]
        mock_service.return_value.get_connected_users.return_value = users
        mock_service.return_value._get_current_user_id.return_value = "me"
        
        render_typing_indicator()
        
        mock_st.caption.assert_not_called()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_typing_with_typing_user(self, mock_service, mock_st):
        """Test render_typing_indicator avec utilisateur qui tape."""
        from src.services.realtime_sync import render_typing_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id="u1", user_name="Alice", is_typing=True)
        ]
        mock_service.return_value.get_connected_users.return_value = users
        mock_service.return_value._get_current_user_id.return_value = "me"
        
        render_typing_indicator()
        
        mock_st.caption.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_typing_ignores_self(self, mock_service, mock_st):
        """Test render_typing_indicator ignore l'utilisateur courant."""
        from src.services.realtime_sync import render_typing_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id="me", user_name="Me", is_typing=True)
        ]
        mock_service.return_value.get_connected_users.return_value = users
        mock_service.return_value._get_current_user_id.return_value = "me"
        
        render_typing_indicator()
        
        mock_st.caption.assert_not_called()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_typing_multiple_users(self, mock_service, mock_st):
        """Test render_typing_indicator avec plusieurs utilisateurs."""
        from src.services.realtime_sync import render_typing_indicator, PresenceInfo
        
        users = [
            PresenceInfo(user_id="u1", user_name="Alice", is_typing=True),
            PresenceInfo(user_id="u2", user_name="Bob", is_typing=True)
        ]
        mock_service.return_value.get_connected_users.return_value = users
        mock_service.return_value._get_current_user_id.return_value = "me"
        
        render_typing_indicator()
        
        mock_st.caption.assert_called_once()
        # VÃ©rifier que le message contient "Ã©crivent" pour le pluriel
        call_arg = mock_st.caption.call_args[0][0]
        assert "Ã©crivent" in call_arg


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RENDER SYNC STATUS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRenderSyncStatusUI:
    """Tests pour render_sync_status."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_sync_status_connected(self, mock_service, mock_st):
        """Test render_sync_status quand connectÃ©."""
        from src.services.realtime_sync import render_sync_status
        
        mock_state = Mock()
        mock_state.connected = True
        mock_state.pending_events = []
        
        mock_service.return_value.state = mock_state
        mock_service.return_value.get_connected_users.return_value = [Mock(), Mock()]
        
        render_sync_status()
        
        mock_st.success.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_sync_status_pending(self, mock_service, mock_st):
        """Test render_sync_status avec Ã©vÃ©nements en attente."""
        from src.services.realtime_sync import render_sync_status
        
        mock_state = Mock()
        mock_state.connected = False
        mock_state.pending_events = [Mock(), Mock()]
        
        mock_service.return_value.state = mock_state
        
        render_sync_status()
        
        mock_st.warning.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.get_realtime_sync_service')
    def test_render_sync_status_offline(self, mock_service, mock_st):
        """Test render_sync_status en mode hors ligne."""
        from src.services.realtime_sync import render_sync_status
        
        mock_state = Mock()
        mock_state.connected = False
        mock_state.pending_events = []
        
        mock_service.return_value.state = mock_state
        
        render_sync_status()
        
        mock_st.info.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestGetRealtimeSyncService:
    """Tests pour get_realtime_sync_service factory."""

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_get_service_creates_instance(self, mock_init):
        """Test crÃ©ation d'instance."""
        import src.services.realtime_sync as module
        from src.services.realtime_sync import get_realtime_sync_service, RealtimeSyncService
        
        # Reset singleton
        module._sync_service = None
        
        service = get_realtime_sync_service()
        
        assert isinstance(service, RealtimeSyncService)

    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_get_service_singleton(self, mock_init):
        """Test singleton pattern."""
        import src.services.realtime_sync as module
        from src.services.realtime_sync import get_realtime_sync_service
        
        # Reset singleton
        module._sync_service = None
        
        service1 = get_realtime_sync_service()
        service2 = get_realtime_sync_service()
        
        assert service1 is service2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HANDLE BROADCAST EXCEPTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestHandleBroadcastExceptions:
    """Tests pour _handle_broadcast avec exceptions."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_broadcast_invalid_payload(self, mock_init, mock_st):
        """Test _handle_broadcast avec payload invalide."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        invalid_payload = {"invalid": "data"}
        
        # Ne doit pas lever d'exception
        service._handle_broadcast(invalid_payload)

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_broadcast_callback_exception(self, mock_init, mock_st):
        """Test _handle_broadcast gÃ¨re les exceptions des callbacks."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, SyncEventType
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        mock_st.rerun = Mock()
        
        service = RealtimeSyncService()
        
        # Mock _get_current_user_id
        service._get_current_user_id = Mock(return_value="me")
        
        # Callback qui Ã©choue
        bad_callback = Mock(side_effect=Exception("Callback error"))
        service._callbacks[SyncEventType.ITEM_ADDED] = [bad_callback]
        
        payload = {
            "event_type": "item_added",
            "liste_id": 1,
            "user_id": "other",
            "user_name": "Other",
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        # Ne doit pas lever d'exception
        service._handle_broadcast(payload)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PRESENCE HANDLERS EXCEPTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestPresenceHandlersExceptions:
    """Tests pour les handlers de prÃ©sence avec exceptions."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_sync_exception(self, mock_init, mock_st):
        """Test _handle_presence_sync gÃ¨re les exceptions."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        # Payload None devrait Ãªtre gÃ©rÃ© gracieusement
        service._handle_presence_sync(None)

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_join_exception(self, mock_init, mock_st):
        """Test _handle_presence_join gÃ¨re les exceptions."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        # Payload None devrait Ãªtre gÃ©rÃ© gracieusement
        service._handle_presence_join(None)

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_handle_presence_leave_exception(self, mock_init, mock_st):
        """Test _handle_presence_leave gÃ¨re les exceptions."""
        from src.services.realtime_sync import RealtimeSyncService
        
        mock_st.session_state = {}
        
        service = RealtimeSyncService()
        
        # Payload None devrait Ãªtre gÃ©rÃ© gracieusement
        service._handle_presence_leave(None)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BROADCAST EVENT WITH CHANNEL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBroadcastEventWithChannel:
    """Tests pour broadcast_event avec channel."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_event_with_channel_success(self, mock_init, mock_st):
        """Test broadcast_event avec channel envoie le message."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, SyncEvent, SyncEventType
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        mock_channel = MagicMock()
        service._channel = mock_channel
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="u",
            user_name="U"
        )
        
        service.broadcast_event(event)
        
        mock_channel.send_broadcast.assert_called_once()

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_broadcast_event_with_channel_exception(self, mock_init, mock_st):
        """Test broadcast_event gÃ¨re exception et stocke localement."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState, SyncEvent, SyncEventType
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        mock_channel = MagicMock()
        mock_channel.send_broadcast.side_effect = Exception("Broadcast failed")
        service._channel = mock_channel
        
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="u",
            user_name="U"
        )
        
        service.broadcast_event(event)
        
        # L'Ã©vÃ©nement doit Ãªtre stockÃ© localement
        assert len(state.pending_events) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS JOIN LIST EXCEPTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestJoinListException:
    """Tests pour join_list avec exception."""

    @patch('src.services.realtime_sync.st')
    @patch('src.services.realtime_sync.RealtimeSyncService._init_client')
    def test_join_list_exception(self, mock_init, mock_st):
        """Test join_list gÃ¨re les exceptions."""
        from src.services.realtime_sync import RealtimeSyncService, SyncState
        
        state = SyncState()
        mock_st.session_state = {RealtimeSyncService.STATE_KEY: state}
        
        service = RealtimeSyncService()
        
        mock_client = MagicMock()
        mock_client.channel.side_effect = Exception("Connection failed")
        service._client = mock_client
        
        result = service.join_list(1, "user1", "User")
        
        assert result is False
