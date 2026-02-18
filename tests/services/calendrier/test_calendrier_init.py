"""
Tests pour src/services/calendrier/__init__.py

Couvre les exports du module calendrier.
"""

import pytest


@pytest.mark.unit
class TestCalendrierModuleExports:
    """Tests pour les exports du module calendrier."""

    def test_exports_calendar_sync_service(self):
        """Export CalendarSyncService."""
        from src.services.calendrier import CalendarSyncService

        assert CalendarSyncService is not None

    def test_exports_get_calendar_sync_service(self):
        """Export get_calendar_sync_service."""
        from src.services.calendrier import get_calendar_sync_service

        assert callable(get_calendar_sync_service)

    def test_exports_ical_generator(self):
        """Export ICalGenerator."""
        from src.services.calendrier import ICalGenerator

        assert ICalGenerator is not None

    def test_exports_schemas(self):
        """Export des schémas."""
        from src.services.calendrier import (
            CalendarProvider,
            ExternalCalendarConfig,
            SyncDirection,
        )

        assert CalendarProvider is not None
        assert SyncDirection is not None
        assert ExternalCalendarConfig is not None
