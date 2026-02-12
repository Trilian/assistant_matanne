"""
Tests additionnels pour atteindre 80% de couverture du module Core.
Cible: offline.py, performance.py, sql_optimizer.py
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestConnectionStatusEnum:
    """Tests pour l'enum StatutConnexion (offline.py)."""
    
    def test_connection_status_values(self):
        """Test des valeurs de l'enum StatutConnexion."""
        from src.core.offline import StatutConnexion
        
        assert StatutConnexion.ONLINE.value == "online"
        assert StatutConnexion.OFFLINE.value == "offline"
        assert StatutConnexion.CONNECTING.value == "connecting"
        assert StatutConnexion.ERROR.value == "error"
    
    def test_connection_status_string_inheritance(self):
        """Test que StatutConnexion hÃ©rite de str."""
        from src.core.offline import StatutConnexion
        
        # Valeur accessible via .value
        assert StatutConnexion.ONLINE.value == "online"
        assert str(StatutConnexion.ONLINE) == "StatutConnexion.ONLINE"


class TestOperationTypeEnum:
    """Tests pour l'enum TypeOperation (offline.py)."""
    
    def test_operation_type_values(self):
        """Test des valeurs de l'enum TypeOperation."""
        from src.core.offline import TypeOperation
        
        assert TypeOperation.CREATE.value == "create"
        assert TypeOperation.UPDATE.value == "update"
        assert TypeOperation.DELETE.value == "delete"


class TestPerformanceMetricDataclass:
    """Tests pour la dataclass MetriquePerformance (performance.py)."""
    
    def test_performance_metric_creation(self):
        """Test crÃ©ation MetriquePerformance avec valeurs par dÃ©faut."""
        from src.core.performance import MetriquePerformance
        
        metric = MetriquePerformance(
            name="test_metric",
            duration_ms=150.5
        )
        
        assert metric.name == "test_metric"
        assert metric.duration_ms == 150.5
        assert metric.memory_delta_kb == 0
        assert isinstance(metric.timestamp, datetime)
        assert metric.metadata == {}
    
    def test_performance_metric_with_metadata(self):
        """Test MetriquePerformance avec metadata."""
        from src.core.performance import MetriquePerformance
        
        metric = MetriquePerformance(
            name="db_query",
            duration_ms=25.3,
            memory_delta_kb=128.5,
            metadata={"table": "recettes", "rows": 100}
        )
        
        assert metric.metadata["table"] == "recettes"
        assert metric.metadata["rows"] == 100
        assert metric.memory_delta_kb == 128.5


class TestFunctionStatsDataclass:
    """Tests pour la dataclass StatistiquesFonction (performance.py)."""
    
    def test_function_stats_defaults(self):
        """Test des valeurs par dÃ©faut de StatistiquesFonction."""
        from src.core.performance import StatistiquesFonction
        
        stats = StatistiquesFonction()
        
        assert stats.call_count == 0
        assert stats.total_time_ms == 0
        assert stats.min_time_ms == float('inf')  # Valeur infinie par dÃ©faut
        assert stats.max_time_ms == 0
        assert stats.avg_time_ms == 0
        assert stats.last_call is None
        assert stats.errors == 0
    
    def test_function_stats_update(self):
        """Test mise Ã  jour manuelle de StatistiquesFonction."""
        from src.core.performance import StatistiquesFonction
        
        stats = StatistiquesFonction()
        stats.call_count = 5
        stats.total_time_ms = 100.0
        stats.min_time_ms = 10.0
        stats.max_time_ms = 30.0
        stats.avg_time_ms = 20.0
        stats.last_call = datetime.now()
        stats.errors = 1
        
        assert stats.call_count == 5
        assert stats.avg_time_ms == 20.0
        assert stats.errors == 1


class TestQueryInfoDataclass:
    """Tests pour la dataclass InfoRequete (sql_optimizer.py)."""
    
    def test_query_info_creation(self):
        """Test crÃ©ation InfoRequete."""
        from src.core.sql_optimizer import InfoRequete
        
        info = InfoRequete(
            sql="SELECT * FROM recettes",
            duration_ms=5.2,
            table="recettes",
            operation="SELECT"
        )
        
        assert info.sql == "SELECT * FROM recettes"
        assert info.duration_ms == 5.2
        assert info.table == "recettes"
        assert info.operation == "SELECT"
        assert isinstance(info.timestamp, datetime)
        assert info.parameters == {}
    
    def test_query_info_with_parameters(self):
        """Test InfoRequete avec paramÃ¨tres."""
        from src.core.sql_optimizer import InfoRequete
        
        info = InfoRequete(
            sql="SELECT * FROM recettes WHERE id = :id",
            duration_ms=3.1,
            parameters={"id": 42}
        )
        
        assert info.parameters["id"] == 42


