"""
Tests pour le module offline (offline.py).

Tests couverts:
- ConnectionManager
- OfflineQueue
- OfflineSynchronizer
- DÃ©corateur @offline_aware
"""

import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_session_state():
    """Mock streamlit session_state."""
    state = {}
    with patch("streamlit.session_state", state):
        yield state


@pytest.fixture
def temp_queue_file():
    """Fichier temporaire pour la queue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        queue_file = Path(tmpdir) / "offline_queue.json"
        with patch("src.core.offline.OfflineQueue.QUEUE_FILE", queue_file):
            yield queue_file


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PENDING OPERATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPendingOperation:
    """Tests pour PendingOperation dataclass."""
    
    def test_create_operation(self):
        """Test crÃ©ation opÃ©ration."""
        from src.core.offline import PendingOperation, OperationType
        
        op = PendingOperation(
            operation_type=OperationType.CREATE,
            model_name="recette",
            data={"nom": "Tarte"},
        )
        
        assert op.id is not None
        assert op.operation_type == OperationType.CREATE
        assert op.model_name == "recette"
        assert op.data["nom"] == "Tarte"
        assert op.retry_count == 0
    
    def test_to_dict(self):
        """Test sÃ©rialisation."""
        from src.core.offline import PendingOperation, OperationType
        
        op = PendingOperation(
            operation_type=OperationType.UPDATE,
            model_name="inventaire",
            data={"id": 1, "quantite": 5},
        )
        
        data = op.to_dict()
        
        assert data["operation_type"] == "update"
        assert data["model_name"] == "inventaire"
        assert "created_at" in data
    
    def test_from_dict(self):
        """Test dÃ©sÃ©rialisation."""
        from src.core.offline import PendingOperation, OperationType
        
        data = {
            "id": "test-123",
            "operation_type": "delete",
            "model_name": "courses",
            "data": {"id": 42},
            "created_at": datetime.now().isoformat(),
            "retry_count": 2,
            "last_error": "Connection timeout",
        }
        
        op = PendingOperation.from_dict(data)
        
        assert op.id == "test-123"
        assert op.operation_type == OperationType.DELETE
        assert op.retry_count == 2
        assert op.last_error == "Connection timeout"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONNECTION MANAGER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConnectionManager:
    """Tests pour ConnectionManager."""
    
    def test_initial_status(self, mock_session_state):
        """Test statut initial."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        status = ConnectionManager.get_status()
        
        # Par dÃ©faut, supposÃ© online
        assert status == ConnectionStatus.ONLINE
    
    def test_set_status(self, mock_session_state):
        """Test changement de statut."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        
        assert ConnectionManager.get_status() == ConnectionStatus.OFFLINE
        assert ConnectionManager.is_online() is False
    
    def test_is_online(self, mock_session_state):
        """Test helper is_online."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        assert ConnectionManager.is_online() is True
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        assert ConnectionManager.is_online() is False
        
        ConnectionManager.set_status(ConnectionStatus.ERROR)
        assert ConnectionManager.is_online() is False
    
    def test_handle_connection_error(self, mock_session_state):
        """Test gestion erreur connexion."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        
        ConnectionManager.handle_connection_error(Exception("Connection failed"))
        
        assert ConnectionManager.get_status() == ConnectionStatus.OFFLINE


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OFFLINE QUEUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOfflineQueue:
    """Tests pour OfflineQueue."""
    
    def test_add_operation(self, mock_session_state, temp_queue_file):
        """Test ajout opÃ©ration."""
        from src.core.offline import OfflineQueue, OperationType
        
        op = OfflineQueue.add(
            operation_type=OperationType.CREATE,
            model_name="recette",
            data={"nom": "Test"},
        )
        
        assert op.id is not None
        assert OfflineQueue.get_count() == 1
    
    def test_get_pending(self, mock_session_state, temp_queue_file):
        """Test rÃ©cupÃ©ration opÃ©rations."""
        from src.core.offline import OfflineQueue, OperationType
        
        OfflineQueue.add(OperationType.CREATE, "model1", {"a": 1})
        OfflineQueue.add(OperationType.UPDATE, "model2", {"b": 2})
        
        pending = OfflineQueue.get_pending()
        
        assert len(pending) == 2
    
    def test_remove_operation(self, mock_session_state, temp_queue_file):
        """Test suppression opÃ©ration."""
        from src.core.offline import OfflineQueue, OperationType
        
        op = OfflineQueue.add(OperationType.CREATE, "test", {})
        
        result = OfflineQueue.remove(op.id)
        
        assert result is True
        assert OfflineQueue.get_count() == 0
    
    def test_remove_nonexistent(self, mock_session_state, temp_queue_file):
        """Test suppression inexistante."""
        from src.core.offline import OfflineQueue
        
        result = OfflineQueue.remove("nonexistent-id")
        assert result is False
    
    def test_update_retry(self, mock_session_state, temp_queue_file):
        """Test mise Ã  jour retry."""
        from src.core.offline import OfflineQueue, OperationType
        
        op = OfflineQueue.add(OperationType.CREATE, "test", {})
        
        OfflineQueue.update_retry(op.id, "Connection error")
        
        pending = OfflineQueue.get_pending()
        updated = [p for p in pending if p.id == op.id][0]
        
        assert updated.retry_count == 1
        assert updated.last_error == "Connection error"
    
    def test_clear(self, mock_session_state, temp_queue_file):
        """Test vidage queue."""
        from src.core.offline import OfflineQueue, OperationType
        
        OfflineQueue.add(OperationType.CREATE, "test1", {})
        OfflineQueue.add(OperationType.CREATE, "test2", {})
        
        count = OfflineQueue.clear()
        
        assert count == 2
        assert OfflineQueue.get_count() == 0
    
    def test_persistence(self, mock_session_state, temp_queue_file):
        """Test persistance fichier."""
        from src.core.offline import OfflineQueue, OperationType
        
        OfflineQueue.add(OperationType.CREATE, "persistent", {"data": "test"})
        
        # VÃ©rifier que le fichier existe
        assert temp_queue_file.exists()
        
        # Lire le contenu
        with open(temp_queue_file) as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["model_name"] == "persistent"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OFFLINE SYNCHRONIZER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOfflineSynchronizer:
    """Tests pour OfflineSynchronizer."""
    
    def test_sync_when_offline(self, mock_session_state, temp_queue_file):
        """Test sync quand offline."""
        from src.core.offline import (
            OfflineSynchronizer,
            OfflineQueue,
            ConnectionManager,
            ConnectionStatus,
            OperationType,
        )
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        OfflineQueue.add(OperationType.CREATE, "test", {})
        
        results = OfflineSynchronizer.sync_all()
        
        assert results["success"] == 0
        assert "Pas de connexion" in results["errors"]
    
    def test_sync_with_progress(self, mock_session_state, temp_queue_file):
        """Test sync avec callback progress."""
        from src.core.offline import (
            OfflineSynchronizer,
            OfflineQueue,
            ConnectionManager,
            ConnectionStatus,
            OperationType,
        )
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        # Mock le sync pour Ã©viter vrai appel DB
        with patch.object(OfflineSynchronizer, "_sync_operation", return_value=True):
            OfflineQueue.add(OperationType.CREATE, "test1", {})
            OfflineQueue.add(OperationType.CREATE, "test2", {})
            
            OfflineSynchronizer.sync_all(progress_callback)
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OFFLINE_AWARE DECORATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOfflineAwareDecorator:
    """Tests pour le dÃ©corateur @offline_aware."""
    
    def test_online_execution(self, mock_session_state, temp_queue_file):
        """Test exÃ©cution en ligne."""
        from src.core.offline import (
            offline_aware,
            OperationType,
            ConnectionManager,
            ConnectionStatus,
        )
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        
        @offline_aware("test_model", OperationType.CREATE)
        def create_item(data: dict):
            return {"id": 1, **data}
        
        result = create_item(data={"name": "Test"})
        
        assert result["id"] == 1
        assert result["name"] == "Test"
    
    def test_offline_queuing(self, mock_session_state, temp_queue_file):
        """Test mise en queue quand offline."""
        from src.core.offline import (
            offline_aware,
            OperationType,
            ConnectionManager,
            ConnectionStatus,
            OfflineQueue,
        )
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        
        @offline_aware("test_model", OperationType.CREATE)
        def create_item(data: dict):
            return {"id": 1, **data}
        
        result = create_item(data={"name": "Offline Test"})
        
        # Doit retourner objet avec flag _offline
        assert result.get("_offline") is True
        
        # Doit avoir ajoutÃ© Ã  la queue
        assert OfflineQueue.get_count() == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOfflineEdgeCases:
    """Tests cas limites."""
    
    def test_queue_with_special_data(self, mock_session_state, temp_queue_file):
        """Test queue avec donnÃ©es spÃ©ciales."""
        from src.core.offline import OfflineQueue, OperationType
        
        special_data = {
            "unicode": "Ã‰mojis: ðŸŽ‰ Accents: Ã©Ã Ã¼",
            "nested": {"a": {"b": [1, 2, 3]}},
            "null": None,
        }
        
        op = OfflineQueue.add(OperationType.CREATE, "special", special_data)
        
        pending = OfflineQueue.get_pending()
        retrieved = [p for p in pending if p.id == op.id][0]
        
        assert retrieved.data["unicode"] == special_data["unicode"]
        assert retrieved.data["nested"]["a"]["b"] == [1, 2, 3]
    
    def test_multiple_retries(self, mock_session_state, temp_queue_file):
        """Test multiples retries."""
        from src.core.offline import OfflineQueue, OperationType
        
        op = OfflineQueue.add(OperationType.CREATE, "retry_test", {})
        
        for i in range(5):
            OfflineQueue.update_retry(op.id, f"Error {i}")
        
        pending = OfflineQueue.get_pending()
        updated = [p for p in pending if p.id == op.id][0]
        
        assert updated.retry_count == 5
        assert updated.last_error == "Error 4"
    
    def test_empty_queue_operations(self, mock_session_state, temp_queue_file):
        """Test opÃ©rations sur queue vide."""
        from src.core.offline import OfflineQueue
        
        assert OfflineQueue.get_count() == 0
        assert OfflineQueue.get_pending() == []
        assert OfflineQueue.clear() == 0

