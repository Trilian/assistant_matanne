"""
Tests pour src/modules/jeux/paris/utils.py

Tests des fonctions utilitaires pour le module paris sportifs.
"""

from contextlib import contextmanager
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mock_equipe():
    """Fixture pour une équipe mock"""
    equipe = MagicMock()
    equipe.id = 1
    equipe.nom = "Paris Saint-Germain"
    equipe.championnat = "Ligue 1"
    equipe.matchs_joues = 20
    equipe.victoires = 15
    equipe.nuls = 3
    equipe.defaites = 2
    equipe.buts_marques = 45
    equipe.buts_encaisses = 12
    return equipe


@pytest.fixture
def mock_equipe_minimale():
    """Fixture pour une équipe avec valeurs None"""
    equipe = MagicMock()
    equipe.id = 2
    equipe.nom = "Nouveau Club"
    equipe.championnat = "Ligue 1"
    equipe.matchs_joues = None
    equipe.victoires = None
    equipe.nuls = None
    equipe.defaites = None
    equipe.buts_marques = None
    equipe.buts_encaisses = None
    return equipe


@pytest.fixture
def mock_match_a_venir(mock_equipe):
    """Fixture pour un match à venir"""
    match = MagicMock()
    match.id = 100
    match.date_match = date.today() + timedelta(days=3)
    match.heure = "20:00"
    match.championnat = "Ligue 1"
    match.equipe_domicile_id = 1
    match.equipe_exterieur_id = 2
    match.equipe_domicile = MagicMock(nom="PSG")
    match.equipe_exterieur = MagicMock(nom="OM")
    match.cote_dom = 1.5
    match.cote_nul = 4.0
    match.cote_ext = 6.0
    match.joue = False
    return match


@pytest.fixture
def mock_match_joue():
    """Fixture pour un match joué"""
    match = MagicMock()
    match.id = 50
    match.date_match = date.today() - timedelta(days=5)
    match.equipe_domicile_id = 1
    match.equipe_exterieur_id = 2
    match.score_domicile = 2
    match.score_exterieur = 1
    match.joue = True
    return match


@pytest.fixture
def mock_pari():
    """Fixture pour un pari sportif"""
    pari = MagicMock()
    pari.id = 200
    pari.match_id = 100
    pari.type_pari = "1X2"
    pari.prediction = "1"
    pari.cote = 1.8
    pari.mise = 10.0
    pari.statut = "en_attente"
    pari.gain = None
    pari.est_virtuel = True
    pari.cree_le = datetime.now()
    return pari


@contextmanager
def mock_db_context(mock_session):
    """Context manager mock pour obtenir_contexte_db"""
    yield mock_session


# ============================================================
# Tests charger_championnats_disponibles
# ============================================================


class TestChargerChampionnatsDisponibles:
    """Tests pour charger_championnats_disponibles"""

    def test_retourne_liste_championnats(self):
        """Vérifie que la fonction retourne la liste des championnats"""
        from src.modules.jeux.paris.utils import charger_championnats_disponibles

        result = charger_championnats_disponibles()

        assert isinstance(result, list)
        assert len(result) > 0
        assert "Ligue 1" in result

    def test_contient_championnats_majeurs(self):
        """Vérifie que les 5 grands championnats sont présents"""
        from src.modules.jeux.paris.utils import charger_championnats_disponibles

        result = charger_championnats_disponibles()

        expected = ["Ligue 1", "Premier League", "La Liga", "Serie A", "Bundesliga"]
        for champ in expected:
            assert champ in result


# ============================================================
# Tests charger_equipes
# ============================================================


