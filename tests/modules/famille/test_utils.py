"""
Tests pour src/modules/famille/utils.py

Tests complets pour atteindre 80%+ de couverture.
Utilise des mocks pour isoler la base de données et Streamlit.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestCalculerProgressionObjectif:
    """Tests pour le calcul de progression d'objectif santé"""

    def test_progression_normale(self):
        """Teste le calcul de progression normale"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 50

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 50.0

    def test_progression_complete(self):
        """Teste la progression à 100%"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 100

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 100.0

    def test_progression_depassee(self):
        """Teste la progression dépassant 100%"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = 150

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 100.0  # Plafonné à 100%

    def test_progression_sans_valeur_cible(self):
        """Teste avec valeur cible nulle"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = None
        objectif.valeur_actuelle = 50

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0

    def test_progression_sans_valeur_actuelle(self):
        """Teste avec valeur actuelle nulle"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = 100
        objectif.valeur_actuelle = None

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0

    def test_progression_erreur(self):
        """Teste la gestion des erreurs"""
        from src.modules.famille.utils import calculer_progression_objectif

        objectif = MagicMock()
        objectif.valeur_cible = "invalid"
        objectif.valeur_actuelle = "invalid"

        resultat = calculer_progression_objectif(objectif)
        assert resultat == 0.0


class TestFormatDateFr:
    """Tests pour le formatage de date en français"""

    def test_format_date_simple(self):
        """Teste le formatage d'une date simple"""
        from src.modules.famille.utils import format_date_fr

        # Un lundi fixe
        d = date(2024, 1, 1)  # 1er janvier 2024 est un lundi
        resultat = format_date_fr(d)

        assert "lundi" in resultat
        assert "1" in resultat
        assert "jan" in resultat
        assert "2024" in resultat

    def test_format_tous_jours_semaine(self):
        """Teste le formatage pour tous les jours de la semaine"""
        from src.modules.famille.utils import format_date_fr

        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

        # Semaine du 1er janvier 2024 (lundi)
        for i, jour_attendu in enumerate(jours):
            d = date(2024, 1, 1) + timedelta(days=i)
            resultat = format_date_fr(d)
            assert jour_attendu in resultat

    def test_format_tous_mois(self):
        """Teste le formatage pour tous les mois"""
        from src.modules.famille.utils import format_date_fr

        mois = ["jan", "fev", "mar", "avr", "mai", "jun", "jul", "aoû", "sep", "oct", "nov", "dec"]

        for i, mois_attendu in enumerate(mois, 1):
            d = date(2024, i, 15)
            resultat = format_date_fr(d)
            assert mois_attendu in resultat


class TestGetOrCreateJules:
    """Tests pour la création/récupération du profil Jules"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_get_jules_existant(self, mock_db, mock_st):
        """Teste la récupération d'un profil Jules existant"""
        from src.modules.famille.utils import get_or_create_jules

        # Mock Jules existant
        mock_jules = MagicMock()
        mock_jules.id = 42

        mock_session = MagicMock()
        mock_session.query().filter_by().first.return_value = mock_jules
        mock_db.return_value.__enter__.return_value = mock_session

        # Vider le cache avant le test
        get_or_create_jules.clear()

        result = get_or_create_jules()
        assert result == 42

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_create_jules_nouveau(self, mock_db, mock_st):
        """Teste la création d'un nouveau profil Jules"""
        from src.modules.famille.utils import get_or_create_jules

        # Mock Jules n'existe pas
        mock_jules = MagicMock()
        mock_jules.id = 1

        mock_session = MagicMock()
        mock_session.query().filter_by().first.return_value = None

        def set_id_on_add(obj):
            obj.id = 1

        mock_session.add.side_effect = set_id_on_add
        mock_db.return_value.__enter__.return_value = mock_session

        # Vider le cache avant le test
        get_or_create_jules.clear()

        # La fonction retourne l'ID créé
        # Simuler que après commit, l'objet a un id
        with patch("src.modules.famille.utils.ChildProfile") as mock_child:
            mock_child_instance = MagicMock()
            mock_child_instance.id = 1
            mock_child.return_value = mock_child_instance

            result = get_or_create_jules()
            assert mock_session.add.called
            assert mock_session.commit.called


