"""
Tests complets pour scraper_loto.py - Couverture â‰¥80%

Ce module teste le scraper Loto FDJ:
- Chargement des tirages depuis API
- Parsing des donnÃ©es
- Calcul des statistiques
- IntÃ©gration BD
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from src.modules.jeux.logic.scraper_loto import (
    ScraperLotoFDJ,
    charger_tirages_loto,
    obtenir_statistiques_loto,
    obtenir_dernier_tirage_loto,
    inserer_tirages_en_bd,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def scraper():
    """Instance du scraper."""
    return ScraperLotoFDJ()


@pytest.fixture
def mock_api_response():
    """RÃ©ponse mock API FDJ."""
    return {
        "results": [
            {
                "date": "2025-02-10",
                "numeros": [5, 12, 23, 34, 45],
                "numero_chance": 7
            },
            {
                "date": "2025-02-08",
                "numeros": [1, 18, 27, 38, 49],
                "numero_chance": 3
            }
        ]
    }


@pytest.fixture
def mock_api_response_alternative():
    """RÃ©ponse API avec format alternatif."""
    return {
        "draws": [
            {
                "datetirage": "2025-02-10",
                "numeroGagnants": [7, 14, 23, 31, 45],
            }
        ]
    }


@pytest.fixture
def tirages_mock():
    """Liste de tirages pour les tests de statistiques."""
    return [
        {"date": "2025-02-10", "numeros": [5, 12, 23, 34, 45], "numero_chance": 7},
        {"date": "2025-02-08", "numeros": [5, 18, 27, 38, 49], "numero_chance": 3},
        {"date": "2025-02-06", "numeros": [5, 12, 23, 34, 42], "numero_chance": 7},
        {"date": "2025-02-03", "numeros": [11, 18, 27, 38, 45], "numero_chance": 5},
        {"date": "2025-02-01", "numeros": [5, 12, 23, 34, 45], "numero_chance": 7},
    ]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - Initialisation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestScraperLotoFDJInit:
    """Tests d'initialisation du scraper."""
    
    def test_init_session(self, scraper):
        """VÃ©rifie que la session est crÃ©Ã©e."""
        assert scraper.session is not None
        assert hasattr(scraper.session, "headers")
    
    def test_endpoints_definis(self, scraper):
        """VÃ©rifie que les endpoints sont dÃ©finis."""
        assert len(scraper.ENDPOINTS_FDJ) >= 1
    
    def test_donnees_demo(self, scraper):
        """VÃ©rifie que les donnÃ©es de dÃ©mo existent."""
        assert len(scraper.DONNEES_DEMO) >= 5
        # VÃ©rifier structure
        for tirage in scraper.DONNEES_DEMO:
            assert "date" in tirage
            assert "numeros" in tirage
            assert len(tirage["numeros"]) == 5


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - charger_derniers_tirages
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerDerniersTirages:
    """Tests pour charger_derniers_tirages."""
    
    def test_charger_api_ok(self, scraper, mock_api_response):
        """Test chargement rÃ©ussi depuis l'API."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            tirages = scraper.charger_derniers_tirages(limite=10)
            
            assert len(tirages) >= 1
    
    def test_charger_fallback_demo(self, scraper):
        """Test fallback vers les donnÃ©es de dÃ©monstration."""
        # Simuler Ã©chec de tous les endpoints
        with patch.object(scraper.session, "get", side_effect=Exception("Network error")):
            tirages = scraper.charger_derniers_tirages(limite=5)
            
            # Doit utiliser les donnÃ©es de dÃ©mo
            assert len(tirages) == 5
            assert tirages[0]["source"] == "demo"
    
    def test_limite_respectee(self, scraper):
        """Test que la limite est respectÃ©e."""
        with patch.object(scraper.session, "get", side_effect=Exception("Error")):
            tirages = scraper.charger_derniers_tirages(limite=3)
            assert len(tirages) <= 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - _charger_depuis_endpoint
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestChargerDepuisEndpoint:
    """Tests pour _charger_depuis_endpoint."""
    
    def test_parsing_format_results(self, scraper, mock_api_response):
        """Test parsing avec clÃ© 'results'."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            tirages = scraper._charger_depuis_endpoint("https://api.test.com", 10)
            assert isinstance(tirages, list)
    
    def test_parsing_format_draws(self, scraper, mock_api_response_alternative):
        """Test parsing avec clÃ© 'draws'."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response_alternative
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            tirages = scraper._charger_depuis_endpoint("https://api.test.com", 10)
            assert isinstance(tirages, list)
    
    def test_http_error(self, scraper):
        """Test gestion erreur HTTP."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError):
                scraper._charger_depuis_endpoint("https://api.test.com", 10)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - _extraire_numeros
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtraireNumeros:
    """Tests pour _extraire_numeros."""
    
    def test_extraire_liste_entiers(self, scraper):
        """Extrait depuis une liste d'entiers."""
        tirage = {"numeros": [1, 12, 23, 34, 45]}
        numeros = scraper._extraire_numeros(tirage)
        
        assert numeros == [1, 12, 23, 34, 45]
    
    def test_extraire_string(self, scraper):
        """Extrait depuis une chaÃ®ne."""
        tirage = {"numerosGagnants": "5, 12, 23, 34, 45"}
        numeros = scraper._extraire_numeros(tirage)
        
        assert 5 in numeros
        assert 45 in numeros
    
    def test_extraire_cle_alternative(self, scraper):
        """Test avec clÃ© alternative."""
        tirage = {"balls": [7, 14, 23, 31, 45]}
        numeros = scraper._extraire_numeros(tirage)
        
        assert 7 in numeros
        assert 45 in numeros
    
    def test_extraire_vide(self, scraper):
        """Tirage sans numÃ©ros retourne liste vide."""
        tirage = {"date": "2025-02-10"}
        numeros = scraper._extraire_numeros(tirage)
        
        assert numeros == []
    
    def test_extraire_filtre_numeros_invalides(self, scraper):
        """Filtre les numÃ©ros > 49."""
        tirage = {"numeros": "5, 12, 55, 34, 100"}
        numeros = scraper._extraire_numeros(tirage)
        
        # 55 et 100 sont > 49, donc filtrÃ©s
        assert 55 not in numeros
        assert 100 not in numeros


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - _extraire_date
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtraireDate:
    """Tests pour _extraire_date."""
    
    def test_extraire_date_classique(self, scraper):
        """Extrait date depuis clÃ© 'date'."""
        tirage = {"date": "2025-02-10"}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == "2025-02-10"
    
    def test_extraire_date_alternative(self, scraper):
        """Test avec clÃ© alternative."""
        tirage = {"datetirage": "2025-02-10"}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == "2025-02-10"
    
    def test_extraire_date_vide(self, scraper):
        """Pas de date retourne chaÃ®ne vide."""
        tirage = {"numeros": [1, 2, 3, 4, 5]}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - calculer_statistiques_historiques
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerStatistiquesHistoriques:
    """Tests pour calculer_statistiques_historiques."""
    
    def test_stats_vide(self, scraper):
        """Liste vide retourne dict vide."""
        stats = scraper.calculer_statistiques_historiques([])
        assert stats == {}
    
    def test_stats_frequences(self, scraper, tirages_mock):
        """VÃ©rifie le calcul des frÃ©quences."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "nombre_tirages" in stats
        assert stats["nombre_tirages"] == 5
        assert "frequences_numeros" in stats
        assert "frequences_chances" in stats
    
    def test_stats_numeros_chauds(self, scraper, tirages_mock):
        """VÃ©rifie l'identification des numÃ©ros chauds."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "numeros_chauds" in stats
        # Le numÃ©ro 5 apparaÃ®t 4 fois, devrait Ãªtre chaud
        assert 5 in stats["numeros_chauds"]
    
    def test_stats_paires_frequentes(self, scraper, tirages_mock):
        """VÃ©rifie le calcul des paires frÃ©quentes."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "paires_frequentes" in stats
        assert len(stats["paires_frequentes"]) <= 10
    
    def test_stats_periode(self, scraper, tirages_mock):
        """VÃ©rifie le calcul de la pÃ©riode."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "periode" in stats
        assert "2025-02" in stats["periode"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - obtenir_dernier_tirage
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestObtenirDernierTirage:
    """Tests pour obtenir_dernier_tirage."""
    
    def test_dernier_tirage_ok(self, scraper):
        """Test rÃ©cupÃ©ration du dernier tirage."""
        mock_tirages = [{"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5]}]
        
        with patch.object(scraper, "charger_derniers_tirages", return_value=mock_tirages):
            tirage = scraper.obtenir_dernier_tirage()
            
            assert tirage is not None
            assert tirage["date"] == "2025-02-10"
    
    def test_dernier_tirage_vide(self, scraper):
        """Pas de tirages retourne None."""
        with patch.object(scraper, "charger_derniers_tirages", return_value=[]):
            tirage = scraper.obtenir_dernier_tirage()
            assert tirage is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ScraperLotoFDJ - obtenir_tirage_du_jour
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestObtenirTirageDuJour:
    """Tests pour obtenir_tirage_du_jour."""
    
    def test_tirage_du_jour_existe(self, scraper):
        """Test quand le tirage du jour existe."""
        today = date.today().strftime("%Y-%m-%d")
        mock_tirages = [
            {"date": today, "numeros": [1, 2, 3, 4, 5]},
            {"date": "2025-02-01", "numeros": [6, 7, 8, 9, 10]}
        ]
        
        with patch.object(scraper, "charger_derniers_tirages", return_value=mock_tirages):
            tirage = scraper.obtenir_tirage_du_jour()
            
            assert tirage is not None
            assert tirage["date"] == today
    
    def test_tirage_du_jour_nexiste_pas(self, scraper):
        """Test quand pas de tirage aujourd'hui."""
        mock_tirages = [
            {"date": "2025-02-01", "numeros": [1, 2, 3, 4, 5]}
        ]
        
        with patch.object(scraper, "charger_derniers_tirages", return_value=mock_tirages):
            tirage = scraper.obtenir_tirage_du_jour()
            assert tirage is None
    
    def test_tirage_du_jour_format_francais(self, scraper):
        """Test avec format de date franÃ§ais."""
        today = date.today()
        date_fr = today.strftime("%d/%m/%Y")
        mock_tirages = [{"date": date_fr, "numeros": [1, 2, 3, 4, 5]}]
        
        with patch.object(scraper, "charger_derniers_tirages", return_value=mock_tirages):
            tirage = scraper.obtenir_tirage_du_jour()
            
            assert tirage is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Fonctions interface simple
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInterfaceSimple:
    """Tests pour les fonctions d'interface simple."""
    
    def test_charger_tirages_loto(self):
        """Test charger_tirages_loto."""
        with patch("src.modules.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages") as mock:
            mock.return_value = [{"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5]}]
            
            tirages = charger_tirages_loto(limite=10)
            
            assert len(tirages) == 1
            mock.assert_called_once_with(10)
    
    def test_obtenir_statistiques_loto(self):
        """Test obtenir_statistiques_loto."""
        tirages_mock = [{"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5], "numero_chance": 7}]
        
        with patch("src.modules.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages", return_value=tirages_mock):
            stats = obtenir_statistiques_loto(limite=10)
            
            assert "nombre_tirages" in stats
    
    def test_obtenir_dernier_tirage_loto(self):
        """Test obtenir_dernier_tirage_loto."""
        tirage_mock = {"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5]}
        
        with patch("src.modules.jeux.logic.scraper_loto.ScraperLotoFDJ.obtenir_dernier_tirage", return_value=tirage_mock):
            tirage = obtenir_dernier_tirage_loto()
            
            assert tirage is not None
            assert tirage["date"] == "2025-02-10"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS inserer_tirages_en_bd
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInsererTiragesEnBd:
    """Tests pour inserer_tirages_en_bd."""
    
    def test_inserer_exception(self):
        """Test gestion des exceptions."""
        # La fonction doit retourner False en cas d'erreur
        with patch("src.modules.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages", side_effect=Exception("Error")):
            result = inserer_tirages_en_bd(limite=10)
            
            assert result is False
    
    def test_inserer_fonction_existe(self):
        """VÃ©rifie que la fonction existe et est callable."""
        assert callable(inserer_tirages_en_bd)
