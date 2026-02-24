"""
conftest.py — Fixtures partagées pour les tests AppTest.

Fournit:
- Configuration Streamlit pour les tests
- Mocks de services (DB, IA, cache)
- Helpers de navigation et assertions
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Assurer le chemin imports
workspace_root = Path(__file__).parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Désactiver rate limiting + DB pour tests UI
os.environ["RATE_LIMITING_DISABLED"] = "true"
os.environ["TESTING"] = "true"


# ═══════════════════════════════════════════════════════════
# FIXTURES MOCK SERVICES
# ═══════════════════════════════════════════════════════════


@pytest.fixture()
def mock_db_context():
    """Mock le contexte DB pour éviter les connexions réelles."""
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []
    mock_session.query.return_value.first.return_value = None

    with patch("src.core.db.session.obtenir_contexte_db") as mock_ctx:
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_session


@pytest.fixture()
def mock_services():
    """Mock tous les service factories pour les tests UI."""
    mocks = {}

    service_patches = {
        "recettes": "src.services.cuisine.recettes.obtenir_service_recettes",
        "inventaire": "src.services.inventaire.obtenir_service_inventaire",
        "courses": "src.services.cuisine.courses.obtenir_service_courses",
        "planning": "src.services.cuisine.planning.obtenir_service_planning",
    }

    patches = {}
    for name, path in service_patches.items():
        mock = MagicMock()

        # Configurer les retours par défaut selon le service
        if name == "recettes":
            mock.get_stats.return_value = {"total": 42, "favorites": 10}
            mock.lister.return_value = []
        elif name == "inventaire":
            mock.get_stats.return_value = {"total": 85, "critique": 3}
            mock.get_inventaire_complet.return_value = []
        elif name == "courses":
            mock.get_stats.return_value = {"total": 12, "achetes": 5}
            mock.get_liste_active.return_value = []
        elif name == "planning":
            planning_mock = MagicMock()
            planning_mock.repas = []
            mock.get_planning.return_value = planning_mock

        mocks[name] = mock

        p = patch(path, return_value=mock)
        patches[name] = p
        p.start()

    yield mocks

    for p in patches.values():
        p.stop()


@pytest.fixture()
def mock_ia_client():
    """Mock le client IA Mistral."""
    mock = MagicMock()
    mock.generer.return_value = "Réponse IA simulée pour les tests."

    with patch("src.core.ai.client.ClientIA", return_value=mock):
        yield mock


# ═══════════════════════════════════════════════════════════
# HELPERS ASSERTIONS STREAMLIT
# ═══════════════════════════════════════════════════════════


class AppTestAssertions:
    """Helpers d'assertions pour les tests AppTest Streamlit."""

    @staticmethod
    def assert_no_exception(at):
        """Vérifie qu'aucune exception n'a été levée pendant le run."""
        if at.exception:
            raise AssertionError(
                f"Exception durant le rendu Streamlit:\n{at.exception}"
            )

    @staticmethod
    def assert_has_title(at, expected_text: str):
        """Vérifie qu'un titre contient le texte attendu."""
        titles = [t.value for t in at.title]
        assert any(
            expected_text in t for t in titles
        ), f"Titre '{expected_text}' non trouvé dans: {titles}"

    @staticmethod
    def assert_has_header(at, expected_text: str):
        """Vérifie qu'un header contient le texte attendu."""
        headers = [h.value for h in at.header]
        assert any(
            expected_text in h for h in headers
        ), f"Header '{expected_text}' non trouvé dans: {headers}"

    @staticmethod
    def assert_has_subheader(at, expected_text: str):
        """Vérifie qu'un subheader contient le texte attendu."""
        subheaders = [s.value for s in at.subheader]
        assert any(
            expected_text in s for s in subheaders
        ), f"Subheader '{expected_text}' non trouvé dans: {subheaders}"

    @staticmethod
    def assert_has_metric(at, label: str | None = None, value: str | None = None):
        """Vérifie qu'une métrique existe avec label/valeur optionnels."""
        metrics = at.metric
        assert len(metrics) > 0, "Aucune métrique trouvée"

        if label:
            labels = [m.label for m in metrics]
            assert any(
                label in lbl for lbl in labels
            ), f"Métrique label '{label}' non trouvée dans: {labels}"

    @staticmethod
    def assert_has_button(at, label: str):
        """Vérifie qu'un bouton avec ce label existe."""
        buttons = at.button
        labels = [b.label for b in buttons]
        assert any(
            label in lbl for lbl in labels
        ), f"Bouton '{label}' non trouvé dans: {labels}"

    @staticmethod
    def assert_has_tabs(at, count: int | None = None):
        """Vérifie la présence d'onglets."""
        tabs = at.tabs
        if count is not None:
            assert len(tabs) >= count, f"Attendu {count}+ onglets, trouvé {len(tabs)}"

    @staticmethod
    def assert_no_error(at):
        """Vérifie qu'aucun st.error() n'a été appelé."""
        errors = at.error
        assert len(errors) == 0, f"Erreurs trouvées: {[e.value for e in errors]}"

    @staticmethod
    def assert_has_warning(at, text: str | None = None):
        """Vérifie la présence d'un warning."""
        warnings_list = at.warning
        assert len(warnings_list) > 0, "Aucun warning trouvé"
        if text:
            values = [w.value for w in warnings_list]
            assert any(text in v for v in values), f"Warning '{text}' non trouvé"


@pytest.fixture()
def assertions():
    """Fournit les helpers d'assertions AppTest."""
    return AppTestAssertions()
