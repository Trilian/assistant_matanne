"""
Tests du package calendar_sync - Schémas Pydantic.

Tests de validation des modèles de données pour la synchronisation calendrier.
"""

from datetime import datetime

from src.services.famille.calendrier.schemas import (
    CalendarEventExternal,
    ConfigCalendrierExterne,
    DirectionSync,
    FournisseurCalendrier,
    SyncResult,
)


class TestCalendarProvider:
    """Tests pour l'enum FournisseurCalendrier."""

    def test_providers_disponibles(self):
        """Vérifie les fournisseurs supportés."""
        assert FournisseurCalendrier.GOOGLE == "google"
        assert FournisseurCalendrier.APPLE == "apple"
        assert FournisseurCalendrier.OUTLOOK == "outlook"
        assert FournisseurCalendrier.ICAL_URL == "ical_url"

    def test_provider_depuis_valeur(self):
        """Création depuis une valeur string."""
        provider = FournisseurCalendrier("google")
        assert provider == FournisseurCalendrier.GOOGLE


class TestSyncDirection:
    """Tests pour l'enum DirectionSync."""

    def test_directions_disponibles(self):
        """Vérifie les directions de sync."""
        assert DirectionSync.IMPORT_ONLY == "import"
        assert DirectionSync.EXPORT_ONLY == "export"
        assert DirectionSync.BIDIRECTIONAL == "both"


class TestExternalCalendarConfig:
    """Tests pour ConfigCalendrierExterne."""

    def test_creation_minimale(self):
        """Création avec les champs requis uniquement."""
        config = ConfigCalendrierExterne(user_id="user123", provider=FournisseurCalendrier.GOOGLE)

        assert config.user_id == "user123"
        assert config.provider == FournisseurCalendrier.GOOGLE
        assert config.name == "Mon calendrier"
        assert config.is_active is True
        assert len(config.id) == 12

    def test_creation_complete(self):
        """Création avec tous les champs."""
        now = datetime.now()
        config = ConfigCalendrierExterne(
            user_id="user456",
            provider=FournisseurCalendrier.OUTLOOK,
            name="Calendrier travail",
            calendar_id="cal_abc123",
            sync_direction=DirectionSync.EXPORT_ONLY,
            sync_meals=True,
            sync_activities=False,
            sync_events=True,
            last_sync=now,
            is_active=True,
        )

        assert config.name == "Calendrier travail"
        assert config.calendar_id == "cal_abc123"
        assert config.sync_direction == DirectionSync.EXPORT_ONLY
        assert config.sync_activities is False
        assert config.last_sync == now

    def test_config_ical_url(self):
        """Configuration pour un calendrier iCal URL."""
        config = ConfigCalendrierExterne(
            user_id="user789",
            provider=FournisseurCalendrier.ICAL_URL,
            name="Vacances scolaires",
            ical_url="https://example.com/calendar.ics",
        )

        assert config.ical_url == "https://example.com/calendar.ics"
        assert config.calendar_id == ""  # Non utilisé pour iCal URL

    def test_valeurs_defaut_oauth(self):
        """Les tokens OAuth sont vides par défaut."""
        config = ConfigCalendrierExterne(user_id="test", provider=FournisseurCalendrier.GOOGLE)

        assert config.access_token == ""
        assert config.refresh_token == ""
        assert config.token_expiry is None

    def test_id_unique_genere(self):
        """Chaque config a un ID unique."""
        config1 = ConfigCalendrierExterne(user_id="u1", provider=FournisseurCalendrier.GOOGLE)
        config2 = ConfigCalendrierExterne(user_id="u2", provider=FournisseurCalendrier.GOOGLE)

        assert config1.id != config2.id


class TestCalendarEventExternal:
    """Tests pour CalendarEventExternal."""

    def test_creation_evenement_minimal(self):
        """Création d'un événement simple."""
        event = CalendarEventExternal(
            title="Réunion",
            start_time=datetime(2026, 2, 10, 14, 0),
            end_time=datetime(2026, 2, 10, 15, 0),
        )

        assert event.title == "Réunion"
        assert event.all_day is False
        assert event.description == ""
        assert event.location == ""

    def test_evenement_journee_entiere(self):
        """Événement sur toute la journée."""
        event = CalendarEventExternal(
            title="Anniversaire",
            start_time=datetime(2026, 3, 15),
            end_time=datetime(2026, 3, 16),
            all_day=True,
        )

        assert event.all_day is True

    def test_evenement_avec_source(self):
        """Événement lié à un repas ou activité."""
        event = CalendarEventExternal(
            title="Dîner famille",
            start_time=datetime(2026, 2, 10, 19, 0),
            end_time=datetime(2026, 2, 10, 20, 30),
            source_type="meal",
            source_id=42,
        )

        assert event.source_type == "meal"
        assert event.source_id == 42

    def test_evenement_avec_external_id(self):
        """Événement importé avec ID externe."""
        event = CalendarEventExternal(
            external_id="google_evt_abc123",
            title="Cours de sport",
            start_time=datetime(2026, 2, 11, 18, 0),
            end_time=datetime(2026, 2, 11, 19, 30),
            location="Salle de sport",
        )

        assert event.external_id == "google_evt_abc123"
        assert event.location == "Salle de sport"

    def test_last_modified_auto(self):
        """last_modified est défini automatiquement."""
        event = CalendarEventExternal(
            title="Test", start_time=datetime.now(), end_time=datetime.now()
        )

        assert event.last_modified is not None
        assert isinstance(event.last_modified, datetime)


class TestSyncResult:
    """Tests pour SyncResult."""

    def test_resultat_defaut_echec(self):
        """Par défaut, success est False."""
        result = SyncResult()

        assert result.success is False
        assert result.message == ""
        assert result.events_imported == 0

    def test_resultat_succes(self):
        """Résultat de synchronisation réussie."""
        result = SyncResult(
            success=True,
            message="Synchronisation complète",
            events_imported=5,
            events_exported=3,
            events_updated=2,
            duration_seconds=1.5,
        )

        assert result.success is True
        assert result.events_imported == 5
        assert result.events_exported == 3
        assert result.duration_seconds == 1.5

    def test_resultat_avec_erreurs(self):
        """Résultat avec erreurs."""
        result = SyncResult(
            success=False,
            message="Synchronisation partielle",
            events_imported=2,
            errors=["Token expiré", "Événement invalide"],
        )

        assert result.success is False
        assert len(result.errors) == 2
        assert "Token expiré" in result.errors

    def test_resultat_avec_conflits(self):
        """Résultat avec conflits détectés."""
        result = SyncResult(
            success=True,
            message="Sync avec conflits",
            conflicts=[
                {"event_id": "e1", "type": "date_mismatch"},
                {"event_id": "e2", "type": "deleted_remotely"},
            ],
        )

        assert len(result.conflicts) == 2
        assert result.conflicts[0]["type"] == "date_mismatch"
