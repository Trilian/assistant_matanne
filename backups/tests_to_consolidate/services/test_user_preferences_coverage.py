"""
Tests complets pour src/services/user_preferences.py
Objectif: Atteindre 80%+ de couverture

Tests couvrant:
- UserPreferenceService init
- charger_preferences (existant, crÃ©ation dÃ©faut)
- sauvegarder_preferences (update, insert, erreur)
- charger_feedbacks
- ajouter_feedback (nouveau, update, erreur)
- supprimer_feedback (succÃ¨s, non trouvÃ©, erreur)
- get_feedbacks_stats
- _get_default_preferences
- _db_to_dataclass, _dataclass_to_db, _update_db_from_dataclass
- get_user_preference_service factory
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone, date


class TestUserPreferenceServiceInit:
    """Tests d'initialisation du service."""

    def test_service_init_default_user(self):
        """Initialisation avec user_id par dÃ©faut."""
        from src.services.user_preferences import UserPreferenceService, DEFAULT_USER_ID
        
        service = UserPreferenceService()
        assert service.user_id == DEFAULT_USER_ID

    def test_service_init_custom_user(self):
        """Initialisation avec user_id personnalisÃ©."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService(user_id="custom_user")
        assert service.user_id == "custom_user"


class TestGetDefaultPreferences:
    """Tests _get_default_preferences."""

    def test_default_preferences_values(self):
        """VÃ©rifie les valeurs par dÃ©faut."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        prefs = service._get_default_preferences()
        
        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        assert prefs.jules_age_mois == 19
        assert prefs.temps_semaine == "normal"
        assert prefs.temps_weekend == "long"
        assert "poulet" in prefs.aliments_favoris
        assert prefs.poisson_par_semaine == 2
        assert "monsieur_cuisine" in prefs.robots
        assert "Carrefour Drive" in prefs.magasins_preferes


class TestDbToDataclass:
    """Tests _db_to_dataclass."""

    def test_conversion_complete(self):
        """Conversion DB â†’ dataclass complÃ¨te."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        # Mock UserPreference DB object
        db_pref = Mock()
        db_pref.nb_adultes = 3
        db_pref.jules_present = False
        db_pref.jules_age_mois = 24
        db_pref.temps_semaine = "express"
        db_pref.temps_weekend = "normal"
        db_pref.aliments_exclus = ["fruits de mer"]
        db_pref.aliments_favoris = ["pizza"]
        db_pref.poisson_par_semaine = 1
        db_pref.vegetarien_par_semaine = 2
        db_pref.viande_rouge_max = 1
        db_pref.robots = ["four"]
        db_pref.magasins_preferes = ["Lidl"]
        
        result = service._db_to_dataclass(db_pref)
        
        assert result.nb_adultes == 3
        assert result.jules_present is False
        assert result.aliments_exclus == ["fruits de mer"]
        assert result.robots == ["four"]

    def test_conversion_with_none_lists(self):
        """Conversion avec listes None â†’ listes vides."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        db_pref = Mock()
        db_pref.nb_adultes = 2
        db_pref.jules_present = True
        db_pref.jules_age_mois = 19
        db_pref.temps_semaine = "normal"
        db_pref.temps_weekend = "long"
        db_pref.aliments_exclus = None
        db_pref.aliments_favoris = None
        db_pref.poisson_par_semaine = 2
        db_pref.vegetarien_par_semaine = 1
        db_pref.viande_rouge_max = 2
        db_pref.robots = None
        db_pref.magasins_preferes = None
        
        result = service._db_to_dataclass(db_pref)
        
        assert result.aliments_exclus == []
        assert result.aliments_favoris == []
        assert result.robots == []
        assert result.magasins_preferes == []


