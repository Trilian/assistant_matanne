"""
Tests pour performance.py - amÃ©lioration de la couverture

Cible:
- MetriquePerformance dataclass
- StatistiquesFonction dataclass
- ProfileurFonction class
- profile decorator
- measure_time context manager
- MoniteurMemoire class
- OptimiseurSQL class
"""

import time
from unittest.mock import patch

import pytest


class TestPerformanceMetric:
    """Tests pour MetriquePerformance dataclass."""

    def test_default_values(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.performance import MetriquePerformance

        metric = MetriquePerformance(name="test", duration_ms=50.0)

        assert metric.name == "test"
        assert metric.duration_ms == 50.0
        assert metric.memory_delta_kb == 0
        assert metric.metadata == {}
        assert metric.timestamp is not None

    def test_with_all_fields(self):
        """CrÃ©ation avec tous les champs."""
        from src.core.performance import MetriquePerformance

        metric = MetriquePerformance(
            name="complex_op",
            duration_ms=125.5,
            memory_delta_kb=1024,
            metadata={"table": "users"},
        )

        assert metric.memory_delta_kb == 1024
        assert metric.metadata == {"table": "users"}


class TestFunctionStats:
    """Tests pour StatistiquesFonction dataclass."""

    def test_default_values(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.performance import StatistiquesFonction

        stats = StatistiquesFonction()

        assert stats.call_count == 0
        assert stats.total_time_ms == 0
        assert stats.min_time_ms == float("inf")
        assert stats.max_time_ms == 0
        assert stats.avg_time_ms == 0
        assert stats.last_call is None
        assert stats.errors == 0


class TestFunctionProfiler:
    """Tests pour ProfileurFonction."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.performance.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_record_first_call(self, mock_streamlit):
        """record crÃ©e les stats pour nouvelle fonction."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("my_function", 50.0)

        stats = ProfileurFonction.get_all_stats()
        assert "my_function" in stats
        assert stats["my_function"].call_count == 1
        assert stats["my_function"].total_time_ms == 50.0

    def test_record_multiple_calls(self, mock_streamlit):
        """record accumule les stats."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("func", 10.0)
        ProfileurFonction.record("func", 20.0)
        ProfileurFonction.record("func", 30.0)

        stats = ProfileurFonction.get_all_stats()["func"]

        assert stats.call_count == 3
        assert stats.total_time_ms == 60.0
        assert stats.avg_time_ms == 20.0
        assert stats.min_time_ms == 10.0
        assert stats.max_time_ms == 30.0

    def test_record_with_error(self, mock_streamlit):
        """record compte les erreurs."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("func", 10.0, error=True)
        ProfileurFonction.record("func", 20.0, error=False)

        stats = ProfileurFonction.get_all_stats()["func"]
        assert stats.errors == 1

    def test_get_slowest(self, mock_streamlit):
        """get_slowest retourne les plus lentes."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("fast", 10.0)
        ProfileurFonction.record("medium", 50.0)
        ProfileurFonction.record("slow", 100.0)

        slowest = ProfileurFonction.get_slowest(n=2)

        assert len(slowest) == 2
        assert slowest[0][0] == "slow"
        assert slowest[1][0] == "medium"

    def test_get_most_called(self, mock_streamlit):
        """get_most_called retourne les plus appelÃ©es."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("rare", 10.0)
        for _ in range(5):
            ProfileurFonction.record("common", 10.0)
        for _ in range(10):
            ProfileurFonction.record("very_common", 10.0)

        most_called = ProfileurFonction.get_most_called(n=2)

        assert len(most_called) == 2
        assert most_called[0][0] == "very_common"
        assert most_called[1][0] == "common"

    def test_clear(self, mock_streamlit):
        """clear rÃ©initialise les stats."""
        from src.core.performance import ProfileurFonction

        ProfileurFonction.record("func", 10.0)
        ProfileurFonction.clear()

        stats = ProfileurFonction.get_all_stats()
        assert stats == {}


class TestProfileDecorator:
    """Tests pour le dÃ©corateur @profile."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.performance.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_profile_records_execution(self, mock_streamlit):
        """@profile enregistre l'exÃ©cution."""
        from src.core.performance import ProfileurFonction, profile

        @profile
        def my_func():
            return "result"

        result = my_func()

        assert result == "result"
        stats = ProfileurFonction.get_all_stats()
        # Le nom contient le module et la fonction
        assert any("my_func" in k for k in stats.keys())

    def test_profile_with_custom_name(self, mock_streamlit):
        """@profile avec nom personnalisÃ©."""
        from src.core.performance import ProfileurFonction, profile

        @profile(name="custom_name")
        def some_func():
            return 42

        some_func()

        stats = ProfileurFonction.get_all_stats()
        assert "custom_name" in stats

    def test_profile_records_errors(self, mock_streamlit):
        """@profile enregistre les erreurs."""
        from src.core.performance import ProfileurFonction, profile

        @profile(name="error_func")
        def failing_func():
            raise ValueError("Error!")

        with pytest.raises(ValueError):
            failing_func()

        stats = ProfileurFonction.get_all_stats()["error_func"]
        assert stats.errors == 1


class TestMeasureTimeContextManager:
    """Tests pour measure_time context manager."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.performance.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_measure_time_records(self, mock_streamlit):
        """measure_time enregistre le temps."""
        from src.core.performance import ProfileurFonction, measure_time

        with measure_time("test_block"):
            time.sleep(0.01)  # 10ms

        stats = ProfileurFonction.get_all_stats()
        assert "test_block" in stats
        assert stats["test_block"].total_time_ms >= 10

    def test_measure_time_records_errors(self, mock_streamlit):
        """measure_time enregistre les erreurs."""
        from src.core.performance import ProfileurFonction, measure_time

        with pytest.raises(RuntimeError):
            with measure_time("error_block"):
                raise RuntimeError("Test error")

        stats = ProfileurFonction.get_all_stats()
        assert stats["error_block"].errors == 1


class TestMemoryMonitor:
    """Tests pour MoniteurMemoire."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.performance.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_start_tracking(self, mock_streamlit):
        """start_tracking dÃ©marre tracemalloc."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = False

        with patch("src.core.performance.tracemalloc") as mock_trace:
            MoniteurMemoire.start_tracking()

            mock_trace.start.assert_called_once()
            assert MoniteurMemoire._tracking_active is True

    def test_start_tracking_already_active(self, mock_streamlit):
        """start_tracking ne redÃ©marre pas si dÃ©jÃ  actif."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = True

        with patch("src.core.performance.tracemalloc") as mock_trace:
            MoniteurMemoire.start_tracking()

            mock_trace.start.assert_not_called()

    def test_stop_tracking(self, mock_streamlit):
        """stop_tracking arrÃªte tracemalloc."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = True

        with patch("src.core.performance.tracemalloc") as mock_trace:
            MoniteurMemoire.stop_tracking()

            mock_trace.stop.assert_called_once()
            assert MoniteurMemoire._tracking_active is False

    def test_get_current_usage(self, mock_streamlit):
        """get_current_usage retourne les infos mÃ©moire."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = False

        usage = MoniteurMemoire.get_current_usage()

        assert "current_mb" in usage
        assert "peak_mb" in usage
        assert "total_objects" in usage
        assert "top_types" in usage

    def test_get_current_usage_with_tracking(self, mock_streamlit):
        """get_current_usage avec tracking actif."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = True

        with patch("src.core.performance.tracemalloc") as mock_trace:
            mock_trace.get_traced_memory.return_value = (1024 * 1024, 2 * 1024 * 1024)

            usage = MoniteurMemoire.get_current_usage()

            assert usage["current_mb"] == 1.0
            assert usage["peak_mb"] == 2.0

    def test_take_snapshot(self, mock_streamlit):
        """take_snapshot prend un snapshot."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = False

        snapshot = MoniteurMemoire.take_snapshot(label="test_snap")

        assert snapshot["label"] == "test_snap"
        assert "timestamp" in snapshot

        snapshots = MoniteurMemoire.get_snapshots()
        assert len(snapshots) == 1

    def test_take_snapshot_limits_count(self, mock_streamlit):
        """take_snapshot garde seulement 20 derniers."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = False

        for i in range(25):
            MoniteurMemoire.take_snapshot(label=f"snap_{i}")

        snapshots = MoniteurMemoire.get_snapshots()
        assert len(snapshots) <= 20

    def test_force_cleanup(self, mock_streamlit):
        """force_cleanup dÃ©clenche gc."""
        from src.core.performance import MoniteurMemoire

        MoniteurMemoire._tracking_active = False

        with patch("src.core.performance.gc") as mock_gc:
            mock_gc.collect.return_value = 100
            mock_gc.get_objects.return_value = []

            result = MoniteurMemoire.force_cleanup()

            mock_gc.collect.assert_called_once()
            assert result["objects_collected"] == 100


class TestSQLOptimizer:
    """Tests pour OptimiseurSQL."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.performance.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_get_stats_empty(self, mock_streamlit):
        """_get_stats retourne structure vide par dÃ©faut."""
        from src.core.performance import OptimiseurSQL

        stats = OptimiseurSQL._get_stats()

        assert "queries" in stats
        assert "slow_queries" in stats
        assert "total_count" in stats
        assert stats["total_count"] == 0
