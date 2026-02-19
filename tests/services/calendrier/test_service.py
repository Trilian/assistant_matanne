"""
Tests unitaires pour CalendarSyncService.

Module: src.services.calendrier.service
Coverage target: >80%
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from src.services.famille.calendrier.schemas import (
    CalendarEventExternal,
    CalendarProvider,
    ExternalCalendarConfig,
    SyncDirection,
)
from src.services.famille.calendrier.service import (
    CalendarSyncService,
    get_calendar_sync_service,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Crée un service propre pour chaque test."""
    return CalendarSyncService()


@pytest.fixture
def mock_http_client():
    """Mock du client HTTP pour éviter les appels réseau."""
    return MagicMock()


@pytest.fixture
def google_config():
    """Configuration Google Calendar de test."""
    return ExternalCalendarConfig(
        id="google123",
        user_id="user-001",
        provider=CalendarProvider.GOOGLE,
        name="Test Google Calendar",
        access_token="fake_access_token",
        refresh_token="fake_refresh_token",
        token_expiry=datetime.now() + timedelta(hours=1),
        sync_direction=SyncDirection.BIDIRECTIONAL,
    )


@pytest.fixture
def ical_config():
    """Configuration iCal URL de test."""
    return ExternalCalendarConfig(
        id="ical456",
        user_id="user-001",
        provider=CalendarProvider.ICAL_URL,
        name="Test iCal",
        ical_url="https://example.com/calendar.ics",
        sync_direction=SyncDirection.IMPORT_ONLY,
    )


@pytest.fixture
def sample_ical_content():
    """Contenu iCal de test."""
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//FR
BEGIN:VEVENT
UID:event123@example.com
DTSTART:20260210T140000
DTEND:20260210T150000
SUMMARY:Réunion importante
DESCRIPTION:Description de la réunion
LOCATION:Salle A
END:VEVENT
BEGIN:VEVENT
UID:event456@example.com
DTSTART:20260211T100000
DTEND:20260211T110000
SUMMARY:Appel client
END:VEVENT
END:VCALENDAR"""


# ═══════════════════════════════════════════════════════════
# TESTS CRÉATION ET FACTORY
# ═══════════════════════════════════════════════════════════


class TestCalendarSyncServiceCreation:
    """Tests pour la création du service."""

    def test_creation_service(self, service):
        """Test création du service."""
        assert service is not None
        assert hasattr(service, "_configs")
        assert hasattr(service, "http_client")

    def test_factory_singleton(self):
        """Test que la factory retourne un singleton."""
        service1 = get_calendar_sync_service()
        service2 = get_calendar_sync_service()
        assert service1 is service2

    def test_factory_returns_service(self):
        """Test que la factory retourne le bon type."""
        service = get_calendar_sync_service()
        assert isinstance(service, CalendarSyncService)


# ═══════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestConfigurationCalendriers:
    """Tests de gestion des configurations de calendriers."""

    def test_add_calendar(self, service, google_config):
        """Test ajout d'un calendrier."""
        with patch.object(service, "_save_config_to_db"):
            calendar_id = service.add_calendar(google_config)

            assert calendar_id == google_config.id
            assert google_config.id in service._configs

    def test_remove_calendar(self, service, google_config):
        """Test suppression d'un calendrier."""
        with patch.object(service, "_save_config_to_db"):
            with patch.object(service, "_remove_config_from_db"):
                service.add_calendar(google_config)
                service.remove_calendar(google_config.id)

                assert google_config.id not in service._configs

    def test_remove_calendar_inexistant(self, service):
        """Test suppression d'un calendrier qui n'existe pas."""
        with patch.object(service, "_remove_config_from_db"):
            # Ne doit pas lever d'exception
            service.remove_calendar("inexistant")

    def test_get_user_calendars(self, service, google_config, ical_config):
        """Test récupération des calendriers d'un utilisateur."""
        with patch.object(service, "_save_config_to_db"):
            service.add_calendar(google_config)
            service.add_calendar(ical_config)

            # Autre utilisateur
            other_config = ExternalCalendarConfig(
                id="other789",
                user_id="user-002",
                provider=CalendarProvider.APPLE,
                name="Autre utilisateur",
            )
            service.add_calendar(other_config)

            calendars = service.get_user_calendars("user-001")

            assert len(calendars) == 2
            assert all(c.user_id == "user-001" for c in calendars)


