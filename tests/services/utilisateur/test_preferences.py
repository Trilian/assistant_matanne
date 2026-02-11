"""
Tests pour le service de préférences utilisateur.

Couvre:
- UserPreferenceService (charger, sauvegarder préférences)
- Gestion des feedbacks recettes (charger, ajouter, supprimer)
- Statistiques de feedbacks
- Conversion DB <-> Dataclass
- Valeurs par défaut
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timezone, date
from contextlib import contextmanager

from sqlalchemy.orm import Session

from src.services.utilisateur.preferences import (
    UserPreferenceService,
    get_user_preference_service,
    DEFAULT_USER_ID,
)
from src.domains.cuisine.logic.schemas import PreferencesUtilisateur, FeedbackRecette
from src.core.models import UserPreference, RecipeFeedback


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_db_session():
    """Mock de session SQLAlchemy."""
    session = MagicMock(spec=Session)
    
    # Mock execute().scalar_one_or_none() et scalars().all()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_result.scalars.return_value.all.return_value = []
    session.execute.return_value = mock_result
    
    return session


@pytest.fixture
def mock_db_context(mock_db_session):
    """Mock du décorateur avec_session_db."""
    @contextmanager
    def mock_context():
        yield mock_db_session
    
    with patch(
        "src.core.database.obtenir_contexte_db",
        mock_context
    ):
        yield mock_db_session


@pytest.fixture
def service():
    """Instance du service avec l'utilisateur par défaut."""
    return UserPreferenceService()


@pytest.fixture
def service_custom_user():
    """Instance du service avec un utilisateur personnalisé."""
    return UserPreferenceService(user_id="custom_user")


# ═══════════════════════════════════════════════════════════
# TESTS: Initialisation
# ═══════════════════════════════════════════════════════════


class TestUserPreferenceServiceInit:
    """Tests pour l'initialisation du service."""

    def test_init_default_user(self):
        """Initialisation avec utilisateur par défaut."""
        service = UserPreferenceService()
        assert service.user_id == DEFAULT_USER_ID

    def test_init_custom_user(self):
        """Initialisation avec utilisateur personnalisé."""
        service = UserPreferenceService(user_id="test_user")
        assert service.user_id == "test_user"

    def test_default_user_id_value(self):
        """Vérifie la valeur par défaut de DEFAULT_USER_ID."""
        assert DEFAULT_USER_ID == "matanne"


# ═══════════════════════════════════════════════════════════
# TESTS: _get_default_preferences
# ═══════════════════════════════════════════════════════════


class TestDefaultPreferences:
    """Tests pour les préférences par défaut."""

    def test_default_preferences_structure(self, service):
        """Vérifie la structure des préférences par défaut."""
        prefs = service._get_default_preferences()
        
        assert isinstance(prefs, PreferencesUtilisateur)
        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        assert prefs.jules_age_mois == 19

    def test_default_preferences_temps_cuisine(self, service):
        """Vérifie les temps de cuisine par défaut."""
        prefs = service._get_default_preferences()
        
        assert prefs.temps_semaine == "normal"
        assert prefs.temps_weekend == "long"

    def test_default_preferences_equilibre(self, service):
        """Vérifie l'équilibre alimentaire par défaut."""
        prefs = service._get_default_preferences()
        
        assert prefs.poisson_par_semaine == 2
        assert prefs.vegetarien_par_semaine == 1
        assert prefs.viande_rouge_max == 2

    def test_default_preferences_listes(self, service):
        """Vérifie les listes par défaut."""
        prefs = service._get_default_preferences()
        
        assert isinstance(prefs.aliments_exclus, list)
        assert isinstance(prefs.aliments_favoris, list)
        assert len(prefs.aliments_favoris) > 0
        assert "poulet" in prefs.aliments_favoris

    def test_default_preferences_robots(self, service):
        """Vérifie les robots par défaut."""
        prefs = service._get_default_preferences()
        
        assert "monsieur_cuisine" in prefs.robots
        assert "cookeo" in prefs.robots
        assert "four" in prefs.robots

    def test_default_preferences_magasins(self, service):
        """Vérifie les magasins préférés par défaut."""
        prefs = service._get_default_preferences()
        
        assert "Carrefour Drive" in prefs.magasins_preferes
        assert len(prefs.magasins_preferes) >= 3


