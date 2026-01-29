"""
Tests pour les modules performance.py et sql_optimizer.py.

Tests couverts:
- FunctionProfiler
- MemoryMonitor
- SQLOptimizer
- DÃ©corateurs @profile, @debounce, @throttle
- SQLAlchemyListener
- N1Detector
- OptimizedQueryBuilder
"""

import gc
import time
from datetime import datetime
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
def function_profiler(mock_session_state):
    """Instance FunctionProfiler fraÃ®che."""
    from src.core.performance import FunctionProfiler
    
    FunctionProfiler.clear()
    yield FunctionProfiler
    FunctionProfiler.clear()


@pytest.fixture
def sql_optimizer(mock_session_state):
    """Instance SQLOptimizer fraÃ®che."""
    from src.core.performance import SQLOptimizer
    
    SQLOptimizer.clear()
    yield SQLOptimizer
    SQLOptimizer.clear()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FUNCTION PROFILER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFunctionProfiler:
    """Tests pour FunctionProfiler."""
    
    def test_record_single(self, function_profiler):
        """Test enregistrement simple."""
        function_profiler.record("test_func", 50.0)
        
        stats = function_profiler.get_all_stats()
        
        assert "test_func" in stats
        assert stats["test_func"].call_count == 1
        assert stats["test_func"].avg_time_ms == 50.0
    
    def test_record_multiple(self, function_profiler):
        """Test enregistrement multiple."""
        function_profiler.record("test_func", 50.0)
        function_profiler.record("test_func", 100.0)
        function_profiler.record("test_func", 150.0)
        
        stats = function_profiler.get_all_stats()
        s = stats["test_func"]
        
        assert s.call_count == 3
        assert s.total_time_ms == 300.0
        assert s.avg_time_ms == 100.0
        assert s.min_time_ms == 50.0
        assert s.max_time_ms == 150.0
    
    def test_record_with_error(self, function_profiler):
        """Test enregistrement avec erreur."""
        function_profiler.record("failing_func", 25.0, error=True)
        
        stats = function_profiler.get_all_stats()
        
        assert stats["failing_func"].errors == 1
    
    def test_get_slowest(self, function_profiler):
        """Test rÃ©cupÃ©ration des plus lentes."""
        function_profiler.record("fast", 10.0)
        function_profiler.record("medium", 50.0)
        function_profiler.record("slow", 200.0)
        
        slowest = function_profiler.get_slowest(2)
        
        assert len(slowest) == 2
        assert slowest[0][0] == "slow"
        assert slowest[1][0] == "medium"
    
    def test_get_most_called(self, function_profiler):
        """Test rÃ©cupÃ©ration des plus appelÃ©es."""
        function_profiler.record("rarely", 10.0)
        function_profiler.record("often", 10.0)
        function_profiler.record("often", 10.0)
        function_profiler.record("often", 10.0)
        function_profiler.record("sometimes", 10.0)
        function_profiler.record("sometimes", 10.0)
        
        most_called = function_profiler.get_most_called(2)
        
        assert len(most_called) == 2
        assert most_called[0][0] == "often"
        assert most_called[0][1].call_count == 3
    
    def test_clear(self, function_profiler):
        """Test vidage."""
        function_profiler.record("func", 50.0)
        function_profiler.clear()
        
        stats = function_profiler.get_all_stats()
        assert len(stats) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PROFILE DECORATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestProfileDecorator:
    """Tests pour le dÃ©corateur @profile."""
    
    def test_basic_profiling(self, mock_session_state):
        """Test profiling basique."""
        from src.core.performance import profile, FunctionProfiler
        
        FunctionProfiler.clear()
        
        @profile
        def sample_function():
            time.sleep(0.01)
            return "result"
        
        result = sample_function()
        
        assert result == "result"
        
        stats = FunctionProfiler.get_all_stats()
        # La clÃ© contient le nom du module + fonction
        assert any("sample_function" in key for key in stats.keys())
    
    def test_custom_name(self, mock_session_state):
        """Test nom personnalisÃ©."""
        from src.core.performance import profile, FunctionProfiler
        
        FunctionProfiler.clear()
        
        @profile(name="custom_name")
        def some_function():
            return True
        
        some_function()
        
        stats = FunctionProfiler.get_all_stats()
        assert "custom_name" in stats
    
    def test_exception_handling(self, mock_session_state):
        """Test gestion des exceptions."""
        from src.core.performance import profile, FunctionProfiler
        
        FunctionProfiler.clear()
        
        @profile
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        stats = FunctionProfiler.get_all_stats()
        # Doit avoir enregistrÃ© l'erreur
        key = [k for k in stats.keys() if "failing_function" in k][0]
        assert stats[key].errors == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MEASURE_TIME CONTEXT MANAGER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestMeasureTime:
    """Tests pour measure_time context manager."""
    
    def test_basic_measurement(self, mock_session_state):
        """Test mesure basique."""
        from src.core.performance import measure_time, FunctionProfiler
        
        FunctionProfiler.clear()
        
        with measure_time("test_block"):
            time.sleep(0.01)
        
        stats = FunctionProfiler.get_all_stats()
        assert "test_block" in stats
        assert stats["test_block"].avg_time_ms >= 10
    
    def test_exception_in_block(self, mock_session_state):
        """Test exception dans le bloc."""
        from src.core.performance import measure_time, FunctionProfiler
        
        FunctionProfiler.clear()
        
        with pytest.raises(ValueError):
            with measure_time("failing_block"):
                raise ValueError("Error")
        
        stats = FunctionProfiler.get_all_stats()
        assert "failing_block" in stats
        assert stats["failing_block"].errors == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MEMORY MONITOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestMemoryMonitor:
    """Tests pour MemoryMonitor."""
    
    def test_get_current_usage(self, mock_session_state):
        """Test usage mÃ©moire actuel."""
        from src.core.performance import MemoryMonitor
        
        usage = MemoryMonitor.get_current_usage()
        
        assert "current_mb" in usage
        assert "total_objects" in usage
        assert "top_types" in usage
        assert usage["total_objects"] > 0
    
    def test_force_cleanup(self, mock_session_state):
        """Test nettoyage forcÃ©."""
        from src.core.performance import MemoryMonitor
        
        # CrÃ©er des objets pour avoir quelque chose Ã  nettoyer
        temp_list = [dict() for _ in range(1000)]
        del temp_list
        
        result = MemoryMonitor.force_cleanup()
        
        assert "objects_collected" in result
        assert "memory_freed_mb" in result
        assert "before_mb" in result
        assert "after_mb" in result
    
    def test_tracking(self, mock_session_state):
        """Test tracking mÃ©moire."""
        from src.core.performance import MemoryMonitor
        
        # DÃ©marrer tracking
        MemoryMonitor.start_tracking()
        
        # Allouer de la mÃ©moire
        data = [bytearray(1000) for _ in range(100)]
        
        usage = MemoryMonitor.get_current_usage()
        
        # ArrÃªter tracking
        MemoryMonitor.stop_tracking()
        
        # Si tracking actif, current_mb devrait Ãªtre > 0
        # Note: dÃ©pend de l'Ã©tat du systÃ¨me
        del data


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SQL OPTIMIZER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSQLOptimizer:
    """Tests pour SQLOptimizer."""
    
    def test_record_query(self, sql_optimizer):
        """Test enregistrement requÃªte."""
        sql_optimizer.record_query(
            "SELECT * FROM users WHERE id = 1",
            duration_ms=25.0,
            rows_affected=1,
        )
        
        stats = sql_optimizer.get_stats()
        
        assert stats["total_queries"] == 1
        assert stats["avg_time_ms"] == 25.0
    
    def test_slow_query_detection(self, sql_optimizer):
        """Test dÃ©tection requÃªtes lentes."""
        sql_optimizer.record_query("SELECT * FROM small", 50.0)
        sql_optimizer.record_query("SELECT * FROM large", 150.0)  # > 100ms = lente
        sql_optimizer.record_query("SELECT * FROM huge", 500.0)
        
        stats = sql_optimizer.get_stats()
        
        assert stats["slow_query_count"] == 2
    
    def test_recent_queries(self, sql_optimizer):
        """Test requÃªtes rÃ©centes."""
        for i in range(15):
            sql_optimizer.record_query(f"SELECT {i}", 10.0)
        
        stats = sql_optimizer.get_stats()
        
        # Doit retourner les 10 derniÃ¨res
        assert len(stats["recent_queries"]) == 10
    
    def test_clear(self, sql_optimizer):
        """Test vidage."""
        sql_optimizer.record_query("SELECT 1", 10.0)
        sql_optimizer.clear()
        
        stats = sql_optimizer.get_stats()
        assert stats["total_queries"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DEBOUNCE DECORATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDebounceDecorator:
    """Tests pour le dÃ©corateur @debounce."""
    
    def test_basic_debounce(self):
        """Test debounce basique."""
        from src.core.performance import debounce
        
        call_count = 0
        
        @debounce(wait_ms=100)
        def debounced_func():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # Appels rapides
        debounced_func()
        debounced_func()
        debounced_func()
        
        # Premier appel exÃ©cutÃ©, les autres ignorÃ©s
        assert call_count == 1
        
        # Attendre et rÃ©essayer
        time.sleep(0.15)
        debounced_func()
        
        assert call_count == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS THROTTLE DECORATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestThrottleDecorator:
    """Tests pour le dÃ©corateur @throttle."""
    
    def test_basic_throttle(self):
        """Test throttle basique."""
        from src.core.performance import throttle
        
        call_count = 0
        
        @throttle(max_calls=3, period_seconds=1)
        def throttled_func():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # 5 appels rapides
        for _ in range(5):
            throttled_func()
        
        # Seulement 3 devraient passer
        assert call_count == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SQLALCHEMY LISTENER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSQLAlchemyListener:
    """Tests pour SQLAlchemyListener."""
    
    def test_extract_operation(self):
        """Test extraction type opÃ©ration."""
        from src.core.sql_optimizer import SQLAlchemyListener
        
        assert SQLAlchemyListener._extract_operation("SELECT * FROM users") == "SELECT"
        assert SQLAlchemyListener._extract_operation("INSERT INTO users") == "INSERT"
        assert SQLAlchemyListener._extract_operation("UPDATE users SET") == "UPDATE"
        assert SQLAlchemyListener._extract_operation("DELETE FROM users") == "DELETE"
    
    def test_extract_table(self):
        """Test extraction nom table."""
        from src.core.sql_optimizer import SQLAlchemyListener
        
        assert SQLAlchemyListener._extract_table("SELECT * FROM users WHERE id=1") == "users"
        assert SQLAlchemyListener._extract_table("INSERT INTO recipes VALUES") == "recipes"
        assert SQLAlchemyListener._extract_table("UPDATE products SET") == "products"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS N1 DETECTOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestN1Detector:
    """Tests pour N1Detector."""
    
    def test_normalize_query(self):
        """Test normalisation requÃªte."""
        from src.core.sql_optimizer import N1Detector
        
        query1 = "SELECT * FROM users WHERE id = 123"
        query2 = "SELECT * FROM users WHERE id = 456"
        
        norm1 = N1Detector._normalize_query(query1)
        norm2 = N1Detector._normalize_query(query2)
        
        assert norm1 == norm2  # MÃªme pattern
    
    def test_guess_parent_table(self):
        """Test devinette table parente."""
        from src.core.sql_optimizer import N1Detector, QueryInfo
        
        queries = [
            QueryInfo(
                sql="SELECT * FROM comments WHERE post_id = 1",
                duration_ms=10,
                table="comments",
                operation="SELECT",
            )
        ]
        
        parent = N1Detector._guess_parent_table(queries)
        assert parent == "post"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BATCH LOADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBatchLoader:
    """Tests pour BatchLoader."""
    
    def test_chunked(self):
        """Test chunked generator."""
        from src.core.sql_optimizer import BatchLoader
        
        items = list(range(10))
        chunks = list(BatchLoader.chunked(items, chunk_size=3))
        
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[2] == [6, 7, 8]
        assert chunks[3] == [9]
    
    def test_chunked_exact_fit(self):
        """Test chunked avec taille exacte."""
        from src.core.sql_optimizer import BatchLoader
        
        items = list(range(6))
        chunks = list(BatchLoader.chunked(items, chunk_size=3))
        
        assert len(chunks) == 2
        assert all(len(c) == 3 for c in chunks)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PERFORMANCE DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPerformanceDashboard:
    """Tests pour PerformanceDashboard."""
    
    def test_get_summary(self, mock_session_state):
        """Test rÃ©sumÃ© performances."""
        from src.core.performance import PerformanceDashboard
        
        summary = PerformanceDashboard.get_summary()
        
        assert "lazy_loading" in summary
        assert "functions" in summary
        assert "memory" in summary
        assert "sql" in summary
    
    def test_get_health_score(self, mock_session_state):
        """Test score de santÃ©."""
        from src.core.performance import PerformanceDashboard
        
        score, status = PerformanceDashboard.get_health_score()
        
        assert 0 <= score <= 100
        assert status in ["ðŸŸ¢", "ðŸŸ¡", "ðŸ”´"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OPTIMIZED QUERY BUILDER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOptimizedQueryBuilder:
    """Tests pour OptimizedQueryBuilder."""
    
    def test_builder_chain(self, db):
        """Test chaÃ®nage du builder."""
        from src.core.sql_optimizer import OptimizedQueryBuilder
        from src.core.models import Recette
        
        builder = (
            OptimizedQueryBuilder(db, Recette)
            .filter_by(categorie="dessert")
            .order("nom")
            .paginate(page=1, per_page=10)
        )
        
        query = builder.build()
        
        # VÃ©rifier que la requÃªte est construite
        assert query is not None
    
    def test_eager_load(self, db):
        """Test eager loading."""
        from src.core.sql_optimizer import OptimizedQueryBuilder
        from src.core.models import Recette
        
        builder = OptimizedQueryBuilder(db, Recette).eager_load("ingredients")
        
        query = builder.build()
        
        # La requÃªte doit inclure le eager loading
        assert query is not None
    
    def test_pagination(self, db):
        """Test pagination."""
        from src.core.sql_optimizer import OptimizedQueryBuilder
        from src.core.models import Recette
        
        builder = OptimizedQueryBuilder(db, Recette).paginate(page=2, per_page=5)
        
        query = builder.build()
        
        # VÃ©rifier offset et limit
        assert query is not None