class TestDataclassToDb:
    """Tests _dataclass_to_db."""

    def test_conversion_to_db(self):
        """Conversion dataclass â†’ DB object."""
        from src.services.user_preferences import UserPreferenceService
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        service = UserPreferenceService(user_id="test_user")
        
        prefs = PreferencesUtilisateur(
            nb_adultes=4,
            jules_present=False,
            jules_age_mois=30,
            temps_semaine="long",
            temps_weekend="express",
            aliments_exclus=["gluten"],
            aliments_favoris=["sushi"],
            poisson_par_semaine=3,
            vegetarien_par_semaine=2,
            viande_rouge_max=0,
            robots=["thermomix"],
            magasins_preferes=["Auchan"],
        )
        
        result = service._dataclass_to_db(prefs)
        
        assert result.user_id == "test_user"
        assert result.nb_adultes == 4
        assert result.jules_present is False
        assert result.aliments_exclus == ["gluten"]


class TestUpdateDbFromDataclass:
    """Tests _update_db_from_dataclass."""

    def test_update_all_fields(self):
        """Mise Ã  jour de tous les champs."""
        from src.services.user_preferences import UserPreferenceService
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        service = UserPreferenceService()
        
        db_pref = Mock()
        prefs = PreferencesUtilisateur(
            nb_adultes=5,
            jules_present=True,
            jules_age_mois=25,
            temps_semaine="express",
            temps_weekend="long",
            aliments_exclus=["lactose"],
            aliments_favoris=["curry"],
            poisson_par_semaine=4,
            vegetarien_par_semaine=3,
            viande_rouge_max=1,
            robots=["cookeo"],
            magasins_preferes=["IntermarchÃ©"],
        )
        
        service._update_db_from_dataclass(db_pref, prefs)
        
        assert db_pref.nb_adultes == 5
        assert db_pref.jules_age_mois == 25
        assert db_pref.aliments_exclus == ["lactose"]
        assert db_pref.robots == ["cookeo"]


class TestChargerPreferences:
    """Tests charger_preferences."""

    @patch('src.services.user_preferences.select')
    def test_charger_preferences_existantes(self, mock_select):
        """Charge des prÃ©fÃ©rences existantes depuis la DB."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService(user_id="test")
        
        # Mock DB preference
        mock_db_pref = Mock()
        mock_db_pref.nb_adultes = 3
        mock_db_pref.jules_present = True
        mock_db_pref.jules_age_mois = 20
        mock_db_pref.temps_semaine = "normal"
        mock_db_pref.temps_weekend = "long"
        mock_db_pref.aliments_exclus = []
        mock_db_pref.aliments_favoris = ["pizza"]
        mock_db_pref.poisson_par_semaine = 2
        mock_db_pref.vegetarien_par_semaine = 1
        mock_db_pref.viande_rouge_max = 2
        mock_db_pref.robots = ["four"]
        mock_db_pref.magasins_preferes = ["Carrefour"]
        
        # Mock session
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_db_pref
        
        result = service.charger_preferences(db=mock_session)
        
        assert result.nb_adultes == 3
        assert result.aliments_favoris == ["pizza"]

    @patch('src.services.user_preferences.select')
    def test_charger_preferences_creation_defaut(self, mock_select):
        """CrÃ©e les prÃ©fÃ©rences par dÃ©faut si inexistantes."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService(user_id="new_user")
        
        # Mock session - premiÃ¨re requÃªte retourne None
        mock_session = Mock()
        # Premier appel: charger_preferences ne trouve rien
        # DeuxiÃ¨me appel: dans sauvegarder_preferences
        mock_session.execute.return_value.scalar_one_or_none.side_effect = [None, None]
        
        result = service.charger_preferences(db=mock_session)
        
        # VÃ©rifie que ce sont les valeurs par dÃ©faut
        assert result.nb_adultes == 2
        assert result.jules_present is True
        assert "poulet" in result.aliments_favoris


