"""
Tests finaux pour atteindre 80% de couverture du module Core.
Cible: lignes non couvertes dans offline.py, performance.py, sql_optimizer.py
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open
import json


class TestOfflineQueueFileMethods:
    """Tests pour FileAttenteHorsLigne - mÃ©thodes de fichier."""
    
    @patch('src.core.offline.st')
    def test_ensure_cache_dir(self, mock_st):
        """Test _ensure_cache_dir crÃ©e le dossier."""
        mock_st.session_state = {}
        from src.core.offline import FileAttenteHorsLigne
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            FileAttenteHorsLigne._ensure_cache_dir()
            mock_mkdir.assert_called_once_with(exist_ok=True)
    
    @patch('src.core.offline.st')
    def test_load_from_file_not_exists(self, mock_st):
        """Test _load_from_file quand le fichier n'existe pas."""
        mock_st.session_state = {}
        from src.core.offline import FileAttenteHorsLigne
        
        with patch.object(Path, 'exists', return_value=False):
            result = FileAttenteHorsLigne._load_from_file()
            assert result == []
    
    @patch('src.core.offline.st')
    def test_load_from_file_exists(self, mock_st):
        """Test _load_from_file quand le fichier existe."""
        mock_st.session_state = {}
        from src.core.offline import FileAttenteHorsLigne
        
        test_data = [{"id": "test123", "operation_type": "create", "model_name": "Test"}]
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
                result = FileAttenteHorsLigne._load_from_file()
                assert len(result) == 1
                assert result[0]["id"] == "test123"
    
    @patch('src.core.offline.st')
    def test_load_from_file_error(self, mock_st):
        """Test _load_from_file avec erreur JSON."""
        mock_st.session_state = {}
        from src.core.offline import FileAttenteHorsLigne
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json")):
                result = FileAttenteHorsLigne._load_from_file()
                assert result == []
    
    @patch('src.core.offline.st')
    def test_save_to_file(self, mock_st):
        """Test _save_to_file."""
        mock_st.session_state = {}
        from src.core.offline import FileAttenteHorsLigne
        
        test_data = [{"id": "abc"}]
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            m = mock_open()
            with patch('builtins.open', m):
                FileAttenteHorsLigne._save_to_file(test_data)
                m.assert_called_once()


class TestConnectionManagerMethods:
    """Tests pour GestionnaireConnexion."""
    
    @patch('src.core.offline.st')
    def test_set_status(self, mock_st):
        """Test set_status met Ã  jour le statut."""
        mock_st.session_state = {}
        from src.core.offline import GestionnaireConnexion, StatutConnexion
        
        GestionnaireConnexion.set_status(StatutConnexion.OFFLINE)
        assert mock_st.session_state[GestionnaireConnexion.SESSION_KEY] == StatutConnexion.OFFLINE
    
    @patch('src.core.offline.st')
    def test_is_online_when_online(self, mock_st):
        """Test is_online retourne True quand ONLINE."""
        from src.core.offline import GestionnaireConnexion, StatutConnexion
        
        mock_st.session_state = {GestionnaireConnexion.SESSION_KEY: StatutConnexion.ONLINE}
        assert GestionnaireConnexion.is_online() is True
    
    @patch('src.core.offline.st')
    def test_is_online_when_offline(self, mock_st):
        """Test is_online retourne False quand OFFLINE."""
        from src.core.offline import GestionnaireConnexion, StatutConnexion
        
        mock_st.session_state = {GestionnaireConnexion.SESSION_KEY: StatutConnexion.OFFLINE}
        assert GestionnaireConnexion.is_online() is False
    
    @patch('src.core.offline.st')
    def test_handle_connection_error(self, mock_st):
        """Test handle_connection_error met le statut Ã  OFFLINE."""
        mock_st.session_state = {}
        from src.core.offline import GestionnaireConnexion, StatutConnexion
        
        error = Exception("Test error")
        GestionnaireConnexion.handle_connection_error(error)
        assert mock_st.session_state[GestionnaireConnexion.SESSION_KEY] == StatutConnexion.OFFLINE


