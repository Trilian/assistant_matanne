"""
UI Testing - Infrastructure de test pour composants UI.

Fournit des outils pour:
- Tests de régression visuelle (snapshots HTML et Playwright)
- Tests unitaires de composants
- Mocks Streamlit

Usage:
    from src.ui.testing import SnapshotTester, PlaywrightConfig
"""

from .playwright_config import (
    PlaywrightConfig,
    get_components_to_test,
    get_pages_to_test,
)
from .playwright_config import (
    config as playwright_config,
)
from .visual_regression import (
    ComponentSnapshot,
    SnapshotTester,
    assert_html_contains,
    assert_html_not_contains,
)

__all__ = [
    # Snapshots HTML
    "SnapshotTester",
    "ComponentSnapshot",
    "assert_html_contains",
    "assert_html_not_contains",
    # Playwright
    "PlaywrightConfig",
    "playwright_config",
    "get_pages_to_test",
    "get_components_to_test",
]
