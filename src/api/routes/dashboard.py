"""
Routes dashboard - re-exports pour compatibilite.

Le code est reparti dans :
- dashboard_accueil.py (endpoints principaux)
- dashboard_gamification.py (badges et points)
- dashboard_widgets.py (documents expirants, actions rapides)
"""

from src.api.routes.dashboard_widgets import WidgetActionRequest, enregistrer_action_widget

__all__ = ["WidgetActionRequest", "enregistrer_action_widget"]
