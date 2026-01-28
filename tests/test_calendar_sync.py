"""
Tests pour le service de synchronisation calendrier (calendar_sync.py).

Ce fichier teste les fonctionnalités de sync calendrier:
- Configuration (ExternalCalendarConfig)
- Événements externes (CalendarEventExternal)
- Génération iCal
- Parsing iCal
- Service de synchronisation
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
from uuid import uuid4


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCalendarProviderEnum:
    """Tests pour CalendarProvider enum."""

    def test_providers_disponibles(self):
        """Vérifie les providers disponibles."""
        from src.services.calendar_sync import CalendarProvider
        
        providers = [p.value for p in CalendarProvider]
        
        assert "google" in providers
        assert "apple" in providers
        assert "outlook" in providers
        assert "ical_url" in providers

    def test_provider_valeur_string(self):
        """CalendarProvider est un string enum."""
        from src.services.calendar_sync import CalendarProvider
        
        assert CalendarProvider.GOOGLE.value == "google"
        assert CalendarProvider.APPLE.value == "apple"


class TestSyncDirectionEnum:
    """Tests pour SyncDirection enum."""

    def test_directions_disponibles(self):
        """Vérifie les directions de sync."""
        from src.services.calendar_sync import SyncDirection
        
        directions = [d.value for d in SyncDirection]
        
        assert "import" in directions
        assert "export" in directions
        assert "both" in directions


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES - CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestExternalCalendarConfigModel:
    """Tests pour ExternalCalendarConfig model."""

    def test_config_creation(self):
        """Création d'une config calendrier."""
        from src.services.calendar_sync import ExternalCalendarConfig, CalendarProvider
        
        config = ExternalCalendarConfig(
            user_id="user123",
            provider=CalendarProvider.GOOGLE,
            name="Mon Google Calendar",
            calendar_id="primary",
        )
        
        assert config.user_id == "user123"
        assert config.provider == CalendarProvider.GOOGLE
        assert config.name == "Mon Google Calendar"

    def test_config_defaults(self):
        """Valeurs par défaut de la config."""
        from src.services.calendar_sync import (
            ExternalCalendarConfig, 
            CalendarProvider, 
            SyncDirection
        )
        
        config = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.ICAL_URL,
        )
        
        assert config.name == "Mon calendrier"
        assert config.sync_direction == SyncDirection.BIDIRECTIONAL
        assert config.sync_meals is True
        assert config.sync_activities is True
        assert config.is_active is True

    def test_config_id_auto_generated(self):
        """ID est auto-généré."""
        from src.services.calendar_sync import ExternalCalendarConfig, CalendarProvider
        
        config1 = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.GOOGLE,
        )
        config2 = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.GOOGLE,
        )
        
        # IDs différents
        assert config1.id != config2.id
        # ID a une longueur raisonnable
        assert len(config1.id) > 0

    def test_config_oauth_tokens(self):
        """Config avec tokens OAuth."""
        from src.services.calendar_sync import ExternalCalendarConfig, CalendarProvider
        
        config = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.GOOGLE,
            access_token="access_token_123",
            refresh_token="refresh_token_456",
            token_expiry=datetime.now() + timedelta(hours=1),
        )
        
        assert config.access_token == "access_token_123"
        assert config.refresh_token == "refresh_token_456"
        assert config.token_expiry > datetime.now()


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES - ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


class TestCalendarEventExternalModel:
    """Tests pour CalendarEventExternal model."""

    def test_event_creation(self):
        """Création d'un événement externe."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            title="Réunion importante",
            description="Discussion projet",
            start_time=datetime(2026, 1, 28, 14, 0),
            end_time=datetime(2026, 1, 28, 15, 0),
        )
        
        assert event.title == "Réunion importante"
        assert event.start_time.hour == 14

    def test_event_all_day(self):
        """Événement toute la journée."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            title="Vacances",
            start_time=datetime(2026, 2, 1, 0, 0),
            end_time=datetime(2026, 2, 8, 0, 0),
            all_day=True,
        )
        
        assert event.all_day is True

    def test_event_with_source(self):
        """Événement avec source (repas, activité)."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            title="Dîner en famille",
            start_time=datetime(2026, 1, 28, 19, 0),
            end_time=datetime(2026, 1, 28, 20, 0),
            source_type="meal",
            source_id=42,
        )
        
        assert event.source_type == "meal"
        assert event.source_id == 42

    def test_event_defaults(self):
        """Valeurs par défaut de l'événement."""
        from src.services.calendar_sync import CalendarEventExternal
        
        event = CalendarEventExternal(
            title="Test",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )
        
        assert event.id == ""
        assert event.external_id == ""
        assert event.description == ""
        assert event.all_day is False
        assert event.location == ""


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES - RÉSULTATS SYNC
# ═══════════════════════════════════════════════════════════


