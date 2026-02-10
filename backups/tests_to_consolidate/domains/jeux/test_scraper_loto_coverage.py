"""
Tests complets pour scraper_loto.py - Couverture ≥80%

Ce module teste le scraper Loto FDJ:
- Chargement des tirages depuis API
- Parsing des données
- Calcul des statistiques
- Intégration BD
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
import requests

from src.domains.jeux.logic.scraper_loto import (
    ScraperLotoFDJ,
    charger_tirages_loto,
    obtenir_statistiques_loto,
    obtenir_dernier_tirage_loto,
    inserer_tirages_en_bd,
)


# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def scraper():
    """Instance du scraper."""
    return ScraperLotoFDJ()


@pytest.fixture
def mock_api_response():
    """Réponse mock API FDJ."""
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
    """Réponse API avec format alternatif."""
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


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - Initialisation
# ═══════════════════════════════════════════════════════════════════


class TestScraperLotoFDJInit:
    """Tests d'initialisation du scraper."""
    
    def test_init_session(self, scraper):
        """Vérifie que la session est créée."""
        assert scraper.session is not None
        assert hasattr(scraper.session, "headers")
    
    def test_endpoints_definis(self, scraper):
        """Vérifie que les endpoints sont définis."""
        assert len(scraper.ENDPOINTS_FDJ) >= 1
    
    def test_donnees_demo(self, scraper):
        """Vérifie que les données de démo existent."""
        assert len(scraper.DONNEES_DEMO) >= 5
        # Vérifier structure
        for tirage in scraper.DONNEES_DEMO:
            assert "date" in tirage
            assert "numeros" in tirage
            assert len(tirage["numeros"]) == 5


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - charger_derniers_tirages
# ═══════════════════════════════════════════════════════════════════


class TestChargerDerniersTirages:
    """Tests pour charger_derniers_tirages."""
    
    def test_charger_api_ok(self, scraper, mock_api_response):
        """Test chargement réussi depuis l'API."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            tirages = scraper.charger_derniers_tirages(limite=10)
            
            assert len(tirages) >= 1
    
    def test_charger_fallback_demo(self, scraper):
        """Test fallback vers les données de démonstration."""
        # Simuler échec de tous les endpoints
        with patch.object(scraper.session, "get", side_effect=Exception("Network error")):
            tirages = scraper.charger_derniers_tirages(limite=5)
            
            # Doit utiliser les données de démo
            assert len(tirages) == 5
            assert tirages[0]["source"] == "demo"
    
    def test_limite_respectee(self, scraper):
        """Test que la limite est respectée."""
        with patch.object(scraper.session, "get", side_effect=Exception("Error")):
            tirages = scraper.charger_derniers_tirages(limite=3)
            assert len(tirages) <= 3


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - _charger_depuis_endpoint
# ═══════════════════════════════════════════════════════════════════


class TestChargerDepuisEndpoint:
    """Tests pour _charger_depuis_endpoint."""
    
    def test_parsing_format_results(self, scraper, mock_api_response):
        """Test parsing avec clé 'results'."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(scraper.session, "get", return_value=mock_response):
            tirages = scraper._charger_depuis_endpoint("https://api.test.com", 10)
            assert isinstance(tirages, list)
    
    def test_parsing_format_draws(self, scraper, mock_api_response_alternative):
        """Test parsing avec clé 'draws'."""
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


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - _extraire_numeros
# ═══════════════════════════════════════════════════════════════════


class TestExtraireNumeros:
    """Tests pour _extraire_numeros."""
    
    def test_extraire_liste_entiers(self, scraper):
        """Extrait depuis une liste d'entiers."""
        tirage = {"numeros": [1, 12, 23, 34, 45]}
        numeros = scraper._extraire_numeros(tirage)
        
        assert numeros == [1, 12, 23, 34, 45]
    
    def test_extraire_string(self, scraper):
        """Extrait depuis une chaîne."""
        tirage = {"numerosGagnants": "5, 12, 23, 34, 45"}
        numeros = scraper._extraire_numeros(tirage)
        
        assert 5 in numeros
        assert 45 in numeros
    
    def test_extraire_cle_alternative(self, scraper):
        """Test avec clé alternative."""
        tirage = {"balls": [7, 14, 23, 31, 45]}
        numeros = scraper._extraire_numeros(tirage)
        
        assert 7 in numeros
        assert 45 in numeros
    
    def test_extraire_vide(self, scraper):
        """Tirage sans numéros retourne liste vide."""
        tirage = {"date": "2025-02-10"}
        numeros = scraper._extraire_numeros(tirage)
        
        assert numeros == []
    
    def test_extraire_filtre_numeros_invalides(self, scraper):
        """Filtre les numéros > 49."""
        tirage = {"numeros": "5, 12, 55, 34, 100"}
        numeros = scraper._extraire_numeros(tirage)
        
        # 55 et 100 sont > 49, donc filtrés
        assert 55 not in numeros
        assert 100 not in numeros


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - _extraire_date
# ═══════════════════════════════════════════════════════════════════


