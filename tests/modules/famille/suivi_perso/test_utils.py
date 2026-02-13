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
    """Tests pour la fonction _calculate_streak"""

    def test_streak_zero_si_pas_de_summaries(self):
        """Retourne 0 si pas de summaries"""
        from src.modules.famille.suivi_perso.utils import _calculate_streak

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        result = _calculate_streak(mock_user, [])

        assert result == 0

    def test_streak_compte_jours_consecutifs(self):
        """Compte les jours consécutifs avec objectif atteint"""
        from src.modules.famille.suivi_perso.utils import _calculate_streak

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        today = date.today()
        mock_summary_1 = MagicMock()
        mock_summary_1.date = today
        mock_summary_1.pas = 12000

        mock_summary_2 = MagicMock()
        mock_summary_2.date = today - timedelta(days=1)
        mock_summary_2.pas = 11000

        result = _calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 2

    def test_streak_arrete_si_objectif_non_atteint(self):
        """Arrête le streak si objectif non atteint"""
        from src.modules.famille.suivi_perso.utils import _calculate_streak

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = 10000

        today = date.today()
        mock_summary_1 = MagicMock()
        mock_summary_1.date = today
        mock_summary_1.pas = 12000

        mock_summary_2 = MagicMock()
        mock_summary_2.date = today - timedelta(days=1)
        mock_summary_2.pas = 5000  # Sous l'objectif

        result = _calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 1

    def test_streak_utilise_objectif_defaut_si_none(self):
        """Utilise 10000 comme objectif par défaut"""
        from src.modules.famille.suivi_perso.utils import _calculate_streak

        mock_user = MagicMock()
        mock_user.objectif_pas_quotidien = None

        today = date.today()
        mock_summary = MagicMock()
        mock_summary.date = today
        mock_summary.pas = 10001

        result = _calculate_streak(mock_user, [mock_summary])

        assert result == 1

    def test_streak_arrete_si_jour_manquant(self):
        """Arrête le streak si un jour est manquant"""
        from src.modules.famille.suivi_perso.utils import _calculate_streak

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

        result = _calculate_streak(mock_user, [mock_summary_1, mock_summary_2])

        assert result == 1


class TestGetUserData:
    """Tests pour la fonction get_user_data"""

    def test_retourne_donnees_utilisateur(self):
        """Récupère les données complètes d'un utilisateur"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_connected = True
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500

        mock_summary = MagicMock()
        mock_summary.pas = 8000
        mock_summary.calories_actives = 300
        mock_summary.minutes_actives = 45
        mock_summary.date = date.today()

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_summary]

        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
                mock_st.error = MagicMock()

                from src.modules.famille.suivi_perso.utils import get_user_data

                result = get_user_data("anne")

                assert "user" in result
                assert "summaries" in result
                assert "total_pas" in result

    def test_cree_utilisateur_si_non_trouve(self):
        """Crée l'utilisateur s'il n'existe pas"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_connected = False
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.modules.famille.suivi_perso.utils.get_or_create_user") as mock_create:
                mock_create.return_value = mock_user

                with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
                    mock_st.error = MagicMock()

                    from src.modules.famille.suivi_perso.utils import get_user_data

                    result = get_user_data("anne")

                    mock_create.assert_called_once()

    def test_retourne_dict_vide_sur_exception(self):
        """Retourne un dict vide en cas d'erreur"""
        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            with patch("src.modules.famille.suivi_perso.utils.st") as mock_st:
                mock_st.error = MagicMock()

                from src.modules.famille.suivi_perso.utils import get_user_data

                result = get_user_data("anne")

                assert result == {}
                mock_st.error.assert_called_once()


class TestGetFoodLogsToday:
    """Tests pour la fonction get_food_logs_today"""

    def test_retourne_logs_du_jour(self):
        """Récupère les logs alimentation du jour"""
        mock_user = MagicMock()
        mock_user.id = 1

        mock_log = MagicMock()
        mock_log.date = date.today()

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.order_by.return_value.all.return_value = [mock_log]

        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert len(result) == 1

    def test_retourne_liste_vide_si_user_non_trouve(self):
        """Retourne une liste vide si l'utilisateur n'existe pas"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("inconnu")

            assert result == []

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert result == []

    def test_retourne_liste_vide_si_aucun_log(self):
        """Retourne une liste vide s'il n'y a pas de log"""
        mock_user = MagicMock()
        mock_user.id = 1

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.order_by.return_value.all.return_value = []

        with patch("src.modules.famille.suivi_perso.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.suivi_perso.utils import get_food_logs_today

            result = get_food_logs_today("anne")

            assert result == []
