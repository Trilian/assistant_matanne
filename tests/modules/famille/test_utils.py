"""
Tests pour src/modules/famille/utils.py

Refactorised: utils.py est desormais une facade mince devant les services.
Les mocks ciblent les accesseurs lazy _get_service_jules et _get_service_sante.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ================================================================
# TESTS CALCULER PROGRESSION OBJECTIF (pure logique)
# ================================================================


class TestCalculerProgressionObjectif:
    """Tests pour le calcul de progression d objectif sante"""

    def test_progression_normale(self):
        """Teste le calcul de progression normale"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 50

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 50.0

    def test_progression_complete(self):
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 100

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 100.0

    def test_progression_depassee(self):
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 150

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 100.0

    def test_progression_sans_valeur_cible(self):
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = None
        objectif.valeur_actuelle = 50

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0

    def test_progression_sans_valeur_actuelle(self):
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = None

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0

    def test_progression_erreur(self):
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = "invalid"
        objectif.valeur_actuelle = "invalid"

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0


# ================================================================
# TESTS FORMAT DATE FR (delegue a core.date_utils)
# ================================================================


class TestFormatDateFr:
    """Tests pour le formatage de date en francais."""

    def test_format_date_simple(self):
        from src.modules.famille.utils import format_date_fr

        d = date(2024, 1, 1)
        resultat = format_date_fr(d)

        assert "Lundi" in resultat
        assert "1" in resultat
        assert "Janvier" in resultat
        assert "2024" in resultat

    def test_format_tous_jours_semaine(self):
        from src.modules.famille.utils import format_date_fr

        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        for i, jour_attendu in enumerate(jours):
            d = date(2024, 1, 1) + timedelta(days=i)
            resultat = format_date_fr(d)
            assert jour_attendu in resultat

    def test_format_tous_mois(self):
        from src.modules.famille.utils import format_date_fr

        mois = [
            "Janvier",
            "Fevrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Decembre",
        ]

        for i, mois_attendu in enumerate(mois, 1):
            d = date(2024, i, 15)
            resultat = format_date_fr(d)
            assert mois_attendu in resultat, f"Mois {i}: '{mois_attendu}' not in '{resultat}'"


# ================================================================
# TESTS GET_OR_CREATE_JULES (delegue a ServiceJules)
# ================================================================


class TestGetOrCreateJules:
    """Tests pour la creation/recuperation du profil Jules."""

    @patch("src.modules.famille.utils._get_service_jules")
    def test_get_jules_existant(self, mock_svc):
        from src.modules.famille.utils import get_or_create_jules

        mock_svc.return_value.get_or_create_jules.return_value = 42

        result = get_or_create_jules()
        assert result == 42

    @patch("src.modules.famille.utils._get_service_jules")
    def test_create_jules_nouveau(self, mock_svc):
        from src.modules.famille.utils import get_or_create_jules

        mock_svc.return_value.get_or_create_jules.return_value = 1

        result = get_or_create_jules()
        assert result == 1
        mock_svc.return_value.get_or_create_jules.assert_called_once()


class TestGetOrCreateJulesErreur:
    """Tests additionnels pour get_or_create_jules."""

    @patch("src.modules.famille.utils._get_service_jules")
    def test_get_jules_erreur_db(self, mock_svc):
        from src.modules.famille.utils import get_or_create_jules

        mock_svc.return_value.get_or_create_jules.side_effect = Exception("DB Error")

        with pytest.raises(Exception):
            get_or_create_jules()


# ================================================================
# TESTS CALCULER_AGE_JULES (delegue a age_utils)
# ================================================================


class TestCalculerAgeJules:
    """Tests pour le calcul de l age de Jules."""

    @patch("src.modules.famille.utils.get_age_jules")
    def test_calculer_age_normal(self, mock_age):
        from src.modules.famille.utils import calculer_age_jules

        mock_age.return_value = {
            "mois": 20,
            "jours": 610,
            "semaines": 87,
            "ans": 1,
            "texte": "20 mois",
            "date_naissance": date(2024, 6, 22),
        }

        result = calculer_age_jules()

        assert "jours" in result
        assert "semaines" in result
        assert "mois" in result
        assert "ans" in result
        assert result["jours"] >= 0

    @patch("src.modules.famille.age_utils._obtenir_date_naissance")
    def test_calculer_age_jules_inexistant(self, mock_naissance):
        from src.core.constants import JULES_NAISSANCE
        from src.modules.famille.utils import calculer_age_jules

        mock_naissance.return_value = JULES_NAISSANCE

        result = calculer_age_jules()

        assert result["mois"] > 0
        assert result["date_naissance"] == JULES_NAISSANCE
        assert "jours" in result and "semaines" in result and "ans" in result

    @patch("src.modules.famille.age_utils._obtenir_date_naissance")
    def test_calculer_age_erreur_db(self, mock_naissance):
        from src.core.constants import JULES_NAISSANCE
        from src.modules.famille.utils import calculer_age_jules

        mock_naissance.return_value = JULES_NAISSANCE

        result = calculer_age_jules()

        assert result["mois"] > 0
        assert result["date_naissance"] == JULES_NAISSANCE