class TestSauvegarderPreferences:
    """Tests sauvegarder_preferences."""

    @patch('src.services.user_preferences.select')
    def test_sauvegarder_update_existant(self, mock_select):
        """Met Ã  jour des prÃ©fÃ©rences existantes."""
        from src.services.user_preferences import UserPreferenceService
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        service = UserPreferenceService()
        
        # Mock existing preference
        mock_db_pref = Mock()
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_db_pref
        
        prefs = PreferencesUtilisateur(nb_adultes=4)
        
        result = service.sauvegarder_preferences(prefs, db=mock_session)
        
        assert result is True
        mock_session.commit.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_sauvegarder_insert_nouveau(self, mock_select):
        """InsÃ¨re de nouvelles prÃ©fÃ©rences."""
        from src.services.user_preferences import UserPreferenceService
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        service = UserPreferenceService()
        
        # Mock: aucune prÃ©fÃ©rence existante
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        prefs = PreferencesUtilisateur(nb_adultes=3)
        
        result = service.sauvegarder_preferences(prefs, db=mock_session)
        
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_sauvegarder_erreur(self, mock_select):
        """Gestion d'erreur lors de la sauvegarde."""
        from src.services.user_preferences import UserPreferenceService
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.side_effect = Exception("DB error")
        
        prefs = PreferencesUtilisateur()
        
        result = service.sauvegarder_preferences(prefs, db=mock_session)
        
        assert result is False
        mock_session.rollback.assert_called_once()


class TestChargerFeedbacks:
    """Tests charger_feedbacks."""

    @patch('src.services.user_preferences.select')
    def test_charger_feedbacks_avec_donnees(self, mock_select):
        """Charge les feedbacks existants."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        # Mock feedbacks
        mock_fb1 = Mock()
        mock_fb1.recette_id = 1
        mock_fb1.notes = "Poulet rÃ´ti"
        mock_fb1.feedback = "like"
        mock_fb1.created_at = datetime(2026, 1, 15, 12, 0, 0)
        mock_fb1.contexte = "DÃ©licieux"
        
        mock_fb2 = Mock()
        mock_fb2.recette_id = 2
        mock_fb2.notes = "Soupe de lÃ©gumes"
        mock_fb2.feedback = "dislike"
        mock_fb2.created_at = datetime(2026, 1, 16, 12, 0, 0)
        mock_fb2.contexte = "Trop fade"
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_fb1, mock_fb2]
        
        result = service.charger_feedbacks(db=mock_session)
        
        assert len(result) == 2
        assert result[0].recette_nom == "Poulet rÃ´ti"
        assert result[0].feedback == "like"
        assert result[1].feedback == "dislike"

    @patch('src.services.user_preferences.select')
    def test_charger_feedbacks_sans_notes(self, mock_select):
        """Feedback sans notes utilise nom par dÃ©faut."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_fb = Mock()
        mock_fb.recette_id = 5
        mock_fb.notes = None  # Pas de notes
        mock_fb.feedback = "neutral"
        mock_fb.created_at = datetime(2026, 1, 20, 12, 0, 0)
        mock_fb.contexte = None
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_fb]
        
        result = service.charger_feedbacks(db=mock_session)
        
        assert result[0].recette_nom == "Recette #5"

    @patch('src.services.user_preferences.select')
    def test_charger_feedbacks_sans_date(self, mock_select):
        """Feedback sans date de crÃ©ation."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_fb = Mock()
        mock_fb.recette_id = 3
        mock_fb.notes = "Test"
        mock_fb.feedback = "like"
        mock_fb.created_at = None  # Pas de date
        mock_fb.contexte = None
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_fb]
        
        result = service.charger_feedbacks(db=mock_session)
        
        assert result[0].date_feedback is None

    @patch('src.services.user_preferences.select')
    def test_charger_feedbacks_vide(self, mock_select):
        """Aucun feedback retourne liste vide."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        result = service.charger_feedbacks(db=mock_session)
        
        assert result == []


