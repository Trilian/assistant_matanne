"""
Classe de base pour les tests UI.

Fournit des méthodes utilitaires et setup/teardown standardisés
pour tester les composants Streamlit de manière cohérente.
"""

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from tests.fixtures.ui_mocks import (
    assert_error_shown,
    assert_metric_displayed,
    assert_streamlit_called,
    assert_success_shown,
    create_ui_test_context,
)


class BaseUITest:
    """
    Classe de base pour les tests de composants UI Streamlit.

    Usage:
        class TestRecettesUI(BaseUITest):
            domain = "cuisine"

            def test_render_liste(self):
                with self.mock_streamlit() as mock_st:
                    from src.modules.cuisine.recettes import render_liste
                    render_liste()
                    self.assert_called(mock_st, "title")
    """

    # À surcharger dans les sous-classes
    domain: str = None
    module_path: str = None  # e.g., "src.modules.cuisine.recettes"

    @pytest.fixture(autouse=True)
    def setup_ui_test(self):
        """Setup automatique pour chaque test."""
        self._patches = []
        yield
        # Cleanup
        for p in self._patches:
            try:
                p.stop()
            except RuntimeError:
                pass

    def get_mock_st(self, extra_state: dict[str, Any] = None) -> MagicMock:
        """
        Retourne un mock Streamlit configuré pour ce domaine.

        Args:
            extra_state: Données supplémentaires pour session_state
        """
        return create_ui_test_context(self.domain, extra_state)

    @contextmanager
    def mock_streamlit(self, session_state: dict[str, Any] = None):
        """
        Context manager pour mocker Streamlit.

        Args:
            session_state: Données initiales pour session_state

        Yields:
            MagicMock configuré comme Streamlit
        """
        mock_st = create_ui_test_context(self.domain, session_state)

        # Patch streamlit dans sys.modules
        with patch.dict("sys.modules", {"streamlit": mock_st}):
            yield mock_st

    @contextmanager
    def mock_module_streamlit(self, module_path: str = None, session_state: dict[str, Any] = None):
        """
        Context manager pour mocker Streamlit dans un module spécifique.

        Args:
            module_path: Chemin du module (défaut: self.module_path)
            session_state: Données pour session_state
        """
        path = module_path or self.module_path
        if not path:
            raise ValueError("module_path must be specified")

        mock_st = create_ui_test_context(self.domain, session_state)

        p = patch(f"{path}.st", mock_st)
        self._patches.append(p)
        p.start()

        try:
            yield mock_st
        finally:
            p.stop()
            self._patches.remove(p)

    @contextmanager
    def mock_database(self, return_data: Any = None):
        """
        Context manager pour mocker les appels à la base de données.

        Args:
            return_data: Données à retourner par les queries
        """
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = return_data or []
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter_by.return_value.all.return_value = return_data or []
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.query.return_value.all.return_value = return_data or []

        @contextmanager
        def mock_context():
            yield mock_db

        p1 = patch("src.core.database.obtenir_contexte_db", mock_context)
        p2 = patch("src.core.database.obtenir_contexte_db", mock_context)

        p1.start()
        p2.start()
        self._patches.extend([p1, p2])

        try:
            yield mock_db
        finally:
            p1.stop()
            p2.stop()
            self._patches.remove(p1)
            self._patches.remove(p2)

    @contextmanager
    def mock_ai_service(self, response: str = "Réponse IA mock"):
        """
        Context manager pour mocker les services IA.

        Args:
            response: Réponse à retourner par les appels IA
        """
        mock_client = MagicMock()
        mock_client.chat.complete.return_value.choices = [
            MagicMock(message=MagicMock(content=response))
        ]

        p = patch("src.core.ai.ClientIA", return_value=mock_client)
        self._patches.append(p)
        p.start()

        try:
            yield mock_client
        finally:
            p.stop()
            self._patches.remove(p)

    # === Assertion Helpers ===

    def assert_called(self, mock_st: MagicMock, method: str, times: int = None):
        """Vérifie qu'une méthode Streamlit a été appelée."""
        assert_streamlit_called(mock_st, method, times)

    def assert_metric(self, mock_st: MagicMock, label: str = None, value: Any = None):
        """Vérifie qu'un metric a été affiché."""
        assert_metric_displayed(mock_st, label, value)

    def assert_error(self, mock_st: MagicMock, contains: str = None):
        """Vérifie qu'une erreur a été affichée."""
        assert_error_shown(mock_st, contains)

    def assert_success(self, mock_st: MagicMock, contains: str = None):
        """Vérifie qu'un succès a été affiché."""
        assert_success_shown(mock_st, contains)

    def assert_not_called(self, mock_st: MagicMock, method: str):
        """Vérifie qu'une méthode n'a PAS été appelée."""
        method_mock = getattr(mock_st, method)
        assert not method_mock.called, f"Expected {method} to NOT be called"

    def assert_form_displayed(self, mock_st: MagicMock, form_key: str = None):
        """Vérifie qu'un formulaire a été affiché."""
        assert mock_st.form.called, "Expected st.form to be called"

        if form_key:
            calls = mock_st.form.call_args_list
            found = any(form_key in str(call) for call in calls)
            assert found, f"Expected form with key '{form_key}'"

    def assert_tabs_displayed(self, mock_st: MagicMock, count: int = None):
        """Vérifie que des tabs ont été affichés."""
        assert mock_st.tabs.called, "Expected st.tabs to be called"

        if count:
            call_args = mock_st.tabs.call_args
            if call_args:
                labels = call_args[0][0] if call_args[0] else call_args[1].get("labels", [])
                assert len(labels) == count, f"Expected {count} tabs, got {len(labels)}"

    # === Test Data Helpers ===

    def create_mock_model(self, model_class: type, **kwargs) -> MagicMock:
        """
        Crée un mock d'un modèle SQLAlchemy.

        Args:
            model_class: Classe du modèle
            **kwargs: Attributs à définir
        """
        mock = MagicMock(spec=model_class)
        for key, value in kwargs.items():
            setattr(mock, key, value)
        return mock


class BaseUITestWithDB(BaseUITest):
    """
    Extension de BaseUITest avec fixtures de base de données intégrées.

    Requiert la fixture `db` du conftest principal.
    """

    @pytest.fixture(autouse=True)
    def setup_db_test(self, db):
        """Setup avec session de test DB."""
        self.db = db
        yield

    @contextmanager
    def with_test_db(self):
        """Utilise la session de test DB."""

        @contextmanager
        def mock_context():
            yield self.db

        with patch("src.core.database.obtenir_contexte_db", mock_context):
            with patch("src.core.database.obtenir_contexte_db", mock_context):
                yield self.db
