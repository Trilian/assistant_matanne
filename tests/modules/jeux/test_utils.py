"""
Tests pour src/modules/jeux/utils.py

Tests des fonctions utilitaires avec fallback API/BD pour le module jeux.
"""

import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mock_match_api():
    """Fixture pour un match depuis l'API"""
    return {
        "id": 1,
        "date": "2026-02-15",
        "heure": "21:00",
        "championnat": "Ligue 1",
        "dom_nom": "PSG",
        "ext_nom": "Lyon",
        "cote_dom": 1.5,
        "cote_nul": 4.0,
        "cote_ext": 6.0,
        "source": "API",
    }


@pytest.fixture
def match_bd_dict():
    """Fixture pour un match depuis la BD (dict retourné par le service)"""
    return {
        "id": 2,
        "date_match": str(date.today() + timedelta(days=2)),
        "heure": "20:00",
        "championnat": "Ligue 1",
        "dom_nom": "Marseille",
        "ext_nom": "Monaco",
        "cote_dom": 2.0,
        "cote_nul": 3.2,
        "cote_ext": 3.5,
        "joue": False,
    }


@pytest.fixture
def equipe_bd_dict():
    """Fixture pour une équipe depuis la BD (dict retourné par le service)"""
    return {
        "nom": "PSG",
        "matchs_joues": 25,
        "victoires": 18,
        "nuls": 4,
        "defaites": 3,
        "buts_marques": 55,
        "buts_encaisses": 20,
        "points": 58,
    }


@pytest.fixture
def historique_bd_dict():
    """Fixture pour un match historique depuis la BD (dict retourné par le service)"""
    return {
        "date_match": str(date.today() - timedelta(days=5)),
        "equipe_domicile": "PSG",
        "equipe_exterieur": "Lille",
        "score_domicile": 3,
        "score_exterieur": 0,
    }


@pytest.fixture
def tirage_bd_dict():
    """Fixture pour un tirage Loto depuis la BD (dict retourné par le service)"""
    return {
        "date": str(date.today() - timedelta(days=1)),
        "numeros": [5, 12, 23, 34, 45],
        "numero_chance": 7,
    }


@pytest.fixture
def stat_bd_dict():
    """Fixture pour des statistiques Loto depuis la BD (dict retourné par le service)"""
    return {"num_5": 45, "num_12": 38, "num_23": 42}


# ============================================================
# Tests charger_matchs_avec_fallback
# ============================================================


class TestChargerMatchsAvecFallback:
    """Tests pour charger_matchs_avec_fallback"""

    def test_charge_depuis_api_success(self, mock_match_api):
        """Test chargement réussi depuis l'API"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.return_value = [mock_match_api]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert source == "API"
            assert len(result) == 1
            assert result[0]["dom_nom"] == "PSG"

    def test_fallback_bd_quand_prefer_api_false(self, match_bd_dict):
        """Test fallback vers BD quand prefer_api=False"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.get_paris_crud_service.return_value.charger_matchs_fallback.return_value = [
            match_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=False
            )

            assert isinstance(result, list)
            assert source == "BD"
            assert len(result) == 1

    def test_api_echoue_fallback_bd(self, match_bd_dict):
        """Test que l'erreur API déclenche le fallback BD"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_matchs_fallback.return_value = [
            match_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert isinstance(result, list)
            assert source == "BD"

    def test_tout_echoue_retourne_liste_vide(self):
        """Test que la fonction retourne liste vide si tout échoue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert result == []

    def test_api_retourne_vide_resultat_vide(self, mock_match_api):
        """Test que la fonction gère les résultats vides gracieusement"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_matchs_a_venir.return_value = []
        mock_services_jeux.get_paris_crud_service.return_value.charger_matchs_fallback.return_value = []

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert isinstance(result, list)


# ============================================================
# Tests charger_classement_avec_fallback
# ============================================================


class TestChargerClassementAvecFallback:
    """Tests pour charger_classement_avec_fallback"""

    def test_charge_classement_api_success(self):
        """Test chargement du classement depuis l'API"""
        classement_api = [
            {"position": 1, "nom": "PSG", "points": 58},
            {"position": 2, "nom": "Monaco", "points": 52},
        ]

        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.return_value = classement_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "API"
            assert len(result) == 2
            assert result[0]["nom"] == "PSG"

    def test_fallback_bd_classement(self, equipe_bd_dict):
        """Test fallback BD pour le classement"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_classement_fallback.return_value = [
            equipe_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["nom"] == "PSG"
            assert result[0]["points"] == 58

    def test_api_retourne_vide_fallback_bd(self, equipe_bd_dict):
        """Test fallback BD quand API retourne vide"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.return_value = []
        mock_services_jeux.get_paris_crud_service.return_value.charger_classement_fallback.return_value = [
            equipe_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"

    def test_classement_tout_echoue(self):
        """Test que la fonction gère tout échoue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_classement.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Championnat inconnu")

            assert result == []


# ============================================================
# Tests charger_historique_equipe_avec_fallback
# ============================================================


class TestChargerHistoriqueEquipeAvecFallback:
    """Tests pour charger_historique_equipe_avec_fallback"""

    def test_charge_historique_api_success(self):
        """Test chargement de l'historique depuis l'API"""
        historique_api = [
            {
                "date": "2026-02-10",
                "equipe_domicile": "PSG",
                "equipe_exterieur": "Lille",
                "score_domicile": 3,
                "score_exterieur": 0,
            }
        ]

        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.return_value = historique_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "API"
            assert len(result) == 1
            assert result[0]["score_domicile"] == 3

    def test_fallback_bd_historique(self, historique_bd_dict):
        """Test fallback BD pour l'historique"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.return_value.charger_historique_equipe_fallback.return_value = [
            historique_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"
            assert len(result) == 1

    def test_api_retourne_vide_fallback_bd(self, historique_bd_dict):
        """Test fallback BD quand API retourne vide"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.return_value = []
        mock_services_jeux.get_paris_crud_service.return_value.charger_historique_equipe_fallback.return_value = [
            historique_bd_dict
        ]

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"

    def test_historique_tout_echoue(self):
        """Test historique tout échoue"""
        mock_services_jeux = MagicMock()
        mock_services_jeux.charger_historique_equipe.side_effect = Exception("API error")
        mock_services_jeux.get_paris_crud_service.side_effect = Exception("DB error")

        with patch.dict(sys.modules, {"src.services.jeux": mock_services_jeux}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("Equipe Fantome")

            assert result == []


# ============================================================
# Tests charger_tirages_loto_avec_fallback
# ============================================================


class TestChargerTiragesLotoAvecFallback:
    """Tests pour charger_tirages_loto_avec_fallback"""

    def test_charge_tirages_scraper_success(self):
        """Test chargement des tirages depuis le scraper FDJ"""
        tirages_scraper = [
            {"date": "2026-02-12", "numeros": [7, 14, 21, 35, 42], "numero_chance": 3}
        ]

        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.return_value = tirages_scraper

        with patch.dict(sys.modules, {"src.modules.jeux.scraper_loto": mock_scraper}):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=50)

            assert source == "Scraper FDJ"
            assert len(result) == 1
            assert result[0]["numeros"] == [7, 14, 21, 35, 42]

    def test_fallback_bd_tirages(self, tirage_bd_dict):
        """Test fallback BD pour les tirages"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_tirages_fallback.return_value = [
            tirage_bd_dict
        ]

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=10)

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["numero_chance"] == 7

    def test_scraper_vide_fallback_bd(self, tirage_bd_dict):
        """Test fallback BD quand scraper retourne vide"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.return_value = []

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_tirages_fallback.return_value = [
            tirage_bd_dict
        ]

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=100)

            assert source == "BD"

    def test_tirages_tout_echoue(self):
        """Test quand tout échoue pour les tirages"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.side_effect = Exception("DB error")

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=100)

            assert result == []