class TestExtraireDate:
    """Tests pour _extraire_date."""
    
    def test_extraire_date_classique(self, scraper):
        """Extrait date depuis clé 'date'."""
        tirage = {"date": "2025-02-10"}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == "2025-02-10"
    
    def test_extraire_date_alternative(self, scraper):
        """Test avec clé alternative."""
        tirage = {"datetirage": "2025-02-10"}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == "2025-02-10"
    
    def test_extraire_date_vide(self, scraper):
        """Pas de date retourne chaîne vide."""
        tirage = {"numeros": [1, 2, 3, 4, 5]}
        date_str = scraper._extraire_date(tirage)
        
        assert date_str == ""


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - calculer_statistiques_historiques
# ═══════════════════════════════════════════════════════════════════


class TestCalculerStatistiquesHistoriques:
    """Tests pour calculer_statistiques_historiques."""
    
    def test_stats_vide(self, scraper):
        """Liste vide retourne dict vide."""
        stats = scraper.calculer_statistiques_historiques([])
        assert stats == {}
    
    def test_stats_frequences(self, scraper, tirages_mock):
        """Vérifie le calcul des fréquences."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "nombre_tirages" in stats
        assert stats["nombre_tirages"] == 5
        assert "frequences_numeros" in stats
        assert "frequences_chances" in stats
    
    def test_stats_numeros_chauds(self, scraper, tirages_mock):
        """Vérifie l'identification des numéros chauds."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "numeros_chauds" in stats
        # Le numéro 5 apparaît 4 fois, devrait être chaud
        assert 5 in stats["numeros_chauds"]
    
    def test_stats_paires_frequentes(self, scraper, tirages_mock):
        """Vérifie le calcul des paires fréquentes."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "paires_frequentes" in stats
        assert len(stats["paires_frequentes"]) <= 10
    
    def test_stats_periode(self, scraper, tirages_mock):
        """Vérifie le calcul de la période."""
        stats = scraper.calculer_statistiques_historiques(tirages_mock)
        
        assert "periode" in stats
        assert "2025-02" in stats["periode"]


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - obtenir_dernier_tirage
# ═══════════════════════════════════════════════════════════════════


class TestObtenirDernierTirage:
    """Tests pour obtenir_dernier_tirage."""
    
    def test_dernier_tirage_ok(self, scraper):
        """Test récupération du dernier tirage."""
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


# ═══════════════════════════════════════════════════════════════════
# TESTS ScraperLotoFDJ - obtenir_tirage_du_jour
# ═══════════════════════════════════════════════════════════════════


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
        """Test avec format de date français."""
        today = date.today()
        date_fr = today.strftime("%d/%m/%Y")
        mock_tirages = [{"date": date_fr, "numeros": [1, 2, 3, 4, 5]}]
        
        with patch.object(scraper, "charger_derniers_tirages", return_value=mock_tirages):
            tirage = scraper.obtenir_tirage_du_jour()
            
            assert tirage is not None


# ═══════════════════════════════════════════════════════════════════
# TESTS Fonctions interface simple
# ═══════════════════════════════════════════════════════════════════


class TestInterfaceSimple:
    """Tests pour les fonctions d'interface simple."""
    
    def test_charger_tirages_loto(self):
        """Test charger_tirages_loto."""
        with patch("src.domains.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages") as mock:
            mock.return_value = [{"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5]}]
            
            tirages = charger_tirages_loto(limite=10)
            
            assert len(tirages) == 1
            mock.assert_called_once_with(10)
    
    def test_obtenir_statistiques_loto(self):
        """Test obtenir_statistiques_loto."""
        tirages_mock = [{"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5], "numero_chance": 7}]
        
        with patch("src.domains.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages", return_value=tirages_mock):
            stats = obtenir_statistiques_loto(limite=10)
            
            assert "nombre_tirages" in stats
    
    def test_obtenir_dernier_tirage_loto(self):
        """Test obtenir_dernier_tirage_loto."""
        tirage_mock = {"date": "2025-02-10", "numeros": [1, 2, 3, 4, 5]}
        
        with patch("src.domains.jeux.logic.scraper_loto.ScraperLotoFDJ.obtenir_dernier_tirage", return_value=tirage_mock):
            tirage = obtenir_dernier_tirage_loto()
            
            assert tirage is not None
            assert tirage["date"] == "2025-02-10"


# ═══════════════════════════════════════════════════════════════════
# TESTS inserer_tirages_en_bd
# ═══════════════════════════════════════════════════════════════════


class TestInsererTiragesEnBd:
    """Tests pour inserer_tirages_en_bd."""
    
    def test_inserer_exception(self):
        """Test gestion des exceptions."""
        # La fonction doit retourner False en cas d'erreur
        with patch("src.domains.jeux.logic.scraper_loto.ScraperLotoFDJ.charger_derniers_tirages", side_effect=Exception("Error")):
            result = inserer_tirages_en_bd(limite=10)
            
            assert result is False
    
    def test_inserer_fonction_existe(self):
        """Vérifie que la fonction existe et est callable."""
        assert callable(inserer_tirages_en_bd)
