"""Tests pour le service de rappels."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.cuisine.planning.rappels import (
    OPTIONS_RAPPEL,
    ServiceRappels,
    format_rappel,
    obtenir_service_rappels,
)


class TestOptionsRappel:
    """Tests pour les options de rappel."""

    def test_options_rappel_structure(self):
        """OPTIONS_RAPPEL contient les bonnes valeurs."""
        assert len(OPTIONS_RAPPEL) >= 5
        assert (None, "Aucun rappel") in OPTIONS_RAPPEL
        assert (15, "15 minutes avant") in OPTIONS_RAPPEL
        assert (60, "1 heure avant") in OPTIONS_RAPPEL

    def test_format_rappel_none(self):
        """format_rappel avec None retourne 'Aucun rappel'."""
        assert format_rappel(None) == "Aucun rappel"

    def test_format_rappel_15(self):
        """format_rappel avec 15 retourne le bon texte."""
        assert format_rappel(15) == "15 minutes avant"

    def test_format_rappel_inconnu(self):
        """format_rappel avec valeur inconnue retourne 'Aucun rappel'."""
        assert format_rappel(999) == "Aucun rappel"


class TestServiceRappels:
    """Tests pour ServiceRappels."""

    def test_singleton_factory(self):
        """obtenir_service_rappels retourne une instance."""
        service = obtenir_service_rappels()
        assert isinstance(service, ServiceRappels)

    @patch("src.services.cuisine.planning.rappels.obtenir_service_webpush")
    def test_envoyer_rappels_vide(self, mock_webpush):
        """envoyer_rappels_en_attente avec aucun rappel retourne 0."""
        service = ServiceRappels()
        with patch.object(service, "get_rappels_imminents", return_value=[]):
            result = service.envoyer_rappels_en_attente()
            assert result == 0
