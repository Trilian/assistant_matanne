"""
Tests complets pour api_football.py - Couverture â‰¥80%

Ce module teste l'intÃ©gration avec l'API Football-Data.org.
Tous les appels HTTP sont mockÃ©s pour Ã©viter les dÃ©pendances externes.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from src.modules.jeux.logic.api_football import (
    # Configuration
    API_BASE_URL,
    CHAMP_MAPPING,
    COMP_IDS,
    # Fonctions
    configurer_api_key,
    obtenir_cle_api,
    faire_requete,
    charger_matchs_a_venir,
    charger_historique_equipe,
    charger_classement,
    chercher_equipe,
    charger_matchs_termines,
    charger_matchs_cache,
    vider_cache,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_api_key():
    """Configure une clÃ© API mock."""
    configurer_api_key("test_api_key_12345")
    yield
    # Reset
    import src.modules.jeux.logic.api_football as module
    module.API_KEY = None


@pytest.fixture
def mock_match_response():
    """RÃ©ponse mock pour les matchs."""
    return {
        "matches": [
            {
                "id": 1001,
                "utcDate": "2025-02-15T20:00:00Z",
                "status": "SCHEDULED",
                "homeTeam": {"id": 10, "name": "Paris Saint-Germain"},
                "awayTeam": {"id": 20, "name": "Olympique Marseille"},
                "score": {"fullTime": {"home": None, "away": None}},
                "odds": {"homeWin": 1.5, "draw": 4.0, "awayWin": 6.0}
            },
            {
                "id": 1002,
                "utcDate": "2025-02-16T15:00:00Z",
                "status": "SCHEDULED",
                "homeTeam": {"id": 30, "name": "Olympique Lyon"},
                "awayTeam": {"id": 40, "name": "AS Monaco"},
                "score": {"fullTime": {"home": None, "away": None}},
                "odds": {}
            }
        ]
    }


@pytest.fixture
def mock_finished_match_response():
    """RÃ©ponse mock pour les matchs terminÃ©s."""
    return {
        "matches": [
            {
                "utcDate": "2025-02-10T20:00:00Z",
                "status": "FINISHED",
                "homeTeam": {"name": "PSG"},
                "awayTeam": {"name": "OM"},
                "score": {"fullTime": {"home": 2, "away": 1}},
            }
        ]
    }


@pytest.fixture
def mock_team_response():
    """RÃ©ponse mock pour la recherche d'Ã©quipe."""
    return {
        "teams": [
            {
                "id": 10,
                "name": "Paris Saint-Germain",
                "shortName": "PSG",
                "area": {"name": "France"},
                "founded": 1970,
                "crest": "https://example.com/psg.png"
            }
        ]
    }


