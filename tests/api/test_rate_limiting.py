import pytest
from src.api import rate_limiting

@pytest.mark.unit
def test_import_rate_limiting():
    """Vérifie que le module rate_limiting s'importe sans erreur."""
    assert hasattr(rate_limiting, "RateLimiter") or hasattr(rate_limiting, "__file__")

# Ajoutez ici des tests de logique de limitation de débit, etc. selon le module

import time
from fastapi import Request
from src.api.rate_limiting import RateLimitStore, RateLimiter, rate_limit_config

@pytest.mark.unit
def test_increment_and_get_count():
    store = RateLimitStore()
    key = "test_key"
    window = 60
    assert store.get_count(key, window) == 0
    store.increment(key, window)
    assert store.get_count(key, window) == 1

@pytest.mark.unit
def test_get_remaining():
    store = RateLimitStore()
    key = "remaining_key"
    window = 60
    limit = 5
    for _ in range(3):
        store.increment(key, window)
    assert store.get_remaining(key, window, limit) == 2

@pytest.mark.unit
def test_block_and_is_blocked():
    store = RateLimitStore()
    key = "block_key"
    assert not store.is_blocked(key)
    store.block(key, 1)
    assert store.is_blocked(key)
    time.sleep(1.1)
    assert not store.is_blocked(key)

@pytest.mark.unit
def test_get_reset_time():
    store = RateLimitStore()
    key = "reset_key"
    window = 2
    store.increment(key, window)
    reset = store.get_reset_time(key, window)
    assert 0 <= reset <= window

@pytest.mark.unit
def test_rate_limiter_get_key():
    class DummyClient:
        host = "127.0.0.1"
    class DummyRequest:
        headers = {}
        client = DummyClient()
    limiter = RateLimiter()
    key = limiter._get_key(DummyRequest(), identifier="user1", endpoint="/test")
    assert "user:user1:endpoint:/test" in key
