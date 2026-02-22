"""
Tests pour src/modules/jeux/paris/utils.py

Tests des fonctions utilitaires pour le module paris sportifs.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# Fixtures (dicts retournés par les services)
# ============================================================


@pytest.fixture
def equipe_dict():
    """Fixture pour une équipe en dict (tel que retourné par le service)"""
    return {
        "id": 1,
        "nom": "Paris Saint-Germain",
        "championnat": "Ligue 1",
        "matchs_joues": 20,
        "victoires": 15,
        "nuls": 3,
        "defaites": 2,
        "buts_marques": 45,
        "buts_encaisses": 12,
        "points": 48,
    }


@pytest.fixture
def equipe_minimale_dict():
    """Fixture pour une équipe avec valeurs zéro"""
    return {
        "id": 2,
        "nom": "Nouveau Club",
        "championnat": "Ligue 1",
        "matchs_joues": 0,
        "victoires": 0,
        "nuls": 0,
        "defaites": 0,
        "buts_marques": 0,
        "buts_encaisses": 0,
        "points": 0,
    }


@pytest.fixture
def match_a_venir_dict():
    """Fixture pour un match à venir en dict"""
    return {
        "id": 100,
        "date_match": str(date.today() + timedelta(days=3)),
        "heure": "20:00",
        "championnat": "Ligue 1",
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "dom_nom": "PSG",
        "ext_nom": "OM",
        "cote_dom": 1.5,
        "cote_nul": 4.0,
        "cote_ext": 6.0,
        "joue": False,
    }


@pytest.fixture
def match_joue_dict():
    """Fixture pour un match joué en dict"""
    return {
        "id": 50,
        "date_match": str(date.today() - timedelta(days=5)),
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "score_domicile": 2,
        "score_exterieur": 1,
        "joue": True,
    }


@pytest.fixture
def pari_dict():
    """Fixture pour un pari sportif en dict"""
    return {
        "id": 200,
        "match_id": 100,
        "type_pari": "1X2",
        "prediction": "1",
        "cote": 1.8,
        "mise": 10.0,
        "statut": "en_attente",
        "gain": None,
        "est_virtuel": True,
        "cree_le": str(datetime.now()),
    }


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
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_toutes_equipes(self, mock_factory, mock_st, equipe_dict):
        """Test chargement de toutes les équipes sans filtre"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["nom"] == "Paris Saint-Germain"
        assert result[0]["points"] == 48

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_equipes_avec_filtre_championnat(self, mock_factory, mock_st, equipe_dict):
        """Test chargement des équipes filtrées par championnat"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes(championnat="Ligue 1")

        assert len(result) == 1
        mock_factory.return_value.charger_equipes.assert_called_once_with("Ligue 1")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_equipe_avec_valeurs_none(self, mock_factory, mock_st, equipe_minimale_dict):
        """Test gestion des équipes avec statistiques zéro"""
        mock_factory.return_value.charger_equipes.return_value = [equipe_minimale_dict]

        from src.modules.jeux.paris.utils import charger_equipes

        result = charger_equipes()

        assert len(result) == 1
        assert result[0]["matchs_joues"] == 0
        assert result[0]["victoires"] == 0
        assert result[0]["points"] == 0

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

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
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_prochains_7_jours(self, mock_factory, mock_st, match_a_venir_dict):
        """Test chargement des matchs des 7 prochains jours"""
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_a_venir_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert len(result) == 1
        assert result[0]["dom_nom"] == "PSG"
        assert result[0]["ext_nom"] == "OM"
        assert result[0]["cote_dom"] == 1.5

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_avec_filtre_championnat(self, mock_factory, mock_st, match_a_venir_dict):
        """Test chargement des matchs filtrés par championnat"""
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_a_venir_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir(jours=14, championnat="Ligue 1")

        assert len(result) == 1
        mock_factory.return_value.charger_matchs_a_venir.assert_called_once_with(14, "Ligue 1")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_match_sans_equipes(self, mock_factory, mock_st):
        """Test match avec équipes inconnues"""
        match_dict = {
            "id": 100,
            "date_match": str(date.today() + timedelta(days=1)),
            "heure": None,
            "championnat": "Ligue 1",
            "equipe_domicile_id": 1,
            "equipe_exterieur_id": 2,
            "dom_nom": "?",
            "ext_nom": "?",
            "cote_dom": None,
            "cote_nul": None,
            "cote_ext": None,
            "joue": False,
        }
        mock_factory.return_value.charger_matchs_a_venir.return_value = [match_dict]

        from src.modules.jeux.paris.utils import charger_matchs_a_venir

        result = charger_matchs_a_venir()

        assert result[0]["dom_nom"] == "?"
        assert result[0]["ext_nom"] == "?"

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

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
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_recents_equipe(self, mock_factory, mock_st, match_joue_dict):
        """Test chargement des matchs récents d'une équipe"""
        mock_factory.return_value.charger_matchs_recents.return_value = [match_joue_dict]

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1)

        assert len(result) == 1
        assert result[0]["score_domicile"] == 2
        assert result[0]["score_exterieur"] == 1

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_matchs_avec_limite_personnalisee(self, mock_factory, mock_st, match_joue_dict):
        """Test chargement avec nombre de matchs personnalisé"""
        mock_factory.return_value.charger_matchs_recents.return_value = [match_joue_dict]

        from src.modules.jeux.paris.utils import charger_matchs_recents

        result = charger_matchs_recents(equipe_id=1, nb_matchs=5)

        assert len(result) == 1
        mock_factory.return_value.charger_matchs_recents.assert_called_once_with(1, 5)

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

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
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_tous_paris(self, mock_factory, mock_st, pari_dict):
        """Test chargement de tous les paris sans filtre"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = [pari_dict]

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert len(result) == 1
        assert result[0]["type_pari"] == "1X2"
        assert result[0]["mise"] == 10.0
        assert result[0]["est_virtuel"] is True

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_charge_paris_par_statut(self, mock_factory, mock_st, pari_dict):
        """Test chargement des paris filtrés par statut"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = [pari_dict]

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur(statut="gagne")

        assert len(result) == 1
        mock_factory.return_value.charger_paris_utilisateur.assert_called_once_with("gagne")

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_erreur_retourne_liste_vide(self, mock_factory, mock_st):
        """Test que les erreurs retournent une liste vide"""
        mock_factory.side_effect = Exception("DB error")

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
        mock_st.error.assert_called_once()

    @patch("src.modules.jeux.paris.utils.st")
    @patch("src.modules.jeux.paris.utils.get_paris_crud_service")
    def test_paris_liste_vide(self, mock_factory, mock_st):
        """Test quand aucun pari n'existe"""
        mock_factory.return_value.charger_paris_utilisateur.return_value = []

        from src.modules.jeux.paris.utils import charger_paris_utilisateur

        result = charger_paris_utilisateur()

        assert result == []
