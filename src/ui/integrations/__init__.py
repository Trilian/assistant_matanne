"""
Intégrations externes - Composants UI pour services tiers.

Fournit des interfaces pour:
- Google Calendar (sync, import, export)
- (Futur: Notion, Google Tasks, etc.)
"""

from .google_calendar import (
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL,
    afficher_bouton_sync_rapide,
    afficher_config_google_calendar,
    afficher_statut_sync_google,
    verifier_config_google,
)

__all__ = [
    # Google Calendar
    "GOOGLE_SCOPES",
    "REDIRECT_URI_LOCAL",
    "verifier_config_google",
    "afficher_config_google_calendar",
    "afficher_statut_sync_google",
    "afficher_bouton_sync_rapide",
]