class TestSyncResultModel:
    """Tests pour SyncResult model."""

    def test_sync_result_success(self):
        """Résultat de sync réussi."""
        from src.services.calendar_sync import SyncResult
        
        result = SyncResult(
            success=True,
            message="Synchronisation terminée",
            events_imported=10,
            events_exported=5,
            events_updated=3,
        )
        
        assert result.success is True
        assert result.events_imported == 10
        assert result.events_exported == 5

    def test_sync_result_with_conflicts(self):
        """Résultat avec conflits."""
        from src.services.calendar_sync import SyncResult
        
        result = SyncResult(
            success=True,
            message="Sync avec conflits",
            events_imported=8,
            conflicts=[
                {"event_id": "123", "reason": "Heure modifiée"},
                {"event_id": "456", "reason": "Supprimé localement"},
            ],
        )
        
        assert len(result.conflicts) == 2

    def test_sync_result_defaults(self):
        """Valeurs par défaut de SyncResult."""
        from src.services.calendar_sync import SyncResult
        
        result = SyncResult()
        
        assert result.success is False
        assert result.events_imported == 0
        assert result.events_exported == 0
        assert result.conflicts == []
        assert result.errors == []


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATEUR iCAL
# ═══════════════════════════════════════════════════════════


class TestICalGenerator:
    """Tests pour ICalGenerator."""

    def test_generate_ical_header(self):
        """Génère un header iCal valide."""
        from src.services.calendar_sync import ICalGenerator
        
        ical = ICalGenerator.generate_ical([], calendar_name="Test")
        
        assert "BEGIN:VCALENDAR" in ical
        assert "VERSION:2.0" in ical
        assert "END:VCALENDAR" in ical
        assert "X-WR-CALNAME:Test" in ical

    def test_generate_ical_with_events(self):
        """Génère un iCal avec événements."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                external_id="event1",
                title="Réunion",
                start_time=datetime(2026, 1, 28, 10, 0),
                end_time=datetime(2026, 1, 28, 11, 0),
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        assert "BEGIN:VEVENT" in ical
        assert "END:VEVENT" in ical
        assert "SUMMARY:Réunion" in ical

    def test_generate_ical_all_day_event(self):
        """Événement toute la journée en iCal."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                external_id="allday1",
                title="Anniversaire",
                start_time=datetime(2026, 2, 15, 0, 0),
                end_time=datetime(2026, 2, 16, 0, 0),
                all_day=True,
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        # Format date seule pour all_day
        assert "DTSTART;VALUE=DATE:20260215" in ical

    def test_generate_ical_escape_special_chars(self):
        """Les caractères spéciaux sont échappés."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                title="Test, avec virgule; et point-virgule",
                start_time=datetime(2026, 1, 28, 10, 0),
                end_time=datetime(2026, 1, 28, 11, 0),
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        # Les virgules et points-virgules sont échappés
        assert "\\," in ical or "\\;" in ical

    def test_generate_ical_with_location(self):
        """Événement avec lieu."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                title="RDV",
                start_time=datetime(2026, 1, 28, 14, 0),
                end_time=datetime(2026, 1, 28, 15, 0),
                location="Café du Centre",
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        assert "LOCATION:Café du Centre" in ical

    def test_generate_ical_meal_category(self):
        """Événement repas a la catégorie Repas."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                title="Dîner",
                start_time=datetime(2026, 1, 28, 19, 0),
                end_time=datetime(2026, 1, 28, 20, 0),
                source_type="meal",
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        assert "CATEGORIES:Repas" in ical


# ═══════════════════════════════════════════════════════════
# TESTS PARSING iCAL
# ═══════════════════════════════════════════════════════════


class TestICalParser:
    """Tests pour parsing iCal."""

    def test_parse_simple_ical(self):
        """Parse un iCal simple."""
        from src.services.calendar_sync import ICalGenerator
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test123@example.com
SUMMARY:Test Event
DTSTART:20260128T100000
DTEND:20260128T110000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 1
        assert events[0].title == "Test Event"

    def test_parse_all_day_event(self):
        """Parse événement toute la journée."""
        from src.services.calendar_sync import ICalGenerator
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:allday@example.com
SUMMARY:Vacances
DTSTART;VALUE=DATE:20260201
DTEND;VALUE=DATE:20260208
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 1
        assert events[0].all_day is True

    def test_parse_event_with_description(self):
        """Parse événement avec description."""
        from src.services.calendar_sync import ICalGenerator
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:desc@example.com
SUMMARY:Réunion
DESCRIPTION:Discussion du projet\\nAvec retour à la ligne
DTSTART:20260128T140000
DTEND:20260128T150000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 1
        # Les \n sont convertis en vrais retours à la ligne
        assert "Discussion du projet" in events[0].description

    def test_parse_multiple_events(self):
        """Parse plusieurs événements."""
        from src.services.calendar_sync import ICalGenerator
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:event1@example.com
SUMMARY:Event 1
DTSTART:20260128T100000
DTEND:20260128T110000
END:VEVENT
BEGIN:VEVENT
UID:event2@example.com
SUMMARY:Event 2
DTSTART:20260128T140000
DTEND:20260128T150000
END:VEVENT
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert len(events) == 2
        titles = [e.title for e in events]
        assert "Event 1" in titles
        assert "Event 2" in titles

    def test_parse_empty_ical(self):
        """Parse iCal vide retourne liste vide."""
        from src.services.calendar_sync import ICalGenerator
        
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
END:VCALENDAR"""
        
        events = ICalGenerator.parse_ical(ical_content)
        
        assert events == []


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE - INITIALISATION
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncServiceInit:
    """Tests pour l'initialisation du service."""

    def test_service_creation(self):
        """Création du service."""
        from src.services.calendar_sync import CalendarSyncService
        
        service = CalendarSyncService()
        
        assert service._configs == {}
        assert service.http_client is not None


