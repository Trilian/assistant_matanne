"""Tests pour le service de templates."""

from datetime import date, timedelta

import pytest

from src.services.cuisine.planning.templates import (
    JOURS_SEMAINE,
    ServiceTemplates,
    obtenir_service_templates,
)


class TestJoursSemaine:
    """Tests pour JOURS_SEMAINE."""

    def test_7_jours(self):
        """JOURS_SEMAINE contient 7 jours."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"


class TestServiceTemplates:
    """Tests pour ServiceTemplates."""

    def test_singleton_factory(self):
        """obtenir_service_templates retourne une instance."""
        service = obtenir_service_templates()
        assert isinstance(service, ServiceTemplates)

    def test_get_items_par_jour_vide(self):
        """get_items_par_jour avec template vide."""
        from unittest.mock import MagicMock

        service = ServiceTemplates()
        template = MagicMock()
        template.items = []

        result = service.get_items_par_jour(template)

        assert len(result) == 7
        for jour in range(7):
            assert result[jour] == []