class TestAjouterFeedback:
    """Tests ajouter_feedback."""

    @patch('src.services.user_preferences.select')
    def test_ajouter_nouveau_feedback(self, mock_select):
        """Ajoute un nouveau feedback."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = service.ajouter_feedback(
            recette_id=1,
            recette_nom="Tarte aux pommes",
            feedback="like",
            contexte="Excellent dessert",
            db=mock_session
        )
        
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_ajouter_feedback_update_existant(self, mock_select):
        """Met Ã  jour un feedback existant."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_existing = Mock()
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_existing
        
        result = service.ajouter_feedback(
            recette_id=1,
            recette_nom="Tarte aux pommes",
            feedback="dislike",
            contexte="Finalement pas terrible",
            db=mock_session
        )
        
        assert result is True
        assert mock_existing.feedback == "dislike"
        assert mock_existing.contexte == "Finalement pas terrible"
        assert mock_existing.notes == "Tarte aux pommes"
        mock_session.commit.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_ajouter_feedback_erreur(self, mock_select):
        """Gestion d'erreur lors de l'ajout."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.side_effect = Exception("DB error")
        
        result = service.ajouter_feedback(
            recette_id=1,
            recette_nom="Test",
            feedback="like",
            db=mock_session
        )
        
        assert result is False
        mock_session.rollback.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_ajouter_feedback_sans_contexte(self, mock_select):
        """Ajoute un feedback sans contexte."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = service.ajouter_feedback(
            recette_id=2,
            recette_nom="Pizza",
            feedback="neutral",
            db=mock_session
        )
        
        assert result is True


class TestSupprimerFeedback:
    """Tests supprimer_feedback."""

    @patch('src.services.user_preferences.select')
    def test_supprimer_feedback_succes(self, mock_select):
        """Supprime un feedback avec succÃ¨s."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_fb = Mock()
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_fb
        
        result = service.supprimer_feedback(recette_id=1, db=mock_session)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_fb)
        mock_session.commit.assert_called_once()

    @patch('src.services.user_preferences.select')
    def test_supprimer_feedback_non_trouve(self, mock_select):
        """Feedback non trouvÃ© retourne False."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = service.supprimer_feedback(recette_id=999, db=mock_session)
        
        assert result is False
        mock_session.delete.assert_not_called()

    @patch('src.services.user_preferences.select')
    def test_supprimer_feedback_erreur(self, mock_select):
        """Gestion d'erreur lors de la suppression."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.side_effect = Exception("DB error")
        
        result = service.supprimer_feedback(recette_id=1, db=mock_session)
        
        assert result is False
        mock_session.rollback.assert_called_once()


class TestGetFeedbacksStats:
    """Tests get_feedbacks_stats."""

    @patch('src.services.user_preferences.select')
    def test_get_stats_avec_feedbacks(self, mock_select):
        """Statistiques avec feedbacks mixtes."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        # 3 likes, 2 dislikes, 1 neutral
        mock_feedbacks = [
            Mock(feedback="like"),
            Mock(feedback="like"),
            Mock(feedback="like"),
            Mock(feedback="dislike"),
            Mock(feedback="dislike"),
            Mock(feedback="neutral"),
        ]
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = mock_feedbacks
        
        result = service.get_feedbacks_stats(db=mock_session)
        
        assert result["like"] == 3
        assert result["dislike"] == 2
        assert result["neutral"] == 1
        assert result["total"] == 6

    @patch('src.services.user_preferences.select')
    def test_get_stats_vide(self, mock_select):
        """Statistiques sans feedbacks."""
        from src.services.user_preferences import UserPreferenceService
        
        service = UserPreferenceService()
        
        mock_session = Mock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        result = service.get_feedbacks_stats(db=mock_session)
        
        assert result["like"] == 0
        assert result["dislike"] == 0
        assert result["neutral"] == 0
        assert result["total"] == 0


