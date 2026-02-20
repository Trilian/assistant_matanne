"""Tests pour error_boundary du framework."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_streamlit():
    """Fixture pour mocker les composants Streamlit."""
    with (
        patch("streamlit.container") as mock_container,
        patch("streamlit.error") as mock_error,
        patch("streamlit.warning") as mock_warning,
        patch("streamlit.markdown") as mock_markdown,
        patch("streamlit.columns") as mock_columns,
        patch("streamlit.button") as mock_button,
        patch("streamlit.caption") as mock_caption,
        patch("streamlit.expander") as mock_expander,
        patch("streamlit.code") as mock_code,
        patch("streamlit.json") as mock_json,
        patch("streamlit.rerun") as mock_rerun,
    ):
        # Configure mocks
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        mock_columns.return_value = [MagicMock(), MagicMock()]
        mock_button.return_value = False

        yield {
            "container": mock_container,
            "error": mock_error,
            "warning": mock_warning,
            "markdown": mock_markdown,
            "columns": mock_columns,
            "button": mock_button,
            "caption": mock_caption,
            "expander": mock_expander,
            "code": mock_code,
            "json": mock_json,
            "rerun": mock_rerun,
        }


class TestErrorBoundary:
    """Tests pour le context manager error_boundary."""

    def test_no_error_passes_through(self, mock_streamlit):
        """Teste que le code sans erreur s'exécute normalement."""
        from src.modules._framework.error_boundary import error_boundary

        result = None
        with error_boundary("Test"):
            result = 42

        assert result == 42
        mock_streamlit["error"].assert_not_called()

    def test_catches_exception(self, mock_streamlit):
        """Teste la capture d'exception."""
        from src.modules._framework.error_boundary import error_boundary

        # Ne doit pas lever d'exception
        with error_boundary("Test"):
            raise ValueError("test error")

        # error() doit avoir été appelé
        mock_streamlit["error"].assert_called()

    def test_fallback_ui_called(self, mock_streamlit):
        """Teste l'appel du fallback_ui."""
        from src.modules._framework.error_boundary import error_boundary

        fallback = MagicMock()

        with error_boundary("Test", fallback_ui=fallback):
            raise ValueError("test")

        fallback.assert_called_once()

    def test_warning_level(self, mock_streamlit):
        """Teste le niveau warning."""
        from src.modules._framework.error_boundary import error_boundary

        with error_boundary("Test", niveau="warning"):
            raise ValueError("test")

        mock_streamlit["warning"].assert_called()
        mock_streamlit["error"].assert_not_called()

    def test_reraise_option(self, mock_streamlit):
        """Teste l'option reraise."""
        from src.modules._framework.error_boundary import error_boundary

        with pytest.raises(ValueError):
            with error_boundary("Test", reraise=True):
                raise ValueError("test")


class TestAvecGestionErreursUi:
    """Tests pour le décorateur avec_gestion_erreurs_ui."""

    def test_decorator_wraps_function(self, mock_streamlit):
        """Teste que le décorateur wrappe la fonction."""
        from src.modules._framework.error_boundary import avec_gestion_erreurs_ui

        @avec_gestion_erreurs_ui("Test")
        def my_function():
            return 42

        result = my_function()
        assert result == 42

    def test_decorator_catches_error(self, mock_streamlit):
        """Teste que le décorateur capture les erreurs."""
        from src.modules._framework.error_boundary import avec_gestion_erreurs_ui

        @avec_gestion_erreurs_ui("Test")
        def failing_function():
            raise ValueError("error")

        # Ne doit pas lever d'exception
        failing_function()
        mock_streamlit["error"].assert_called()


class TestSafeCall:
    """Tests pour safe_call."""

    def test_returns_result(self):
        """Teste le retour normal."""
        from src.modules._framework.error_boundary import safe_call

        result = safe_call(lambda: 42)
        assert result == 42

    def test_returns_default_on_error(self):
        """Teste le retour de default en cas d'erreur."""
        from src.modules._framework.error_boundary import safe_call

        def failing():
            raise ValueError("error")

        result = safe_call(failing, default="fallback")
        assert result == "fallback"

    def test_passes_args(self):
        """Teste le passage des arguments."""
        from src.modules._framework.error_boundary import safe_call

        def add(a, b):
            return a + b

        result = safe_call(add, 2, 3)
        assert result == 5

    def test_passes_kwargs(self):
        """Teste le passage des kwargs."""
        from src.modules._framework.error_boundary import safe_call

        def greet(name, prefix="Hello"):
            return f"{prefix}, {name}!"

        result = safe_call(greet, "World", prefix="Hi")
        assert result == "Hi, World!"


class TestErrorBoundaryContext:
    """Tests pour ErrorBoundaryContext."""

    def test_auto_generates_retry_key(self):
        """Teste la génération automatique de retry_key."""
        from src.modules._framework.error_boundary import ErrorBoundaryContext

        ctx = ErrorBoundaryContext(
            titre="Test Error",
            exception=ValueError("test"),
        )

        assert ctx.retry_key.startswith("retry_")

    def test_captures_traceback(self):
        """Teste la capture du traceback."""
        from src.modules._framework.error_boundary import ErrorBoundaryContext

        try:
            raise ValueError("test error")
        except ValueError as e:
            ctx = ErrorBoundaryContext(
                titre="Test",
                exception=e,
            )

        assert "ValueError" in ctx.traceback_str
        assert "test error" in ctx.traceback_str
