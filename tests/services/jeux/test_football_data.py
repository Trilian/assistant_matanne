"""
Tests pour FootballDataService - Service données Football-Data.org.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.services.jeux.football_data import (
    COMPETITIONS,
    FootballDataService,
    Match,
    ResultatFinal,
    ResultatMiTemps,
    ScoreMatch,
    StatistiquesMarcheData,
    get_football_data_service,
)


class TestFootballDataServiceFactory:
    """Tests de la factory."""

    def test_get_football_data_service(self):
        """Test création service via factory."""
        service = get_football_data_service()
        assert isinstance(service, FootballDataService)

    def test_get_football_data_service_with_api_key(self):
        """Test création service avec clé API."""
        service = get_football_data_service("test_api_key")
        assert isinstance(service, FootballDataService)
        assert service.api_key == "test_api_key"


class TestFootballDataServiceConstantes:
    """Tests des constantes."""

    def test_competitions_disponibles(self):
        """Vérifie les compétitions configurées."""
        assert "FL1" in COMPETITIONS  # Ligue 1
        assert "PL" in COMPETITIONS  # Premier League
        assert "BL1" in COMPETITIONS  # Bundesliga
        assert "SA" in COMPETITIONS  # Serie A
        assert "PD" in COMPETITIONS  # La Liga

    def test_competitions_noms(self):
        """Vérifie les noms des compétitions."""
        assert COMPETITIONS["FL1"] == "Ligue 1"
        assert COMPETITIONS["PL"] == "Premier League"


class TestScoreMatch:
    """Tests du modèle ScoreMatch."""

    def test_score_defaut(self):
        """Test score par défaut."""
        score = ScoreMatch()
        assert score.domicile_mi_temps == 0
        assert score.exterieur_mi_temps == 0
        assert score.domicile_final == 0
        assert score.exterieur_final == 0

    def test_score_avec_valeurs(self):
        """Test score avec valeurs."""
        score = ScoreMatch(
            domicile_mi_temps=1,
            exterieur_mi_temps=0,
            domicile_final=2,
            exterieur_final=1,
        )
        assert score.domicile_mi_temps == 1
        assert score.domicile_final == 2


class TestMatch:
    """Tests du modèle Match."""

    def test_match_est_termine(self):
        """Test propriété est_termine."""
        match = Match(
            id=1,
            competition="FL1",
            date_match=date(2026, 2, 15),
            equipe_domicile="PSG",
            equipe_exterieur="OM",
            statut="FINISHED",
        )
        assert match.est_termine is True

        match_en_cours = Match(
            id=2,
            competition="FL1",
            date_match=date(2026, 2, 15),
            equipe_domicile="Lyon",
            equipe_exterieur="Lille",
            statut="LIVE",
        )
        assert match_en_cours.est_termine is False


class TestFootballDataServiceCalculs:
    """Tests des calculs de statistiques."""

    @pytest.fixture
    def service(self):
        """Service avec mock HTTP."""
        return FootballDataService(api_key="test")

    @pytest.fixture
    def matchs_exemple(self):
        """Liste de matchs pour tests."""
        return [
            Match(
                id=1,
                competition="FL1",
                date_match=date(2026, 2, 10),
                equipe_domicile="PSG",
                equipe_exterieur="OM",
                resultat_mi_temps=ResultatMiTemps.DOMICILE,
                resultat_final=ResultatFinal.DOMICILE,
                statut="FINISHED",
            ),
            Match(
                id=2,
                competition="FL1",
                date_match=date(2026, 2, 11),
                equipe_domicile="Lyon",
                equipe_exterieur="Lille",
                resultat_mi_temps=ResultatMiTemps.NUL,
                resultat_final=ResultatFinal.EXTERIEUR,
                statut="FINISHED",
            ),
            Match(
                id=3,
                competition="FL1",
                date_match=date(2026, 2, 12),
                equipe_domicile="Monaco",
                equipe_exterieur="Nice",
                resultat_mi_temps=ResultatMiTemps.NUL,
                resultat_final=ResultatFinal.NUL,
                statut="FINISHED",
            ),
            Match(
                id=4,
                competition="FL1",
                date_match=date(2026, 2, 13),
                equipe_domicile="Rennes",
                equipe_exterieur="Nantes",
                resultat_mi_temps=ResultatMiTemps.DOMICILE,
                resultat_final=ResultatFinal.DOMICILE,
                statut="FINISHED",
            ),
        ]

    def test_calculer_statistiques_domicile_mi_temps(self, service, matchs_exemple):
        """Test statistiques victoire domicile mi-temps."""
        stats = service.calculer_statistiques_marche(matchs_exemple, "domicile_mi_temps")

        assert stats.marche == "domicile_mi_temps"
        assert stats.total_matchs == 4
        assert stats.nb_occurrences == 2  # PSG et Rennes
        assert stats.frequence == 0.5
        assert stats.serie_actuelle == 0  # Dernier match est domicile

    def test_calculer_statistiques_nul_mi_temps(self, service, matchs_exemple):
        """Test statistiques nul mi-temps."""
        stats = service.calculer_statistiques_marche(matchs_exemple, "nul_mi_temps")

        assert stats.marche == "nul_mi_temps"
        assert stats.total_matchs == 4
        assert stats.nb_occurrences == 2  # Lyon et Monaco
        assert stats.frequence == 0.5
        assert stats.serie_actuelle == 1  # 1 match sans nul après Monaco

    def test_calculer_statistiques_exterieur_final(self, service, matchs_exemple):
        """Test statistiques victoire extérieur finale."""
        stats = service.calculer_statistiques_marche(matchs_exemple, "exterieur_final")

        assert stats.marche == "exterieur_final"
        assert stats.total_matchs == 4
        assert stats.nb_occurrences == 1  # Lille vs Lyon
        assert stats.frequence == 0.25
        assert stats.serie_actuelle == 2  # Monaco (nul) + Rennes (dom)

    def test_calculer_statistiques_liste_vide(self, service):
        """Test avec liste vide."""
        stats = service.calculer_statistiques_marche([], "domicile_mi_temps")

        assert stats.total_matchs == 0
        assert stats.frequence == 0.0

    def test_match_correspond_marche(self, service, matchs_exemple):
        """Test correspondance marché."""
        match_dom = matchs_exemple[0]  # PSG domicile

        assert service._match_correspond_marche(match_dom, "domicile_mi_temps") is True
        assert service._match_correspond_marche(match_dom, "nul_mi_temps") is False
        assert service._match_correspond_marche(match_dom, "domicile_final") is True


class TestFootballDataServiceAPI:
    """Tests d'intégration API (mocked)."""

    @pytest.fixture
    def mock_response_data(self):
        """Données de réponse API simulées."""
        return {
            "matches": [
                {
                    "id": 123,
                    "utcDate": "2026-02-15T20:00:00Z",
                    "homeTeam": {"shortName": "PSG"},
                    "awayTeam": {"shortName": "OM"},
                    "status": "FINISHED",
                    "score": {
                        "halfTime": {"home": 1, "away": 0},
                        "fullTime": {"home": 2, "away": 1},
                    },
                }
            ]
        }

    @patch("httpx.Client.get")
    def test_obtenir_matchs_termines(self, mock_get, mock_response_data):
        """Test récupération matchs avec mock."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        service = FootballDataService(api_key="test_key")
        matchs = service.obtenir_matchs_termines("FL1")

        assert len(matchs) == 1
        assert matchs[0].equipe_domicile == "PSG"
        assert matchs[0].equipe_exterieur == "OM"
        assert matchs[0].resultat_mi_temps == ResultatMiTemps.DOMICILE
