"""Fixtures pour tests batch cooking."""

from contextlib import contextmanager
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def patched_db_context(test_db):
    """Patch obtenir_contexte_db + cache + bus pour isoler les tests batch cooking.

    Le ServiceBatchCooking utilise :
    - obtenir_contexte_db (via @avec_session_db dans get_config, etc.)
    - obtenir_cache (via @avec_cache et invalidation directe)
    - obtenir_bus (émission d'événements domaine)
    """

    @contextmanager
    def mock_context():
        yield test_db

    mock_cache = Mock()
    mock_cache.get.side_effect = lambda key, default=None: default
    mock_cache.invalidate.return_value = None

    mock_bus = Mock()
    mock_bus.emettre.return_value = None

    with (
        patch("src.core.db.obtenir_contexte_db", mock_context),
        patch(
            "src.services.cuisine.batch_cooking.service.obtenir_cache",
            return_value=mock_cache,
        ),
        patch(
            "src.services.cuisine.batch_cooking.service.obtenir_bus",
            return_value=mock_bus,
        ),
        patch(
            "src.core.caching.obtenir_cache",
            return_value=mock_cache,
        ),
    ):
        yield test_db