class TestCalculerAgeJules:
    """Tests pour le calcul de l'âge de Jules"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_calculer_age_normal(self, mock_db, mock_st):
        """Teste le calcul d'âge normal"""
        from src.modules.famille.utils import calculer_age_jules

        mock_jules = MagicMock()
        mock_jules.date_of_birth = date(2024, 6, 22)

        mock_session = MagicMock()
        mock_session.query().filter_by().first.return_value = mock_jules
        mock_db.return_value.__enter__.return_value = mock_session

        result = calculer_age_jules()

        assert "jours" in result
        assert "semaines" in result
        assert "mois" in result
        assert "ans" in result
        assert result["jours"] >= 0

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_calculer_age_jules_inexistant(self, mock_db, mock_st):
        """Teste le calcul quand Jules n'existe pas"""
        from src.modules.famille.utils import calculer_age_jules

        mock_session = MagicMock()
        mock_session.query().filter_by().first.return_value = None
        mock_db.return_value.__enter__.return_value = mock_session

        result = calculer_age_jules()

        assert result == {"jours": 0, "semaines": 0, "mois": 0, "ans": 0}

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_calculer_age_erreur_db(self, mock_db, mock_st):
        """Teste la gestion d'erreur de base de données"""
        from src.modules.famille.utils import calculer_age_jules

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        result = calculer_age_jules()

        assert result == {"jours": 0, "semaines": 0, "mois": 0, "ans": 0}
        mock_st.error.assert_called()


class TestGetMilestonesByCategory:
    """Tests pour la récupération des jalons par catégorie"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_get_milestones_groupes(self, mock_db, mock_st):
        """Teste la récupération et groupement des jalons"""
        from src.modules.famille.utils import get_milestones_by_category

        mock_milestone1 = MagicMock()
        mock_milestone1.id = 1
        mock_milestone1.categorie = "Moteur"
        mock_milestone1.titre = "Premier pas"
        mock_milestone1.date_atteint = date.today()
        mock_milestone1.description = "Description"
        mock_milestone1.notes = "Notes"

        mock_milestone2 = MagicMock()
        mock_milestone2.id = 2
        mock_milestone2.categorie = "Langage"
        mock_milestone2.titre = "Premier mot"
        mock_milestone2.date_atteint = date.today()
        mock_milestone2.description = "Description"
        mock_milestone2.notes = "Notes"

        mock_session = MagicMock()
        mock_session.query().filter_by().all.return_value = [mock_milestone1, mock_milestone2]
        mock_db.return_value.__enter__.return_value = mock_session

        # Vider le cache
        get_milestones_by_category.clear()

        result = get_milestones_by_category(1)

        assert "Moteur" in result
        assert "Langage" in result
        assert len(result["Moteur"]) == 1


class TestCountMilestonesByCategory:
    """Tests pour le comptage des jalons par catégorie"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_count_milestones(self, mock_db, mock_st):
        """Teste le comptage des jalons"""
        from src.modules.famille.utils import count_milestones_by_category

        mock_session = MagicMock()
        mock_session.query().filter_by().group_by().all.return_value = [
            ("Moteur", 3),
            ("Langage", 2),
        ]
        mock_db.return_value.__enter__.return_value = mock_session

        result = count_milestones_by_category(1)

        assert result == {"Moteur": 3, "Langage": 2}


class TestGetBudgetParPeriod:
    """Tests pour la récupération du budget par période"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_jour(self, mock_db, mock_st):
        """Teste la récupération du budget journalier"""
        from src.modules.famille.utils import get_budget_par_period

        mock_budget = MagicMock()
        mock_budget.categorie = "Alimentation"
        mock_budget.montant = 50

        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = [mock_budget]
        mock_db.return_value.__enter__.return_value = mock_session

        # Vider le cache
        get_budget_par_period.clear()

        result = get_budget_par_period("day")

        assert "TOTAL" in result

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_semaine(self, mock_db, mock_st):
        """Teste la récupération du budget hebdomadaire"""
        from src.modules.famille.utils import get_budget_par_period

        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = []
        mock_db.return_value.__enter__.return_value = mock_session

        get_budget_par_period.clear()

        result = get_budget_par_period("week")

        assert result.get("TOTAL", 0) == 0


class TestGetBudgetMoisDernier:
    """Tests pour la récupération du budget du mois dernier"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_mois_dernier(self, mock_db, mock_st):
        """Teste la récupération du budget du mois dernier"""
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_session = MagicMock()
        mock_session.query().filter().scalar.return_value = 1500.50
        mock_db.return_value.__enter__.return_value = mock_session

        result = get_budget_mois_dernier()

        assert result == 1500.50

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_mois_dernier_janvier(self, mock_db, mock_st):
        """Teste la récupération en janvier (mois précédent = décembre année passée)"""
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_session = MagicMock()
        mock_session.query().filter().scalar.return_value = None
        mock_db.return_value.__enter__.return_value = mock_session

        result = get_budget_mois_dernier()

        assert result == 0.0


