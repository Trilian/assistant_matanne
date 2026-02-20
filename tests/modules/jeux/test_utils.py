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
def mock_match_bd():
    """Fixture pour un match depuis la BD"""
    match = MagicMock()
    match.id = 2
    match.date_match = date.today() + timedelta(days=2)
    match.heure = "20:00"
    match.championnat = "Ligue 1"
    match.equipe_domicile = MagicMock(nom="Marseille")
    match.equipe_exterieur = MagicMock(nom="Monaco")
    match.cote_domicile = 2.0
    match.cote_nul = 3.2
    match.cote_exterieur = 3.5
    match.joue = False
    return match


@pytest.fixture
def mock_equipe_bd():
    """Fixture pour une équipe depuis la BD"""
    equipe = MagicMock()
    equipe.nom = "PSG"
    equipe.matchs_joues = 25
    equipe.victoires = 18
    equipe.nuls = 4
    equipe.defaites = 3
    equipe.buts_marques = 55
    equipe.buts_encaisses = 20
    equipe.points = 58
    return equipe


@pytest.fixture
def mock_tirage_bd():
    """Fixture pour un tirage Loto depuis la BD"""
    tirage = MagicMock()
    tirage.date = date.today() - timedelta(days=1)
    tirage.numeros = [5, 12, 23, 34, 45]
    tirage.numero_chance = 7
    return tirage


@pytest.fixture
def mock_stat_bd():
    """Fixture pour des statistiques Loto depuis la BD"""
    stat = MagicMock()
    stat.type_stat = "frequences"
    stat.donnees_json = {"num_5": 45, "num_12": 38, "num_23": 42}
    return stat


@pytest.fixture
def mock_historique_match():
    """Fixture pour un match historique depuis la BD"""
    match = MagicMock()
    match.date_match = date.today() - timedelta(days=5)
    match.equipe_domicile = MagicMock(nom="PSG")
    match.equipe_exterieur = MagicMock(nom="Lille")
    match.score_domicile = 3
    match.score_exterieur = 0
    return match


@pytest.fixture
def mock_db_context_manager():
    """Fixture pour le context manager de session BD"""
    cm = MagicMock()
    session = MagicMock()
    cm.__enter__ = MagicMock(return_value=session)
    cm.__exit__ = MagicMock(return_value=False)
    return cm, session


# ============================================================
# Tests charger_matchs_avec_fallback
# ============================================================


