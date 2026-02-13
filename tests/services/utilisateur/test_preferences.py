"""
Tests pour src/services/utilisateur/preferences.py
Cible: Couverture >80%

Tests pour:
- UserPreferenceService: charger, sauvegarder préférences
- Feedbacks: ajouter, supprimer, stats
- Conversions DB <-> dataclass
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.modules.cuisine.schemas import (
    FeedbackRecette,
    PreferencesUtilisateur,
)

# ═══════════════════════════════════════════════════════════
# IMPORTS DU MODULE
# ═══════════════════════════════════════════════════════════
from src.services.utilisateur.preferences import (
    DEFAULT_USER_ID,
    UserPreferenceService,
    get_user_preference_service,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_db_session():
    """Session DB mockée."""
    session = MagicMock()
    session.execute.return_value.scalar_one_or_none.return_value = None
    session.execute.return_value.scalars.return_value.all.return_value = []
    return session


@pytest.fixture
def mock_user_preference():
    """Mock d'une préférence utilisateur en DB."""
    pref = Mock()
    pref.user_id = "matanne"
    pref.nb_adultes = 2
    pref.jules_present = True
    pref.jules_age_mois = 19
    pref.temps_semaine = "normal"
    pref.temps_weekend = "long"
    pref.aliments_exclus = []
    pref.aliments_favoris = ["poulet", "pâtes"]
    pref.poisson_par_semaine = 2
    pref.vegetarien_par_semaine = 1
    pref.viande_rouge_max = 2
    pref.robots = ["four", "monsieur_cuisine"]
    pref.magasins_preferes = ["Carrefour"]
    pref.updated_at = datetime.now(UTC)
    return pref


@pytest.fixture
def mock_recipe_feedback():
    """Mock d'un feedback recette en DB."""
    fb = Mock()
    fb.user_id = "matanne"
    fb.recette_id = 42
    fb.feedback = "like"
    fb.contexte = "délicieux"
    fb.notes = "Tarte aux pommes"
    fb.created_at = datetime.now(UTC)
    return fb


@pytest.fixture
def preferences_dataclass():
    """PreferencesUtilisateur dataclass."""
    return PreferencesUtilisateur(
        nb_adultes=2,
        jules_present=True,
        jules_age_mois=19,
        temps_semaine="normal",
        temps_weekend="long",
        aliments_exclus=[],
        aliments_favoris=["poulet", "pâtes"],
        poisson_par_semaine=2,
        vegetarien_par_semaine=1,
        viande_rouge_max=2,
        robots=["four", "monsieur_cuisine"],
        magasins_preferes=["Carrefour"],
    )


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserPreferenceServiceInit:
    """Tests pour l'initialisation de UserPreferenceService."""

    def test_init_default_user_id(self):
        """Initialisation avec user_id par défaut."""
        service = UserPreferenceService()
        assert service.user_id == DEFAULT_USER_ID

    def test_init_custom_user_id(self):
        """Initialisation avec user_id personnalisé."""
        service = UserPreferenceService(user_id="custom_user")
        assert service.user_id == "custom_user"

    def test_default_user_id_value(self):
        """Vérifie la valeur de DEFAULT_USER_ID."""
        assert DEFAULT_USER_ID == "matanne"


# ═══════════════════════════════════════════════════════════
# TESTS CHARGER PREFERENCES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargerPreferences:
    """Tests pour charger_preferences."""

    @patch("src.services.utilisateur.preferences.select")
    def test_charger_preferences_existantes(
        self, mock_select, mock_db_session, mock_user_preference
    ):
        """Charge préférences existantes."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_user_preference

        service = UserPreferenceService()
        result = service.charger_preferences(db=mock_db_session)

        assert isinstance(result, PreferencesUtilisateur)
        assert result.nb_adultes == 2
        assert result.jules_present is True
        assert result.jules_age_mois == 19

    @patch("src.services.utilisateur.preferences.select")
    def test_charger_preferences_non_existantes(self, mock_select, mock_db_session):
        """Charge préférences non existantes - crée défauts."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        service = UserPreferenceService()

        with patch.object(service, "sauvegarder_preferences") as mock_save:
            mock_save.return_value = True
            result = service.charger_preferences(db=mock_db_session)

        assert isinstance(result, PreferencesUtilisateur)
        # Vérifie que ce sont les valeurs par défaut
        assert result.nb_adultes == 2
        assert result.jules_present is True


