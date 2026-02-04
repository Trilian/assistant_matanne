# -*- coding: utf-8 -*-
"""
Tests pour offline.py - amélioration de la couverture

Cible:
- ConnectionStatus, OperationType enums
- PendingOperation dataclass
- ConnectionManager class
- OfflineQueue class
- OfflineSynchronizer class
"""
import pytest
import time
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestConnectionStatus:
    """Tests pour ConnectionStatus enum."""
    
    def test_online_value(self):
        """ONLINE a la valeur 'online'."""
        from src.core.offline import ConnectionStatus
        assert ConnectionStatus.ONLINE.value == "online"
    
    def test_offline_value(self):
        """OFFLINE a la valeur 'offline'."""
        from src.core.offline import ConnectionStatus
        assert ConnectionStatus.OFFLINE.value == "offline"
    
    def test_connecting_value(self):
        """CONNECTING a la valeur 'connecting'."""
        from src.core.offline import ConnectionStatus
        assert ConnectionStatus.CONNECTING.value == "connecting"
    
    def test_error_value(self):
        """ERROR a la valeur 'error'."""
        from src.core.offline import ConnectionStatus
        assert ConnectionStatus.ERROR.value == "error"


class TestOperationType:
    """Tests pour OperationType enum."""
    
    def test_create_value(self):
        """CREATE a la valeur 'create'."""
        from src.core.offline import OperationType
        assert OperationType.CREATE.value == "create"
    
    def test_update_value(self):
        """UPDATE a la valeur 'update'."""
        from src.core.offline import OperationType
        assert OperationType.UPDATE.value == "update"
    
    def test_delete_value(self):
        """DELETE a la valeur 'delete'."""
        from src.core.offline import OperationType
        assert OperationType.DELETE.value == "delete"


class TestPendingOperation:
    """Tests pour PendingOperation dataclass."""
    
    def test_default_values(self):
        """Valeurs par défaut correctes."""
        from src.core.offline import PendingOperation, OperationType
        
        op = PendingOperation()
        
        assert op.operation_type == OperationType.CREATE
        assert op.model_name == ""
        assert op.data == {}
        assert op.retry_count == 0
        assert op.last_error is None
        assert op.id is not None
    
    def test_to_dict(self):
        """to_dict convertit correctement."""
        from src.core.offline import PendingOperation, OperationType
        
        op = PendingOperation(
            operation_type=OperationType.UPDATE,
            model_name="Recette",
            data={"id": 1, "nom": "Tarte"},
        )
        
        d = op.to_dict()
        
        assert d["operation_type"] == "update"
        assert d["model_name"] == "Recette"
        assert d["data"] == {"id": 1, "nom": "Tarte"}
        assert "created_at" in d
        assert "id" in d
    
    def test_from_dict(self):
        """from_dict crée correctement."""
        from src.core.offline import PendingOperation, OperationType
        
        data = {
            "id": "abc123",
            "operation_type": "delete",
            "model_name": "Ingredient",
            "data": {"id": 5},
            "retry_count": 2,
            "last_error": "Timeout",
            "created_at": datetime.now().isoformat(),
        }
        
        op = PendingOperation.from_dict(data)
        
        assert op.id == "abc123"
        assert op.operation_type == OperationType.DELETE
        assert op.model_name == "Ingredient"
        assert op.retry_count == 2
        assert op.last_error == "Timeout"


