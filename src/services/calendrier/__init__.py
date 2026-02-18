"""
Package de synchronisation des calendriers externes.

Exports:
- CalendarSyncService: Service principal
- get_calendar_sync_service: Factory
- Schémas: CalendarProvider, SyncDirection, ExternalCalendarConfig, etc.
- ICalGenerator: Génération/parsing iCal

NOTE: render_calendar_sync_ui déplacé vers src/modules/planning/calendar_sync_ui.py
"""

from .generateur import ICalGenerator
from .schemas import (
    CalendarEventExternal,
    CalendarProvider,
    ExternalCalendarConfig,
    SyncDirection,
    SyncResult,
)
from .service import (
    CalendarSyncService,
    get_calendar_sync_service,
)

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
]