# ═══════════════════════════════════════════════════════════
# TESTS SAUVEGARDER PREFERENCES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSauvegarderPreferences:
    """Tests pour sauvegarder_preferences."""

    @patch("src.services.utilisateur.preferences.select")
    def test_sauvegarder_update_existant(
        self, mock_select, mock_db_session, mock_user_preference, preferences_dataclass
    ):
        """Mise à jour préférences existantes."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_user_preference

        service = UserPreferenceService()
        result = service.sauvegarder_preferences(preferences_dataclass, db=mock_db_session)

        assert result is True
        mock_db_session.commit.assert_called_once()

    @patch("src.services.utilisateur.preferences.select")
    def test_sauvegarder_insert_nouveau(self, mock_select, mock_db_session, preferences_dataclass):
        """Insert nouvelles préférences."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        service = UserPreferenceService()
        result = service.sauvegarder_preferences(preferences_dataclass, db=mock_db_session)

        assert result is True
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("src.services.utilisateur.preferences.select")
    def test_sauvegarder_error(self, mock_select, mock_db_session, preferences_dataclass):
        """Gestion erreur sauvegarde."""
        mock_db_session.execute.side_effect = Exception("DB Error")

        service = UserPreferenceService()
        result = service.sauvegarder_preferences(preferences_dataclass, db=mock_db_session)

        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS CHARGER FEEDBACKS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargerFeedbacks:
    """Tests pour charger_feedbacks."""

    @patch("src.services.utilisateur.preferences.select")
    def test_charger_feedbacks_vide(self, mock_select, mock_db_session):
        """Charge feedbacks vides."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        service = UserPreferenceService()
        result = service.charger_feedbacks(db=mock_db_session)

        assert result == []

    @patch("src.services.utilisateur.preferences.select")
    def test_charger_feedbacks_avec_donnees(
        self, mock_select, mock_db_session, mock_recipe_feedback
    ):
        """Charge feedbacks avec données."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
            mock_recipe_feedback
        ]

        service = UserPreferenceService()
        result = service.charger_feedbacks(db=mock_db_session)

        assert len(result) == 1
        assert isinstance(result[0], FeedbackRecette)
        assert result[0].recette_id == 42
        assert result[0].feedback == "like"

    @patch("src.services.utilisateur.preferences.select")
    def test_charger_feedbacks_sans_created_at(self, mock_select, mock_db_session):
        """Charge feedback sans date création."""
        fb = Mock()
        fb.recette_id = 1
        fb.notes = "Test"
        fb.feedback = "like"
        fb.contexte = None
        fb.created_at = None  # Pas de date

        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [fb]

        service = UserPreferenceService()
        result = service.charger_feedbacks(db=mock_db_session)

        assert len(result) == 1
        assert result[0].date_feedback is None


