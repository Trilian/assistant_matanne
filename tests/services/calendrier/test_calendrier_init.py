"""
Tests pour src/services/calendrier/__init__.py

Couvre les fonctions wrapper de rétrocompatibilité.
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestRenderCalendarSyncUI:
    """Tests pour render_calendar_sync_ui (rétrocompatibilité)."""

    @patch("src.modules.planning.calendar_sync_ui.render_calendar_sync_ui")
    def test_render_calendar_sync_ui_calls_underlying(self, mock_render):
        """La fonction wrapper appelle la fonction sous-jacente."""
        mock_render.return_value = "sync_result"

        # Import APRÈS le patch pour que le lazy import utilise le mock
        from src.services.calendrier import render_calendar_sync_ui

        result = render_calendar_sync_ui()

        mock_render.assert_called_once()
        assert result == "sync_result"

    def test_render_calendar_sync_ui_import(self):
        """Import de render_calendar_sync_ui fonctionne."""
        from src.services.calendrier import render_calendar_sync_ui

        assert callable(render_calendar_sync_ui)


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
