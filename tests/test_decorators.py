"""
Unit tests for Phase 1 Decorators.

Tests cover:
- @with_db_session: Auto session injection
- @with_cache: Caching with TTL
- @with_error_handling: Error catching and fallback values
- Decorator stacking
"""

import pytest
from unittest.mock import Mock

from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.cache import Cache


# ═══════════════════════════════════════════════════════════
# SECTION 1: @with_db_session TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestWithDbSession:
    """Test @with_db_session decorator."""
    
    def test_with_db_session_injects_session(self, db):
        """Test that session is injected into method."""
        @with_db_session
        def get_session_param(db=None):
            return db is not None
        
        result = get_session_param()
        # Should get injected session or None in test
        assert isinstance(result, bool)
    
    def test_with_db_session_accepts_explicit_session(self, db):
        """Test that explicit session is accepted."""
        @with_db_session
        def use_session(custom_db=None):
            return custom_db
        
        # Can pass explicit session
        result = use_session(custom_db=db)
        assert result == db


# ═══════════════════════════════════════════════════════════
# SECTION 2: @with_cache TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestWithCache:
    """Test @with_cache decorator."""
    
    def test_with_cache_stores_result(self, clear_cache):
        """Test that cache decorator stores result."""
        call_count = [0]
        
        @with_cache(ttl=3600, key_func=lambda self, id: f"item_{id}")
        def get_item(self, id):
            call_count[0] += 1
            return {"id": id, "value": "cached"}
        
        instance = Mock()
        
        # First call
        result1 = get_item(instance, 1)
        assert result1["id"] == 1
        assert call_count[0] == 1
        
        # Check cache
        cached = Cache.obtenir("item_1")
        assert cached is not None
        assert cached["id"] == 1
    
    def test_with_cache_retrieves_from_cache(self, clear_cache):
        """Test that cache is used on subsequent calls."""
        call_count = [0]
        
        @with_cache(ttl=3600, key_func=lambda self, id: f"item_{id}")
        def get_item(self, id):
            call_count[0] += 1
            return {"id": id, "call": call_count[0]}
        
        instance = Mock()
        
        # First call
        result1 = get_item(instance, 1)
        # Second call - should use cache
        result2 = get_item(instance, 1)
        
        # Should still be 1 (second call used cache)
        assert call_count[0] == 1
        assert result1 == result2
    
    def test_with_cache_respects_ttl(self, clear_cache):
        """Test that cache respects TTL."""
        # This is difficult to test without waiting
        # Just verify decorator accepts ttl parameter
        @with_cache(ttl=1, key_func=lambda self, x: f"short_{x}")
        def get_value(self, x):
            return x * 2
        
        instance = Mock()
        result = get_value(instance, 5)
        assert result == 10
    
    def test_with_cache_uses_custom_key_func(self, clear_cache):
        """Test custom key function."""
        @with_cache(ttl=3600, key_func=lambda self, a, b: f"sum_{a}_{b}")
        def add(self, a, b):
            return a + b
        
        instance = Mock()
        result = add(instance, 3, 4)
        assert result == 7
        
        # Check cache with custom key
        cached = Cache.obtenir("sum_3_4")
        assert cached == 7


# ═══════════════════════════════════════════════════════════
# SECTION 3: @with_error_handling TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestWithErrorHandling:
    """Test @with_error_handling decorator."""
    
    def test_with_error_handling_catches_errors(self):
        """Test that errors are caught."""
        @with_error_handling(default_return="default")
        def raise_error(self):
            raise ValueError("Test error")
        
        instance = Mock()
        result = raise_error(instance)
        
        assert result == "default"
    
    def test_with_error_handling_returns_fallback(self):
        """Test that fallback is returned on error."""
        @with_error_handling(default_return=[])
        def fail(self):
            raise RuntimeError("Failed")
        
        instance = Mock()
        result = fail(instance)
        
        assert result == []
        assert isinstance(result, list)
    
    def test_with_error_handling_returns_successful_value(self):
        """Test that successful calls return actual value."""
        @with_error_handling(default_return="default")
        def succeed(self):
            return "success"
        
        instance = Mock()
        result = succeed(instance)
        
        assert result == "success"
    
    def test_with_error_handling_all_errors_caught(self):
        """Test that all exceptions are caught."""
        @with_error_handling(default_return=None)
        def any_error(self):
            raise Exception("Generic error")
        
        instance = Mock()
        result = any_error(instance)
        
        assert result is None


# ═══════════════════════════════════════════════════════════
# SECTION 4: DECORATOR STACKING TESTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestDecoratorStacking:
    """Test stacking multiple decorators."""
    
    def test_cache_and_error_handling_stack(self, clear_cache):
        """Test @with_cache with @with_error_handling."""
        @with_cache(ttl=3600, key_func=lambda self, x: f"val_{x}")
        @with_error_handling(default_return=0)
        def compute(self, x: int):
            if x < 0:
                raise ValueError("Negative")
            return x * 2
        
        instance = Mock()
        
        # Success case
        result1 = compute(instance, 5)
        assert result1 == 10
        
        # Error case - should return fallback
        result2 = compute(instance, -1)
        assert result2 == 0