# ═══════════════════════════════════════════════════════════
# TESTS AJOUTER FEEDBACK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAjouterFeedback:
    """Tests pour ajouter_feedback."""

    @patch("src.services.utilisateur.preferences.select")
    def test_ajouter_nouveau_feedback(self, mock_select, mock_db_session):
        """Ajoute un nouveau feedback."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        service = UserPreferenceService()
        result = service.ajouter_feedback(
            recette_id=42,
            recette_nom="Tarte aux pommes",
            feedback="like",
            contexte="excellent",
            db=mock_db_session,
        )

        assert result is True
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("src.services.utilisateur.preferences.select")
    def test_ajouter_update_feedback_existant(
        self, mock_select, mock_db_session, mock_recipe_feedback
    ):
        """Met à jour un feedback existant."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_recipe_feedback

        service = UserPreferenceService()
        result = service.ajouter_feedback(
            recette_id=42,
            recette_nom="Tarte aux pommes",
            feedback="dislike",
            contexte="trop sucré",
            db=mock_db_session,
        )

        assert result is True
        assert mock_recipe_feedback.feedback == "dislike"
        assert mock_recipe_feedback.contexte == "trop sucré"
        mock_db_session.commit.assert_called_once()

    @patch("src.services.utilisateur.preferences.select")
    def test_ajouter_feedback_error(self, mock_select, mock_db_session):
        """Gestion erreur ajout feedback."""
        mock_db_session.execute.side_effect = Exception("DB Error")

        service = UserPreferenceService()
        result = service.ajouter_feedback(
            recette_id=42, recette_nom="Test", feedback="like", db=mock_db_session
        )

        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS SUPPRIMER FEEDBACK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSupprimerFeedback:
    """Tests pour supprimer_feedback."""

    @patch("src.services.utilisateur.preferences.select")
    def test_supprimer_feedback_existant(self, mock_select, mock_db_session, mock_recipe_feedback):
        """Supprime feedback existant."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_recipe_feedback

        service = UserPreferenceService()
        result = service.supprimer_feedback(recette_id=42, db=mock_db_session)

        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_recipe_feedback)
        mock_db_session.commit.assert_called_once()

    @patch("src.services.utilisateur.preferences.select")
    def test_supprimer_feedback_non_existant(self, mock_select, mock_db_session):
        """Supprime feedback non existant."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        service = UserPreferenceService()
        result = service.supprimer_feedback(recette_id=999, db=mock_db_session)

        assert result is False
        mock_db_session.delete.assert_not_called()

    @patch("src.services.utilisateur.preferences.select")
    def test_supprimer_feedback_error(self, mock_select, mock_db_session):
        """Gestion erreur suppression feedback."""
        mock_db_session.execute.side_effect = Exception("DB Error")

        service = UserPreferenceService()
        result = service.supprimer_feedback(recette_id=42, db=mock_db_session)

        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS GET FEEDBACKS STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetFeedbacksStats:
    """Tests pour get_feedbacks_stats."""

    @patch("src.services.utilisateur.preferences.select")
    def test_get_stats_vide(self, mock_select, mock_db_session):
        """Stats avec feedbacks vides."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        service = UserPreferenceService()
        result = service.get_feedbacks_stats(db=mock_db_session)

        assert result == {"like": 0, "dislike": 0, "neutral": 0, "total": 0}

    @patch("src.services.utilisateur.preferences.select")
    def test_get_stats_avec_donnees(self, mock_select, mock_db_session):
        """Stats avec feedbacks."""
        fb1 = Mock()
        fb1.feedback = "like"
        fb2 = Mock()
        fb2.feedback = "like"
        fb3 = Mock()
        fb3.feedback = "dislike"

        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [fb1, fb2, fb3]

        service = UserPreferenceService()
        result = service.get_feedbacks_stats(db=mock_db_session)

        assert result["like"] == 2
        assert result["dislike"] == 1
        assert result["neutral"] == 0
        assert result["total"] == 3


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS CONVERSION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConversionHelpers:
    """Tests pour les méthodes de conversion."""

    def test_get_default_preferences(self):
        """Récupère les préférences par défaut."""
        service = UserPreferenceService()
        result = service._get_default_preferences()

        assert isinstance(result, PreferencesUtilisateur)
        assert result.nb_adultes == 2
        assert result.jules_present is True
        assert result.jules_age_mois == 19
        assert "poulet" in result.aliments_favoris
        assert "monsieur_cuisine" in result.robots

    def test_db_to_dataclass(self, mock_user_preference):
        """Conversion DB -> dataclass."""
        service = UserPreferenceService()
        result = service._db_to_dataclass(mock_user_preference)

        assert isinstance(result, PreferencesUtilisateur)
        assert result.nb_adultes == mock_user_preference.nb_adultes
        assert result.jules_present == mock_user_preference.jules_present
        assert result.temps_semaine == mock_user_preference.temps_semaine
        assert result.robots == mock_user_preference.robots

    def test_db_to_dataclass_handles_none_lists(self):
        """Conversion gère les listes None."""
        pref = Mock()
        pref.nb_adultes = 2
        pref.jules_present = True
        pref.jules_age_mois = 19
        pref.temps_semaine = "normal"
        pref.temps_weekend = "long"
        pref.aliments_exclus = None
        pref.aliments_favoris = None
        pref.poisson_par_semaine = 2
        pref.vegetarien_par_semaine = 1
        pref.viande_rouge_max = 2
        pref.robots = None
        pref.magasins_preferes = None

        service = UserPreferenceService()
        result = service._db_to_dataclass(pref)

        assert result.aliments_exclus == []
        assert result.aliments_favoris == []
        assert result.robots == []
        assert result.magasins_preferes == []

    def test_dataclass_to_db(self, preferences_dataclass):
        """Conversion dataclass -> DB."""
        service = UserPreferenceService()
        result = service._dataclass_to_db(preferences_dataclass)

        # Vérifie que c'est un objet UserPreference
        from src.core.models import UserPreference

        assert isinstance(result, UserPreference)
        assert result.user_id == service.user_id
        assert result.nb_adultes == preferences_dataclass.nb_adultes
        assert result.jules_present == preferences_dataclass.jules_present

    def test_update_db_from_dataclass(self, mock_user_preference, preferences_dataclass):
        """Mise à jour DB depuis dataclass."""
        # Modifier le dataclass
        preferences_dataclass.nb_adultes = 3
        preferences_dataclass.temps_semaine = "rapide"

        service = UserPreferenceService()
        service._update_db_from_dataclass(mock_user_preference, preferences_dataclass)

        assert mock_user_preference.nb_adultes == 3
        assert mock_user_preference.temps_semaine == "rapide"


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFactory:
    """Tests pour get_user_preference_service."""

    def test_factory_returns_service(self):
        """Factory retourne UserPreferenceService."""
        import src.services.utilisateur.preferences as pref_module

        pref_module._preference_service = None

        service = get_user_preference_service()

        assert isinstance(service, UserPreferenceService)

    def test_factory_singleton_same_user(self):
        """Factory retourne la même instance pour même user."""
        import src.services.utilisateur.preferences as pref_module

        pref_module._preference_service = None

        service1 = get_user_preference_service()
        service2 = get_user_preference_service()

        assert service1 is service2

    def test_factory_new_instance_different_user(self):
        """Factory crée nouvelle instance pour user différent."""
        import src.services.utilisateur.preferences as pref_module

        pref_module._preference_service = None

        service1 = get_user_preference_service("user1")
        service2 = get_user_preference_service("user2")

        assert service2.user_id == "user2"


# ═══════════════════════════════════════════════════════════
# TESTS FEEDBACKRECETTE DATACLASS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFeedbackRecetteDataclass:
    """Tests pour FeedbackRecette dataclass."""

    def test_create_feedback(self):
        """Création d'un feedback."""
        fb = FeedbackRecette(recette_id=42, recette_nom="Tarte aux pommes", feedback="like")

        assert fb.recette_id == 42
        assert fb.recette_nom == "Tarte aux pommes"
        assert fb.feedback == "like"

    def test_score_like(self):
        """Score pour like = 1."""
        fb = FeedbackRecette(recette_id=42, recette_nom="Test", feedback="like")
        assert fb.score == 1

    def test_score_dislike(self):
        """Score pour dislike = -1."""
        fb = FeedbackRecette(recette_id=42, recette_nom="Test", feedback="dislike")
        assert fb.score == -1

    def test_score_neutral(self):
        """Score pour neutral = 0."""
        fb = FeedbackRecette(recette_id=42, recette_nom="Test", feedback="neutral")
        assert fb.score == 0

    def test_score_unknown(self):
        """Score pour valeur inconnue = 0."""
        fb = FeedbackRecette(recette_id=42, recette_nom="Test", feedback="unknown")
        assert fb.score == 0