class TestN1DetectionDataclass:
    """Tests pour la dataclass DetectionN1 (sql_optimizer.py)."""
    
    def test_n1_detection_creation(self):
        """Test crÃ©ation DetectionN1."""
        from src.core.sql_optimizer import DetectionN1
        
        detection = DetectionN1(
            table="ingredients",
            parent_table="recettes",
            count=50,
            sample_query="SELECT * FROM ingredients WHERE recette_id = ?"
        )
        
        assert detection.table == "ingredients"
        assert detection.parent_table == "recettes"
        assert detection.count == 50
        assert "ingredients" in detection.sample_query
        assert isinstance(detection.first_seen, datetime)
    
    def test_n1_detection_defaults(self):
        """Test DetectionN1 valeurs par dÃ©faut."""
        from src.core.sql_optimizer import DetectionN1
        
        detection = DetectionN1(
            table="test",
            parent_table="parent",
            count=10
        )
        
        assert detection.sample_query == ""


class TestPendingOperationExtended:
    """Tests Ã©tendus pour OperationEnAttente (offline.py)."""
    
    def test_pending_operation_operation_types(self):
        """Test crÃ©ation avec diffÃ©rents types d'opÃ©ration."""
        from src.core.offline import OperationEnAttente, TypeOperation
        
        for op_type in [TypeOperation.CREATE, TypeOperation.UPDATE, TypeOperation.DELETE]:
            op = OperationEnAttente(
                operation_type=op_type,
                model_name="Test"
            )
            assert op.operation_type == op_type
    
    def test_pending_operation_to_dict_last_error_none(self):
        """Test to_dict avec last_error None."""
        from src.core.offline import OperationEnAttente
        
        op = OperationEnAttente(model_name="Recette", data={"nom": "Tarte"})
        d = op.to_dict()
        
        assert d["last_error"] is None
        assert d["model_name"] == "Recette"
        assert d["data"]["nom"] == "Tarte"
    
    def test_pending_operation_to_dict_with_error(self):
        """Test to_dict avec last_error dÃ©finie."""
        from src.core.offline import OperationEnAttente
        
        op = OperationEnAttente(
            model_name="Test",
            last_error="Connection timeout",
            retry_count=3
        )
        d = op.to_dict()
        
        assert d["last_error"] == "Connection timeout"
        assert d["retry_count"] == 3
    
    def test_pending_operation_from_dict_missing_created_at(self):
        """Test from_dict sans created_at."""
        from src.core.offline import OperationEnAttente
        
        data = {
            "id": "ABC123",
            "operation_type": "update",
            "model_name": "Test",
            "data": {},
            "retry_count": 0
            # created_at manquant - doit utiliser datetime.now()
        }
        
        op = OperationEnAttente.from_dict(data)
        assert isinstance(op.created_at, datetime)
    
    def test_pending_operation_from_dict_with_null_last_error(self):
        """Test from_dict avec last_error null."""
        from src.core.offline import OperationEnAttente
        
        data = {
            "id": "XYZ789",
            "operation_type": "delete",
            "model_name": "Item",
            "data": {"id": 1},
            "created_at": "2024-01-01T12:00:00",
            "retry_count": 2,
            "last_error": None
        }
        
        op = OperationEnAttente.from_dict(data)
        assert op.last_error is None
        assert op.id == "XYZ789"


class TestSQLAlchemyListenerStatic:
    """Tests pour les mÃ©thodes statiques de EcouteurSQLAlchemy."""
    
    def test_extract_operation_select(self):
        """Test extraction opÃ©ration SELECT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_operation("SELECT * FROM users")
        assert result == "SELECT"
    
    def test_extract_operation_insert(self):
        """Test extraction opÃ©ration INSERT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_operation("INSERT INTO users VALUES (1)")
        assert result == "INSERT"
    
    def test_extract_operation_update(self):
        """Test extraction opÃ©ration UPDATE."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_operation("UPDATE users SET name='test'")
        assert result == "UPDATE"
    
    def test_extract_operation_delete(self):
        """Test extraction opÃ©ration DELETE."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_operation("DELETE FROM users WHERE id=1")
        assert result == "DELETE"
    
    def test_extract_table_from_select(self):
        """Test extraction table depuis SELECT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_table("SELECT * FROM recettes WHERE id = 1")
        assert result == "recettes"
    
    def test_extract_table_from_insert(self):
        """Test extraction table depuis INSERT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy
        
        result = EcouteurSQLAlchemy._extract_table("INSERT INTO ingredients VALUES (1, 'test')")
        assert result == "ingredients"