# ============================================================
# Tests charger_stats_loto_avec_fallback
# ============================================================


class TestChargerStatsLotoAvecFallback:
    """Tests pour charger_stats_loto_avec_fallback"""

    def test_charge_stats_scraper_success(self):
        """Test chargement des stats depuis le scraper"""
        stats_scraper = {"frequences": {"5": 45, "12": 38}, "derniere_maj": "2026-02-12"}

        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.return_value = stats_scraper

        with patch.dict(sys.modules, {"src.modules.jeux.scraper_loto": mock_scraper}):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__(limite=50)

            assert source == "Scraper FDJ"
            assert "frequences" in result

    def test_fallback_bd_stats(self, stat_bd_dict):
        """Test fallback BD pour les statistiques"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_stats_fallback.return_value = stat_bd_dict

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"
            assert result["num_5"] == 45

    def test_scraper_vide_fallback_bd(self, stat_bd_dict):
        """Test fallback BD quand scraper retourne vide"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.return_value = {}

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.return_value.charger_stats_fallback.return_value = stat_bd_dict

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"

    def test_stats_tout_echoue(self):
        """Test quand aucune statistique n'est disponible"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_services_jeux = MagicMock()
        mock_services_jeux.get_loto_crud_service.side_effect = Exception("DB error")

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.services.jeux": mock_services_jeux,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert result == {}


# ============================================================
# Tests bouton_actualiser_api
# ============================================================


class TestBoutonActualiserApi:
    """Tests pour bouton_actualiser_api"""

    @patch("src.modules.jeux.utils.st")
    def test_bouton_non_clique(self, mock_st):
        """Test quand le bouton n'est pas cliqué"""
        mock_st.button.return_value = False
        mock_st.session_state = {}

        from src.modules.jeux.utils import bouton_actualiser_api

        result = bouton_actualiser_api("matchs_test")

        assert result is False
        mock_st.button.assert_called_once()

    @patch("src.modules.jeux.utils.Cache")
    @patch("src.modules.jeux.utils.st")
    def test_bouton_clique_nettoie_cache(self, mock_st, mock_cache):
        """Test que le clic nettoie le cache et retourne True"""
        mock_st.button.return_value = True
        mock_st.session_state = {}

        from src.modules.jeux.utils import bouton_actualiser_api

        result = bouton_actualiser_api("test_key")

        assert result is True
        mock_cache.invalider.assert_called_once_with(pattern="charger_")
        assert mock_st.session_state["test_key_updated"] is True


# ============================================================
# Tests message_source_donnees
# ============================================================


class TestMessageSourceDonnees:
    """Tests pour message_source_donnees"""

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_api(self, mock_st):
        """Test affichage pour source API"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("API")

        mock_st.caption.assert_called_once()
        call_args = mock_st.caption.call_args[0][0]
        assert "\U0001f310" in call_args
        assert "API" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_bd(self, mock_st):
        """Test affichage pour source BD"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("BD")

        call_args = mock_st.caption.call_args[0][0]
        assert "\U0001f4be" in call_args
        assert "BD" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_scraper(self, mock_st):
        """Test affichage pour source Scraper"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Scraper FDJ")

        call_args = mock_st.caption.call_args[0][0]
        assert "\U0001f577\ufe0f" in call_args
        assert "Scraper FDJ" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_inconnue(self, mock_st):
        """Test affichage pour source inconnue"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Autre")

        call_args = mock_st.caption.call_args[0][0]
        assert "\U0001f577\ufe0f" in call_args
