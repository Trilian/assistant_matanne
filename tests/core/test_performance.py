"""
Tests pour src/core/performance.py
Couvre :
- MetriquePerformance
- StatistiquesFonction
"""
import pytest
from datetime import datetime
from src.core.performance import MetriquePerformance, StatistiquesFonction

def test_performance_metric_fields():
    m = MetriquePerformance(name="test", duration_ms=123.4, memory_delta_kb=10)
    assert m.name == "test"
    assert m.duration_ms == 123.4
    assert isinstance(m.timestamp, datetime)
    assert m.memory_delta_kb == 10
    assert isinstance(m.metadata, dict)

def test_function_stats_fields():
    s = StatistiquesFonction(call_count=5, total_time_ms=100, min_time_ms=10, max_time_ms=50, avg_time_ms=20)
    assert s.call_count == 5
    assert s.total_time_ms == 100
    assert s.min_time_ms == 10
    assert s.max_time_ms == 50
    assert s.avg_time_ms == 20
    assert s.errors == 0 or isinstance(s.errors, int)
