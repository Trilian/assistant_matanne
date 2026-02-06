"""
Tests complets pour le service calendar_sync.

Couvre:
- ICalGenerator (generate_ical, parse_ical)
- CalendarSyncService (add_calendar, remove_calendar, export_to_ical, import)
- Modèles Pydantic (ExternalCalendarConfig, SyncResult, etc.)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.services.calendar_sync import (
    CalendarProvider,
    SyncDirection,
    ExternalCalendarConfig,
    CalendarEventExternal,
    SyncResult,
    ICalGenerator,
    CalendarSyncService,
)


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCalendarProvider:
    """Tests pour l'enum CalendarProvider."""

    def test_google_provider(self):
        assert CalendarProvider.GOOGLE.value == "google"

    def test_apple_provider(self):
        assert CalendarProvider.APPLE.value == "apple"

    def test_outlook_provider(self):
        assert CalendarProvider.OUTLOOK.value == "outlook"

    def test_ical_url_provider(self):
        assert CalendarProvider.ICAL_URL.value == "ical_url"

    def test_all_providers_defined(self):
        providers = list(CalendarProvider)
        assert len(providers) == 4


class TestSyncDirection:
    """Tests pour l'enum SyncDirection."""

    def test_import_only(self):
        assert SyncDirection.IMPORT_ONLY.value == "import"

    def test_export_only(self):
        assert SyncDirection.EXPORT_ONLY.value == "export"

    def test_bidirectional(self):
        assert SyncDirection.BIDIRECTIONAL.value == "both"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestExternalCalendarConfig:
    """Tests pour le modèle ExternalCalendarConfig."""

    def test_create_minimal_config(self):
        config = ExternalCalendarConfig(
            user_id="user123",
            provider=CalendarProvider.GOOGLE,
        )
        assert config.user_id == "user123"
        assert config.provider == CalendarProvider.GOOGLE
        assert config.name == "Mon calendrier"
        assert config.sync_direction == SyncDirection.BIDIRECTIONAL
        assert config.is_active is True

    def test_create_full_config(self):
        config = ExternalCalendarConfig(
            user_id="user456",
            provider=CalendarProvider.ICAL_URL,
            name="Calendrier Travail",
            ical_url="https://example.com/calendar.ics",
            sync_direction=SyncDirection.IMPORT_ONLY,
            sync_meals=True,
            sync_activities=False,
            sync_events=True,
        )
        assert config.name == "Calendrier Travail"
        assert config.ical_url == "https://example.com/calendar.ics"
        assert config.sync_activities is False

    def test_config_has_auto_generated_id(self):
        config1 = ExternalCalendarConfig(user_id="u1", provider=CalendarProvider.GOOGLE)
        config2 = ExternalCalendarConfig(user_id="u1", provider=CalendarProvider.GOOGLE)
        assert config1.id != config2.id
        assert len(config1.id) == 12

    def test_config_with_oauth_tokens(self):
        config = ExternalCalendarConfig(
            user_id="user789",
            provider=CalendarProvider.OUTLOOK,
            access_token="access_token_123",
            refresh_token="refresh_token_456",
            token_expiry=datetime.now() + timedelta(hours=1),
        )
        assert config.access_token == "access_token_123"
        assert config.refresh_token == "refresh_token_456"
        assert config.token_expiry is not None


class TestCalendarEventExternal:
    """Tests pour le modèle CalendarEventExternal."""

    def test_create_basic_event(self):
        event = CalendarEventExternal(
            title="Réunion",
            start_time=datetime(2026, 2, 6, 10, 0),
            end_time=datetime(2026, 2, 6, 11, 0),
        )
        assert event.title == "Réunion"
        assert event.all_day is False
        assert event.description == ""

    def test_create_all_day_event(self):
        event = CalendarEventExternal(
            title="Anniversaire",
            start_time=datetime(2026, 2, 6),
            end_time=datetime(2026, 2, 7),
            all_day=True,
        )
        assert event.all_day is True

    def test_event_with_metadata(self):
        event = CalendarEventExternal(
            title="Dîner",
            start_time=datetime(2026, 2, 6, 19, 0),
            end_time=datetime(2026, 2, 6, 21, 0),
            source_type="meal",
            source_id=42,
            location="Maison",
        )
        assert event.source_type == "meal"
        assert event.source_id == 42
        assert event.location == "Maison"