class TestMemoryMonitorMethods:
    """Tests pour MoniteurMemoire."""
    
    @patch('src.core.performance.st')
    @patch('src.core.performance.tracemalloc')
    def test_start_tracking(self, mock_tracemalloc, mock_st):
        """Test start_tracking dÃ©marre le tracking."""
        mock_st.session_state = {}
        from src.core.performance import MoniteurMemoire
        
        # Reset le flag internal
        MoniteurMemoire._tracking_active = False
        
        MoniteurMemoire.start_tracking()
        mock_tracemalloc.start.assert_called_once()
        assert MoniteurMemoire._tracking_active is True
    
    @patch('src.core.performance.st')
    @patch('src.core.performance.tracemalloc')
    def test_stop_tracking(self, mock_tracemalloc, mock_st):
        """Test stop_tracking arrÃªte le tracking."""
        mock_st.session_state = {}
        from src.core.performance import MoniteurMemoire
        
        MoniteurMemoire._tracking_active = True
        
        MoniteurMemoire.stop_tracking()
        mock_tracemalloc.stop.assert_called_once()
        assert MoniteurMemoire._tracking_active is False
    
    @patch('src.core.performance.st')
    @patch('src.core.performance.tracemalloc')
    @patch('src.core.performance.gc')
    def test_get_current_usage_not_tracking(self, mock_gc, mock_tracemalloc, mock_st):
        """Test get_current_usage quand pas de tracking."""
        mock_st.session_state = {}
        mock_gc.get_objects.return_value = [1, 2, 3]
        from src.core.performance import MoniteurMemoire
        
        MoniteurMemoire._tracking_active = False
        
        result = MoniteurMemoire.get_current_usage()
        assert result["current_mb"] == 0
        assert result["peak_mb"] == 0
        assert result["total_objects"] == 3
    
    @patch('src.core.performance.st')
    @patch('src.core.performance.tracemalloc')
    @patch('src.core.performance.gc')
    def test_get_current_usage_with_tracking(self, mock_gc, mock_tracemalloc, mock_st):
        """Test get_current_usage avec tracking actif."""
        mock_st.session_state = {}
        mock_gc.get_objects.return_value = []
        mock_tracemalloc.get_traced_memory.return_value = (1024*1024*10, 1024*1024*15)  # 10MB, 15MB
        from src.core.performance import MoniteurMemoire
        
        MoniteurMemoire._tracking_active = True
        
        result = MoniteurMemoire.get_current_usage()
        assert result["current_mb"] == 10.0
        assert result["peak_mb"] == 15.0
    
    @patch('src.core.performance.st')
    @patch('src.core.performance.gc')
    def test_force_cleanup(self, mock_gc, mock_st):
        """Test force_cleanup collecte les objets."""
        mock_st.session_state = {}
        mock_gc.get_objects.return_value = []
        mock_gc.collect.return_value = 50
        from src.core.performance import MoniteurMemoire
        
        MoniteurMemoire._tracking_active = False
        
        result = MoniteurMemoire.force_cleanup()
        assert result["objects_collected"] == 50
        mock_gc.collect.assert_called_once()