# ═══════════════════════════════════════════════════════════
# TESTS GESTION CALENDRIERS
# ═══════════════════════════════════════════════════════════


class TestCalendarManagement:
    """Tests pour gestion des calendriers."""

    def test_add_calendar(self):
        """Ajout d'un calendrier."""
        from src.services.calendar_sync import (
            CalendarSyncService, 
            ExternalCalendarConfig, 
            CalendarProvider
        )
        
        service = CalendarSyncService()
        
        config = ExternalCalendarConfig(
            id="cal1",
            user_id="user123",
            provider=CalendarProvider.GOOGLE,
            name="Mon Calendar",
        )
        
        with patch.object(service, '_save_config_to_db'):
            calendar_id = service.add_calendar(config)
        
        assert calendar_id == "cal1"
        assert "cal1" in service._configs

    def test_remove_calendar(self):
        """Suppression d'un calendrier."""
        from src.services.calendar_sync import (
            CalendarSyncService, 
            ExternalCalendarConfig, 
            CalendarProvider
        )
        
        service = CalendarSyncService()
        
        config = ExternalCalendarConfig(
            id="cal_to_remove",
            user_id="user1",
            provider=CalendarProvider.ICAL_URL,
        )
        
        with patch.object(service, '_save_config_to_db'):
            service.add_calendar(config)
        
        with patch.object(service, '_remove_config_from_db'):
            service.remove_calendar("cal_to_remove")
        
        assert "cal_to_remove" not in service._configs

    def test_get_user_calendars(self):
        """Récupération des calendriers d'un utilisateur."""
        from src.services.calendar_sync import (
            CalendarSyncService, 
            ExternalCalendarConfig, 
            CalendarProvider
        )
        
        service = CalendarSyncService()
        
        # Ajouter 3 calendriers, 2 pour user1 et 1 pour user2
        configs = [
            ExternalCalendarConfig(
                id="cal1", user_id="user1", provider=CalendarProvider.GOOGLE
            ),
            ExternalCalendarConfig(
                id="cal2", user_id="user1", provider=CalendarProvider.APPLE
            ),
            ExternalCalendarConfig(
                id="cal3", user_id="user2", provider=CalendarProvider.OUTLOOK
            ),
        ]
        
        with patch.object(service, '_save_config_to_db'):
            for config in configs:
                service.add_calendar(config)
        
        user1_cals = service.get_user_calendars("user1")
        user2_cals = service.get_user_calendars("user2")
        
        assert len(user1_cals) == 2
        assert len(user2_cals) == 1


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT iCAL
# ═══════════════════════════════════════════════════════════