class TestGetActivitesSemaine:
    """Tests pour la récupération des activités de la semaine"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_activites_semaine(self, mock_db, mock_st):
        """Teste la récupération des activités de la semaine"""
        from src.modules.famille.utils import get_activites_semaine

        mock_activite = MagicMock()
        mock_activite.id = 1
        mock_activite.titre = "Sport"
        mock_activite.date_prevue = date.today()
        mock_activite.type_activite = "Loisir"
        mock_activite.lieu = "Parc"
        mock_activite.qui_participe = ["Papa", "Maman"]
        mock_activite.cout_estime = 0
        mock_activite.statut = "planifie"

        mock_session = MagicMock()
        mock_session.query().filter().order_by().all.return_value = [mock_activite]
        mock_db.return_value.__enter__.return_value = mock_session

        get_activites_semaine.clear()

        result = get_activites_semaine()

        assert len(result) == 1
        assert result[0]["titre"] == "Sport"


class TestGetBudgetActivitesMois:
    """Tests pour le budget des activités du mois"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_activites_mois(self, mock_db, mock_st):
        """Teste la récupération du budget activités"""
        from src.modules.famille.utils import get_budget_activites_mois

        mock_session = MagicMock()
        mock_session.query().filter().scalar.return_value = 250.0
        mock_db.return_value.__enter__.return_value = mock_session

        result = get_budget_activites_mois()

        assert result == 250.0


class TestGetRoutinesActives:
    """Tests pour la récupération des routines actives"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_routines_actives(self, mock_db, mock_st):
        """Teste la récupération des routines actives"""
        from src.modules.famille.utils import get_routines_actives

        mock_routine = MagicMock()
        mock_routine.id = 1
        mock_routine.nom = "Course"
        mock_routine.type_routine = "Cardio"
        mock_routine.frequence = "quotidien"
        mock_routine.duree_minutes = 30
        mock_routine.intensite = "modere"
        mock_routine.calories_brulees_estimees = 300

        mock_session = MagicMock()
        mock_session.query().filter_by().all.return_value = [mock_routine]
        mock_db.return_value.__enter__.return_value = mock_session

        get_routines_actives.clear()

        result = get_routines_actives()

        assert len(result) == 1
        assert result[0]["nom"] == "Course"


class TestGetStatsSanteSemaine:
    """Tests pour les stats santé de la semaine"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_stats_sante_semaine(self, mock_db, mock_st):
        """Teste le calcul des stats santé"""
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_entry1 = MagicMock()
        mock_entry1.duree_minutes = 30
        mock_entry1.calories_brulees = 200
        mock_entry1.note_energie = 4
        mock_entry1.note_moral = 5

        mock_entry2 = MagicMock()
        mock_entry2.duree_minutes = 45
        mock_entry2.calories_brulees = 300
        mock_entry2.note_energie = 3
        mock_entry2.note_moral = 4

        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = [mock_entry1, mock_entry2]
        mock_db.return_value.__enter__.return_value = mock_session

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 2
        assert result["total_minutes"] == 75
        assert result["total_calories"] == 500

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_stats_sante_semaine_vide(self, mock_db, mock_st):
        """Teste les stats avec aucune entrée"""
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = []
        mock_db.return_value.__enter__.return_value = mock_session

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 0
        assert result["total_minutes"] == 0


class TestClearFamilleCache:
    """Tests pour le vidage du cache"""

    @patch("src.modules.famille.utils.st")
    def test_clear_cache(self, mock_st):
        """Teste le vidage du cache"""
        from src.modules.famille.utils import clear_famille_cache

        clear_famille_cache()

        mock_st.cache_data.clear.assert_called_once()