class TestSQLAlchemyListenerLogQuery:
    """Tests pour EcouteurSQLAlchemy._log_query."""
    
    @patch('src.core.sql_optimizer.st')
    def test_log_query_basic(self, mock_st):
        """Test _log_query enregistre la requÃªte."""
        mock_st.session_state = {}
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        EcouteurSQLAlchemy._log_query("SELECT * FROM users", 50.0, {"id": 1})
        
        queries = mock_st.session_state[EcouteurSQLAlchemy.SESSION_KEY]
        assert len(queries) == 1
        assert queries[0].sql == "SELECT * FROM users"
        assert queries[0].duration_ms == 50.0
    
    @patch('src.core.sql_optimizer.st')
    def test_log_query_slow(self, mock_st):
        """Test _log_query pour requÃªte lente (>100ms)."""
        mock_st.session_state = {}
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        with patch('src.core.sql_optimizer.logger') as mock_logger:
            EcouteurSQLAlchemy._log_query("SELECT * FROM big_table", 150.0, {})
            mock_logger.warning.assert_called()
    
    @patch('src.core.sql_optimizer.st')
    def test_log_query_truncates_at_200(self, mock_st):
        """Test _log_query garde seulement 200 derniÃ¨res requÃªtes."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        mock_st.session_state = {EcouteurSQLAlchemy.SESSION_KEY: []}
        
        # Ajouter 205 requÃªtes
        for i in range(205):
            EcouteurSQLAlchemy._log_query(f"SELECT {i}", 1.0, {})
        
        queries = mock_st.session_state[EcouteurSQLAlchemy.SESSION_KEY]
        assert len(queries) == 200


class TestSQLAlchemyListenerGetStats:
    """Tests pour EcouteurSQLAlchemy.get_stats."""
    
    @patch('src.core.sql_optimizer.st')
    def test_get_stats_empty(self, mock_st):
        """Test get_stats avec queue vide."""
        mock_st.session_state = {}
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        stats = EcouteurSQLAlchemy.get_stats()
        assert stats["total"] == 0
        assert stats["by_operation"] == {}
        assert stats["avg_time_ms"] == 0
    
    @patch('src.core.sql_optimizer.st')
    def test_get_stats_with_queries(self, mock_st):
        """Test get_stats avec des requÃªtes."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete
        from datetime import datetime
        
        queries = [
            InfoRequete(sql="SELECT *", duration_ms=50.0, table="users", operation="SELECT"),
            InfoRequete(sql="SELECT *", duration_ms=150.0, table="users", operation="SELECT"),  # slow
        ]
        mock_st.session_state = {EcouteurSQLAlchemy.SESSION_KEY: queries}
        
        stats = EcouteurSQLAlchemy.get_stats()
        assert stats["total"] == 2
        assert stats["by_operation"]["SELECT"] == 2
        assert stats["avg_time_ms"] == 100.0
        assert len(stats["slow_queries"]) == 1
    
    @patch('src.core.sql_optimizer.st')
    def test_clear(self, mock_st):
        """Test clear vide le log."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete
        
        queries = [InfoRequete(sql="SELECT *", duration_ms=50.0)]
        mock_st.session_state = {EcouteurSQLAlchemy.SESSION_KEY: queries}
        
        EcouteurSQLAlchemy.clear()
        assert mock_st.session_state[EcouteurSQLAlchemy.SESSION_KEY] == []


class TestSQLOptimizer:
    """Tests pour OptimiseurSQL dans performance.py."""
    
    @patch('src.core.performance.st')
    def test_record_query(self, mock_st):
        """Test record_query enregistre une requÃªte."""
        mock_st.session_state = {}
        from src.core.performance import OptimiseurSQL
        
        OptimiseurSQL.record_query("SELECT * FROM users", 50.0, 10)
        
        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert stats["total_count"] == 1
        assert stats["total_time_ms"] == 50.0
    
    @patch('src.core.performance.st')
    def test_record_query_slow(self, mock_st):
        """Test record_query pour requÃªte lente."""
        mock_st.session_state = {}
        from src.core.performance import OptimiseurSQL
        
        with patch('src.core.performance.logger') as mock_logger:
            OptimiseurSQL.record_query("SELECT * FROM big_table", 150.0, 1000)
            mock_logger.warning.assert_called()
            
        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert len(stats["slow_queries"]) == 1
    
    @patch('src.core.performance.st')
    def test_get_stats_empty(self, mock_st):
        """Test get_stats avec donnÃ©es vides."""
        mock_st.session_state = {}
        from src.core.performance import OptimiseurSQL
        
        stats = OptimiseurSQL.get_stats()
        assert stats["total_queries"] == 0
        assert stats["avg_time_ms"] == 0
    
    @patch('src.core.performance.st')
    def test_clear(self, mock_st):
        """Test clear rÃ©initialise."""
        from src.core.performance import OptimiseurSQL
        
        mock_st.session_state = {OptimiseurSQL.SESSION_KEY: {
            "queries": [{"q": 1}],
            "slow_queries": [],
            "total_count": 5,
            "total_time_ms": 100.0,
        }}
        
        OptimiseurSQL.clear()
        
        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert stats["total_count"] == 0


class TestOfflineQueueMethods:
    """Tests pour FileAttenteHorsLigne - mÃ©thodes de queue."""
    
    @patch('src.core.offline.st')
    def test_get_queue_from_session(self, mock_st):
        """Test _get_queue retourne de session."""
        from src.core.offline import FileAttenteHorsLigne
        
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "test"}]}
        
        queue = FileAttenteHorsLigne._get_queue()
        assert len(queue) == 1
        assert queue[0]["id"] == "test"
    
    @patch('src.core.offline.st')
    def test_get_count(self, mock_st):
        """Test get_count retourne le nombre d'opÃ©rations."""
        from src.core.offline import FileAttenteHorsLigne
        
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "1"}, {"id": "2"}]}
        
        with patch.object(Path, 'exists', return_value=False):
            count = FileAttenteHorsLigne.get_count()
            assert count == 2
    
    @patch('src.core.offline.st')
    def test_remove_success(self, mock_st):
        """Test remove supprime l'opÃ©ration."""
        from src.core.offline import FileAttenteHorsLigne
        
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "abc"}, {"id": "def"}]}
        
        with patch.object(Path, 'mkdir'):
            with patch('builtins.open', mock_open()):
                result = FileAttenteHorsLigne.remove("abc")
                assert result is True
                assert len(mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY]) == 1
    
    @patch('src.core.offline.st')
    def test_remove_not_found(self, mock_st):
        """Test remove retourne False si non trouvÃ©."""
        from src.core.offline import FileAttenteHorsLigne
        
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "abc"}]}
        
        with patch.object(Path, 'exists', return_value=False):
            result = FileAttenteHorsLigne.remove("xyz")
            assert result is False
