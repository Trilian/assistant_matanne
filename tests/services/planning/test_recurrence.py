"""Tests pour le service de récurrence."""

from datetime import date, datetime, timedelta

import pytest

from src.services.planning.recurrence import (
    JOURS_SEMAINE,
    OPTIONS_RECURRENCE,
    ServiceRecurrence,
    TypeRecurrence,
    format_recurrence,
    obtenir_service_recurrence,
)


class TestTypeRecurrence:
    """Tests pour l'enum TypeRecurrence."""

    def test_valeurs_enum(self):
        """TypeRecurrence contient les bonnes valeurs."""
        assert TypeRecurrence.AUCUNE == "none"
        assert TypeRecurrence.QUOTIDIEN == "daily"
        assert TypeRecurrence.HEBDOMADAIRE == "weekly"
        assert TypeRecurrence.MENSUEL == "monthly"
        assert TypeRecurrence.ANNUEL == "yearly"

    def test_options_recurrence(self):
        """OPTIONS_RECURRENCE a 5 entrées."""
        assert len(OPTIONS_RECURRENCE) == 5


class TestJoursSemaine:
    """Tests pour JOURS_SEMAINE."""

    def test_7_jours(self):
        """JOURS_SEMAINE contient 7 jours."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == (0, "Lun")
        assert JOURS_SEMAINE[6] == (6, "Dim")


class TestFormatRecurrence:
    """Tests pour format_recurrence."""

    def test_format_sans_recurrence(self):
        """Event sans récurrence retourne chaîne vide."""
        from unittest.mock import MagicMock

        event = MagicMock()
        event.recurrence_type = None
        assert format_recurrence(event) == ""

    def test_format_recurrence_none_value(self):
        """Event avec type 'none' retourne chaîne vide."""
        from unittest.mock import MagicMock

        event = MagicMock()
        event.recurrence_type = "none"
        assert format_recurrence(event) == ""


class TestServiceRecurrence:
    """Tests pour ServiceRecurrence."""

    def test_singleton_factory(self):
        """obtenir_service_recurrence retourne une instance."""
        service = obtenir_service_recurrence()
        assert isinstance(service, ServiceRecurrence)

    def test_generer_occurrences_sans_recurrence(self):
        """generer_occurrences sans récurrence retourne liste vide."""
        from unittest.mock import MagicMock

        service = ServiceRecurrence()
        event = MagicMock()
        event.recurrence_type = None

        result = service.generer_occurrences(
            event,
            date.today(),
            date.today() + timedelta(days=7),
        )
        assert result == []