# ═══════════════════════════════════════════════════════════
# TESTS: charger_preferences
# ═══════════════════════════════════════════════════════════


class TestChargerPreferences:
    """Tests pour le chargement des préférences."""

    def test_charger_preferences_existantes(self, service, mock_db_session):
        """Charge les préférences existantes depuis la DB."""
        # Setup mock DB preference
        db_pref = MagicMock(spec=UserPreference)
        db_pref.user_id = "matanne"
        db_pref.nb_adultes = 3
        db_pref.jules_present = True
        db_pref.jules_age_mois = 20
        db_pref.temps_semaine = "express"
        db_pref.temps_weekend = "long"
        db_pref.aliments_exclus = ["arachides"]
        db_pref.aliments_favoris = ["pasta"]
        db_pref.poisson_par_semaine = 3
        db_pref.vegetarien_par_semaine = 2
        db_pref.viande_rouge_max = 1
        db_pref.robots = ["four"]
        db_pref.magasins_preferes = ["Lidl"]
        
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = db_pref
        
        # Call avec session injectée
        prefs = service.charger_preferences(db=mock_db_session)
        
        assert prefs.nb_adultes == 3
        assert prefs.jules_age_mois == 20
        assert prefs.temps_semaine == "express"
        assert "arachides" in prefs.aliments_exclus

    def test_charger_preferences_inexistantes_cree_defaut(self, service, mock_db_session):
        """Crée les préférences par défaut si elles n'existent pas."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        with patch.object(service, "sauvegarder_preferences", return_value=True) as mock_save:
            prefs = service.charger_preferences(db=mock_db_session)
        
        # Vérifie que les préférences par défaut sont retournées
        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        
        # Vérifie que sauvegarder a été appelé
        mock_save.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS: sauvegarder_preferences
# ═══════════════════════════════════════════════════════════


class TestSauvegarderPreferences:
    """Tests pour la sauvegarde des préférences."""

    def test_sauvegarder_update_existant(self, service, mock_db_session):
        """Met à jour les préférences existantes."""
        # Préférences existantes en DB
        db_pref = MagicMock(spec=UserPreference)
        db_pref.user_id = "matanne"
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = db_pref
        
        prefs = PreferencesUtilisateur(nb_adultes=4)
        result = service.sauvegarder_preferences(prefs, db=mock_db_session)
        
        assert result is True
        mock_db_session.commit.assert_called_once()
        assert db_pref.nb_adultes == 4

    def test_sauvegarder_insert_nouveau(self, service, mock_db_session):
        """Crée de nouvelles préférences si inexistantes."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        prefs = PreferencesUtilisateur(nb_adultes=3)
        result = service.sauvegarder_preferences(prefs, db=mock_db_session)
        
        assert result is True
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_sauvegarder_erreur_rollback(self, service, mock_db_session):
        """Rollback en cas d'erreur."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_db_session.commit.side_effect = Exception("DB Error")
        
        prefs = PreferencesUtilisateur()
        result = service.sauvegarder_preferences(prefs, db=mock_db_session)
        
        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS: charger_feedbacks
# ═══════════════════════════════════════════════════════════


class TestChargerFeedbacks:
    """Tests pour le chargement des feedbacks."""

    def test_charger_feedbacks_vide(self, service, mock_db_session):
        """Retourne liste vide si aucun feedback."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        feedbacks = service.charger_feedbacks(db=mock_db_session)
        
        assert feedbacks == []

    def test_charger_feedbacks_avec_donnees(self, service, mock_db_session):
        """Charge et convertit les feedbacks."""
        # Mock feedbacks DB
        fb1 = MagicMock(spec=RecipeFeedback)
        fb1.recette_id = 1
        fb1.feedback = "like"
        fb1.notes = "Poulet rôti"
        fb1.contexte = "Délicieux"
        fb1.created_at = datetime(2026, 2, 10, 12, 0, tzinfo=timezone.utc)
        
        fb2 = MagicMock(spec=RecipeFeedback)
        fb2.recette_id = 2
        fb2.feedback = "dislike"
        fb2.notes = "Épinards"
        fb2.contexte = "Trop amer"
        fb2.created_at = datetime(2026, 2, 9, 18, 0, tzinfo=timezone.utc)
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [fb1, fb2]
        
        feedbacks = service.charger_feedbacks(db=mock_db_session)
        
        assert len(feedbacks) == 2
        assert feedbacks[0].recette_id == 1
        assert feedbacks[0].feedback == "like"
        assert feedbacks[0].recette_nom == "Poulet rôti"
        assert feedbacks[1].feedback == "dislike"

    def test_charger_feedbacks_sans_created_at(self, service, mock_db_session):
        """Gère les feedbacks sans date de création."""
        fb = MagicMock(spec=RecipeFeedback)
        fb.recette_id = 1
        fb.feedback = "neutral"
        fb.notes = "Test"
        fb.contexte = None
        fb.created_at = None
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [fb]
        
        feedbacks = service.charger_feedbacks(db=mock_db_session)
        
        assert len(feedbacks) == 1
        assert feedbacks[0].date_feedback is None


