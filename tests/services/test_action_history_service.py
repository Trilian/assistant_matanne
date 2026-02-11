import pytest
import importlib

@pytest.mark.unit
def test_import_action_history_service():
    """Vérifie que le module utilisateur.historique s'importe sans erreur."""
    module = importlib.import_module("src.services.utilisateur.historique")
    assert module is not None


import types
from src.services.utilisateur import historique

def test_action_history_service_log_action():
    service = historique.ActionHistoryService()
    entry = service.log_action(
        action_type=historique.ActionType.RECETTE_CREATED,
        entity_type="recette",
        description="Test création recette",
        entity_id=1,
        entity_name="Tarte",
        details={"test": True},
        old_value=None,
        new_value={"nom": "Tarte"},
    )
    assert entry.action_type == historique.ActionType.RECETTE_CREATED
    assert entry.entity_type == "recette"

def test_action_history_service_get_recent_actions():
    service = historique.ActionHistoryService()
    actions = service.get_recent_actions(limit=2)
    assert isinstance(actions, list)

def test_action_history_service_get_stats():
    service = historique.ActionHistoryService()
    stats = service.get_stats(days=1)
    assert hasattr(stats, "total_actions")

def test_action_history_service_can_undo_false():
    service = historique.ActionHistoryService()
    assert service.can_undo(999999) is False
