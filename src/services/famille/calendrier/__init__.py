"""
Package de synchronisation des calendriers externes.

Exports:
- CalendarSyncService: Service principal
- get_calendar_sync_service: Factory
- Schémas: FournisseurCalendrier, DirectionSync, ConfigCalendrierExterne, etc.
- ICalGenerator: Génération/parsing iCal

NOTE: afficher_calendar_sync_ui déplacé vers src/modules/planning/calendar_sync_ui.py
"""

from .generateur import ICalGenerator
from .google_calendar import GoogleCalendarMixin
from .schemas import (
    CalendarEventExternal,
    ConfigCalendrierExterne,
    DirectionSync,
    FournisseurCalendrier,
    SyncResult,
)
from .service import (
    CalendarSyncService,
    get_calendar_sync_service,
    obtenir_service_synchronisation_calendrier,
)

__all__ = [
    # Schémas
    "FournisseurCalendrier",
    "DirectionSync",
    "ConfigCalendrierExterne",
    "CalendarEventExternal",
    "SyncResult",
    # Générateur iCal
    "ICalGenerator",
    # Mixin Google Calendar
    "GoogleCalendarMixin",
    # Service
    "CalendarSyncService",
    "get_calendar_sync_service",
    "obtenir_service_synchronisation_calendrier",
]