class TestConnectionManager:
    """Tests pour ConnectionManager."""
    
    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch('src.core.offline.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    def test_get_status_default_online(self, mock_streamlit):
        """get_status retourne ONLINE par défaut."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        status = ConnectionManager.get_status()
        assert status == ConnectionStatus.ONLINE
    
    def test_set_and_get_status(self, mock_streamlit):
        """set_status puis get_status fonctionne."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        
        assert ConnectionManager.get_status() == ConnectionStatus.OFFLINE
    
    def test_is_online_true(self, mock_streamlit):
        """is_online retourne True si ONLINE."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        assert ConnectionManager.is_online() is True
    
    def test_is_online_false(self, mock_streamlit):
        """is_online retourne False si pas ONLINE."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        assert ConnectionManager.is_online() is False
    
    def test_check_connection_success(self, mock_streamlit):
        """check_connection met ONLINE si connexion OK."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        with patch('src.core.offline.verifier_connexion') as mock_verify:
            mock_verify.return_value = True
            
            result = ConnectionManager.check_connection(force=True)
            
            assert result is True
            assert ConnectionManager.get_status() == ConnectionStatus.ONLINE
    
    def test_check_connection_failure(self, mock_streamlit):
        """check_connection met OFFLINE si connexion KO."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        with patch('src.core.offline.verifier_connexion') as mock_verify:
            mock_verify.return_value = False
            
            result = ConnectionManager.check_connection(force=True)
            
            assert result is False
            assert ConnectionManager.get_status() == ConnectionStatus.OFFLINE
    
    def test_check_connection_error(self, mock_streamlit):
        """check_connection met ERROR si exception."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        with patch('src.core.offline.verifier_connexion') as mock_verify:
            mock_verify.side_effect = Exception("DB error")
            
            result = ConnectionManager.check_connection(force=True)
            
            assert result is False
            assert ConnectionManager.get_status() == ConnectionStatus.ERROR
    
    def test_check_connection_uses_cache(self, mock_streamlit):
        """check_connection utilise le cache si récent."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        # Simuler un check récent
        mock_streamlit.session_state["_connection_status"] = ConnectionStatus.ONLINE
        mock_streamlit.session_state["_connection_last_check"] = time.time()
        
        with patch('src.core.offline.verifier_connexion') as mock_verify:
            result = ConnectionManager.check_connection(force=False)
            
            # Ne doit pas appeler verifier_connexion
            mock_verify.assert_not_called()
            assert result is True
    
    def test_handle_connection_error(self, mock_streamlit):
        """handle_connection_error met OFFLINE."""
        from src.core.offline import ConnectionManager, ConnectionStatus
        
        ConnectionManager.handle_connection_error(Exception("Test error"))
        
        assert ConnectionManager.get_status() == ConnectionStatus.OFFLINE


class TestOfflineQueue:
    """Tests pour OfflineQueue."""
    
    @pytest.fixture(autouse=True)
    def mock_streamlit_and_file(self, tmp_path):
        """Mock streamlit et fichiers."""
        with patch('src.core.offline.st') as mock_st:
            mock_st.session_state = {}
            
            with patch.object(
                __import__('src.core.offline', fromlist=['OfflineQueue']).OfflineQueue,
                'QUEUE_FILE',
                tmp_path / "offline_queue.json"
            ):
                yield mock_st, tmp_path
    
    def test_add_operation(self, mock_streamlit_and_file):
        """add ajoute une opération."""
        from src.core.offline import OfflineQueue, OperationType
        
        mock_st, _ = mock_streamlit_and_file
        
        op = OfflineQueue.add(
            operation_type=OperationType.CREATE,
            model_name="Recette",
            data={"nom": "Tarte"},
        )
        
        assert op.model_name == "Recette"
        assert op.operation_type == OperationType.CREATE
        assert OfflineQueue.get_count() == 1
    
    def test_get_pending(self, mock_streamlit_and_file):
        """get_pending retourne les opérations."""
        from src.core.offline import OfflineQueue, OperationType
        
        mock_st, _ = mock_streamlit_and_file
        
        OfflineQueue.add(OperationType.CREATE, "Model1", {"id": 1})
        OfflineQueue.add(OperationType.UPDATE, "Model2", {"id": 2})
        
        pending = OfflineQueue.get_pending()
        
        assert len(pending) == 2
    
    def test_remove(self, mock_streamlit_and_file):
        """remove supprime une opération."""
        from src.core.offline import OfflineQueue, OperationType
        
        mock_st, _ = mock_streamlit_and_file
        
        op = OfflineQueue.add(OperationType.CREATE, "Test", {})
        
        result = OfflineQueue.remove(op.id)
        
        assert result is True
        assert OfflineQueue.get_count() == 0
    
    def test_remove_nonexistent(self, mock_streamlit_and_file):
        """remove retourne False si id inexistant."""
        from src.core.offline import OfflineQueue
        
        mock_st, _ = mock_streamlit_and_file
        
        result = OfflineQueue.remove("nonexistent")
        assert result is False
    
    def test_update_retry(self, mock_streamlit_and_file):
        """update_retry incrémente le compteur."""
        from src.core.offline import OfflineQueue, OperationType
        
        mock_st, _ = mock_streamlit_and_file
        
        op = OfflineQueue.add(OperationType.CREATE, "Test", {})
        
        OfflineQueue.update_retry(op.id, "Error message")
        
        pending = OfflineQueue.get_pending()
        assert pending[0].retry_count == 1
        assert pending[0].last_error == "Error message"
    
    def test_clear(self, mock_streamlit_and_file):
        """clear vide la queue."""
        from src.core.offline import OfflineQueue, OperationType
        
        mock_st, _ = mock_streamlit_and_file
        
        OfflineQueue.add(OperationType.CREATE, "Test1", {})
        OfflineQueue.add(OperationType.CREATE, "Test2", {})
        
        count = OfflineQueue.clear()
        
        assert count == 2
        assert OfflineQueue.get_count() == 0


class TestOfflineSynchronizer:
    """Tests pour OfflineSynchronizer."""
    
    @pytest.fixture(autouse=True)
    def mock_dependencies(self, tmp_path):
        """Mock toutes les dépendances."""
        with patch('src.core.offline.st') as mock_st:
            mock_st.session_state = {}
            
            with patch.object(
                __import__('src.core.offline', fromlist=['OfflineQueue']).OfflineQueue,
                'QUEUE_FILE',
                tmp_path / "offline_queue.json"
            ):
                yield mock_st
    
    def test_sync_all_offline(self, mock_dependencies):
        """sync_all retourne erreur si offline."""
        from src.core.offline import OfflineSynchronizer, ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.OFFLINE)
        
        result = OfflineSynchronizer.sync_all()
        
        assert result["success"] == 0
        assert "Pas de connexion" in result["errors"]
    
    def test_sync_all_empty_queue(self, mock_dependencies):
        """sync_all avec queue vide."""
        from src.core.offline import OfflineSynchronizer, ConnectionManager, ConnectionStatus
        
        ConnectionManager.set_status(ConnectionStatus.ONLINE)
        
        result = OfflineSynchronizer.sync_all()
        
        assert result["success"] == 0
        assert result["failed"] == 0
        assert result["errors"] == []