# ================================================================
# TESTS MILESTONES (delegue a ServiceJules)
# ================================================================


class TestGetMilestonesByCategory:
    """Tests pour la recuperation des jalons par categorie."""

    @patch("src.modules.famille.utils._get_service_jules")
    def test_get_milestones_groupes(self, mock_svc):
        from src.modules.famille.utils import get_milestones_by_category

        mock_svc.return_value.get_milestones_by_category.return_value = {
            "Moteur": [{"id": 1, "titre": "Premier pas"}],
            "Langage": [{"id": 2, "titre": "Premier mot"}],
        }

        result = get_milestones_by_category(1)

        assert "Moteur" in result
        assert "Langage" in result
        assert len(result["Moteur"]) == 1


class TestCountMilestonesByCategory:
    """Tests pour le comptage des jalons par categorie."""

    @patch("src.modules.famille.utils._get_service_jules")
    def test_count_milestones(self, mock_svc):
        from src.modules.famille.utils import count_milestones_by_category

        mock_svc.return_value.count_milestones_by_category.return_value = {
            "Moteur": 3,
            "Langage": 2,
        }

        result = count_milestones_by_category(1)

        assert result == {"Moteur": 3, "Langage": 2}


class TestGetMilestonesErreur:
    """Tests d erreur pour les milestones."""

    @patch("src.modules.famille.utils._get_service_jules")
    def test_milestones_erreur_db(self, mock_svc):
        from src.modules.famille.utils import get_milestones_by_category

        mock_svc.return_value.get_milestones_by_category.side_effect = Exception("DB Error")

        result = get_milestones_by_category(1)

        assert result == {}

    @patch("src.modules.famille.utils._get_service_jules")
    def test_count_milestones_erreur_db(self, mock_svc):
        from src.modules.famille.utils import count_milestones_by_category

        mock_svc.return_value.count_milestones_by_category.side_effect = Exception("DB Error")

        result = count_milestones_by_category(1)

        assert result == {}


# ================================================================
# TESTS OBJECTIFS (delegue a ServiceSante)
# ================================================================


class TestGetObjectifsActifs:
    """Tests pour la recuperation des objectifs actifs."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_objectifs_actifs(self, mock_svc):
        from src.modules.famille.utils import get_objectives_actifs

        mock_svc.return_value.get_objectives_actifs.return_value = [
            {
                "titre": "Perdre 5kg",
                "categorie": "Poids",
                "progression": 42.8,
                "jours_restants": 30,
            }
        ]

        result = get_objectives_actifs()

        assert len(result) == 1
        assert result[0]["titre"] == "Perdre 5kg"
        assert "progression" in result[0]
        assert "jours_restants" in result[0]

    @patch("src.modules.famille.utils._get_service_sante")
    def test_objectifs_actifs_erreur(self, mock_svc):
        from src.modules.famille.utils import get_objectives_actifs

        mock_svc.return_value.get_objectives_actifs.side_effect = Exception("DB Error")

        result = get_objectives_actifs()

        assert result == []


# ================================================================
# TESTS BUDGET (delegue a ServiceSante)
# ================================================================


class TestGetBudgetParPeriod:
    """Tests pour la recuperation du budget par periode."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_jour(self, mock_svc):
        from src.modules.famille.utils import get_budget_par_period

        mock_svc.return_value.get_budget_par_period.return_value = {
            "Alimentation": 50.0,
            "TOTAL": 50.0,
        }

        result = get_budget_par_period("day")

        assert "TOTAL" in result

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_semaine(self, mock_svc):
        from src.modules.famille.utils import get_budget_par_period

        mock_svc.return_value.get_budget_par_period.return_value = {"TOTAL": 0}

        result = get_budget_par_period("week")

        assert result.get("TOTAL", 0) == 0

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_mois_decembre(self, mock_svc):
        from src.modules.famille.utils import get_budget_par_period

        mock_svc.return_value.get_budget_par_period.return_value = {
            "Alimentation": 100.0,
            "TOTAL": 100.0,
        }

        result = get_budget_par_period("month")

        assert "TOTAL" in result