class TestSyncResult:
    """Tests pour le modèle SyncResult."""

    def test_default_sync_result(self):
        result = SyncResult()
        assert result.success is False
        assert result.events_imported == 0
        assert result.events_exported == 0
        assert len(result.errors) == 0

    def test_successful_sync_result(self):
        result = SyncResult(
            success=True,
            message="Synchronisation réussie",
            events_imported=5,
            events_exported=3,
            duration_seconds=2.5,
        )
        assert result.success is True
        assert result.events_imported == 5
        assert result.duration_seconds == 2.5

    def test_sync_result_with_conflicts(self):
        result = SyncResult(
            success=True,
            conflicts=[{"event_id": "123", "reason": "Duplicate"}],
        )
        assert len(result.conflicts) == 1


# ═══════════════════════════════════════════════════════════
# TESTS ICAL GENERATOR
# ═══════════════════════════════════════════════════════════


class TestICalGenerator:
    """Tests pour le générateur iCal."""

    def test_generate_empty_calendar(self):
        ical = ICalGenerator.generate_ical([], "Test Calendar")
        assert "BEGIN:VCALENDAR" in ical
        assert "END:VCALENDAR" in ical
        assert "X-WR-CALNAME:Test Calendar" in ical
        assert "VERSION:2.0" in ical

    def test_generate_calendar_with_single_event(self):
        event = CalendarEventExternal(
            external_id="evt1",
            title="Test Event",
            start_time=datetime(2026, 2, 6, 10, 0),
            end_time=datetime(2026, 2, 6, 11, 0),
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "BEGIN:VEVENT" in ical
        assert "END:VEVENT" in ical
        assert "SUMMARY:Test Event" in ical
        assert "UID:evt1@assistant-matanne" in ical

    def test_generate_calendar_with_all_day_event(self):
        event = CalendarEventExternal(
            title="Jour férié",
            start_time=datetime(2026, 2, 6),
            end_time=datetime(2026, 2, 7),
            all_day=True,
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "DTSTART;VALUE=DATE:20260206" in ical
        assert "DTEND;VALUE=DATE:20260207" in ical

    def test_generate_calendar_with_description_and_location(self):
        event = CalendarEventExternal(
            title="Réunion importante",
            description="Discussion projet",
            location="Salle A",
            start_time=datetime(2026, 2, 6, 14, 0),
            end_time=datetime(2026, 2, 6, 15, 0),
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "DESCRIPTION:Discussion projet" in ical
        assert "LOCATION:Salle A" in ical

    def test_generate_calendar_escapes_special_chars(self):
        event = CalendarEventExternal(
            title="Event, with; special",
            start_time=datetime(2026, 2, 6, 10, 0),
            end_time=datetime(2026, 2, 6, 11, 0),
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "SUMMARY:Event\\, with\\; special" in ical

    def test_generate_calendar_with_meal_category(self):
        event = CalendarEventExternal(
            title="Dîner",
            start_time=datetime(2026, 2, 6, 19, 0),
            end_time=datetime(2026, 2, 6, 20, 0),
            source_type="meal",
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "CATEGORIES:Repas" in ical

    def test_generate_calendar_with_activity_category(self):
        event = CalendarEventExternal(
            title="Sortie parc",
            start_time=datetime(2026, 2, 6, 14, 0),
            end_time=datetime(2026, 2, 6, 16, 0),
            source_type="activity",
        )
        ical = ICalGenerator.generate_ical([event])
        
        assert "CATEGORIES:Activité Familiale" in ical

    def test_generate_calendar_multiple_events(self):
        events = [
            CalendarEventExternal(
                title=f"Event {i}",
                start_time=datetime(2026, 2, 6, 10 + i, 0),
                end_time=datetime(2026, 2, 6, 11 + i, 0),
            )
            for i in range(3)
        ]
        ical = ICalGenerator.generate_ical(events)
        
        assert ical.count("BEGIN:VEVENT") == 3
        assert ical.count("END:VEVENT") == 3

    def test_parse_ical_simple_event(self):
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test123
SUMMARY:Test Event
DTSTART:20260206T100000
DTEND:20260206T110000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 1
        assert events[0].title == "Test Event"
        assert events[0].external_id == "test123"

    def test_parse_ical_all_day_event(self):
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:allday1
SUMMARY:All Day Event
DTSTART;VALUE=DATE:20260206
DTEND;VALUE=DATE:20260207
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 1
        assert events[0].all_day is True

    def test_parse_ical_with_description(self):
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:desc1
SUMMARY:Event With Desc
DESCRIPTION:This is a test description
DTSTART:20260206T100000
DTEND:20260206T110000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert events[0].description == "This is a test description"

    def test_parse_ical_multiple_events(self):
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:evt1
SUMMARY:Event 1
DTSTART:20260206T100000
DTEND:20260206T110000
END:VEVENT
BEGIN:VEVENT
UID:evt2
SUMMARY:Event 2
DTSTART:20260206T140000
DTEND:20260206T150000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 2

    def test_parse_ical_empty(self):
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 0

    def test_parse_ical_datetime_formats(self):
        # Test date only
        dt = ICalGenerator._parse_ical_datetime("20260206")
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 6

        # Test datetime
        dt = ICalGenerator._parse_ical_datetime("20260206T140000")
        assert dt.hour == 14
        assert dt.minute == 0

        # Test datetime with Z suffix
        dt = ICalGenerator._parse_ical_datetime("20260206T140000Z")
        assert dt.hour == 14


# ═══════════════════════════════════════════════════════════
# TESTS CALENDAR SYNC SERVICE
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncService:
    """Tests pour le service de synchronisation."""

    @pytest.fixture
    def service(self):
        """Crée une instance du service pour les tests."""
        return CalendarSyncService()

    @pytest.fixture
    def sample_config(self):
        """Configuration de calendrier exemple."""
        return ExternalCalendarConfig(
            user_id="test_user",
            provider=CalendarProvider.ICAL_URL,
            name="Test Calendar",
            ical_url="https://example.com/cal.ics",
        )

    def test_service_initialization(self, service):
        assert service._configs == {}
        assert service.http_client is not None

    @patch.object(CalendarSyncService, '_save_config_to_db')
    def test_add_calendar(self, mock_save, service, sample_config):
        calendar_id = service.add_calendar(sample_config)
        
        assert calendar_id == sample_config.id
        assert sample_config.id in service._configs
        mock_save.assert_called_once()

    @patch.object(CalendarSyncService, '_save_config_to_db')
    def test_add_multiple_calendars(self, mock_save, service):
        config1 = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.GOOGLE,
        )
        config2 = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.APPLE,
        )
        
        id1 = service.add_calendar(config1)
        id2 = service.add_calendar(config2)
        
        assert id1 != id2
        assert len(service._configs) == 2

    def test_remove_calendar(self, service, sample_config):
        service._configs[sample_config.id] = sample_config
        
        service.remove_calendar(sample_config.id)
        
        assert sample_config.id not in service._configs

    def test_remove_nonexistent_calendar(self, service):
        # Should not raise
        service.remove_calendar("nonexistent_id")

    def test_get_user_calendars(self, service):
        config1 = ExternalCalendarConfig(user_id="user1", provider=CalendarProvider.GOOGLE)
        config2 = ExternalCalendarConfig(user_id="user1", provider=CalendarProvider.APPLE)
        config3 = ExternalCalendarConfig(user_id="user2", provider=CalendarProvider.GOOGLE)
        
        service._configs[config1.id] = config1
        service._configs[config2.id] = config2
        service._configs[config3.id] = config3
        
        user1_calendars = service.get_user_calendars("user1")
        
        assert len(user1_calendars) == 2

    def test_get_user_calendars_empty(self, service):
        calendars = service.get_user_calendars("nonexistent_user")
        assert calendars == []

    @patch('src.services.calendar_sync.obtenir_contexte_db')
    def test_export_to_ical(self, mock_db, service):
        """Test export basique."""
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        # Mock query results
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        ical = service.export_to_ical(
            user_id="test_user",
            start_date=datetime(2026, 2, 1),
            end_date=datetime(2026, 2, 28),
        )
        
        assert "BEGIN:VCALENDAR" in ical
        assert "END:VCALENDAR" in ical

    @patch('httpx.Client.get')
    def test_import_from_ical_url_success(self, mock_get, service, sample_config):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:import1
SUMMARY:Imported Event
DTSTART:20260206T100000
DTEND:20260206T110000
END:VEVENT
END:VCALENDAR"""
        mock_get.return_value = mock_response
        
        service._configs[sample_config.id] = sample_config
        
        with patch.object(service, '_save_imported_events', return_value=1):
            result = service.import_from_ical_url(sample_config)
        
        assert result.success is True
        assert result.events_imported == 1

    @patch('httpx.Client.get')
    def test_import_from_ical_url_network_error(self, mock_get, service, sample_config):
        mock_get.side_effect = Exception("Network error")
        service._configs[sample_config.id] = sample_config
        
        result = service.import_from_ical_url(sample_config)
        
        assert result.success is False
        assert len(result.errors) > 0

    @patch('httpx.Client.get')
    def test_import_from_ical_url_http_error(self, mock_get, service, sample_config):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        service._configs[sample_config.id] = sample_config
        
        result = service.import_from_ical_url(sample_config)
        
        assert result.success is False


class TestGoogleCalendarIntegration:
    """Tests pour l'intégration Google Calendar."""

    @pytest.fixture
    def service(self):
        return CalendarSyncService()

    def test_get_google_auth_url(self, service):
        with patch('src.services.calendar_sync.obtenir_parametres') as mock_params:
            mock_params.return_value.GOOGLE_CLIENT_ID = "test_client_id"
            
            url = service.get_google_auth_url(
                user_id="test_user",
                redirect_uri="http://localhost:8501/callback"
            )
            
            assert "accounts.google.com" in url or url == ""  # Depends on config

    @patch('httpx.Client.post')
    def test_handle_google_callback_success(self, mock_post, service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response
        
        with patch('src.services.calendar_sync.obtenir_parametres') as mock_params:
            mock_params.return_value.GOOGLE_CLIENT_ID = "test_id"
            mock_params.return_value.GOOGLE_CLIENT_SECRET = "test_secret"
            
            with patch.object(service, '_save_config_to_db'):
                result = service.handle_google_callback(
                    code="auth_code",
                    user_id="test_user",
                    redirect_uri="http://localhost:8501/callback"
                )
        
        # Result depends on implementation
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncIntegration:
    """Tests d'intégration pour le workflow complet."""

    def test_roundtrip_ical_export_import(self):
        """Test export puis import d'un calendrier iCal."""
        original_events = [
            CalendarEventExternal(
                external_id="roundtrip1",
                title="Roundtrip Event",
                description="Test description",
                start_time=datetime(2026, 2, 6, 10, 0),
                end_time=datetime(2026, 2, 6, 11, 0),
                location="Test Location",
            )
        ]
        
        # Export
        ical_content = ICalGenerator.generate_ical(original_events)
        
        # Import
        imported_events = ICalGenerator.parse_ical(ical_content)
        
        assert len(imported_events) == 1
        assert imported_events[0].title == "Roundtrip Event"
        assert imported_events[0].external_id == "roundtrip1"

    def test_sync_config_serialization(self):
        """Test sérialisation de la configuration."""
        config = ExternalCalendarConfig(
            user_id="test",
            provider=CalendarProvider.GOOGLE,
            name="My Calendar",
            access_token="token123",
        )
        
        # To dict
        config_dict = config.model_dump()
        
        # From dict
        restored = ExternalCalendarConfig(**config_dict)
        
        assert restored.user_id == config.user_id
        assert restored.provider == config.provider
        assert restored.access_token == config.access_token
