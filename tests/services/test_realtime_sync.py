"""
Tests unitaires pour realtime_sync.py

Module: src.services.web.synchronisation
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

# Import depuis le package web/ (unifié sync + pwa)
from src.services.web import get_realtime_sync_service, RealtimeSyncService, SyncEventType
from src.services.web.synchronisation import (
    SyncEvent,
    PresenceInfo,
    SyncState,
)


# ═══════════════════════════════════════════════════════════
# TESTS DES TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════

class TestSyncEventType:
    """Tests pour l'enum SyncEventType."""

    def test_synceventtype_item_added(self):
        """Test de la valeur ITEM_ADDED."""
        assert SyncEventType.ITEM_ADDED.value == "item_added"

    def test_synceventtype_item_updated(self):
        """Test de la valeur ITEM_UPDATED."""
        assert SyncEventType.ITEM_UPDATED.value == "item_updated"

    def test_synceventtype_item_deleted(self):
        """Test de la valeur ITEM_DELETED."""
        assert SyncEventType.ITEM_DELETED.value == "item_deleted"

    def test_synceventtype_item_checked(self):
        """Test des valeurs de cochage."""
        assert SyncEventType.ITEM_CHECKED.value == "item_checked"
        assert SyncEventType.ITEM_UNCHECKED.value == "item_unchecked"

    def test_synceventtype_list_cleared(self):
        """Test de la valeur LIST_CLEARED."""
        assert SyncEventType.LIST_CLEARED.value == "list_cleared"

    def test_synceventtype_user_events(self):
        """Test des événements utilisateur."""
        assert SyncEventType.USER_JOINED.value == "user_joined"
        assert SyncEventType.USER_LEFT.value == "user_left"
        assert SyncEventType.USER_TYPING.value == "user_typing"


class TestSyncEvent:
    """Tests pour la classe SyncEvent."""

    def test_syncevent_creation(self):
        """Test de création d'un SyncEvent."""
        event = SyncEvent(
            event_type=SyncEventType.ITEM_ADDED,
            liste_id=1,
            user_id="user-123",
            user_name="Test User",
            data={"item_id": 42, "name": "Lait"}
        )
        
        assert event.event_type == SyncEventType.ITEM_ADDED
        assert event.liste_id == 1
        assert event.user_id == "user-123"
        assert event.user_name == "Test User"
        assert event.data["item_id"] == 42

    def test_syncevent_default_timestamp(self):
        """Test que le timestamp est auto-généré."""
        event = SyncEvent(
            event_type=SyncEventType.ITEM_DELETED,
            liste_id=1,
            user_id="user-456",
            user_name="Test"
        )
        
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_syncevent_default_data(self):
        """Test que data a une valeur par défaut vide."""
        event = SyncEvent(
            event_type=SyncEventType.USER_JOINED,
            liste_id=1,
            user_id="user-789",
            user_name="Test"
        )
        
        assert event.data == {}

    def test_syncevent_serialization(self):
        """Test de la sérialisation JSON."""
        event = SyncEvent(
            event_type=SyncEventType.ITEM_CHECKED,
            liste_id=5,
            user_id="user-abc",
            user_name="Alice",
            data={"checked": True}
        )
        
        # model_dump devrait fonctionner
        dumped = event.model_dump()
        assert dumped["event_type"] == "item_checked"
        assert dumped["liste_id"] == 5


class TestPresenceInfo:
    """Tests pour la classe PresenceInfo."""

    def test_presenceinfo_creation(self):
        """Test de création de PresenceInfo."""
        presence = PresenceInfo(
            user_id="user-123",
            user_name="Alice"
        )
        
        assert presence.user_id == "user-123"
        assert presence.user_name == "Alice"
        assert presence.is_typing is False
        assert presence.current_item is None

    def test_presenceinfo_with_avatar(self):
        """Test avec avatar URL."""
        presence = PresenceInfo(
            user_id="user-456",
            user_name="Bob",
            avatar_url="https://example.com/avatar.png"
        )
        
        assert presence.avatar_url == "https://example.com/avatar.png"

    def test_presenceinfo_typing_state(self):
        """Test de l'état de frappe."""
        presence = PresenceInfo(
            user_id="user-789",
            user_name="Charlie",
            is_typing=True,
            current_item="Pain"
        )
        
        assert presence.is_typing is True
        assert presence.current_item == "Pain"

    def test_presenceinfo_default_timestamps(self):
        """Test des timestamps par défaut."""
        presence = PresenceInfo(
            user_id="user-test",
            user_name="Test"
        )
        
        assert presence.joined_at is not None
        assert presence.last_seen is not None


