"""
Tests unitaires pour calendrier.py

Module: src.core.models.calendrier
Contient: CalendrierExterne, EvenementCalendrier
"""

from datetime import datetime

from src.core.models.calendrier import (
    CalendrierExterne,
    DirectionSync,
    EvenementCalendrier,
    FournisseurCalendrier,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestCalendarProvider:
    """Tests pour l'énumération FournisseurCalendrier."""

    def test_valeurs_disponibles(self):
        """Vérifie que tous les providers existent."""
        assert FournisseurCalendrier.GOOGLE.value == "google"
        assert FournisseurCalendrier.APPLE.value == "apple"
        assert FournisseurCalendrier.OUTLOOK.value == "outlook"
        assert FournisseurCalendrier.ICAL_URL.value == "ical_url"


class TestSyncDirection:
    """Tests pour l'énumération DirectionSync."""

    def test_valeurs_disponibles(self):
        """Vérifie les directions de sync."""
        assert DirectionSync.IMPORT.value == "import"
        assert DirectionSync.EXPORT.value == "export"
        assert DirectionSync.BIDIRECTIONAL.value == "bidirectional"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestCalendrierExterne:
    """Tests pour le modèle CalendrierExterne."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert CalendrierExterne.__tablename__ == "calendriers_externes"

    def test_creation_instance(self):
        """Test de création d'un calendrier."""
        cal = CalendrierExterne(
            provider="google",
            nom="Calendrier famille",
        )
        assert cal.provider == "google"
        assert cal.nom == "Calendrier famille"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = CalendrierExterne.__table__.columns
        assert colonnes["enabled"].default is not None
        assert colonnes["sync_interval_minutes"].default is not None
        assert colonnes["sync_direction"].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        cal = CalendrierExterne(id=1, provider="google", nom="Mon Cal")
        result = repr(cal)
        assert "CalendrierExterne" in result
        assert "google" in result
        assert "Mon Cal" in result


class TestEvenementCalendrier:
    """Tests pour le modèle EvenementCalendrier."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert EvenementCalendrier.__tablename__ == "evenements_calendrier"

    def test_creation_instance(self):
        """Test de création d'un événement."""
        event = EvenementCalendrier(
            uid="event-123",
            titre="Réunion famille",
            date_debut=datetime(2026, 2, 15, 14, 0),
        )
        assert event.uid == "event-123"
        assert event.titre == "Réunion famille"
        assert event.date_debut.hour == 14

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = EvenementCalendrier.__table__.columns
        assert colonnes["all_day"].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        event = EvenementCalendrier(
            id=1, uid="abc", titre="Anniversaire", date_debut=datetime(2026, 3, 1)
        )
        result = repr(event)
        assert "EvenementCalendrier" in result
        assert "Anniversaire" in result