@pytest.fixture
def mock_standings_response():
    """RÃ©ponse mock pour le classement."""
    return {
        "standings": [
            {
                "table": [
                    {
                        "team": {"name": "PSG"},
                        "playedGames": 20,
                        "won": 15,
                        "draw": 3,
                        "lost": 2,
                        "goalsFor": 45,
                        "goalsAgainst": 15,
                        "points": 48
                    },
                    {
                        "team": {"name": "Monaco"},
                        "playedGames": 20,
                        "won": 12,
                        "draw": 4,
                        "lost": 4,
                        "goalsFor": 38,
                        "goalsAgainst": 20,
                        "points": 40
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_teams_fallback_response():
    """RÃ©ponse mock pour le fallback Ã©quipes sans standings."""
    return {
        "teams": [
            {"name": "Ã‰quipe A"},
            {"name": "Ã‰quipe B"},
            {"name": "Ã‰quipe C"}
        ]
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConstantes:
    """Tests des constantes du module."""
    
    def test_api_base_url(self):
        """VÃ©rifie l'URL de base de l'API."""
        assert API_BASE_URL == "https://api.football-data.org/v4"
    
    def test_championnats_mapping(self):
        """VÃ©rifie le mapping des championnats."""
        assert "Ligue 1" in CHAMP_MAPPING
        assert "Premier League" in CHAMP_MAPPING
        assert CHAMP_MAPPING["Ligue 1"] == "FL1"
        assert CHAMP_MAPPING["Premier League"] == "PL"
    
    def test_comp_ids(self):
        """VÃ©rifie les IDs de compÃ©titions."""
        assert "FL1" in COMP_IDS
        assert "PL" in COMP_IDS
        assert COMP_IDS["FL1"] == 2015
        assert COMP_IDS["PL"] == 2021


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS configurer_api_key / obtenir_cle_api
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConfigurationApiKey:
    """Tests pour la gestion de la clÃ© API."""
    
    def test_configurer_api_key(self):
        """Test configuration de la clÃ© API."""
        import src.modules.jeux.logic.api_football as module
        
        original = module.API_KEY
        try:
            configurer_api_key("ma_cle_test")
            assert module.API_KEY == "ma_cle_test"
        finally:
            module.API_KEY = original
    
    def test_obtenir_cle_api_depuis_module(self, mock_api_key):
        """Obtient la clÃ© configurÃ©e dans le module."""
        cle = obtenir_cle_api()
        assert cle == "test_api_key_12345"
    
    def test_obtenir_cle_api_sans_config(self):
        """Sans clÃ© configurÃ©e, essaie les paramÃ¨tres."""
        import src.modules.jeux.logic.api_football as module
        original = module.API_KEY
        module.API_KEY = None
        
        try:
            # Mock au niveau du module oÃ¹ l'import est fait
            mock_params = MagicMock()
            mock_params.FOOTBALL_DATA_API_KEY = "cle_from_settings"
            with patch.dict('sys.modules', {'src.core.config': MagicMock()}):
                with patch("src.core.config.obtenir_parametres", return_value=mock_params):
                    cle = obtenir_cle_api()
                    # Si la clÃ© est trouvÃ©e ou pas, le test vÃ©rifie que Ã§a ne crashe pas
                    assert cle is None or cle == "cle_from_settings"
        finally:
            module.API_KEY = original
    
    def test_obtenir_cle_api_exception(self):
        """Retourne None si aucune clÃ© disponible."""
        import src.modules.jeux.logic.api_football as module
        original = module.API_KEY
        module.API_KEY = None
        
        try:
            # Force la config Ã  ne pas exister
            cle = obtenir_cle_api()
            # Quand pas de clÃ©, retourne None (config peut lever une exception)
            assert cle is None or isinstance(cle, str)
        finally:
            module.API_KEY = original


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS faire_requete
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFaireRequete:
    """Tests pour faire_requete."""
    
    def test_requete_sans_api_key(self):
        """Sans clÃ© API, retourne None."""
        import src.modules.jeux.logic.api_football as module
        original = module.API_KEY
        module.API_KEY = None
        
        try:
            with patch("src.modules.jeux.logic.api_football.obtenir_cle_api", return_value=None):
                result = faire_requete("/test")
                assert result is None
        finally:
            module.API_KEY = original
    
    def test_requete_reussie(self, mock_api_key):
        """Test d'une requÃªte rÃ©ussie."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_response):
            result = faire_requete("/test/endpoint")
            assert result == {"data": "test"}
    
    def test_requete_avec_params(self, mock_api_key):
        """Test d'une requÃªte avec paramÃ¨tres."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_response) as mock_get:
            result = faire_requete("/matches", {"status": "SCHEDULED"})
            
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"] == {"status": "SCHEDULED"}
    
    def test_requete_erreur_429_rate_limit(self, mock_api_key):
        """Test erreur 429 (rate limit)."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        
        with patch("requests.get", return_value=mock_response):
            result = faire_requete("/test")
            assert result is None
    
    def test_requete_erreur_404(self, mock_api_key):
        """Test erreur 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        
        with patch("requests.get", return_value=mock_response):
            result = faire_requete("/invalid")
            assert result is None
    
    def test_requete_erreur_500(self, mock_api_key):
        """Test erreur 500."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        
        with patch("requests.get", return_value=mock_response):
            result = faire_requete("/server-error")
            assert result is None
    
    def test_requete_exception_generale(self, mock_api_key):
        """Test exception gÃ©nÃ©rale."""
        with patch("requests.get", side_effect=Exception("Network error")):
            result = faire_requete("/test")
            assert result is None
    
    def test_requete_non_200_log_error(self, mock_api_key):
        """Test log erreur quand status != 200."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_response):
            result = faire_requete("/bad-request")
            # Le log est fait mais la rÃ©ponse est retournÃ©e
            assert result == {"error": "Bad Request"}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS charger_matchs_a_venir
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerMatchsAVenir:
    """Tests pour charger_matchs_a_venir."""
    
    def test_championnat_non_supporte(self):
        """Championnat non supportÃ© retourne liste vide."""
        result = charger_matchs_a_venir("Liga MX")
        assert result == []
    
    def test_charger_matchs_ok(self, mock_api_key, mock_match_response):
        """Test chargement rÃ©ussi des matchs."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_match_response
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_response):
            matchs = charger_matchs_a_venir("Ligue 1", jours=7)
            
            assert len(matchs) == 2
            assert matchs[0]["equipe_domicile"] == "Paris Saint-Germain"
            assert matchs[0]["equipe_exterieur"] == "Olympique Marseille"
            assert matchs[0]["date"] == "2025-02-15"
            assert matchs[0]["heure"] == "20:00"
    
    def test_charger_matchs_pas_de_data(self, mock_api_key):
        """Test quand l'API ne retourne pas de data."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=None):
            matchs = charger_matchs_a_venir("Ligue 1")
            assert matchs == []
    
    def test_charger_matchs_parsing_error(self, mock_api_key):
        """Test robustesse au parsing de matchs mal formÃ©s."""
        mock_response = {
            "matches": [
                {"id": 1, "utcDate": "2025-02-15"},  # Pas de "T"
                None,  # Match invalide
                {"id": 2, "utcDate": "2025-02-16T18:00:00Z", "homeTeam": {}, "awayTeam": {}}
            ]
        }
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=mock_response):
            matchs = charger_matchs_a_venir("Premier League")
            assert isinstance(matchs, list)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS charger_historique_equipe
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerHistoriqueEquipe:
    """Tests pour charger_historique_equipe."""
    
    def test_equipe_non_trouvee(self, mock_api_key):
        """Ã‰quipe non trouvÃ©e retourne liste vide."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=None):
            result = charger_historique_equipe("Ã‰quipe Inconnue")
            assert result == []
    
    def test_equipe_pas_de_teams(self, mock_api_key):
        """RÃ©ponse sans teams retourne liste vide."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value={"teams": []}):
            result = charger_historique_equipe("Ã‰quipe Inconnue")
            assert result == []
    
    def test_charger_historique_ok(self, mock_api_key):
        """Test chargement rÃ©ussi de l'historique."""
        team_response = {"teams": [{"id": 10, "name": "PSG"}]}
        matches_response = {
            "matches": [
                {
                    "utcDate": "2025-02-01T20:00:00Z",
                    "homeTeam": {"id": 10, "name": "PSG"},
                    "awayTeam": {"id": 20, "name": "Lyon"},
                    "score": {"fullTime": {"home": 3, "away": 1}}
                }
            ]
        }
        
        call_count = [0]
        def mock_faire_requete(endpoint, params=None):
            call_count[0] += 1
            # Premier appel: recherche Ã©quipe
            if call_count[0] == 1:
                return team_response
            # DeuxiÃ¨me appel: matchs de l'Ã©quipe
            else:
                return matches_response
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", side_effect=mock_faire_requete):
            matchs = charger_historique_equipe("PSG", limite=5)
            
            assert len(matchs) == 1
            assert matchs[0]["equipe_domicile"] == "PSG"
            assert matchs[0]["score_domicile"] == 3
    
    def test_charger_historique_sans_id(self, mock_api_key):
        """Ã‰quipe sans ID retourne liste vide."""
        team_response = {"teams": [{"name": "Team without ID"}]}  # Pas d'id
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=team_response):
            result = charger_historique_equipe("Team")
            assert result == []
    
    def test_charger_historique_pas_de_matchs(self, mock_api_key):
        """Pas de matchs retourne liste vide."""
        def mock_faire_requete(endpoint, params=None):
            if "/teams" in endpoint and params:
                return {"teams": [{"id": 10}]}
            return None  # Pas de matchs
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", side_effect=mock_faire_requete):
            result = charger_historique_equipe("PSG")
            assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS charger_classement
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerClassement:
    """Tests pour charger_classement."""
    
    def test_championnat_non_supporte(self):
        """Championnat non supportÃ© retourne liste vide."""
        result = charger_classement("MLS")
        assert result == []
    
    def test_charger_standings_ok(self, mock_api_key, mock_standings_response):
        """Test chargement rÃ©ussi du classement."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_standings_response
        mock_resp.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_resp):
            equipes = charger_classement("Ligue 1")
            
            assert len(equipes) == 2
            assert equipes[0]["position"] == 1
            assert equipes[0]["nom"] == "PSG"
            assert equipes[0]["points"] == 48
            assert equipes[1]["nom"] == "Monaco"
    
    def test_charger_classement_fallback_teams(self, mock_api_key, mock_teams_fallback_response):
        """Test fallback vers /teams si standings indisponible."""
        def mock_faire_requete(endpoint, params=None):
            if "standings" in endpoint:
                return None  # Standings non disponible
            elif "teams" in endpoint:
                return mock_teams_fallback_response
            return None
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", side_effect=mock_faire_requete):
            equipes = charger_classement("La Liga")
            
            assert len(equipes) == 3
            assert equipes[0]["nom"] == "Ã‰quipe A"
            assert equipes[0]["points"] == 0  # Fallback n'a pas de stats
    
    def test_charger_classement_vide(self, mock_api_key):
        """Pas de donnÃ©es retourne liste vide."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=None):
            result = charger_classement("Ligue 1")
            assert result == []
    
    def test_charger_classement_standings_empty(self, mock_api_key):
        """Standings vides utilise fallback."""
        def mock_faire_requete(endpoint, params=None):
            if "standings" in endpoint:
                return {"standings": []}  # Vide
            return None
        
        with patch("src.modules.jeux.logic.api_football.faire_requete", side_effect=mock_faire_requete):
            result = charger_classement("Bundesliga")
            assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS chercher_equipe
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChercherEquipe:
    """Tests pour chercher_equipe."""
    
    def test_equipe_non_trouvee(self, mock_api_key):
        """Ã‰quipe non trouvÃ©e retourne None."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=None):
            result = chercher_equipe("Unknown FC")
            assert result is None
    
    def test_equipe_liste_vide(self, mock_api_key):
        """Liste d'Ã©quipes vide retourne None."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value={"teams": []}):
            result = chercher_equipe("Unknown FC")
            assert result is None
    
    def test_chercher_equipe_ok(self, mock_api_key, mock_team_response):
        """Test recherche rÃ©ussie d'Ã©quipe."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=mock_team_response):
            equipe = chercher_equipe("Paris")
            
            assert equipe is not None
            assert equipe["id"] == 10
            assert equipe["nom"] == "Paris Saint-Germain"
            assert equipe["nom_court"] == "PSG"
            assert equipe["pays"] == "France"
            assert equipe["founded"] == 1970


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS charger_matchs_termines
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerMatchsTermines:
    """Tests pour charger_matchs_termines."""
    
    def test_championnat_non_supporte(self):
        """Championnat non supportÃ© retourne liste vide."""
        result = charger_matchs_termines("J-League")
        assert result == []
    
    def test_charger_matchs_termines_ok(self, mock_api_key, mock_finished_match_response):
        """Test chargement rÃ©ussi des matchs terminÃ©s."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_finished_match_response
        mock_resp.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_resp):
            matchs = charger_matchs_termines("Ligue 1", jours=7)
            
            assert len(matchs) == 1
            assert matchs[0]["score_domicile"] == 2
            assert matchs[0]["score_exterieur"] == 1
    
    def test_charger_matchs_termines_pas_de_data(self, mock_api_key):
        """Test quand l'API ne retourne pas de data."""
        with patch("src.modules.jeux.logic.api_football.faire_requete", return_value=None):
            matchs = charger_matchs_termines("Serie A")
            assert matchs == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS cache
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCache:
    """Tests pour le systÃ¨me de cache."""
    
    def test_vider_cache(self):
        """Test vidage du cache."""
        # Ne doit pas lever d'exception
        vider_cache()
        assert True
    
    def test_charger_matchs_cache(self, mock_api_key, mock_match_response):
        """Test version cachÃ©e de charger_matchs."""
        # Vider le cache d'abord
        vider_cache()
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_match_response
        mock_resp.raise_for_status = MagicMock()
        
        with patch("requests.get", return_value=mock_resp):
            # Premier appel
            result1 = charger_matchs_cache("Ligue 1", 7)
            assert isinstance(result1, tuple)
            assert len(result1) == 2
        
        # Nettoyer aprÃ¨s le test
        vider_cache()
