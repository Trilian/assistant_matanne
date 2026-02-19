"""
Tests pour SeriesService - Service de calcul des séries (loi des séries).
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.services.jeux import (
    SEUIL_SERIES_MINIMUM,
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    SeriesService,
    get_series_service,
)


class TestSeriesServiceCalculs:
    """Tests des calculs de base."""

    def test_calculer_value(self):
        """Test calcul value = fréquence × série."""
        assert SeriesService.calculer_value(0.5, 4) == 2.0
        assert SeriesService.calculer_value(0.25, 8) == 2.0
        assert SeriesService.calculer_value(0.35, 10) == 3.5
        assert SeriesService.calculer_value(0.0, 10) == 0.0
        assert SeriesService.calculer_value(0.5, 0) == 0.0

    def test_calculer_frequence(self):
        """Test calcul fréquence = occurrences / total."""
        assert SeriesService.calculer_frequence(50, 100) == 0.5
        assert SeriesService.calculer_frequence(25, 100) == 0.25
        assert SeriesService.calculer_frequence(0, 100) == 0.0
        assert SeriesService.calculer_frequence(100, 100) == 1.0
        # Division par zéro
        assert SeriesService.calculer_frequence(50, 0) == 0.0

    def test_est_opportunite(self):
        """Test détection d'opportunité."""
        assert SeriesService.est_opportunite(2.5) is True
        assert SeriesService.est_opportunite(2.0) is True
        assert SeriesService.est_opportunite(1.9) is False
        assert SeriesService.est_opportunite(1.5, seuil=1.5) is True
        assert SeriesService.est_opportunite(3.0, seuil=2.5) is True

    def test_niveau_opportunite(self):
        """Test niveau d'opportunité pour affichage."""
        assert SeriesService.niveau_opportunite(3.0) == "🟢"  # Haute
        assert SeriesService.niveau_opportunite(2.5) == "🟢"  # Haute (seuil)
        assert SeriesService.niveau_opportunite(2.2) == "🟡"  # Moyenne
        assert SeriesService.niveau_opportunite(2.0) == "🟡"  # Moyenne (seuil)
        assert SeriesService.niveau_opportunite(1.5) == "⚪"  # Faible
        assert SeriesService.niveau_opportunite(0.5) == "⚪"  # Faible


class TestSeriesServiceFactory:
    """Tests de la factory."""

    def test_get_series_service(self):
        """Test création service via factory."""
        service = get_series_service()
        assert isinstance(service, SeriesService)

    def test_get_series_service_with_session(self):
        """Test création service avec session."""
        mock_session = MagicMock()
        service = get_series_service(mock_session)
        assert isinstance(service, SeriesService)
        assert service._session == mock_session


class TestSeriesServiceConstantes:
    """Tests des constantes."""

    def test_seuil_value_alerte(self):
        """Vérifie la valeur par défaut du seuil d'alerte."""
        assert SEUIL_VALUE_ALERTE == 2.0

    def test_seuil_value_haute(self):
        """Vérifie la valeur par défaut du seuil haute."""
        assert SEUIL_VALUE_HAUTE == 2.5

    def test_seuil_series_minimum(self):
        """Vérifie la valeur par défaut du seuil série minimum."""
        assert SEUIL_SERIES_MINIMUM == 3


class TestSeriesServiceIntegration:
    """Tests d'intégration avec mocks de base de données."""

    @pytest.fixture
    def mock_serie(self):
        """Crée un mock de SerieJeux."""
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
        serie.value = 2.0  # frequence × serie = 0.4 × 5
        return serie

    @pytest.fixture
    def mock_session(self, mock_serie):
        """Crée un mock de session SQLAlchemy."""
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
        assert service._session is None

        mock_session = MagicMock()
        service_with_session = SeriesService(mock_session)
        assert service_with_session._session == mock_session


class TestSeriesServiceCasUtilisation:
    """Tests des cas d'utilisation typiques."""

    def test_scenario_paris_domicile_mi_temps(self):
        """
        Scénario: Série de 8 matchs sans victoire domicile à la mi-temps.
        Fréquence historique: 35%
        Value attendue: 0.35 × 8 = 2.8 (haute opportunité)
        """
        frequence = 0.35
        serie = 8
        value = SeriesService.calculer_value(frequence, serie)

        assert value == 2.8
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "🟢"

    def test_scenario_loto_numero_en_retard(self):
        """
        Scénario: Numéro 23 pas sorti depuis 15 tirages.
        Fréquence théorique: 5/49 ≈ 10.2%
        Value attendue: 0.102 × 15 = 1.53 (pas encore opportunité)
        """
        frequence = 5 / 49  # Fréquence théorique Loto
        serie = 15
        value = SeriesService.calculer_value(frequence, serie)

        assert round(value, 2) == 1.53
        assert SeriesService.est_opportunite(value) is False

    def test_scenario_loto_numero_tres_en_retard(self):
        """
        Scénario: Numéro 7 pas sorti depuis 25 tirages.
        Fréquence théorique: 10.2%
        Value attendue: 0.102 × 25 = 2.55 (opportunité haute)
        """
        frequence = 5 / 49
        serie = 25
        value = SeriesService.calculer_value(frequence, serie)

        assert value > SEUIL_VALUE_HAUTE
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "🟢"

    def test_scenario_paris_nul_mi_temps(self):
        """
        Scénario: Match nul mi-temps pas arrivé depuis 6 matchs.
        Fréquence historique: 40%
        Value attendue: 0.4 × 6 = 2.4 (opportunité moyenne)
        """
        frequence = 0.40
        serie = 6
        value = SeriesService.calculer_value(frequence, serie)

        assert round(value, 10) == 2.4  # Utilise round pour éviter erreurs float
        assert SeriesService.est_opportunite(value) is True
        assert SeriesService.niveau_opportunite(value) == "🟡"


class TestSeriesServiceEdgeCases:
    """Tests des cas limites."""

    def test_frequence_zero(self):
        """Test avec fréquence à 0."""
        value = SeriesService.calculer_value(0.0, 100)
        assert value == 0.0
        assert SeriesService.est_opportunite(value) is False

    def test_serie_zero(self):
        """Test avec série à 0 (événement vient d'arriver)."""
        value = SeriesService.calculer_value(0.5, 0)
        assert value == 0.0
        assert SeriesService.est_opportunite(value) is False

    def test_frequence_cent_pourcent(self):
        """Test avec fréquence à 100% (événement arrive toujours)."""
        value = SeriesService.calculer_value(1.0, 5)
        assert value == 5.0
        assert SeriesService.est_opportunite(value) is True

    def test_tres_longue_serie(self):
        """Test avec série très longue."""
        frequence = 0.1
        serie = 50
        value = SeriesService.calculer_value(frequence, serie)

        assert value == 5.0
        assert SeriesService.niveau_opportunite(value) == "🟢"

    def test_seuil_personnalise(self):
        """Test avec seuil personnalisé."""
        # Value de 1.5, pas opportunité avec seuil par défaut
        assert SeriesService.est_opportunite(1.5, seuil=2.0) is False
        # Mais opportunité avec seuil abaissé
        assert SeriesService.est_opportunite(1.5, seuil=1.5) is True
        assert SeriesService.est_opportunite(1.5, seuil=1.0) is True
