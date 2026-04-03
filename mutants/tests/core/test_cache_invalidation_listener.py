"""Tests du listener d'invalidation cache PostgreSQL."""

from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from src.core.caching.base import EntreeCache
from src.core.caching.file import CacheFichierN3
from src.core.caching import invalidation_listener


class _FakeCache:
    def __init__(self):
        self.patterns: list[str] = []
        self.clear_levels: list[str] = []

    def invalidate(self, pattern: str | None = None):
        if pattern:
            self.patterns.append(pattern)
            return 1
        return 0

    def clear(self, levels: str = "all"):
        self.clear_levels.append(levels)


def test_traiter_notification_invalide_patterns_et_l3(monkeypatch: MonkeyPatch):
    """Le handler invalide les patterns attendus puis purge L3."""
    fake_cache = _FakeCache()
    monkeypatch.setattr(invalidation_listener, "obtenir_cache", lambda: fake_cache)

    invalidation_listener.traiter_notification_cache("user-123")

    assert fake_cache.patterns == [
        "planning_",
        "planning_full_",
        "semaine_complete_",
        "semaine_ia_",
        "batch_",
    ]
    # L3 clear was removed — pattern invalidation is sufficient
    assert fake_cache.clear_levels == []


def test_extraire_payload_notification_objet():
    """Compatibilité payload psycopg2: notif.payload."""

    class _Notification:
        payload = "abc"

    assert invalidation_listener.extraire_payload_notification(_Notification()) == "abc"
    assert invalidation_listener.extraire_payload_notification(42) == "42"


def test_cache_fichier_invalidation_pattern(tmp_path: Path):
    """Le cache fichier supprime bien les clés matchant un pattern."""
    cache = CacheFichierN3(cache_dir=str(tmp_path))
    cache.set("planning_123", EntreeCache(value={"ok": True}, ttl=300))
    cache.set("autre_456", EntreeCache(value={"ok": True}, ttl=300))

    nb = cache.invalidate(pattern="planning_")

    assert nb == 1
    assert cache.get("planning_123") is None
    assert cache.get("autre_456") is not None