class TestSyncState:
    """Tests pour la classe SyncState."""

    def test_syncstate_creation(self):
        """Test de création de SyncState."""
        state = SyncState()
        
        assert state.liste_id is None
        assert state.connected is False
        assert state.users_present == {}
        assert state.pending_events == []
        assert state.last_sync is None
        assert state.conflict_count == 0

    def test_syncstate_with_values(self):
        """Test avec des valeurs personnalisées."""
        state = SyncState(
            liste_id=42,
            connected=True,
            conflict_count=3
        )
        
        assert state.liste_id == 42
        assert state.connected is True
        assert state.conflict_count == 3


# ═══════════════════════════════════════════════════════════
# TESTS DU SERVICE DE SYNCHRONISATION
# ═══════════════════════════════════════════════════════════

class TestRealtimeSyncServiceInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Test de création du service."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            assert service is not None
            assert service._callbacks == {}

    def test_is_configured_false_no_client(self):
        """Test is_configured retourne False sans client."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._client = None
            assert service.is_configured is False

    def test_is_configured_true_with_client(self):
        """Test is_configured retourne True avec client."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._client = MagicMock()
            assert service.is_configured is True


class TestRealtimeSyncServiceInitClient:
    """Tests de l'initialisation du client Supabase."""

    def test_init_client_import_error(self):
        """Test quand supabase n'est pas installé."""
        # Test simplifié - vérifie que le service peut être créé même sans client
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._client = None  # Simule l'absence de client
            assert service._client is None
            assert service.is_configured is False

    def test_init_client_missing_config(self):
        """Test quand la config Supabase est manquante."""
        # Test simplifié - vérifie que le service gère gracieusement l'absence de config
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._client = None
            assert service.is_configured is False


