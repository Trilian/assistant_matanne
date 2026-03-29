"""
Tests pour SeriesService - Service de calcul des sÃ©ries (loi des sÃ©ries).
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.services.jeux import (
    SEUIL_SERIES_MINIMUM,
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    SeriesService,
    obtenir_series_service,
)


class TestSeriesServiceCalculs:
    """Tests des calculs de base."""

    def test_calculer_value(self):
        """Test calcul value = frÃ©quence Ã— sÃ©rie."""
        assert SeriesService.calculer_value(0.5, 4) == 2.0
        assert SeriesService.calculer_value(0.25, 8) == 2.0
        assert SeriesService.calculer_value(0.35, 10) == 3.5
        assert SeriesService.calculer_value(0.0, 10) == 0.0
        assert SeriesService.calculer_value(0.5, 0) == 0.0

    def test_calculer_frequence(self):
        """Test calcul frÃ©quence = occurrences / total."""
        assert SeriesService.calculer_frequence(50, 100) == 0.5
        assert SeriesService.calculer_frequence(25, 100) == 0.25
        assert SeriesService.calculer_frequence(0, 100) == 0.0
        assert SeriesService.calculer_frequence(100, 100) == 1.0
        # Division par zÃ©ro
        assert SeriesService.calculer_frequence(50, 0) == 0.0

    def test_est_opportunite(self):
        """Test dÃ©tection d'opportunitÃ©."""
        assert SeriesService.est_opportunite(2.5) is True
        assert SeriesService.est_opportunite(2.0) is True
        assert SeriesService.est_opportunite(1.9) is False
        assert SeriesService.est_opportunite(1.5, seuil=1.5) is True
        assert SeriesService.est_opportunite(3.0, seuil=2.5) is True

    def test_niveau_opportunite(self):
        """Test niveau d'opportunitÃ© pour affichage."""
        assert SeriesService.niveau_opportunite(3.0) == "ðŸŸ¢"  # Haute
        assert SeriesService.niveau_opportunite(2.5) == "ðŸŸ¢"  # Haute (seuil)
        assert SeriesService.niveau_opportunite(2.2) == "ðŸŸ¡"  # Moyenne
        assert SeriesService.niveau_opportunite(2.0) == "ðŸŸ¡"  # Moyenne (seuil)
        assert SeriesService.niveau_opportunite(1.5) == "âšª"  # Faible
        assert SeriesService.niveau_opportunite(0.5) == "âšª"  # Faible


class TestSeriesServiceFactory:
    """Tests de la factory."""

    def test_get_series_service(self):
        """Test crÃ©ation service via factory."""
        service = obtenir_series_service()
        assert isinstance(service, SeriesService)


class TestSeriesServiceConstantes:
    """Tests des constantes."""

    def test_seuil_value_alerte(self):
        """VÃ©rifie la valeur par dÃ©faut du seuil d'alerte."""
        assert SEUIL_VALUE_ALERTE == 2.0

    def test_seuil_value_haute(self):
        """VÃ©rifie la valeur par dÃ©faut du seuil haute."""
        assert SEUIL_VALUE_HAUTE == 2.5

    def test_seuil_series_minimum(self):
        """VÃ©rifie la valeur par dÃ©faut du seuil sÃ©rie minimum."""
        assert SEUIL_SERIES_MINIMUM == 3


class TestSeriesServiceIntegration:
    """Tests d'intÃ©gration avec mocks de base de donnÃ©es."""

    @pytest.fixture
    def mock_serie(self):
        """CrÃ©e un mock de SerieJeux."""
        serie = MagicMock()
        serie.id = 1
        serie.type_jeu = "paris"
        serie.championnat = "Ligue 1"
        serie.marche = "domicile_mi_temps"
        serie.serie_actuelle = 5
        serie.frequence = 0.4
        serie.nb_occurrences = 40
        serie.nb_total = 100
        serie.derniere_occurrence = date(2026, 2, 10)
        serie.value = 2.0  # frequence Ã— serie = 0.4 Ã— 5
        return serie

    @pytest.fixture
    def mock_session(self, mock_serie):
        """CrÃ©e un mock de session SQLAlchemy."""
        session = MagicMock()
        query = MagicMock()
        query.filter.return_value = query
        query.first.return_value = mock_serie
        query.all.return_value = [mock_serie]
        session.query.return_value = query
        return session

    def test_service_init(self):
        """Test initialisation du service."""
        service = SeriesService()
        assert isinstance(service, SeriesService)