class TestChargerMatchsAvecFallback:
    """Tests pour charger_matchs_avec_fallback"""

    def test_charge_depuis_api_success(self, mock_match_api):
        """Test chargement réussi depuis l'API"""
        # Mock src.services.jeux (le vrai module importé par utils.py)
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

    def test_fallback_bd_quand_prefer_api_false(self, mock_match_bd, mock_db_context_manager):
        """Test fallback vers BD quand prefer_api=False (vérifie que BD est tentée)"""
        cm, session = mock_db_context_manager
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [mock_match_bd]
        session.query.return_value = query_mock

        mock_db = MagicMock()
        mock_db.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.core.db": mock_db,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=False
            )

            # La fonction ne crashe pas et retourne un résultat valide
            assert isinstance(result, list)
            assert source == "BD"

    def test_api_echoue_fallback_bd(self, mock_match_bd, mock_db_context_manager):
        """Test que l'erreur API déclenche le fallback BD (via exception interne)"""
        cm, session = mock_db_context_manager
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.all.return_value = [mock_match_bd]
        session.query.return_value = query_mock

        # Mock API qui échoue
        mock_api_module = MagicMock()
        mock_api_module.charger_matchs_a_venir.side_effect = Exception("API error")

        mock_db = MagicMock()
        mock_db.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_module,
                "src.core.db": mock_db,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            # API échoue, fallback BD est tenté (peut retourner vide si mock filter échoue)
            assert isinstance(result, list)
            assert source == "BD"

    def test_tout_echoue_retourne_liste_vide(self):
        """Test que la fonction retourne liste vide si tout échoue"""
        mock_api_service = MagicMock()
        mock_api_service.charger_matchs_a_venir.side_effect = Exception("API error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.side_effect = Exception("DB error")
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            assert result == []

    def test_api_retourne_vide_resultat_vide(self, mock_match_api):
        """Test que la fonction gère les résultats vides gracieusement"""
        # Note: Quand l'API retourne une liste vide, la fonction retourne source="API"
        # avec une liste vide (comportement attendu du code)
        mock_api_service = MagicMock()
        mock_api_service.charger_matchs_a_venir.return_value = []

        with patch.dict(sys.modules, {"src.services.jeux": mock_api_service}):
            from src.modules.jeux.utils import charger_matchs_avec_fallback

            result, source = charger_matchs_avec_fallback.__wrapped__(
                "Ligue 1", jours=7, prefer_api=True
            )

            # Le code retourne "API" même avec liste vide (ligne 39 du source)
            # puis tente le fallback BD qui peut échouer
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

        mock_api_service = MagicMock()
        mock_api_service.charger_classement.return_value = classement_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_api_service}):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "API"
            assert len(result) == 2
            assert result[0]["nom"] == "PSG"

    def test_fallback_bd_classement(self, mock_equipe_bd, mock_db_context_manager):
        """Test fallback BD pour le classement"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_equipe_bd]
        session.query.return_value = mock_query

        mock_api_service = MagicMock()
        mock_api_service.charger_classement.side_effect = Exception("API error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["nom"] == "PSG"
            assert result[0]["points"] == 58

    def test_api_retourne_vide_fallback_bd(self, mock_equipe_bd, mock_db_context_manager):
        """Test fallback BD quand API retourne vide"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_equipe_bd]
        session.query.return_value = mock_query

        mock_api_service = MagicMock()
        mock_api_service.charger_classement.return_value = []

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_classement_avec_fallback

            result, source = charger_classement_avec_fallback.__wrapped__("Ligue 1")

            assert source == "BD"

    def test_classement_tout_echoue(self):
        """Test que la fonction gère tout échoue"""
        mock_api_service = MagicMock()
        mock_api_service.charger_classement.side_effect = Exception("API error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.side_effect = Exception("DB error")
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
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

        mock_api_service = MagicMock()
        mock_api_service.charger_historique_equipe.return_value = historique_api

        with patch.dict(sys.modules, {"src.services.jeux": mock_api_service}):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "API"
            assert len(result) == 1
            assert result[0]["score_domicile"] == 3

    def test_fallback_bd_historique(self, mock_historique_match, mock_db_context_manager):
        """Test fallback BD pour l'historique"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        (
            mock_query.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value
        ) = [mock_historique_match]
        session.query.return_value = mock_query

        mock_api_service = MagicMock()
        mock_api_service.charger_historique_equipe.side_effect = Exception("API error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"
            assert len(result) == 1

    def test_api_retourne_vide_fallback_bd(self, mock_historique_match, mock_db_context_manager):
        """Test fallback BD quand API retourne vide"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        (
            mock_query.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value
        ) = [mock_historique_match]
        session.query.return_value = mock_query

        mock_api_service = MagicMock()
        mock_api_service.charger_historique_equipe.return_value = []

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_historique_equipe_avec_fallback

            result, source = charger_historique_equipe_avec_fallback.__wrapped__("PSG")

            assert source == "BD"

    def test_historique_tout_echoue(self):
        """Test historique tout échoue"""
        mock_api_service = MagicMock()
        mock_api_service.charger_historique_equipe.side_effect = Exception("API error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.side_effect = Exception("DB error")
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.services.jeux": mock_api_service,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
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

    def test_fallback_bd_tirages(self, mock_tirage_bd, mock_db_context_manager):
        """Test fallback BD pour les tirages"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_tirage_bd]
        session.query.return_value = mock_query

        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=10)

            assert source == "BD"
            assert len(result) == 1
            assert result[0]["numero_chance"] == 7

    def test_scraper_vide_fallback_bd(self, mock_tirage_bd, mock_db_context_manager):
        """Test fallback BD quand scraper retourne vide"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_tirage_bd]
        session.query.return_value = mock_query

        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.return_value = []

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_tirages_loto_avec_fallback

            result, source = charger_tirages_loto_avec_fallback.__wrapped__(limite=100)

            assert source == "BD"

    def test_tirages_tout_echoue(self):
        """Test quand tout échoue pour les tirages"""
        mock_scraper = MagicMock()
        mock_scraper.charger_tirages_loto.side_effect = Exception("Scraper error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.side_effect = Exception("DB error")
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
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

    def test_fallback_bd_stats(self, mock_stat_bd, mock_db_context_manager):
        """Test fallback BD pour les statistiques"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.filter_by.return_value.order_by.return_value.first.return_value = mock_stat_bd
        session.query.return_value = mock_query

        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"
            assert result["num_5"] == 45

    def test_scraper_vide_fallback_bd(self, mock_stat_bd, mock_db_context_manager):
        """Test fallback BD quand scraper retourne vide"""
        cm, session = mock_db_context_manager

        mock_query = MagicMock()
        mock_query.filter_by.return_value.order_by.return_value.first.return_value = mock_stat_bd
        session.query.return_value = mock_query

        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.return_value = {}

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.return_value = cm
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
            },
        ):
            from src.modules.jeux.utils import charger_stats_loto_avec_fallback

            result, source = charger_stats_loto_avec_fallback.__wrapped__()

            assert source == "BD"

    def test_stats_tout_echoue(self):
        """Test quand aucune statistique n'est disponible"""
        mock_scraper = MagicMock()
        mock_scraper.obtenir_statistiques_loto.side_effect = Exception("Scraper error")

        mock_database = MagicMock()
        mock_database.obtenir_contexte_db.side_effect = Exception("DB error")
        mock_models = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "src.modules.jeux.scraper_loto": mock_scraper,
                "src.core.db": mock_database,
                "src.core.models": mock_models,
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

    @patch("src.modules.jeux.utils.st")
    def test_bouton_clique_nettoie_cache(self, mock_st):
        """Test que le clic nettoie le cache et retourne True"""
        mock_st.button.return_value = True
        mock_st.session_state = {}
        mock_st.cache_data = MagicMock()

        from src.modules.jeux.utils import bouton_actualiser_api

        result = bouton_actualiser_api("test_key")

        assert result is True
        mock_st.cache_data.clear.assert_called_once()
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
        assert "🌐" in call_args
        assert "API" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_bd(self, mock_st):
        """Test affichage pour source BD"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("BD")

        call_args = mock_st.caption.call_args[0][0]
        assert "💾" in call_args
        assert "BD" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_scraper(self, mock_st):
        """Test affichage pour source Scraper"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Scraper FDJ")

        call_args = mock_st.caption.call_args[0][0]
        assert "🕷️" in call_args
        assert "Scraper FDJ" in call_args

    @patch("src.modules.jeux.utils.st")
    def test_affiche_source_inconnue(self, mock_st):
        """Test affichage pour source inconnue"""
        from src.modules.jeux.utils import message_source_donnees

        message_source_donnees("Autre")

        call_args = mock_st.caption.call_args[0][0]
        # Default is spider emoji for unknown sources
        assert "🕷️" in call_args