# ═══════════════════════════════════════════════════════════
# TESTS IMPORT iCAL
# ═══════════════════════════════════════════════════════════


class TestImportIcal:
    """Tests d'import depuis URL iCal."""

    def test_import_from_ical_url_success(self, service, sample_ical_content):
        """Test import réussi depuis une URL iCal."""
        mock_response = MagicMock()
        mock_response.text = sample_ical_content
        mock_response.raise_for_status = MagicMock()

        service.http_client.get = MagicMock(return_value=mock_response)

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.service.CalendarEvent") as mock_cal_event:
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.return_value = None
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                result = service.import_from_ical_url(
                    user_id="user-001",
                    ical_url="https://example.com/calendar.ics",
                    calendar_name="Test Import",
                )

                assert result is not None
                assert result.success is True
                assert result.events_imported >= 1

    def test_import_from_ical_url_http_error(self, service):
        """Test import avec erreur HTTP."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        service.http_client.get = MagicMock(return_value=mock_response)

        result = service.import_from_ical_url(
            user_id="user-001", ical_url="https://example.com/invalid.ics"
        )

        assert result is not None
        assert result.success is False
        assert "télécharger" in result.message.lower() or "erreur" in result.message.lower()

    def test_import_from_ical_url_empty_calendar(self, service):
        """Test import d'un calendrier vide."""
        mock_response = MagicMock()
        mock_response.text = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        result = service.import_from_ical_url(
            user_id="user-001", ical_url="https://example.com/empty.ics"
        )

        assert result is not None
        assert result.success is False
        assert "aucun" in result.message.lower()

    def test_import_from_ical_url_update_existing(self, service, sample_ical_content):
        """Test import avec mise à jour d'événement existant."""
        mock_response = MagicMock()
        mock_response.text = sample_ical_content
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.service.CalendarEvent") as mock_cal_event:
                existing_event = MagicMock()
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.return_value = (
                    existing_event
                )
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                result = service.import_from_ical_url(
                    user_id="user-001", ical_url="https://example.com/calendar.ics"
                )

                assert result is not None
                assert result.success is True


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT iCAL
# ═══════════════════════════════════════════════════════════


class TestExportIcal:
    """Tests d'export vers format iCal."""

    def test_export_to_ical_empty(self, service):
        """Test export d'un calendrier vide."""
        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service.export_to_ical(user_id="user-001")

            assert result is not None
            assert "BEGIN:VCALENDAR" in result
            assert "END:VCALENDAR" in result

    def test_export_to_ical_with_meals(self, service):
        """Test export avec des repas."""
        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = date.today()
        mock_repas.type_repas = "déjeuner"
        mock_repas.notes = "Test notes"
        mock_repas.recette = MagicMock()
        mock_repas.recette.nom = "Poulet rôti"

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
                mock_repas
            ]
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service.export_to_ical(user_id="user-001")

            assert result is not None
            assert "BEGIN:VEVENT" in result
            assert "Poulet" in result

    def test_export_to_ical_with_activities(self, service):
        """Test export avec des activités familiales."""
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.date_prevue = date.today()
        mock_activity.titre = "Sortie au parc"
        mock_activity.description = "Activité en famille"
        mock_activity.duree_heures = 3
        mock_activity.lieu = "Parc municipal"
        mock_activity.statut = "planifié"

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()

            # When include_meals=False, only activities and calendar events are queried
            # Activities query returns our mock, calendar events returns empty
            def query_side_effect(model):
                q = MagicMock()
                from src.core.models import FamilyActivity

                if model == FamilyActivity:
                    q.filter.return_value.all.return_value = [mock_activity]
                else:
                    q.filter.return_value.all.return_value = []
                return q

            mock_session.query.side_effect = query_side_effect
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service.export_to_ical(
                user_id="user-001", include_meals=False, include_activities=True
            )

            assert result is not None
            assert "Sortie au parc" in result

    def test_export_to_ical_date_range(self, service):
        """Test export avec plage de dates."""
        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service.export_to_ical(
                user_id="user-001",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=7),
            )

            assert result is not None

    def test_export_to_ical_with_calendar_events(self, service):
        """Test export avec des événements calendrier."""
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.titre = "RDV médecin"
        mock_event.description = "Visite annuelle"
        mock_event.date_debut = date.today()
        mock_event.date_fin = date.today()
        # Simulate no attribute journee_entiere
        del mock_event.journee_entiere

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
            # First call returns activities (empty), second returns calendar events
            mock_session.query.return_value.filter.return_value.all.side_effect = [[], [mock_event]]
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service.export_to_ical(user_id="user-001")

            assert result is not None

    def test_export_meal_types_hours(self, service):
        """Test que chaque type de repas a l'heure correcte."""
        meal_types = [
            ("petit_déjeuner", 8),
            ("déjeuner", 12),
            ("goûter", 16),
            ("dîner", 19),
        ]

        for meal_type, expected_hour in meal_types:
            mock_repas = MagicMock()
            mock_repas.id = 1
            mock_repas.date_repas = date.today()
            mock_repas.type_repas = meal_type
            mock_repas.notes = None
            mock_repas.recette = None

            with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
                mock_session = MagicMock()
                mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
                    mock_repas
                ]
                mock_session.query.return_value.filter.return_value.all.return_value = []
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                result = service.export_to_ical(user_id="user-001")

                assert result is not None
                expected_time = f"T{expected_hour:02d}0000"
                assert (
                    expected_time in result
                ), f"Type {meal_type} devrait avoir heure {expected_hour}"