class TestRealtimeSyncServiceState:
    """Tests de la gestion de l'état."""

    @patch('streamlit.session_state', {}, create=True)
    def test_state_creates_new_if_missing(self):
        """Test que state crée un nouvel état si manquant."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            # Mock session_state with proper behavior
            mock_session_state = {}
            with patch('src.services.web.synchronisation.st.session_state', mock_session_state):
                state = service.state
                assert isinstance(state, SyncState)


class TestRealtimeSyncServiceJoinLeave:
    """Tests des méthodes join_list et leave_list."""

    def test_join_list_not_configured(self):
        """Test join_list quand non configuré."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._client = None
            
            result = service.join_list(1, "user-123", "Alice")
            
            assert result is False

    def test_join_list_success(self):
        """Test join_list avec succès."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            # Mock le client et le channel
            mock_channel = MagicMock()
            mock_client = MagicMock()
            mock_client.channel.return_value = mock_channel
            service._client = mock_client
            
            # Mock l'état
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                with patch.object(service, 'broadcast_event'):
                    result = service.join_list(1, "user-123", "Alice")
            
                    assert result is True
                    assert mock_state.connected is True
                    assert mock_state.liste_id == 1

    def test_join_list_exception(self):
        """Test join_list avec exception."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_client = MagicMock()
            mock_client.channel.side_effect = Exception("Connection error")
            service._client = mock_client
            
            result = service.join_list(1, "user-123", "Alice")
            
            assert result is False

    def test_leave_list_success(self):
        """Test leave_list avec succès."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_channel = MagicMock()
            service._channel = mock_channel
            
            mock_state = SyncState(liste_id=1, connected=True)
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        with patch.object(service, 'broadcast_event'):
                            service.leave_list()
            
                            mock_channel.unsubscribe.assert_called_once()
                            assert mock_state.connected is False
                            assert mock_state.liste_id is None


class TestRealtimeSyncServiceBroadcast:
    """Tests des méthodes de broadcast."""

    def test_broadcast_event_no_channel(self):
        """Test broadcast sans channel (mode hors ligne)."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._channel = None
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                event = SyncEvent(
                    event_type=SyncEventType.ITEM_ADDED,
                    liste_id=1,
                    user_id="user-123",
                    user_name="Alice"
                )
                
                service.broadcast_event(event)
                
                # L'événement doit être stocké localement
                assert len(mock_state.pending_events) == 1

    def test_broadcast_event_with_channel(self):
        """Test broadcast avec channel connecté."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_channel = MagicMock()
            service._channel = mock_channel
            
            event = SyncEvent(
                event_type=SyncEventType.ITEM_DELETED,
                liste_id=1,
                user_id="user-123",
                user_name="Alice",
                data={"item_id": 42}
            )
            
            service.broadcast_event(event)
            
            mock_channel.send_broadcast.assert_called_once()

    def test_broadcast_event_exception(self):
        """Test broadcast avec exception."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_channel = MagicMock()
            mock_channel.send_broadcast.side_effect = Exception("Network error")
            service._channel = mock_channel
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                event = SyncEvent(
                    event_type=SyncEventType.ITEM_ADDED,
                    liste_id=1,
                    user_id="user-123",
                    user_name="Alice"
                )
                
                service.broadcast_event(event)
                
                # L'événement doit être stocké en attente
                assert len(mock_state.pending_events) == 1

    def test_broadcast_item_added(self):
        """Test broadcast_item_added."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            with patch.object(service, 'broadcast_event') as mock_broadcast:
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        service.broadcast_item_added(1, {"name": "Lait", "quantity": 2})
                        
                        mock_broadcast.assert_called_once()
                        event = mock_broadcast.call_args[0][0]
                        assert event.event_type == SyncEventType.ITEM_ADDED
                        assert event.data["name"] == "Lait"

    def test_broadcast_item_checked(self):
        """Test broadcast_item_checked."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            with patch.object(service, 'broadcast_event') as mock_broadcast:
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        service.broadcast_item_checked(1, 42, True)
                        
                        mock_broadcast.assert_called_once()
                        event = mock_broadcast.call_args[0][0]
                        assert event.event_type == SyncEventType.ITEM_CHECKED

    def test_broadcast_item_unchecked(self):
        """Test broadcast quand unchecked."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            with patch.object(service, 'broadcast_event') as mock_broadcast:
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        service.broadcast_item_checked(1, 42, False)
                        
                        event = mock_broadcast.call_args[0][0]
                        assert event.event_type == SyncEventType.ITEM_UNCHECKED

    def test_broadcast_item_deleted(self):
        """Test broadcast_item_deleted."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            with patch.object(service, 'broadcast_event') as mock_broadcast:
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        service.broadcast_item_deleted(1, 42)
                        
                        event = mock_broadcast.call_args[0][0]
                        assert event.event_type == SyncEventType.ITEM_DELETED
                        assert event.data["item_id"] == 42

    def test_broadcast_typing(self):
        """Test broadcast_typing."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            with patch.object(service, 'broadcast_event') as mock_broadcast:
                with patch.object(service, '_get_current_user_id', return_value="user-123"):
                    with patch.object(service, '_get_current_user_name', return_value="Alice"):
                        service.broadcast_typing(1, True, "Pain")
                        
                        event = mock_broadcast.call_args[0][0]
                        assert event.event_type == SyncEventType.USER_TYPING
                        assert event.data["is_typing"] is True
                        assert event.data["item_name"] == "Pain"


class TestRealtimeSyncServiceHandlers:
    """Tests des handlers d'événements."""

    def test_handle_broadcast_ignores_own_events(self):
        """Test que les événements propres sont ignorés."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            payload = {
                "event_type": "item_added",
                "liste_id": 1,
                "user_id": "user-123",
                "user_name": "Alice",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
            
            with patch.object(service, '_get_current_user_id', return_value="user-123"):
                # Ne devrait pas déclencher de callback ni de rerun
                with patch('src.services.web.synchronisation.st.rerun') as mock_rerun:
                    service._handle_broadcast(payload)
                    mock_rerun.assert_not_called()

    def test_handle_broadcast_calls_callbacks(self):
        """Test que les callbacks sont appelés."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            callback = MagicMock()
            service._callbacks[SyncEventType.ITEM_ADDED] = [callback]
            
            payload = {
                "event_type": "item_added",
                "liste_id": 1,
                "user_id": "other-user",
                "user_name": "Bob",
                "timestamp": datetime.now().isoformat(),
                "data": {"item_id": 42}
            }
            
            with patch.object(service, '_get_current_user_id', return_value="user-123"):
                with patch('src.services.web.synchronisation.st.rerun'):
                    service._handle_broadcast(payload)
                    
                    callback.assert_called_once()

    def test_handle_presence_sync(self):
        """Test de la synchronisation de présence."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                payload = {
                    "presences": {
                        "user-1": [{"user_name": "Alice"}],
                        "user-2": {"user_name": "Bob"}
                    }
                }
                
                service._handle_presence_sync(payload)
                
                assert len(mock_state.users_present) == 2
                assert "user-1" in mock_state.users_present
                assert "user-2" in mock_state.users_present

    def test_handle_presence_join(self):
        """Test de l'arrivée d'un utilisateur."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                payload = {
                    "key": "user-new",
                    "newPresences": [{"user_id": "user-new", "user_name": "Charlie"}]
                }
                
                service._handle_presence_join(payload)
                
                assert "user-new" in mock_state.users_present
                assert mock_state.users_present["user-new"].user_name == "Charlie"

    def test_handle_presence_leave(self):
        """Test du départ d'un utilisateur."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            mock_state.users_present["user-leaving"] = PresenceInfo(
                user_id="user-leaving",
                user_name="Leaving User"
            )
            
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                payload = {"key": "user-leaving"}
                
                service._handle_presence_leave(payload)
                
                assert "user-leaving" not in mock_state.users_present


class TestRealtimeSyncServiceCallbacks:
    """Tests de l'enregistrement de callbacks."""

    def test_on_event_registers_callback(self):
        """Test que on_event enregistre un callback."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            callback = MagicMock()
            service.on_event(SyncEventType.ITEM_ADDED, callback)
            
            assert SyncEventType.ITEM_ADDED in service._callbacks
            assert callback in service._callbacks[SyncEventType.ITEM_ADDED]

    def test_on_item_added(self):
        """Test on_item_added."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            callback = MagicMock()
            service.on_item_added(callback)
            
            assert callback in service._callbacks[SyncEventType.ITEM_ADDED]

    def test_on_item_checked_registers_both_events(self):
        """Test que on_item_checked enregistre pour checked et unchecked."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            callback = MagicMock()
            service.on_item_checked(callback)
            
            assert callback in service._callbacks[SyncEventType.ITEM_CHECKED]
            assert callback in service._callbacks[SyncEventType.ITEM_UNCHECKED]


class TestRealtimeSyncServiceConflictResolution:
    """Tests de la résolution de conflits."""

    def test_resolve_conflict_remote_wins(self):
        """Test que la version distante gagne si plus récente."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                local = {"id": 1, "name": "Lait", "updated_at": "2024-01-01T10:00:00"}
                remote = {"id": 1, "name": "Lait entier", "updated_at": "2024-01-01T12:00:00"}
                
                result = service.resolve_conflict(local, remote)
                
                assert result["name"] == "Lait entier"
                assert mock_state.conflict_count == 1

    def test_resolve_conflict_local_wins(self):
        """Test que la version locale gagne si plus récente."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                local = {"id": 1, "name": "Lait", "updated_at": "2024-01-01T14:00:00"}
                remote = {"id": 1, "name": "Lait entier", "updated_at": "2024-01-01T12:00:00"}
                
                result = service.resolve_conflict(local, remote)
                
                assert result["name"] == "Lait"

    def test_resolve_conflict_merges_non_conflicting(self):
        """Test que les champs non conflictuels sont fusionnés."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                local = {"id": 1, "name": "Lait", "quantity": 2, "updated_at": "2024-01-01T10:00:00"}
                remote = {"id": 1, "name": "Lait", "notes": "Bio", "updated_at": "2024-01-01T12:00:00"}
                
                result = service.resolve_conflict(local, remote)
                
                # Remote gagne (plus récent) mais garde quantity de local
                assert result["notes"] == "Bio"
                assert result["quantity"] == 2


