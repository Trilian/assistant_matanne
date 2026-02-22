"""
Tests pour src/modules/famille/suivi_perso/utils.py

Tests complets pour les fonctions utilitaires du module suivi_perso.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


class TestGetCurrentUser:
    """Tests pour la fonction get_current_user"""

    def test_retourne_utilisateur_courant(self):
        """Récupère l'utilisateur courant depuis session_state"""
        mock_session_state = {"suivi_user": "mathieu"}

        with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
            mock_st.session_state = mock_session_state

            from src.modules.famille.suivi_perso.utils import get_current_user

            result = get_current_user()

            assert result == "mathieu"

    def test_retourne_anne_par_defaut(self):
        """Retourne 'anne' par défaut si pas de session"""
        mock_session_state = {}

        with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
            mock_st.session_state = mock_session_state

            from src.modules.famille.suivi_perso.utils import get_current_user

            result = get_current_user()

            assert result == "anne"


class TestSetCurrentUser:
    """Tests pour la fonction set_current_user"""

    def test_definit_utilisateur_courant(self):
        """Définit l'utilisateur courant dans session_state"""
        mock_session_state = {}

        with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
            mock_st.session_state = mock_session_state

            from src.modules.famille.suivi_perso.utils import set_current_user

            set_current_user("mathieu")

            assert mock_session_state["suivi_user"] == "mathieu"

    def test_ecrase_utilisateur_existant(self):
        """Écrase l'utilisateur existant"""
        mock_session_state = {"suivi_user": "anne"}

        with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
            mock_st.session_state = mock_session_state

            from src.modules.famille.suivi_perso.utils import set_current_user

            set_current_user("mathieu")

            assert mock_session_state["suivi_user"] == "mathieu"


class TestCalculateStreak:
    """Tests pour la méthode _calculate_streak du service suivi perso"""

    def _make_service(self):
        """Crée une instance du service suivi perso."""
        from src.services.famille.suivi_perso import ServiceSuiviPerso

        return ServiceSuiviPerso()

    def test_streak_zero_si_pas_de_summaries(self):
        """Retourne 0 si pas de summaries"""
        service = self._make_service()

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        result = service._calculate_streak(mock_user, [])

        assert result == 0

    def test_streak_compte_jours_consecutifs(self):
        """Compte les jours consécutifs avec objectif atteint"""
        service = self._make_service()

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        today = date.today()
        mock_summary_1 = MagicMock()
        mock_summary_1.date = today
        mock_summary_1.pas = 12000

        mock_summary_2 = MagicMock()
        mock_summary_2.date = today - timedelta(days=1)
        mock_summary_2.pas = 11000

        result = service._calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 2

    def test_streak_arrete_si_objectif_non_atteint(self):
        """Arrête le streak si objectif non atteint"""
        service = self._make_service()

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        today = date.today()
        mock_summary_1 = MagicMock()
        mock_summary_1.date = today
        mock_summary_1.pas = 12000

        mock_summary_2 = MagicMock()
        mock_summary_2.date = today - timedelta(days=1)
        mock_summary_2.pas = 5000  # Sous l'objectif

        result = service._calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 1

    def test_streak_utilise_objectif_defaut_si_none(self):
        """Utilise 10000 comme objectif par défaut"""
        service = self._make_service()

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = None

        today = date.today()
        mock_summary = MagicMock()
        mock_summary.date = today
        mock_summary.pas = 10001

        result = service._calculate_streak(mock_user, [mock_summary])

        assert result == 1

    def test_streak_arrete_si_jour_manquant(self):
        """Arrête le streak si un jour est manquant"""
        service = self._make_service()

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        today = date.today()
        mock_summary_1 = MagicMock()
        mock_summary_1.date = today
        mock_summary_1.pas = 12000

        # Pas de summary pour hier
        mock_summary_2 = MagicMock()
        mock_summary_2.date = today - timedelta(days=2)
        mock_summary_2.pas = 11000

        result = service._calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 1


class TestGetUserData:
    """Tests pour la fonction get_user_data"""

    def test_retourne_donnees_utilisateur(self):
        """Récupère les données utilisateur complètes"""
        mock_service = MagicMock()
        mock_service.get_user_data.return_value = {
            "user": MagicMock(),
            "summaries": [MagicMock()],
            "total_pas": 8000,
        }

        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            return_value=mock_service,
        ):
            from src.modules.famille.suivi_perso.utils import get_user_data

            result = get_user_data("anne")

            assert "user" in result
            assert "summaries" in result
            assert "total_pas" in result

    def test_cree_utilisateur_si_non_trouve(self):
        """Délègue au service la création utilisateur"""
        mock_service = MagicMock()
        mock_service.get_user_data.return_value = {"user": MagicMock()}

        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            return_value=mock_service,
        ):
            from src.modules.famille.suivi_perso.utils import get_user_data

            result = get_user_data("anne")

            mock_service.get_user_data.assert_called_once_with("anne")

    def test_retourne_dict_vide_sur_exception(self):
        """Retourne un dict vide en cas d'erreur"""
        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.suivi_perso.utils import get_user_data

            result = get_user_data("anne")

            assert result == {}


class TestGetFoodLogsToday:
    """Tests pour la fonction get_food_logs_today"""

    def test_retourne_logs_du_jour(self):
        """Récupère les logs alimentation du jour"""
        mock_log = MagicMock(date=date.today())
        mock_service = MagicMock()
        mock_service.get_food_logs_today.return_value = [mock_log]

        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            return_value=mock_service,
        ):
            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert len(result) == 1

    def test_retourne_liste_vide_si_user_non_trouve(self):
        """Retourne une liste vide si l'utilisateur n'existe pas"""
        mock_service = MagicMock()
        mock_service.get_food_logs_today.return_value = []

        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            return_value=mock_service,
        ):
            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("inconnu")

            assert result == []

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert result == []

    def test_retourne_liste_vide_si_aucun_log(self):
        """Retourne une liste vide s'il n'y a pas de log"""
        mock_service = MagicMock()
        mock_service.get_food_logs_today.return_value = []

        with patch(
            "src.modules.famille.suivi_perso.utils.obtenir_service_suivi_perso",
            return_value=mock_service,
        ):
            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert result == []
