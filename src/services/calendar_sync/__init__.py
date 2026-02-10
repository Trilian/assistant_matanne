"""
Package de synchronisation des calendriers externes.

Exports:
- CalendarSyncService: Service principal
- get_calendar_sync_service: Factory
- Schémas: CalendarProvider, SyncDirection, ExternalCalendarConfig, etc.
- ICalGenerator: Génération/parsing iCal
"""

from .schemas import (
    CalendarProvider,
    SyncDirection,
    ExternalCalendarConfig,
    CalendarEventExternal,
    SyncResult,
)

from .ical_generator import ICalGenerator

from .service import (
    CalendarSyncService,
    get_calendar_sync_service,
)


def render_calendar_sync_ui():
    """
    Interface Streamlit pour la synchronisation des calendriers.
    
    Déplacé vers src/domains/planning/ui/calendar_sync_ui.py
    Cette fonction assure la rétrocompatibilité.
    """
    from src.domains.planning.ui.calendar_sync_ui import render_calendar_sync_ui as _render
    return _render()


__all__ = [
    # Schémas
    "CalendarProvider",
    "SyncDirection",
    "ExternalCalendarConfig",
    "CalendarEventExternal",
    "SyncResult",
    # Générateur iCal
    "ICalGenerator",
    # Service
    "CalendarSyncService",
    "get_calendar_sync_service",
    # UI (rétrocompatibilité)
    "render_calendar_sync_ui",
]