class TestGetUserPreferenceServiceFactory:
    """Tests factory get_user_preference_service."""

    def test_factory_default_user(self):
        """Factory avec user_id par dÃ©faut."""
        from src.services.user_preferences import get_user_preference_service, DEFAULT_USER_ID
        
        # Reset singleton
        import src.services.user_preferences as module
        module._preference_service = None
        
        service = get_user_preference_service()
        assert service.user_id == DEFAULT_USER_ID

    def test_factory_custom_user(self):
        """Factory avec user_id personnalisÃ©."""
        from src.services.user_preferences import get_user_preference_service
        
        # Reset singleton
        import src.services.user_preferences as module
        module._preference_service = None
        
        service = get_user_preference_service(user_id="custom")
        assert service.user_id == "custom"

    def test_factory_singleton_same_user(self):
        """Factory retourne le mÃªme service pour le mÃªme user."""
        from src.services.user_preferences import get_user_preference_service
        
        # Reset singleton
        import src.services.user_preferences as module
        module._preference_service = None
        
        service1 = get_user_preference_service(user_id="test")
        service2 = get_user_preference_service(user_id="test")
        
        assert service1 is service2

    def test_factory_new_service_different_user(self):
        """Factory crÃ©e un nouveau service pour user diffÃ©rent."""
        from src.services.user_preferences import get_user_preference_service
        
        # Reset singleton
        import src.services.user_preferences as module
        module._preference_service = None
        
        service1 = get_user_preference_service(user_id="user1")
        service2 = get_user_preference_service(user_id="user2")
        
        assert service2.user_id == "user2"


class TestPreferencesUtilisateurDataclass:
    """Tests du dataclass PreferencesUtilisateur (importÃ© dans le service)."""

    def test_preferences_default_values(self):
        """Valeurs par dÃ©faut du dataclass."""
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        prefs = PreferencesUtilisateur()
        
        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        assert prefs.temps_semaine == "normal"

    def test_preferences_to_dict(self):
        """Conversion en dictionnaire."""
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        prefs = PreferencesUtilisateur(nb_adultes=3, jules_present=False)
        
        result = prefs.to_dict()
        
        assert result["nb_adultes"] == 3
        assert result["jules_present"] is False

    def test_preferences_from_dict(self):
        """CrÃ©ation depuis dictionnaire."""
        from src.modules.cuisine.logic.schemas import PreferencesUtilisateur
        
        data = {
            "nb_adultes": 4,
            "jules_present": False,
            "temps_semaine": "express",
        }
        
        prefs = PreferencesUtilisateur.from_dict(data)
        
        assert prefs.nb_adultes == 4
        assert prefs.jules_present is False
        assert prefs.temps_semaine == "express"


class TestFeedbackRecetteDataclass:
    """Tests du dataclass FeedbackRecette."""

    def test_feedback_creation(self):
        """CrÃ©ation d'un feedback."""
        from src.modules.cuisine.logic.schemas import FeedbackRecette
        
        fb = FeedbackRecette(
            recette_id=1,
            recette_nom="Test",
            feedback="like",
        )
        
        assert fb.recette_id == 1
        assert fb.feedback == "like"

    def test_feedback_score_like(self):
        """Score pour like = 1."""
        from src.modules.cuisine.logic.schemas import FeedbackRecette
        
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="like")
        assert fb.score == 1

    def test_feedback_score_dislike(self):
        """Score pour dislike = -1."""
        from src.modules.cuisine.logic.schemas import FeedbackRecette
        
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="dislike")
        assert fb.score == -1

    def test_feedback_score_neutral(self):
        """Score pour neutral = 0."""
        from src.modules.cuisine.logic.schemas import FeedbackRecette
        
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="neutral")
        assert fb.score == 0

    def test_feedback_score_unknown(self):
        """Score pour feedback inconnu = 0."""
        from src.modules.cuisine.logic.schemas import FeedbackRecette
        
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="unknown")
        assert fb.score == 0
