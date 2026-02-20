"""Tests pour state_manager du framework."""

from unittest.mock import patch

import pytest


class MockSessionState(dict):
    """Mock de st.session_state."""

    pass


@pytest.fixture
def mock_session_state():
    """Fixture pour mocker st.session_state."""
    state = MockSessionState()
    with patch("streamlit.session_state", state):
        yield state


class TestModuleState:
    """Tests pour ModuleState."""

    def test_init_with_defaults(self, mock_session_state):
        """Teste l'initialisation avec valeurs par défaut."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"count": 0, "active": True})

        assert mock_session_state["_mod_test_count"] == 0
        assert mock_session_state["_mod_test_active"] is True

    def test_get_value(self, mock_session_state):
        """Teste la récupération d'une valeur."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"count": 42})

        assert state.get("count") == 42
        assert state.get("missing", "default") == "default"

    def test_set_value(self, mock_session_state):
        """Teste la définition d'une valeur."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {})
        state.set("new_key", "new_value")

        assert mock_session_state["_mod_test_new_key"] == "new_value"

    def test_update_multiple(self, mock_session_state):
        """Teste la mise à jour de plusieurs valeurs."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {})
        state.update({"a": 1, "b": 2, "c": 3})

        assert state.get("a") == 1
        assert state.get("b") == 2
        assert state.get("c") == 3

    def test_delete_value(self, mock_session_state):
        """Teste la suppression d'une valeur."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"to_delete": "value"})
        assert state.get("to_delete") == "value"

        state.delete("to_delete")
        assert "_mod_test_to_delete" not in mock_session_state

    def test_reset(self, mock_session_state):
        """Teste la réinitialisation."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"count": 0})
        state.set("count", 100)
        state.set("extra", "value")

        state.reset()

        assert state.get("count") == 0
        assert state.get("extra") is None

    def test_all(self, mock_session_state):
        """Teste la récupération de tout le state."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"a": 1, "b": 2})

        all_state = state.all()

        assert all_state == {"a": 1, "b": 2}

    def test_has(self, mock_session_state):
        """Teste la vérification d'existence."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"exists": True})

        assert state.has("exists") is True
        assert state.has("not_exists") is False

    def test_increment(self, mock_session_state):
        """Teste l'incrémentation."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"count": 10})

        new_value = state.increment("count", 5)

        assert new_value == 15
        assert state.get("count") == 15

    def test_toggle(self, mock_session_state):
        """Teste le toggle."""
        from src.modules._framework.state_manager import ModuleState

        state = ModuleState("test", {"active": False})

        result = state.toggle("active")

        assert result is True
        assert state.get("active") is True


class TestInitModuleState:
    """Tests pour init_module_state."""

    def test_creates_module_state(self, mock_session_state):
        """Teste la création d'un ModuleState."""
        from src.modules._framework.state_manager import init_module_state

        state = init_module_state("my_module", {"key": "value"})

        assert state.get("key") == "value"
        assert state.module_name == "my_module"


class TestResetModuleState:
    """Tests pour reset_module_state."""

    def test_clears_module_keys(self, mock_session_state):
        """Teste la suppression des clés du module."""
        from src.modules._framework.state_manager import (
            ModuleState,
            reset_module_state,
        )

        # Créer du state
        mock_session_state["_mod_test_a"] = 1
        mock_session_state["_mod_test_b"] = 2
        mock_session_state["_mod_other_c"] = 3

        reset_module_state("test")

        assert "_mod_test_a" not in mock_session_state
        assert "_mod_test_b" not in mock_session_state
        assert "_mod_other_c" in mock_session_state  # Non affecté


class TestGetAllModuleStates:
    """Tests pour get_all_module_states."""

    def test_returns_all_states(self, mock_session_state):
        """Teste le retour de tous les states."""
        from src.modules._framework.state_manager import get_all_module_states

        mock_session_state["_mod_mod1_key1"] = "v1"
        mock_session_state["_mod_mod1_key2"] = "v2"
        mock_session_state["_mod_mod2_key3"] = "v3"
        mock_session_state["other_key"] = "ignored"

        result = get_all_module_states()

        assert "mod1" in result
        assert result["mod1"] == {"key1": "v1", "key2": "v2"}
        assert "mod2" in result
        assert result["mod2"] == {"key3": "v3"}
