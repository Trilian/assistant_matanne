"""Tests pour les hooks du framework."""

from unittest.mock import MagicMock, patch

import pytest


class MockSessionState(dict):
    """Mock de st.session_state qui se comporte comme un dict."""

    pass


@pytest.fixture
def mock_session_state():
    """Fixture pour mocker st.session_state."""
    state = MockSessionState()
    with patch("streamlit.session_state", state):
        yield state


class TestUseState:
    """Tests pour use_state hook."""

    def test_initial_value(self, mock_session_state):
        """Teste la valeur initiale."""
        from src.modules._framework.hooks import use_state

        result = use_state("counter", 0)

        assert result.value == 0
        assert result.key == "counter"
        assert "counter" in mock_session_state

    def test_setter_updates_value(self, mock_session_state):
        """Teste que le setter met à jour la valeur."""
        from src.modules._framework.hooks import use_state

        result = use_state("counter", 0)
        result.setter(42)

        assert mock_session_state["counter"] == 42

    def test_preserves_existing_value(self, mock_session_state):
        """Teste que la valeur existante est préservée."""
        mock_session_state["existing"] = 100

        from src.modules._framework.hooks import use_state

        result = use_state("existing", 0)

        assert result.value == 100

    def test_with_prefix(self, mock_session_state):
        """Teste l'utilisation d'un préfixe."""
        from src.modules._framework.hooks import use_state

        result = use_state("counter", 0, prefix="mod")

        assert result.key == "mod_counter"
        assert "mod_counter" in mock_session_state

    def test_update_method(self, mock_session_state):
        """Teste la méthode update."""
        from src.modules._framework.hooks import use_state

        result = use_state("counter", 10)
        result.update(lambda x: x * 2)

        assert mock_session_state["counter"] == 20


class TestUseService:
    """Tests pour use_service hook."""

    def test_creates_service_once(self, mock_session_state):
        """Teste que le service est créé une seule fois."""
        from src.modules._framework.hooks import use_service

        factory = MagicMock(return_value="service_instance")
        factory.__name__ = "test_factory"

        result1 = use_service(factory)
        result2 = use_service(factory)

        assert result1 == "service_instance"
        assert result2 == "service_instance"
        factory.assert_called_once()

    def test_custom_cache_key(self, mock_session_state):
        """Teste l'utilisation d'une clé de cache personnalisée."""
        from src.modules._framework.hooks import use_service

        factory = MagicMock(return_value="service")
        factory.__name__ = "factory"

        use_service(factory, cache_key="my_service")

        assert "my_service" in mock_session_state


class TestUseQuery:
    """Tests pour use_query hook."""

    def test_successful_query(self, mock_session_state):
        """Teste une requête réussie."""
        from src.modules._framework.hooks import use_query

        query_fn = MagicMock(return_value=["data1", "data2"])
        result = use_query(query_fn, "test_key", ttl=300)

        assert result.data == ["data1", "data2"]
        assert result.loading is False
        assert result.error is None
        assert result.is_success is True
        query_fn.assert_called_once()

    def test_error_handling(self, mock_session_state):
        """Teste la gestion d'erreur."""
        from src.modules._framework.hooks import use_query

        query_fn = MagicMock(side_effect=ValueError("test error"))
        result = use_query(query_fn, "error_key", ttl=300)

        assert result.data is None
        assert result.loading is False
        assert result.error is not None
        assert result.is_error is True
        assert isinstance(result.error, ValueError)

    def test_disabled_query(self, mock_session_state):
        """Teste une requête désactivée."""
        from src.modules._framework.hooks import use_query

        query_fn = MagicMock(return_value="data")
        result = use_query(query_fn, "disabled_key", enabled=False)

        assert result.loading is True
        query_fn.assert_not_called()

    def test_refetch_resets_state(self, mock_session_state):
        """Teste que refetch remet l'état en loading."""
        from src.modules._framework.hooks import use_query

        query_fn = MagicMock(return_value="data")
        result = use_query(query_fn, "refetch_key", ttl=300)

        assert result.loading is False
        result.refetch()

        state = mock_session_state["_query_refetch_key"]
        assert state["loading"] is True
        assert state["timestamp"] == 0

    def test_callbacks(self, mock_session_state):
        """Teste les callbacks on_success et on_error."""
        from src.modules._framework.hooks import use_query

        on_success = MagicMock()
        on_error = MagicMock()

        # Test success
        query_fn = MagicMock(return_value="data")
        use_query(query_fn, "cb_success", on_success=on_success)
        on_success.assert_called_once_with("data")

        # Test error
        query_fn = MagicMock(side_effect=ValueError("error"))
        use_query(query_fn, "cb_error", on_error=on_error)
        on_error.assert_called_once()


class TestUseMemo:
    """Tests pour use_memo hook."""

    def test_memoizes_result(self, mock_session_state):
        """Teste la mémorisation du résultat."""
        from src.modules._framework.hooks import use_memo

        compute_fn = MagicMock(return_value=42)

        result1 = use_memo(compute_fn, deps=["a", "b"], cache_key="memo_test")
        result2 = use_memo(compute_fn, deps=["a", "b"], cache_key="memo_test")

        assert result1 == 42
        assert result2 == 42
        compute_fn.assert_called_once()

    def test_recomputes_on_deps_change(self, mock_session_state):
        """Teste le recalcul quand les dépendances changent."""
        from src.modules._framework.hooks import use_memo

        compute_fn = MagicMock(side_effect=[10, 20])

        result1 = use_memo(compute_fn, deps=["a"], cache_key="memo_deps")
        result2 = use_memo(compute_fn, deps=["b"], cache_key="memo_deps")

        assert result1 == 10
        assert result2 == 20
        assert compute_fn.call_count == 2


class TestUseEffect:
    """Tests pour use_effect hook."""

    def test_executes_effect(self, mock_session_state):
        """Teste l'exécution de l'effet."""
        from src.modules._framework.hooks import use_effect

        effect_fn = MagicMock(return_value=None)

        use_effect(effect_fn, deps=["a"], effect_key="effect_test")

        effect_fn.assert_called_once()

    def test_runs_cleanup(self, mock_session_state):
        """Teste l'appel du cleanup."""
        from src.modules._framework.hooks import use_effect

        cleanup = MagicMock()
        effect_fn = MagicMock(return_value=cleanup)

        # Première exécution
        use_effect(effect_fn, deps=["a"], effect_key="cleanup_test")

        # Changement de deps
        use_effect(effect_fn, deps=["b"], effect_key="cleanup_test")

        cleanup.assert_called_once()


class TestUsePrevious:
    """Tests pour use_previous hook."""

    def test_returns_previous_value(self, mock_session_state):
        """Teste le retour de la valeur précédente."""
        from src.modules._framework.hooks import use_previous

        prev1 = use_previous(10, "test_prev")
        assert prev1 is None  # Première exécution

        prev2 = use_previous(20, "test_prev")
        assert prev2 == 10

        prev3 = use_previous(30, "test_prev")
        assert prev3 == 20