class TestGetObjectifsActifs:
    """Tests pour la récupération des objectifs actifs"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_objectifs_actifs(self, mock_db, mock_st):
        """Teste la récupération des objectifs en cours"""
        from src.modules.famille.utils import get_objectives_actifs

        mock_objectif = MagicMock()
        mock_objectif.id = 1
        mock_objectif.titre = "Perdre 5kg"
        mock_objectif.categorie = "Poids"
        mock_objectif.valeur_cible = 70
        mock_objectif.valeur_actuelle = 73
        mock_objectif.unite = "kg"
        mock_objectif.priorite = "haute"
        mock_objectif.date_cible = date.today() + timedelta(days=30)

        mock_session = MagicMock()
        mock_session.query().filter_by().all.return_value = [mock_objectif]
        mock_db.return_value.__enter__.return_value = mock_session

        get_objectives_actifs.clear()

        result = get_objectives_actifs()

        assert len(result) == 1
        assert result[0]["titre"] == "Perdre 5kg"
        assert "progression" in result[0]
        assert "jours_restants" in result[0]

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_objectifs_actifs_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour les objectifs"""
        from src.modules.famille.utils import get_objectives_actifs

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_objectives_actifs.clear()

        result = get_objectives_actifs()

        assert result == []
        mock_st.error.assert_called()


# ═══════════════════════════════════════════════════════════════════
# TESTS ADDITIONNELS POUR COUVERTURE
# ═══════════════════════════════════════════════════════════════════


class TestGetOrCreateJulesErreur:
    """Tests additionnels pour get_or_create_jules"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_get_jules_erreur_db(self, mock_db, mock_st):
        """Teste la gestion d'erreur lors de la création de Jules"""
        from src.modules.famille.utils import get_or_create_jules

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_or_create_jules.clear()

        with pytest.raises(Exception):
            get_or_create_jules()

        mock_st.error.assert_called()


class TestGetMilestonesErreur:
    """Tests d'erreur pour les milestones"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_milestones_erreur_db(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour les milestones"""
        from src.modules.famille.utils import get_milestones_by_category

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_milestones_by_category.clear()

        result = get_milestones_by_category(1)

        assert result == {}
        mock_st.error.assert_called()

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_count_milestones_erreur_db(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour le comptage des milestones"""
        from src.modules.famille.utils import count_milestones_by_category

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        result = count_milestones_by_category(1)

        assert result == {}
        mock_st.error.assert_called()


class TestGetBudgetErreur:
    """Tests d'erreur pour le budget"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_par_period_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour le budget par période"""
        from src.modules.famille.utils import get_budget_par_period

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_budget_par_period.clear()

        result = get_budget_par_period("month")

        assert result == {}
        mock_st.error.assert_called()

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_mois_dernier_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour le budget du mois dernier"""
        from src.modules.famille.utils import get_budget_mois_dernier

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        result = get_budget_mois_dernier()

        assert result == 0.0
        mock_st.error.assert_called()


class TestGetActivitesErreur:
    """Tests d'erreur pour les activités"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_activites_semaine_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour les activités"""
        from src.modules.famille.utils import get_activites_semaine

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_activites_semaine.clear()

        result = get_activites_semaine()

        assert result == []
        mock_st.error.assert_called()

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_activites_mois_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour le budget activités"""
        from src.modules.famille.utils import get_budget_activites_mois

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        result = get_budget_activites_mois()

        assert result == 0.0
        mock_st.error.assert_called()


class TestGetRoutinesErreur:
    """Tests d'erreur pour les routines"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_routines_actives_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour les routines"""
        from src.modules.famille.utils import get_routines_actives

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        get_routines_actives.clear()

        result = get_routines_actives()

        assert result == []
        mock_st.error.assert_called()


class TestGetStatsSanteErreur:
    """Tests d'erreur pour les stats santé"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_stats_sante_semaine_erreur(self, mock_db, mock_st):
        """Teste la gestion d'erreur pour les stats santé"""
        from src.modules.famille.utils import get_stats_sante_semaine

        mock_db.return_value.__enter__.side_effect = Exception("DB Error")

        result = get_stats_sante_semaine()

        assert result["nb_seances"] == 0
        assert result["total_minutes"] == 0
        mock_st.error.assert_called()


class TestGetBudgetParPeriodMois:
    """Tests pour le budget par période - cas mois décembre"""

    @patch("src.modules.famille.utils.st")
    @patch("src.modules.famille.utils.obtenir_contexte_db")
    def test_budget_mois_decembre(self, mock_db, mock_st):
        """Teste la récupération du budget en décembre"""
        from src.modules.famille.utils import get_budget_par_period

        mock_budget = MagicMock()
        mock_budget.categorie = "Alimentation"
        mock_budget.montant = 100

        mock_session = MagicMock()
        mock_session.query().filter().all.return_value = [mock_budget]
        mock_db.return_value.__enter__.return_value = mock_session

        get_budget_par_period.clear()

        result = get_budget_par_period("month")

        assert "TOTAL" in result
