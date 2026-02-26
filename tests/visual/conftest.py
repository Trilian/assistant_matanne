"""
Configuration pytest pour les tests visuels Playwright.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip si Playwright n'est pas installé
try:
    from playwright.sync_api import sync_playwright

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def pytest_configure(config: pytest.Config) -> None:
    """Ajoute les markers pour les tests visuels."""
    config.addinivalue_line("markers", "visual: Tests de régression visuelle")
    config.addinivalue_line("markers", "a11y: Tests d'accessibilité")


@pytest.fixture(scope="session")
def browser_type():
    """Type de navigateur à utiliser."""
    return "chromium"


@pytest.fixture(scope="session")
def browser_context_args():
    """Arguments pour le contexte du navigateur."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url():
    """URL de base pour les tests."""
    return "http://localhost:8501"


@pytest.fixture(scope="session")
def _playwright_browser():
    """Lance une instance de navigateur Playwright pour la session de tests."""
    if not HAS_PLAYWRIGHT:
        pytest.skip("Playwright non installé")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(_playwright_browser):
    """Fournit une page Playwright fraîche pour chaque test.

    La page est fermée automatiquement à la fin du test.
    """
    context = _playwright_browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
    )
    _page = context.new_page()
    yield _page
    _page.close()
    context.close()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip les tests visuels si Playwright n'est pas installé."""
    if not HAS_PLAYWRIGHT:
        skip_playwright = pytest.mark.skip(reason="Playwright non installé")
        for item in items:
            if "visual" in item.keywords or "a11y" in item.keywords:
                item.add_marker(skip_playwright)