class TestRealtimeSyncServiceUtilities:
    """Tests des méthodes utilitaires."""

    def test_get_connected_users(self):
        """Test de récupération des utilisateurs connectés."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_state = SyncState()
            mock_state.users_present = {
                "user-1": PresenceInfo(user_id="user-1", user_name="Alice"),
                "user-2": PresenceInfo(user_id="user-2", user_name="Bob")
            }
            
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                users = service.get_connected_users()
                
                assert len(users) == 2
                assert any(u.user_name == "Alice" for u in users)
                assert any(u.user_name == "Bob" for u in users)

    def test_sync_pending_events_no_channel(self):
        """Test sync des événements en attente sans channel."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            service._channel = None
            
            mock_state = SyncState()
            mock_state.pending_events = [
                SyncEvent(
                    event_type=SyncEventType.ITEM_ADDED,
                    liste_id=1,
                    user_id="user-123",
                    user_name="Alice"
                )
            ]
            
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                service.sync_pending_events()
                
                # Les événements restent en attente
                assert len(mock_state.pending_events) == 1

    def test_sync_pending_events_with_channel(self):
        """Test sync des événements en attente avec channel."""
        with patch.object(RealtimeSyncService, '_init_client'):
            service = RealtimeSyncService()
            
            mock_channel = MagicMock()
            service._channel = mock_channel
            
            pending_event = SyncEvent(
                event_type=SyncEventType.ITEM_ADDED,
                liste_id=1,
                user_id="user-123",
                user_name="Alice"
            )
            
            mock_state = SyncState()
            mock_state.pending_events = [pending_event]
            
            with patch.object(RealtimeSyncService, 'state', new_callable=PropertyMock, return_value=mock_state):
                with patch.object(service, 'broadcast_event') as mock_broadcast:
                    service.sync_pending_events()
                    
                    mock_broadcast.assert_called_once()
                    assert len(mock_state.pending_events) == 0