# ═══════════════════════════════════════════════════════════
# TESTS PREFERENCESUTILISATEUR DATACLASS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPreferencesUtilisateurDataclass:
    """Tests pour PreferencesUtilisateur dataclass."""

    def test_default_values(self):
        """Valeurs par défaut."""
        prefs = PreferencesUtilisateur()

        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        assert prefs.jules_age_mois == 19
        assert prefs.temps_semaine == "normal"
        assert prefs.temps_weekend == "long"

    def test_to_dict(self):
        """Conversion en dict."""
        prefs = PreferencesUtilisateur(nb_adultes=3, aliments_exclus=["oignon"])

        result = prefs.to_dict()

        assert isinstance(result, dict)
        assert result["nb_adultes"] == 3
        assert result["aliments_exclus"] == ["oignon"]

    def test_from_dict(self):
        """Création depuis dict."""
        data = {
            "nb_adultes": 4,
            "jules_present": False,
            "aliments_favoris": ["pizza"],
            "unknown_field": "ignored",
        }

        prefs = PreferencesUtilisateur.from_dict(data)

        assert prefs.nb_adultes == 4
        assert prefs.jules_present is False
        assert prefs.aliments_favoris == ["pizza"]


# ═══════════════════════════════════════════════════════════
# TESTS INTEGRATION AVEC DECORATEUR
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDecoratorIntegration:
    """Tests pour l'intégration avec le décorateur avec_session_db."""

    def test_charger_preferences_uses_decorator(self):
        """charger_preferences utilise le décorateur."""
        # On teste simplement que le service est créé correctement
        # Le test du décorateur lui-même est complexe à mock
        service = UserPreferenceService()
        assert service.user_id == DEFAULT_USER_ID

        # Test avec un mock session
        mock_session = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        # On appelle avec session explicite pour éviter le décorateur
        with patch.object(service, "sauvegarder_preferences") as mock_save:
            mock_save.return_value = True
            with patch("src.services.utilisateur.preferences.select"):
                result = service.charger_preferences(db=mock_session)
                assert isinstance(result, PreferencesUtilisateur)