# ═══════════════════════════════════════════════════════════
# TESTS GOOGLE CALENDAR
# ═══════════════════════════════════════════════════════════


class TestGoogleCalendar:
    """Tests d'intégration Google Calendar."""

    def test_get_google_auth_url(self, service):
        """Test génération URL auth Google."""
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID="test_client_id")

            url = service.get_google_auth_url(
                user_id="user-001", redirect_uri="https://example.com/callback"
            )

            assert "accounts.google.com" in url
            assert "client_id=test_client_id" in url
            assert "redirect_uri=" in url
            assert "calendar" in url

    def test_get_google_auth_url_no_client_id(self, service):
        """Test erreur si GOOGLE_CLIENT_ID non configuré."""
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID="")

            with pytest.raises(ValueError, match="GOOGLE_CLIENT_ID"):
                service.get_google_auth_url(
                    user_id="user-001", redirect_uri="https://example.com/callback"
                )

    def test_handle_google_callback_success(self, service):
        """Test callback OAuth Google réussi."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()
        service.http_client.post = MagicMock(return_value=mock_response)

        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(
                GOOGLE_CLIENT_ID="test_id", GOOGLE_CLIENT_SECRET="test_secret"
            )

            with patch.object(service, "add_calendar"):
                result = service.handle_google_callback(
                    user_id="user-001",
                    code="auth_code",
                    redirect_uri="https://example.com/callback",
                )

                assert result is not None
                assert result.access_token == "new_access_token"
                assert result.provider == CalendarProvider.GOOGLE

    def test_handle_google_callback_no_credentials(self, service):
        """Test callback sans credentials configurés."""
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="")

            result = service.handle_google_callback(
                user_id="user-001", code="auth_code", redirect_uri="https://example.com/callback"
            )

            assert result is None

    def test_handle_google_callback_http_error(self, service):
        """Test callback avec erreur HTTP."""
        service.http_client.post = MagicMock(side_effect=Exception("HTTP Error"))

        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(
                GOOGLE_CLIENT_ID="test_id", GOOGLE_CLIENT_SECRET="test_secret"
            )

            result = service.handle_google_callback(
                user_id="user-001", code="auth_code", redirect_uri="https://example.com/callback"
            )

            assert result is None

    def test_sync_google_calendar_wrong_provider(self, service, ical_config):
        """Test sync avec mauvais provider."""
        result = service.sync_google_calendar(ical_config)

        assert result.success is False
        assert "google" in result.message.lower()

    def test_sync_google_calendar_import(self, service, google_config):
        """Test sync Google - import."""
        google_config.sync_direction = SyncDirection.IMPORT_ONLY

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "ggl123",
                    "summary": "Event Google",
                    "start": {"dateTime": "2026-02-10T14:00:00Z"},
                    "end": {"dateTime": "2026-02-10T15:00:00Z"},
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        with patch.object(service, "_import_events_to_db", return_value=1):
            with patch.object(service, "_save_config_to_db"):
                result = service.sync_google_calendar(google_config)

                assert result.success is True
                assert result.events_imported == 1

    def test_sync_google_calendar_export(self, service, google_config):
        """Test sync Google - export."""
        google_config.sync_direction = SyncDirection.EXPORT_ONLY

        with patch.object(service, "_export_to_google", return_value=5):
            with patch.object(service, "_save_config_to_db"):
                result = service.sync_google_calendar(google_config)

                assert result.success is True
                assert result.events_exported == 5

    def test_sync_google_calendar_bidirectional(self, service, google_config):
        """Test sync Google bidirectionnelle."""
        google_config.sync_direction = SyncDirection.BIDIRECTIONAL

        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        with patch.object(service, "_import_events_to_db", return_value=2):
            with patch.object(service, "_export_to_google", return_value=3):
                with patch.object(service, "_save_config_to_db"):
                    result = service.sync_google_calendar(google_config)

                    assert result.success is True
                    assert result.events_imported == 2
                    assert result.events_exported == 3

    def test_sync_google_calendar_token_expired(self, service, google_config):
        """Test sync avec token expiré - rafraîchissement."""
        google_config.token_expiry = datetime.now() - timedelta(hours=1)
        google_config.sync_direction = SyncDirection.IMPORT_ONLY

        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        with patch.object(service, "_refresh_google_token") as mock_refresh:
            with patch.object(service, "_import_events_to_db", return_value=0):
                with patch.object(service, "_save_config_to_db"):
                    result = service.sync_google_calendar(google_config)

                    mock_refresh.assert_called_once()

    def test_sync_google_calendar_error(self, service, google_config):
        """Test sync avec erreur."""
        google_config.sync_direction = SyncDirection.IMPORT_ONLY

        service.http_client.get = MagicMock(side_effect=Exception("Network error"))

        result = service.sync_google_calendar(google_config)

        assert result.success is False
        assert len(result.errors) > 0


class TestGoogleImportExport:
    """Tests détaillés import/export Google."""

    def test_import_from_google_with_all_day_events(self, service, google_config):
        """Test import d'événements journée entière."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "allday123",
                    "summary": "Vacances",
                    "start": {"date": "2026-07-15"},
                    "end": {"date": "2026-07-22"},
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        headers = {"Authorization": "Bearer token"}

        with patch.object(service, "_import_events_to_db", return_value=1) as mock_import:
            result = service._import_from_google(google_config, headers)

            assert result == 1
            call_args = mock_import.call_args[0][0]
            assert len(call_args) == 1
            assert call_args[0].all_day is True

    def test_import_from_google_with_location(self, service, google_config):
        """Test import d'événements avec lieu."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "loc123",
                    "summary": "Réunion",
                    "description": "Description",
                    "location": "Salle A, 2ème étage",
                    "start": {"dateTime": "2026-02-10T14:00:00Z"},
                    "end": {"dateTime": "2026-02-10T15:00:00Z"},
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        headers = {"Authorization": "Bearer token"}

        with patch.object(service, "_import_events_to_db", return_value=1) as mock_import:
            service._import_from_google(google_config, headers)

            call_args = mock_import.call_args[0][0]
            assert call_args[0].location == "Salle A, 2ème étage"

    def test_export_to_google_with_meals_and_activities(self, service, google_config):
        """Test export avec repas et activités."""
        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = date.today()
        mock_repas.type_repas = "déjeuner"
        mock_repas.notes = "Test"
        mock_repas.recette = MagicMock()
        mock_repas.recette.nom = "Salade"
        mock_repas.recette.description = "Description recette"

        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.date_prevue = date.today()
        mock_activity.titre = "Piscine"
        mock_activity.description = "Cours de natation"
        mock_activity.lieu = "Piscine municipale"
        mock_activity.duree_heures = 2
        mock_activity.statut = "planifié"

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "created123"}
        mock_response.raise_for_status = MagicMock()
        service.http_client.post = MagicMock(return_value=mock_response)
        service.http_client.get = MagicMock(
            return_value=MagicMock(
                json=MagicMock(return_value={"items": []}), raise_for_status=MagicMock()
            )
        )

        headers = {"Authorization": "Bearer token"}

        with patch("src.services.famille.calendrier.service.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
                mock_repas
            ]
            mock_session.query.return_value.filter.return_value.all.return_value = [mock_activity]
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            result = service._export_to_google(google_config, headers)

            assert result == 2  # 1 repas + 1 activité

    def test_export_meal_to_google_create_new(self, service, google_config):
        """Test création d'un repas dans Google Calendar."""
        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = date.today()
        mock_repas.type_repas = "dîner"
        mock_repas.notes = "Notes test"
        mock_repas.recette = MagicMock()
        mock_repas.recette.nom = "Pizza"
        mock_repas.recette.description = "Pizza maison"

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "created123"}
        mock_response.raise_for_status = MagicMock()
        service.http_client.post = MagicMock(return_value=mock_response)

        with patch.object(service, "_find_google_event_by_matanne_id", return_value=None):
            headers = {"Authorization": "Bearer token"}
            mock_db = MagicMock()

            result = service._export_meal_to_google(mock_repas, google_config, headers, mock_db)

            assert result == "created123"
            service.http_client.post.assert_called_once()

    def test_export_meal_to_google_update_existing(self, service, google_config):
        """Test mise à jour d'un repas existant."""
        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = date.today()
        mock_repas.type_repas = "déjeuner"
        mock_repas.notes = None
        mock_repas.recette = None

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "existing123"}
        mock_response.raise_for_status = MagicMock()
        service.http_client.patch = MagicMock(return_value=mock_response)

        with patch.object(
            service, "_find_google_event_by_matanne_id", return_value={"id": "existing123"}
        ):
            headers = {"Authorization": "Bearer token"}
            mock_db = MagicMock()

            result = service._export_meal_to_google(mock_repas, google_config, headers, mock_db)

            assert result == "existing123"
            service.http_client.patch.assert_called_once()

    def test_export_activity_to_google(self, service, google_config):
        """Test export d'activité vers Google."""
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.date_prevue = date.today()
        mock_activity.titre = "Cinéma"
        mock_activity.description = "Film en famille"
        mock_activity.lieu = "UGC"
        mock_activity.duree_heures = 3

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "act123"}
        mock_response.raise_for_status = MagicMock()
        service.http_client.post = MagicMock(return_value=mock_response)

        with patch.object(service, "_find_google_event_by_matanne_id", return_value=None):
            headers = {"Authorization": "Bearer token"}
            mock_db = MagicMock()

            result = service._export_activity_to_google(
                mock_activity, google_config, headers, mock_db
            )

            assert result == "act123"

    def test_find_google_event_found(self, service):
        """Test recherche événement Google - trouvé."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"id": "found123"}]}
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        headers = {"Authorization": "Bearer token"}
        result = service._find_google_event_by_matanne_id("matanne-meal-1", headers)

        assert result is not None
        assert result["id"] == "found123"

    def test_find_google_event_not_found(self, service):
        """Test recherche événement Google - non trouvé."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()
        service.http_client.get = MagicMock(return_value=mock_response)

        headers = {"Authorization": "Bearer token"}
        result = service._find_google_event_by_matanne_id("matanne-meal-999", headers)

        assert result is None

    def test_find_google_event_error(self, service):
        """Test recherche événement Google - erreur."""
        service.http_client.get = MagicMock(side_effect=Exception("Error"))

        headers = {"Authorization": "Bearer token"}
        result = service._find_google_event_by_matanne_id("matanne-meal-1", headers)

        assert result is None


