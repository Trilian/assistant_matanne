"""Compatibilité legacy pour le bridge Dashboard → actions rapides.

Ce module conserve les imports historiques `inter_module_*` après le
renommage vers `bridges_dashboard_actions.py`.
"""

from src.services.utilitaires.bridges_dashboard_actions import (
    DashboardActionsRapidesInteractionService,
    get_dashboard_actions_rapides_service,
)

__all__ = [
    "DashboardActionsRapidesInteractionService",
    "get_dashboard_actions_rapides_service",
]