class TestGetBudgetMoisDernier:
    """Tests pour la recuperation du budget du mois dernier."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_mois_dernier(self, mock_svc):
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_svc.return_value.get_budget_mois_dernier.return_value = 1500.50

        result = get_budget_mois_dernier()

        assert result == 1500.50

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_mois_dernier_janvier(self, mock_svc):
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_svc.return_value.get_budget_mois_dernier.return_value = 0.0

        result = get_budget_mois_dernier()

        assert result == 0.0


class TestGetBudgetErreur:
    """Tests d erreur pour le budget."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_par_period_erreur(self, mock_svc):
        from src.modules.famille.utils import get_budget_par_period

        mock_svc.return_value.get_budget_par_period.side_effect = Exception("DB Error")

        result = get_budget_par_period("month")

        assert result == {}

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_mois_dernier_erreur(self, mock_svc):
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_svc.return_value.get_budget_mois_dernier.side_effect = Exception("DB Error")

        result = get_budget_mois_dernier()

        assert result == 0.0


# ================================================================
# TESTS ACTIVITES (delegue a ServiceSante)
# ================================================================


class TestGetActivitesSemaine:
    """Tests pour la recuperation des activites de la semaine."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_activites_semaine(self, mock_svc):
        from src.modules.famille.utils import get_activites_semaine

        mock_svc.return_value.get_activites_semaine.return_value = [
            {"titre": "Sport", "date_prevue": date.today().isoformat()}
        ]

        result = get_activites_semaine()

        assert len(result) == 1
        assert result[0]["titre"] == "Sport"


class TestGetBudgetActivitesMois:
    """Tests pour le budget des activites du mois."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_activites_mois(self, mock_svc):
        from src.modules.famille.utils import get_budget_activites_mois

        mock_svc.return_value.get_budget_activites_mois.return_value = 250.0

        result = get_budget_activites_mois()

        assert result == 250.0


class TestGetActivitesErreur:
    """Tests d erreur pour les activites."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_activites_semaine_erreur(self, mock_svc):
        from src.modules.famille.utils import get_activites_semaine

        mock_svc.return_value.get_activites_semaine.side_effect = Exception("DB Error")

        result = get_activites_semaine()

        assert result == []

    @patch("src.modules.famille.utils._get_service_sante")
    def test_budget_activites_mois_erreur(self, mock_svc):
        from src.modules.famille.utils import get_budget_activites_mois

        mock_svc.return_value.get_budget_activites_mois.side_effect = Exception("DB Error")

        result = get_budget_activites_mois()

        assert result == 0.0


# ================================================================
# TESTS ROUTINES & STATS SANTE (delegue a ServiceSante)
# ================================================================


class TestGetRoutinesActives:
    """Tests pour la recuperation des routines actives."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_routines_actives(self, mock_svc):
        from src.modules.famille.utils import get_routines_actives

        mock_svc.return_value.get_routines_actives.return_value = [
            {"nom": "Course", "type_routine": "Cardio", "frequence": "quotidien"}
        ]

        result = get_routines_actives()

        assert len(result) == 1
        assert result[0]["nom"] == "Course"


class TestGetStatsSanteSemaine:
    """Tests pour les stats sante de la semaine."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_stats_sante_semaine(self, mock_svc):
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_svc.return_value.get_stats_sante_semaine.return_value = {
            "nb_seances": 2,
            "total_minutes": 75,
            "total_calories": 500,
            "energie_moyenne": 3.5,
            "moral_moyen": 4.5,
        }

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 2
        assert result["total_minutes"] == 75
        assert result["total_calories"] == 500

    @patch("src.modules.famille.utils._get_service_sante")
    def test_stats_sante_semaine_vide(self, mock_svc):
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_svc.return_value.get_stats_sante_semaine.return_value = {
            "nb_seances": 0,
            "total_minutes": 0,
            "total_calories": 0,
            "energie_moyenne": 0,
            "moral_moyen": 0,
        }

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 0
        assert result["total_minutes"] == 0


class TestGetRoutinesErreur:
    """Tests d erreur pour les routines."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_routines_actives_erreur(self, mock_svc):
        from src.modules.famille.utils import get_routines_actives

        mock_svc.return_value.get_routines_actives.side_effect = Exception("DB Error")

        result = get_routines_actives()

        assert result == []


class TestGetStatsSanteErreur:
    """Tests d erreur pour les stats sante."""

    @patch("src.modules.famille.utils._get_service_sante")
    def test_stats_sante_semaine_erreur(self, mock_svc):
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_svc.return_value.get_stats_sante_semaine.side_effect = Exception("DB Error")

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 0
        assert result["total_minutes"] == 0


# ================================================================
# TESTS CACHE & UTILITAIRES
# ================================================================


class TestClearFamilleCache:
    """Tests pour le vidage du cache."""

    def test_clear_cache_ne_leve_pas_exception(self):
        from src.modules.famille.utils import clear_famille_cache

        clear_famille_cache()