# ═══════════════════════════════════════════════════════════
# TESTS: ajouter_feedback
# ═══════════════════════════════════════════════════════════


class TestAjouterFeedback:
    """Tests pour l'ajout de feedbacks."""

    def test_ajouter_nouveau_feedback(self, service, mock_db_session):
        """Ajoute un nouveau feedback."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = service.ajouter_feedback(
            recette_id=42,
            recette_nom="Tarte aux pommes",
            feedback="like",
            contexte="Excellente",
            db=mock_db_session,
        )
        
        assert result is True
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_ajouter_feedback_update_existant(self, service, mock_db_session):
        """Met à jour un feedback existant."""
        existing_fb = MagicMock(spec=RecipeFeedback)
        existing_fb.recette_id = 42
        existing_fb.feedback = "neutral"
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = existing_fb
        
        result = service.ajouter_feedback(
            recette_id=42,
            recette_nom="Tarte aux pommes",
            feedback="like",
            contexte="Finalement excellente",
            db=mock_db_session,
        )
        
        assert result is True
        assert existing_fb.feedback == "like"
        assert existing_fb.contexte == "Finalement excellente"
        mock_db_session.add.assert_not_called()  # Update, pas add

    def test_ajouter_feedback_erreur(self, service, mock_db_session):
        """Gère les erreurs lors de l'ajout."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        mock_db_session.commit.side_effect = Exception("DB Error")
        
        result = service.ajouter_feedback(
            recette_id=42,
            recette_nom="Test",
            feedback="like",
            db=mock_db_session,
        )
        
        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS: supprimer_feedback
# ═══════════════════════════════════════════════════════════


class TestSupprimerFeedback:
    """Tests pour la suppression de feedbacks."""

    def test_supprimer_feedback_existant(self, service, mock_db_session):
        """Supprime un feedback existant."""
        fb = MagicMock(spec=RecipeFeedback)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = fb
        
        result = service.supprimer_feedback(recette_id=42, db=mock_db_session)
        
        assert result is True
        mock_db_session.delete.assert_called_once_with(fb)
        mock_db_session.commit.assert_called_once()

    def test_supprimer_feedback_inexistant(self, service, mock_db_session):
        """Retourne False si le feedback n'existe pas."""
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = service.supprimer_feedback(recette_id=999, db=mock_db_session)
        
        assert result is False
        mock_db_session.delete.assert_not_called()

    def test_supprimer_feedback_erreur(self, service, mock_db_session):
        """Gère les erreurs lors de la suppression."""
        fb = MagicMock(spec=RecipeFeedback)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = fb
        mock_db_session.commit.side_effect = Exception("DB Error")
        
        result = service.supprimer_feedback(recette_id=42, db=mock_db_session)
        
        assert result is False
        mock_db_session.rollback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS: get_feedbacks_stats
# ═══════════════════════════════════════════════════════════