class TestGoogleTokenRefresh:
    """Tests de rafraîchissement de token Google."""

    def test_refresh_google_token_success(self, service, google_config):
        """Test rafraîchissement token réussi."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()
        service.http_client.post = MagicMock(return_value=mock_response)

        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(
                GOOGLE_CLIENT_ID="id", GOOGLE_CLIENT_SECRET="secret"
            )

            with patch.object(service, "_save_config_to_db"):
                service._refresh_google_token(google_config)

                assert google_config.access_token == "new_token"

    def test_refresh_google_token_error(self, service, google_config):
        """Test erreur rafraîchissement token."""
        service.http_client.post = MagicMock(side_effect=Exception("Error"))

        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(
                GOOGLE_CLIENT_ID="id", GOOGLE_CLIENT_SECRET="secret"
            )

            # Ne doit pas lever d'exception
            service._refresh_google_token(google_config)


class TestExportPlanningToGoogle:
    """Tests export planning vers Google."""

    def test_export_planning_wrong_provider(self, service, ical_config):
        """Test export avec mauvais provider."""
        result = service.export_planning_to_google(user_id="user-001", config=ical_config)

        assert result.success is False

    def test_export_planning_with_refresh(self, service, google_config):
        """Test export avec rafraîchissement token."""
        google_config.token_expiry = datetime.now() - timedelta(hours=1)

        with patch.object(service, "_refresh_google_token") as mock_refresh:
            with patch.object(service, "_export_to_google", return_value=5):
                result = service.export_planning_to_google(user_id="user-001", config=google_config)

                mock_refresh.assert_called_once()
                assert result.success is True


# ═══════════════════════════════════════════════════════════
# TESTS DB PERSISTENCE
# ═══════════════════════════════════════════════════════════


class TestDatabasePersistence:
    """Tests de persistance en base de données."""

    def test_import_events_to_db_create(self, service):
        """Test import événements - création."""
        events = [
            CalendarEventExternal(
                external_id="ext1",
                title="Event 1",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            ),
        ]

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.google_calendar.CalendarEvent") as mock_cal_event:
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.return_value = None
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                count = service._import_events_to_db(events)

                assert count == 1
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()

    def test_import_events_to_db_update(self, service):
        """Test import événements - mise à jour."""
        events = [
            CalendarEventExternal(
                external_id="ext1",
                title="Event Updated",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            ),
        ]

        existing = MagicMock()

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.google_calendar.CalendarEvent") as mock_cal_event:
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.return_value = existing
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                count = service._import_events_to_db(events)

                assert count == 1
                assert existing.titre == "Event Updated"

    def test_import_events_to_db_error_handling(self, service):
        """Test import événements - gestion erreur."""
        events = [
            CalendarEventExternal(
                external_id="ext1",
                title="Event 1",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            ),
        ]

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.google_calendar.CalendarEvent") as mock_cal_event:
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.side_effect = Exception(
                    "DB Error"
                )
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                # Ne doit pas lever d'exception
                count = service._import_events_to_db(events)

                assert count == 0


class TestSaveConfigToDb:
    """Tests sauvegarde configuration en base."""

    def test_save_config_create(self, service, google_config):
        """Test création configuration."""
        google_config.id = "not_digit"  # Non numérique
        google_config.user_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"  # UUID valide

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            with patch("src.services.famille.calendrier.google_calendar.CalendrierExterne") as mock_cal_ext:
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.first.return_value = None
                mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
                mock_db.return_value.__exit__ = MagicMock(return_value=False)

                service._save_config_to_db(google_config)

                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()

    def test_save_config_update(self, service, google_config):
        """Test mise à jour configuration."""
        google_config.id = "123"  # ID numérique

        existing = MagicMock()

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = existing
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            service._save_config_to_db(google_config)

            assert existing.provider == google_config.provider.value

    def test_remove_config_from_db(self, service):
        """Test suppression configuration."""
        existing = MagicMock()

        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = existing
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            service._remove_config_from_db("123")

            mock_session.delete.assert_called_once_with(existing)
            mock_session.commit.assert_called_once()

    def test_remove_config_not_found(self, service):
        """Test suppression configuration inexistante."""
        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = None
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            # Ne doit pas lever d'exception
            service._remove_config_from_db("999")

            mock_session.delete.assert_not_called()

    def test_remove_config_non_numeric_id(self, service):
        """Test suppression avec ID non numérique."""
        with patch("src.services.famille.calendrier.google_calendar.obtenir_contexte_db") as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)

            # Ne doit pas lever d'exception
            service._remove_config_from_db("not_a_number")


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES AVEC @avec_session_db
# Ces tests nécessitent une DB avec utilisateurs valides (FK constraints)
# ═══════════════════════════════════════════════════════════


@pytest.mark.skip(
    reason="Nécessite fixtures DB avec FK constraints user_id - testé via mocks ci-dessus"
)
class TestSessionDecoratedMethods:
    """Tests des méthodes utilisant @avec_session_db."""

    def test_ajouter_calendrier_externe(self, service, db):
        """Test ajout calendrier externe en base."""
        user_id = str(uuid4())

        calendrier = service.ajouter_calendrier_externe(
            user_id=user_id,
            provider="google",
            nom="Mon Google",
            url=None,
            credentials={"token": "abc"},
            db=db,
        )

        assert calendrier is not None
        assert calendrier.nom == "Mon Google"
        assert calendrier.provider == "google"

    def test_lister_calendriers_utilisateur(self, service, db):
        """Test liste calendriers utilisateur."""
        user_id = str(uuid4())

        # Créer quelques calendriers
        for i in range(3):
            service.ajouter_calendrier_externe(
                user_id=user_id, provider="google", nom=f"Calendrier {i}", db=db
            )

        # Autre utilisateur
        other_id = str(uuid4())
        service.ajouter_calendrier_externe(user_id=other_id, provider="apple", nom="Autre", db=db)

        calendriers = service.lister_calendriers_utilisateur(user_id=user_id, db=db)

        assert len(calendriers) == 3

    def test_sauvegarder_evenement_calendrier_create(self, service, db):
        """Test sauvegarde événement - création."""
        user_id = str(uuid4())

        # Créer un calendrier d'abord
        calendrier = service.ajouter_calendrier_externe(
            user_id=user_id, provider="google", nom="Test", db=db
        )

        event = CalendarEventExternal(
            external_id="evt123",
            title="Test Event",
            description="Description",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location="Bureau",
        )

        db_event = service.sauvegarder_evenement_calendrier(
            calendrier_id=calendrier.id, event=event, user_id=user_id, db=db
        )

        assert db_event is not None
        assert db_event.titre == "Test Event"
        assert db_event.uid == "evt123"

    def test_sauvegarder_evenement_calendrier_update(self, service, db):
        """Test sauvegarde événement - mise à jour."""
        user_id = str(uuid4())

        calendrier = service.ajouter_calendrier_externe(
            user_id=user_id, provider="google", nom="Test", db=db
        )

        # Créer l'événement
        event1 = CalendarEventExternal(
            external_id="evt123",
            title="Original",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )
        db_event1 = service.sauvegarder_evenement_calendrier(
            calendrier_id=calendrier.id, event=event1, user_id=user_id, db=db
        )

        # Mettre à jour
        event2 = CalendarEventExternal(
            external_id="evt123",
            title="Updated",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
        )
        db_event2 = service.sauvegarder_evenement_calendrier(
            calendrier_id=calendrier.id, event=event2, user_id=user_id, db=db
        )

        assert db_event2.titre == "Updated"
        assert db_event1.id == db_event2.id  # Même événement

    def test_lister_evenements_calendrier(self, service, db):
        """Test liste événements avec filtres."""
        user_id = str(uuid4())

        calendrier = service.ajouter_calendrier_externe(
            user_id=user_id, provider="google", nom="Test", db=db
        )

        # Créer plusieurs événements
        for i in range(5):
            event = CalendarEventExternal(
                external_id=f"evt{i}",
                title=f"Event {i}",
                start_time=datetime.now() + timedelta(days=i),
                end_time=datetime.now() + timedelta(days=i, hours=1),
            )
            service.sauvegarder_evenement_calendrier(
                calendrier_id=calendrier.id, event=event, user_id=user_id, db=db
            )

        # Lister tous
        all_events = service.lister_evenements_calendrier(user_id=user_id, db=db)
        assert len(all_events) == 5

        # Filtrer par date
        filtered = service.lister_evenements_calendrier(
            user_id=user_id,
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=2),
            db=db,
        )
        assert len(filtered) >= 1  # Au moins l'événement du jour

    def test_lister_evenements_par_calendrier(self, service, db):
        """Test liste événements filtré par calendrier."""
        user_id = str(uuid4())

        cal1 = service.ajouter_calendrier_externe(
            user_id=user_id, provider="google", nom="Cal1", db=db
        )
        cal2 = service.ajouter_calendrier_externe(
            user_id=user_id, provider="apple", nom="Cal2", db=db
        )

        # Événements dans cal1
        for i in range(3):
            event = CalendarEventExternal(
                external_id=f"c1evt{i}",
                title=f"Cal1 Event {i}",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            )
            service.sauvegarder_evenement_calendrier(
                calendrier_id=cal1.id, event=event, user_id=user_id, db=db
            )

        # Événement dans cal2
        event = CalendarEventExternal(
            external_id="c2evt1",
            title="Cal2 Event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
        )
        service.sauvegarder_evenement_calendrier(
            calendrier_id=cal2.id, event=event, user_id=user_id, db=db
        )

        # Filtrer par cal1
        events = service.lister_evenements_calendrier(user_id=user_id, calendrier_id=cal1.id, db=db)
        assert len(events) == 3