class TestExportIcal:
    """Tests pour export vers iCal."""

    @patch('src.services.calendar_sync.obtenir_contexte_db')
    def test_export_to_ical_empty(self, mock_db):
        """Export sans données retourne iCal vide."""
        from src.services.calendar_sync import CalendarSyncService
        
        # Mock la session sans données
        mock_session = MagicMock()
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
        mock_db.return_value.__enter__.return_value = mock_session
        
        service = CalendarSyncService()
        
        ical = service.export_to_ical("user1")
        
        if ical:
            assert "BEGIN:VCALENDAR" in ical
            assert "END:VCALENDAR" in ical


# ═══════════════════════════════════════════════════════════
# TESTS DATETIME PARSING
# ═══════════════════════════════════════════════════════════


class TestICalDatetimeParsing:
    """Tests pour parsing des dates iCal."""

    def test_parse_datetime_full(self):
        """Parse datetime complet."""
        from src.services.calendar_sync import ICalGenerator
        
        dt = ICalGenerator._parse_ical_datetime("20260128T143000")
        
        assert dt.year == 2026
        assert dt.month == 1
        assert dt.day == 28
        assert dt.hour == 14
        assert dt.minute == 30

    def test_parse_datetime_utc(self):
        """Parse datetime UTC (avec Z)."""
        from src.services.calendar_sync import ICalGenerator
        
        dt = ICalGenerator._parse_ical_datetime("20260128T143000Z")
        
        assert dt.year == 2026
        assert dt.hour == 14

    def test_parse_date_only(self):
        """Parse date seule."""
        from src.services.calendar_sync import ICalGenerator
        
        dt = ICalGenerator._parse_ical_datetime("20260201")
        
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 1


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncEdgeCases:
    """Tests pour cas limites."""

    def test_generate_ical_empty_list(self):
        """Génération avec liste vide."""
        from src.services.calendar_sync import ICalGenerator
        
        ical = ICalGenerator.generate_ical([])
        
        assert "BEGIN:VCALENDAR" in ical
        assert "BEGIN:VEVENT" not in ical

    def test_parse_malformed_ical(self):
        """Parse iCal malformé ne crash pas."""
        from src.services.calendar_sync import ICalGenerator
        
        malformed = "Not valid iCal content"
        
        # Ne devrait pas lever d'exception
        events = ICalGenerator.parse_ical(malformed)
        
        assert events == []

    def test_event_without_external_id(self):
        """Événement sans external_id génère un UID."""
        from src.services.calendar_sync import ICalGenerator, CalendarEventExternal
        
        events = [
            CalendarEventExternal(
                title="Sans ID",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                # Pas d'external_id
            ),
        ]
        
        ical = ICalGenerator.generate_ical(events)
        
        # Un UID est quand même généré
        assert "UID:" in ical

    def test_config_ical_url_provider(self):
        """Config pour URL iCal générique."""
        from src.services.calendar_sync import (
            ExternalCalendarConfig, 
            CalendarProvider
        )
        
        config = ExternalCalendarConfig(
            user_id="user1",
            provider=CalendarProvider.ICAL_URL,
            ical_url="https://calendar.example.com/feed.ics",
        )
        
        assert config.ical_url == "https://calendar.example.com/feed.ics"
        assert config.provider == CalendarProvider.ICAL_URL