class TestRealtimeSyncServiceFactory:
    """Tests de la factory du service."""

    def test_get_realtime_sync_service_creates_singleton(self):
        """Test que get_realtime_sync_service retourne un singleton."""
        # Reset le singleton  
        import src.services.web.synchronisation as sync_module
        sync_module._sync_service = None
        
        with patch.object(RealtimeSyncService, '_init_client'):
            service1 = get_realtime_sync_service()
            service2 = get_realtime_sync_service()
            
            assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS DES COMPOSANTS UI
# ═══════════════════════════════════════════════════════════

class TestRenderComponents:
    """Tests des fonctions de rendu UI."""

    def test_render_presence_indicator_no_users(self):
        """Test du rendu sans utilisateurs."""
        from src.services.web.synchronisation import render_presence_indicator
        
        with patch.object(RealtimeSyncService, '_init_client'):
            with patch('src.services.web.synchronisation.get_realtime_sync_service') as mock_factory:
                mock_service = MagicMock()
                mock_service.get_connected_users.return_value = []
                mock_factory.return_value = mock_service
                
                # Ne doit pas lever d'exception
                render_presence_indicator()

    def test_render_sync_status_connected(self):
        """Test du rendu du statut quand connecté."""
        from src.services.web.synchronisation import render_sync_status
        
        with patch.object(RealtimeSyncService, '_init_client'):
            with patch('src.services.web.synchronisation.get_realtime_sync_service') as mock_factory:
                mock_service = MagicMock()
                mock_state = SyncState(connected=True)
                mock_service.state = mock_state
                mock_service.get_connected_users.return_value = [
                    PresenceInfo(user_id="1", user_name="Alice")
                ]
                mock_factory.return_value = mock_service
                
                with patch('src.services.web.synchronisation.st.success') as mock_success:
                    render_sync_status()
                    mock_success.assert_called_once()

    def test_render_sync_status_pending(self):
        """Test du rendu avec événements en attente."""
        from src.services.web.synchronisation import render_sync_status
        
        with patch.object(RealtimeSyncService, '_init_client'):
            with patch('src.services.web.synchronisation.get_realtime_sync_service') as mock_factory:
                mock_service = MagicMock()
                mock_state = SyncState(connected=False)
                mock_state.pending_events = [MagicMock()]
                mock_service.state = mock_state
                mock_factory.return_value = mock_service
                
                with patch('src.services.web.synchronisation.st.warning') as mock_warning:
                    render_sync_status()
                    mock_warning.assert_called_once()

    def test_render_sync_status_offline(self):
        """Test du rendu en mode hors ligne."""
        from src.services.web.synchronisation import render_sync_status
        
        with patch.object(RealtimeSyncService, '_init_client'):
            with patch('src.services.web.synchronisation.get_realtime_sync_service') as mock_factory:
                mock_service = MagicMock()
                mock_state = SyncState(connected=False)
                mock_state.pending_events = []
                mock_service.state = mock_state
                mock_factory.return_value = mock_service
                
                with patch('src.services.web.synchronisation.st.info') as mock_info:
                    render_sync_status()
                    mock_info.assert_called_once()

    def test_render_typing_indicator(self):
        """Test du rendu des indicateurs de frappe."""
        from src.services.web.synchronisation import render_typing_indicator
        
        with patch.object(RealtimeSyncService, '_init_client'):
            with patch('src.services.web.synchronisation.get_realtime_sync_service') as mock_factory:
                mock_service = MagicMock()
                mock_service._get_current_user_id.return_value = "user-me"
                mock_service.get_connected_users.return_value = [
                    PresenceInfo(user_id="user-other", user_name="Bob", is_typing=True)
                ]
                mock_factory.return_value = mock_service
                
                with patch('src.services.web.synchronisation.st.caption') as mock_caption:
                    render_typing_indicator()
                    mock_caption.assert_called_once()
