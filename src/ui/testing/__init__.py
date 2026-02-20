"""
UI Testing - Infrastructure de test pour composants UI.

Fournit des outils pour:
- Tests de régression visuelle (snapshots)
- Tests unitaires de composants
- Mocks Streamlit

Usage:
    from src.ui.testing import SnapshotTester, mock_streamlit_context
"""

from .visual_regression import (
    ComponentSnapshot,
    SnapshotTester,
    assert_html_contains,
    assert_html_not_contains,
)

__all__ = [
    "SnapshotTester",
    "ComponentSnapshot",
    "assert_html_contains",
    "assert_html_not_contains",
]
