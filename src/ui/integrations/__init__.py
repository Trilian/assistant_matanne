"""
Intégrations externes - Composants UI pour services tiers.

Fournit des interfaces pour:
- Google Calendar (sync, import, export)
- (Futur: Notion, Google Tasks, etc.)
"""

from .google_calendar import (
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL,
    render_google_calendar_config,
    render_quick_sync_button,
    render_sync_status,
    verifier_config_google,
)

__all__ = [
    # Google Calendar
    "GOOGLE_SCOPES",
    "REDIRECT_URI_LOCAL",
    "verifier_config_google",
    "render_google_calendar_config",
    "render_sync_status",
    "render_quick_sync_button",
]
