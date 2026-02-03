import pytest
import importlib

@pytest.mark.unit
def test_import_action_history_service():
    """Vérifie que le module action_history s'importe sans erreur."""
    module = importlib.import_module("src.services.action_history")
    assert module is not None


import types
from src.services import action_history

def test_action_history_service_log_action():
    service = action_history.ActionHistoryService()
    entry = service.log_action(
        action_type=action_history.ActionType.RECETTE_CREATED,
        entity_type="recette",
        description="Test création recette",
        entity_id=1,
        entity_name="Tarte",
        details={"test": True},
        old_value=None,
        new_value={"nom": "Tarte"},
    )
    assert entry.action_type == action_history.ActionType.RECETTE_CREATED
    assert entry.entity_type == "recette"

def test_action_history_service_get_recent_actions():
    service = action_history.ActionHistoryService()
    actions = service.get_recent_actions(limit=2)
    assert isinstance(actions, list)

def test_action_history_service_get_stats():
    service = action_history.ActionHistoryService()
    stats = service.get_stats(days=1)
    assert hasattr(stats, "total_actions")

def test_action_history_service_can_undo_false():
    service = action_history.ActionHistoryService()
    assert service.can_undo(999999) is False
