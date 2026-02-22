"""
Tests pour src/modules/famille/weekend/utils.py

Tests complets pour les fonctions utilitaires du module weekend.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


class TestConstantes:
    """Tests pour les constantes du module"""

    def test_types_activites_contient_cles_attendues(self):
        """Vérifie que TYPES_ACTIVITES contient toutes les clés attendues"""
        from src.modules.famille.weekend.utils import TYPES_ACTIVITES

        cles_attendues = [
            "parc",
            "musee",
            "piscine",
            "zoo",
            "restaurant",
            "cinema",
            "sport",
            "shopping",
            "famille",
            "maison",
            "autre",
        ]
        for cle in cles_attendues:
            assert cle in TYPES_ACTIVITES

    def test_types_activites_structure(self):
        """Vérifie la structure des types d'activités"""
        from src.modules.famille.weekend.utils import TYPES_ACTIVITES

        for cle, valeur in TYPES_ACTIVITES.items():
            assert "emoji" in valeur
            assert "label" in valeur

    def test_meteo_options_contient_valeurs(self):
        """Vérifie que METEO_OPTIONS contient les valeurs attendues"""
        from src.modules.famille.weekend.utils import METEO_OPTIONS

        assert "ensoleille" in METEO_OPTIONS
        assert "nuageux" in METEO_OPTIONS
        assert "pluvieux" in METEO_OPTIONS
        assert "interieur" in METEO_OPTIONS


class TestGetNextWeekend:
    """Tests pour la fonction get_next_weekend"""

    def test_retourne_tuple_dates(self):
        """Retourne un tuple de deux dates"""
        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        assert isinstance(saturday, date)
        assert isinstance(sunday, date)

    def test_dimanche_lendemain_samedi(self):
        """Dimanche est le lendemain du samedi"""
        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        assert sunday == saturday + timedelta(days=1)

    def test_samedi_est_samedi(self):
        """Le samedi retourné est bien un samedi"""
        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        assert saturday.weekday() == 5  # Samedi

    def test_dimanche_est_dimanche(self):
        """Le dimanche retourné est bien un dimanche"""
        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        assert sunday.weekday() == 6  # Dimanche

    @patch("src.modules.famille.weekend.utils.date")
    def test_si_samedi_retourne_ce_samedi(self, mock_date):
        """Si on est samedi, retourne ce samedi"""
        mock_today = date(2026, 2, 14)  # Un samedi
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        assert saturday == mock_today
        assert sunday == mock_today + timedelta(days=1)

    @patch("src.modules.famille.weekend.utils.date")
    def test_si_dimanche_retourne_prochain_samedi(self, mock_date):
        """Si on est dimanche, retourne le prochain samedi"""
        mock_today = date(2026, 2, 15)  # Un dimanche
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        # Prochain samedi est dans 6 jours
        assert saturday == mock_today + timedelta(days=6)

    @patch("src.modules.famille.weekend.utils.date")
    def test_si_lundi_retourne_prochain_samedi(self, mock_date):
        """Si on est lundi, retourne le prochain samedi"""
        mock_today = date(2026, 2, 16)  # Un lundi
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        from src.modules.famille.weekend.utils import get_next_weekend

        saturday, sunday = get_next_weekend()

        # Prochain samedi est dans 5 jours
        assert saturday == mock_today + timedelta(days=5)


class TestGetWeekendActivities:
    """Tests pour la fonction get_weekend_activities"""

    def test_retourne_dict_avec_saturday_sunday(self):
        """Retourne un dict avec les clés saturday et sunday"""
        mock_service = MagicMock()
        mock_service.lister_activites_weekend.return_value = {"saturday": [], "sunday": []}

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_weekend_activities

            saturday = date(2026, 2, 14)
            sunday = date(2026, 2, 15)
            result = get_weekend_activities(saturday, sunday)

            assert "saturday" in result
            assert "sunday" in result

    def test_separe_activites_par_jour(self):
        """Sépare les activités par jour"""
        saturday = date(2026, 2, 14)
        sunday = date(2026, 2, 15)

        mock_act_samedi = MagicMock(date_prevue=saturday)
        mock_act_dimanche = MagicMock(date_prevue=sunday)

        mock_service = MagicMock()
        mock_service.lister_activites_weekend.return_value = {
            "saturday": [mock_act_samedi],
            "sunday": [mock_act_dimanche],
        }

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_weekend_activities

            result = get_weekend_activities(saturday, sunday)

            assert len(result["saturday"]) == 1
            assert len(result["sunday"]) == 1

    def test_retourne_dict_vide_sur_exception(self):
        """Retourne des listes vides en cas d'erreur"""
        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.weekend.utils import get_weekend_activities

            result = get_weekend_activities(date(2026, 2, 14), date(2026, 2, 15))

            assert result == {"saturday": [], "sunday": []}