class TestFeedbacksStats:
    """Tests pour les statistiques de feedbacks."""

    def test_stats_vides(self, service, mock_db_session):
        """Retourne des stats vides sans feedbacks."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        stats = service.get_feedbacks_stats(db=mock_db_session)
        
        assert stats["total"] == 0
        assert stats["like"] == 0
        assert stats["dislike"] == 0
        assert stats["neutral"] == 0

    def test_stats_avec_feedbacks(self, service, mock_db_session):
        """Calcule les stats correctement."""
        fb1 = MagicMock()
        fb1.feedback = "like"
        fb2 = MagicMock()
        fb2.feedback = "like"
        fb3 = MagicMock()
        fb3.feedback = "dislike"
        fb4 = MagicMock()
        fb4.feedback = "neutral"
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
            fb1, fb2, fb3, fb4
        ]
        
        stats = service.get_feedbacks_stats(db=mock_db_session)
        
        assert stats["total"] == 4
        assert stats["like"] == 2
        assert stats["dislike"] == 1
        assert stats["neutral"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS: Conversions DB <-> Dataclass
# ═══════════════════════════════════════════════════════════


class TestConversions:
    """Tests pour les conversions entre modèles."""

    def test_db_to_dataclass(self, service):
        """Convertit UserPreference DB en PreferencesUtilisateur."""
        db_pref = MagicMock(spec=UserPreference)
        db_pref.nb_adultes = 3
        db_pref.jules_present = False
        db_pref.jules_age_mois = 24
        db_pref.temps_semaine = "express"
        db_pref.temps_weekend = "normal"
        db_pref.aliments_exclus = ["gluten"]
        db_pref.aliments_favoris = ["pizza"]
        db_pref.poisson_par_semaine = 1
        db_pref.vegetarien_par_semaine = 3
        db_pref.viande_rouge_max = 0
        db_pref.robots = []
        db_pref.magasins_preferes = ["Bio Coop"]
        
        result = service._db_to_dataclass(db_pref)
        
        assert isinstance(result, PreferencesUtilisateur)
        assert result.nb_adultes == 3
        assert result.jules_present is False
        assert result.temps_semaine == "express"
        assert "gluten" in result.aliments_exclus

    def test_dataclass_to_db(self, service):
        """Convertit PreferencesUtilisateur en UserPreference DB."""
        prefs = PreferencesUtilisateur(
            nb_adultes=4,
            jules_present=True,
            jules_age_mois=18,
            temps_semaine="long",
            aliments_exclus=["soja"],
            robots=["thermomix"],
        )
        
        result = service._dataclass_to_db(prefs)
        
        assert isinstance(result, UserPreference)
        assert result.user_id == service.user_id
        assert result.nb_adultes == 4
        assert result.jules_age_mois == 18
        assert "soja" in result.aliments_exclus

    def test_update_db_from_dataclass(self, service):
        """Met à jour un objet DB depuis un dataclass."""
        db_pref = MagicMock(spec=UserPreference)
        
        prefs = PreferencesUtilisateur(
            nb_adultes=5,
            jules_present=False,
            temps_weekend="express",
        )
        
        service._update_db_from_dataclass(db_pref, prefs)
        
        assert db_pref.nb_adultes == 5
        assert db_pref.jules_present is False
        assert db_pref.temps_weekend == "express"


# ═══════════════════════════════════════════════════════════
# TESTS: Validation des données
# ═══════════════════════════════════════════════════════════


class TestValidation:
    """Tests pour la validation des données de préférences."""

    def test_preferences_valeurs_limites_adultes(self):
        """Test des valeurs limites pour nb_adultes."""
        prefs = PreferencesUtilisateur(nb_adultes=0)
        assert prefs.nb_adultes == 0
        
        prefs = PreferencesUtilisateur(nb_adultes=10)
        assert prefs.nb_adultes == 10

    def test_preferences_listes_vides(self):
        """Test avec listes vides."""
        prefs = PreferencesUtilisateur(
            aliments_exclus=[],
            aliments_favoris=[],
            robots=[],
            magasins_preferes=[],
        )
        assert prefs.aliments_exclus == []
        assert prefs.aliments_favoris == []

    def test_preferences_to_dict(self):
        """Test conversion en dictionnaire."""
        prefs = PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            aliments_favoris=["pasta"],
        )
        
        result = prefs.to_dict()
        
        assert isinstance(result, dict)
        assert result["nb_adultes"] == 2
        assert result["jules_present"] is True
        assert "pasta" in result["aliments_favoris"]

    def test_preferences_from_dict(self):
        """Test création depuis dictionnaire."""
        data = {
            "nb_adultes": 3,
            "jules_present": False,
            "temps_semaine": "express",
            "aliments_favoris": ["poulet", "riz"],
            "champ_inconnu": "ignoré",  # Doit être ignoré
        }
        
        prefs = PreferencesUtilisateur.from_dict(data)
        
        assert prefs.nb_adultes == 3
        assert prefs.jules_present is False


# ═══════════════════════════════════════════════════════════
# TESTS: FeedbackRecette
# ═══════════════════════════════════════════════════════════


class TestFeedbackRecette:
    """Tests pour le dataclass FeedbackRecette."""

    def test_creation_feedback(self):
        """Création d'un feedback basique."""
        fb = FeedbackRecette(
            recette_id=1,
            recette_nom="Test",
            feedback="like",
        )
        assert fb.recette_id == 1
        assert fb.feedback == "like"

    def test_score_like(self):
        """Score pour feedback like."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="like")
        assert fb.score == 1

    def test_score_dislike(self):
        """Score pour feedback dislike."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="dislike")
        assert fb.score == -1

    def test_score_neutral(self):
        """Score pour feedback neutral."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="neutral")
        assert fb.score == 0

    def test_score_inconnu(self):
        """Score pour feedback inconnu."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="unknown")
        assert fb.score == 0

    def test_feedback_avec_contexte(self):
        """Feedback avec contexte."""
        fb = FeedbackRecette(
            recette_id=1,
            recette_nom="Épinards",
            feedback="dislike",
            contexte="Jules n'a pas aimé",
        )
        assert fb.contexte == "Jules n'a pas aimé"