class TestSeriesServiceCasUtilisation:
    """Tests des cas d'utilisation typiques."""

    def test_scenario_paris_domicile_mi_temps(self):
        """
        ScÃ©nario: SÃ©rie de 8 matchs sans victoire domicile Ã  la mi-temps.
        FrÃ©quence historique: 35%
        Value attendue: 0.35 Ã— 8 = 2.8 (haute opportunitÃ©)
        """
        frequence = 0.35
        serie = 8
        value = SeriesService.calculer_value(frequence, serie)

        assert value == 2.8
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "ðŸŸ¢"

    def test_scenario_loto_numero_en_retard(self):
        """
        ScÃ©nario: NumÃ©ro 23 pas sorti depuis 15 tirages.
        FrÃ©quence thÃ©orique: 5/49 â‰ˆ 10.2%
        Value attendue: 0.102 Ã— 15 = 1.53 (pas encore opportunitÃ©)
        """
        frequence = 5 / 49  # FrÃ©quence thÃ©orique Loto
        serie = 15
        value = SeriesService.calculer_value(frequence, serie)

        assert round(value, 2) == 1.53
        assert SeriesService.est_opportunite(value) is False

    def test_scenario_loto_numero_tres_en_retard(self):
        """
        ScÃ©nario: NumÃ©ro 7 pas sorti depuis 25 tirages.
        FrÃ©quence thÃ©orique: 10.2%
        Value attendue: 0.102 Ã— 25 = 2.55 (opportunitÃ© haute)
        """
        frequence = 5 / 49
        serie = 25
        value = SeriesService.calculer_value(frequence, serie)

        assert value > SEUIL_VALUE_HAUTE
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "ðŸŸ¢"

    def test_scenario_paris_nul_mi_temps(self):
        """
        ScÃ©nario: Match nul mi-temps pas arrivÃ© depuis 6 matchs.
        FrÃ©quence historique: 40%
        Value attendue: 0.4 Ã— 6 = 2.4 (opportunitÃ© moyenne)
        """
        frequence = 0.40
        serie = 6
        value = SeriesService.calculer_value(frequence, serie)

        assert round(value, 10) == 2.4  # Utilise round pour Ã©viter erreurs float
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "ðŸŸ¡"


class TestSeriesServiceEdgeCases:
    """Tests des cas limites."""

    def test_frequence_zero(self):
        """Test avec frÃ©quence Ã  0."""
        value = SeriesService.calculer_value(0.0, 100)
        assert value == 0.0
        assert SeriesService.est_opportunite(value) is False

    def test_serie_zero(self):
        """Test avec sÃ©rie Ã  0 (Ã©vÃ©nement vient d'arriver)."""
        value = SeriesService.calculer_value(0.5, 0)
        assert value == 0.0
        assert SeriesService.est_opportunite(value) is False

    def test_frequence_cent_pourcent(self):
        """Test avec frÃ©quence Ã  100% (Ã©vÃ©nement arrive toujours)."""
        value = SeriesService.calculer_value(1.0, 5)
        assert value == 5.0
        assert SeriesService.est_opportunite(value) is True

    def test_tres_longue_serie(self):
        """Test avec sÃ©rie trÃ¨s longue."""
        frequence = 0.1
        serie = 50
        value = SeriesService.calculer_value(frequence, serie)

        assert value == 5.0
        assert SeriesService.niveau_opportunite(value) == "ðŸŸ¢"

    def test_seuil_personnalise(self):
        """Test avec seuil personnalisÃ©."""
        # Value de 1.5, pas opportunitÃ© avec seuil par dÃ©faut
        assert SeriesService.est_opportunite(1.5, seuil=2.0) is False
        # Mais opportunitÃ© avec seuil abaissÃ©
        assert SeriesService.est_opportunite(1.5, seuil=1.5) is True
        assert SeriesService.est_opportunite(1.5, seuil=1.0) is True