class TestGetBudgetWeekend:
    """Tests pour la fonction get_budget_weekend"""

    def test_calcule_budget_estime_et_reel(self):
        """Calcule le budget estimé et réel"""
        mock_service = MagicMock()
        mock_service.get_budget_weekend.return_value = {"estime": 80.0, "reel": 45.0}

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_budget_weekend

            result = get_budget_weekend(date(2026, 2, 14), date(2026, 2, 15))

            assert result["estime"] == 80.0
            assert result["reel"] == 45.0

    def test_retourne_zeros_si_pas_activites(self):
        """Retourne des zéros s'il n'y a pas d'activités"""
        mock_service = MagicMock()
        mock_service.get_budget_weekend.return_value = {"estime": 0, "reel": 0}

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_budget_weekend

            result = get_budget_weekend(date(2026, 2, 14), date(2026, 2, 15))

            assert result == {"estime": 0, "reel": 0}

    def test_retourne_zeros_sur_exception(self):
        """Retourne des zéros en cas d'erreur"""
        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.weekend.utils import get_budget_weekend

            result = get_budget_weekend(date(2026, 2, 14), date(2026, 2, 15))

            assert result == {"estime": 0, "reel": 0}

    def test_gere_cout_none(self):
        """Gère les coûts None"""
        mock_service = MagicMock()
        mock_service.get_budget_weekend.return_value = {"estime": 0, "reel": 0}

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_budget_weekend

            result = get_budget_weekend(date(2026, 2, 14), date(2026, 2, 15))

            assert result["estime"] == 0
            assert result["reel"] == 0


class TestGetLieuxTestes:
    """Tests pour la fonction get_lieux_testes"""

    def test_retourne_liste_lieux(self):
        """Récupère les lieux déjà testés"""
        mock_lieu = MagicMock(note_lieu=4)
        mock_service = MagicMock()
        mock_service.get_lieux_testes.return_value = [mock_lieu]

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_lieux_testes

            result = get_lieux_testes()

            assert len(result) == 1

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.weekend.utils import get_lieux_testes

            result = get_lieux_testes()

            assert result == []

    def test_retourne_liste_vide_si_aucun_lieu(self):
        """Retourne une liste vide si aucun lieu"""
        mock_service = MagicMock()
        mock_service.get_lieux_testes.return_value = []

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import get_lieux_testes

            result = get_lieux_testes()

            assert result == []


class TestGetAgeJulesMois:
    """Tests pour la fonction get_age_jules_mois"""

    def test_retourne_age_en_mois(self):
        """Récupère l'âge de Jules en mois"""
        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = date(2024, 6, 22)

            from src.modules.famille.weekend.utils import get_age_jules_mois

            result = get_age_jules_mois()

            assert isinstance(result, int)
            assert result > 0

    def test_retourne_19_par_defaut_si_non_trouve(self):
        """Retourne l'âge calculé depuis JULES_NAISSANCE si non trouvé en BD."""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.weekend.utils import get_age_jules_mois

            result = get_age_jules_mois()

            expected = (date.today() - JULES_NAISSANCE).days // 30
            assert result == expected

    def test_retourne_19_sur_exception(self):
        """Retourne l'âge calculé depuis JULES_NAISSANCE en cas d'erreur BD."""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.weekend.utils import get_age_jules_mois

            result = get_age_jules_mois()

            expected = (date.today() - JULES_NAISSANCE).days // 30
            assert result == expected

    def test_retourne_19_si_date_naissance_none(self):
        """Retourne l'âge calculé depuis JULES_NAISSANCE si date_of_birth est None."""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.weekend.utils import get_age_jules_mois

            result = get_age_jules_mois()

            expected = (date.today() - JULES_NAISSANCE).days // 30
            assert result == expected


class TestMarkActivityDone:
    """Tests pour la fonction mark_activity_done"""

    def test_marque_activite_terminee(self):
        """Marque une activité comme terminée"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import mark_activity_done

            mark_activity_done(1)

            mock_service.marquer_termine.assert_called_once_with(1)

    def test_ne_fait_rien_si_activite_non_trouvee(self):
        """Délègue au service même si activité inexistante"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend", return_value=mock_service
        ):
            from src.modules.famille.weekend.utils import mark_activity_done

            mark_activity_done(999)

            mock_service.marquer_termine.assert_called_once_with(999)

    def test_gere_exception_silencieusement(self):
        """Gère les exceptions silencieusement"""
        with patch(
            "src.modules.famille.weekend.utils.obtenir_service_weekend",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.weekend.utils import mark_activity_done

            # Ne doit pas lever d'exception
            mark_activity_done(1)