class TestChargerEquipes:
    """Tests pour charger_equipes"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_toutes_equipes(self, mock_db, mock_st, mock_equipe):
        """Test chargement de toutes les équipes sans filtre"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = [mock_equipe]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["nom"] == "Paris Saint-Germain"
        assert result[0]["points"] == 15 * 3 + 3  # 48 points

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_equipes_avec_filtre_championnat(self, mock_db, mock_st, mock_equipe):
        """Test chargement des équipes filtrées par championnat"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_equipe]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes(championnat="Ligue 1")

        assert len(result) == 1
        mock_query.filter.assert_called_once()

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_equipe_avec_valeurs_none(self, mock_db, mock_st, mock_equipe_minimale):
        """Test gestion des équipes avec statistiques None"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = [mock_equipe_minimale]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["matchs_joues"] == 0
        assert result[0]["victoires"] == 0
        assert result[0]["points"] == 0

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_erreur_retourne_liste_vide(self, mock_db, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_db.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_matchs_a_venir
# ============================================================


class TestChargerMatchsAVenir:
    """Tests pour charger_matchs_a_venir"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_matchs_prochains_7_jours(self, mock_db, mock_st, mock_match_a_venir):
        """Test chargement des matchs des 7 prochains jours"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_match_a_venir]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert len(result) == 1
        assert result[0]["dom_nom"] == "PSG"
        assert result[0]["ext_nom"] == "OM"
        assert result[0]["cote_dom"] == 1.5

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_matchs_avec_filtre_championnat(self, mock_db, mock_st, mock_match_a_venir):
        """Test chargement des matchs filtrés par championnat"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_match_a_venir
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir(jours=14, championnat="Ligue 1")

        assert len(result) == 1

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_match_sans_equipes(self, mock_db, mock_st):
        """Test match avec équipes None"""
        mock_match = MagicMock()
        mock_match.id = 100
        mock_match.date_match = date.today() + timedelta(days=1)
        mock_match.heure = None
        mock_match.championnat = "Ligue 1"
        mock_match.equipe_domicile_id = 1
        mock_match.equipe_exterieur_id = 2
        mock_match.equipe_domicile = None
        mock_match.equipe_exterieur = None
        mock_match.cote_dom = None
        mock_match.cote_nul = None
        mock_match.cote_ext = None
        mock_match.joue = False

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_match]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert result[0]["dom_nom"] == "?"
        assert result[0]["ext_nom"] == "?"

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_erreur_retourne_liste_vide(self, mock_db, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_db.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_matchs_recents
# ============================================================


class TestChargerMatchsRecents:
    """Tests pour charger_matchs_recents"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_matchs_recents_equipe(self, mock_db, mock_st, mock_match_joue):
        """Test chargement des matchs récents d'une équipe"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_match_joue
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1)

        assert len(result) == 1
        assert result[0]["score_domicile"] == 2
        assert result[0]["score_exterieur"] == 1

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_matchs_avec_limite_personnalisee(self, mock_db, mock_st, mock_match_joue):
        """Test chargement avec nombre de matchs personnalisé"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_match_joue
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1, nb_matchs=5)

        assert len(result) == 1
        mock_query.filter.return_value.order_by.return_value.limit.assert_called_with(5)

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_erreur_retourne_liste_vide(self, mock_db, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_db.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1)

        assert result == []
        mock_st.error.assert_called_once()


# ============================================================
# Tests charger_paris_utilisateur
# ============================================================


class TestChargerParisUtilisateur:
    """Tests pour charger_paris_utilisateur"""

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_tous_paris(self, mock_db, mock_st, mock_pari):
        """Test chargement de tous les paris sans filtre"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_pari]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert len(result) == 1
        assert result[0]["type_pari"] == "1X2"
        assert result[0]["mise"] == 10.0
        assert result[0]["est_virtuel"] is True

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_charge_paris_par_statut(self, mock_db, mock_st, mock_pari):
        """Test chargement des paris filtrés par statut"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_pari
        ]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur(statut="gagne")

        assert len(result) == 1
        mock_query.filter.assert_called_once()

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_erreur_retourne_liste_vide(self, mock_db, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_db.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
        mock_st.error.assert_called_once()

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.obtenir_contexte_db")
    def test_paris_liste_vide(self, mock_db, mock_st):
        """Test quand aucun pari n'existe"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