# ═══════════════════════════════════════════════════════════
# TESTS: Factory
# ═══════════════════════════════════════════════════════════


class TestPreferenceFactory:
    """Tests pour get_user_preference_service."""

    def test_factory_retourne_singleton_meme_user(self, monkeypatch):
        """La factory retourne un singleton pour le même utilisateur."""
        import src.services.utilisateur.preferences as prefs_module
        monkeypatch.setattr(prefs_module, "_preference_service", None)
        
        service1 = get_user_preference_service()
        service2 = get_user_preference_service()
        
        assert service1 is service2

    def test_factory_nouveau_service_different_user(self, monkeypatch):
        """La factory crée un nouveau service pour un utilisateur différent."""
        import src.services.utilisateur.preferences as prefs_module
        monkeypatch.setattr(prefs_module, "_preference_service", None)
        
        service1 = get_user_preference_service("user1")
        service2 = get_user_preference_service("user2")
        
        # Le deuxième appel remplace le singleton
        assert service2.user_id == "user2"

    def test_factory_retourne_instance_valide(self):
        """La factory retourne une instance valide."""
        service = get_user_preference_service()
        
        assert isinstance(service, UserPreferenceService)
        assert service.user_id is not None


# ═══════════════════════════════════════════════════════════
# TESTS: Intégration avec vrai modèle (si disponible)
# ═══════════════════════════════════════════════════════════


class TestIntegrationDB:
    """Tests d'intégration avec la base de données de test."""

    @pytest.fixture
    def db_with_user_preference(self, db):
        """DB de test avec une préférence utilisateur."""
        pref = UserPreference(
            user_id="test_integration",
            nb_adultes=2,
            jules_present=True,
            jules_age_mois=19,
            temps_semaine="normal",
            temps_weekend="long",
            aliments_exclus=[],
            aliments_favoris=["poulet"],
            poisson_par_semaine=2,
            vegetarien_par_semaine=1,
            viande_rouge_max=2,
            robots=["four"],
            magasins_preferes=["Carrefour"],
        )
        db.add(pref)
        db.commit()
        return db

    @pytest.mark.integration
    def test_charger_depuis_vraie_db(self, db_with_user_preference):
        """Charge des préférences depuis la vraie DB de test."""
        service = UserPreferenceService(user_id="test_integration")
        
        prefs = service.charger_preferences(db=db_with_user_preference)
        
        assert prefs.nb_adultes == 2
        assert "poulet" in prefs.aliments_favoris

    @pytest.mark.integration
    def test_sauvegarder_dans_vraie_db(self, db):
        """Sauvegarde de nouvelles préférences dans la DB de test."""
        service = UserPreferenceService(user_id="new_test_user")
        
        prefs = PreferencesUtilisateur(
            nb_adultes=3,
            jules_present=False,
            temps_semaine="express",
        )
        
        result = service.sauvegarder_preferences(prefs, db=db)
        
        assert result is True
        
        # Vérifier que c'est bien sauvegardé
        from sqlalchemy import select
        stmt = select(UserPreference).where(UserPreference.user_id == "new_test_user")
        saved = db.execute(stmt).scalar_one_or_none()
        
        assert saved is not None
        assert saved.nb_adultes == 3
