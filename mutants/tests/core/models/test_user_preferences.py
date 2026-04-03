"""
Tests unitaires pour user_preferences.py

Module: src.core.models.user_preferences
"""

from src.core.models.user_preferences import (
    PreferenceUtilisateur,
    RetourRecette,
    OpenFoodFactsCache,
    TypeRetour,
)


class TestUserPreferences:
    """Tests pour le module user_preferences."""

    class TestFeedbackType:
        """Tests pour la classe TypeRetour."""

        def test_feedbacktype_creation(self):
            assert TypeRetour.LIKE == "like"
            assert TypeRetour.DISLIKE == "dislike"
            assert TypeRetour.NEUTRAL == "neutral"

        def test_feedbacktype_est_str_enum(self):
            assert isinstance(TypeRetour.LIKE, str)

    class TestUserPreference:
        """Tests pour la classe PreferenceUtilisateur."""

        def test_userpreference_creation(self):
            pref = PreferenceUtilisateur(
                user_id="user-123",
                nb_adultes=2,
                jules_present=True,
                jules_age_mois=18,
            )
            assert pref.user_id == "user-123"
            assert pref.nb_adultes == 2
            assert pref.jules_present is True
            assert pref.jules_age_mois == 18

        def test_userpreference_tablename(self):
            assert PreferenceUtilisateur.__tablename__ == "preferences_utilisateurs"

    class TestRecipeFeedback:
        """Tests pour la classe RetourRecette."""

        def test_recipefeedback_creation(self):
            fb = RetourRecette(
                user_id="user-123",
                recette_id=42,
                feedback="like",
            )
            assert fb.user_id == "user-123"
            assert fb.recette_id == 42
            assert fb.feedback == "like"

        def test_recipefeedback_tablename(self):
            assert RetourRecette.__tablename__ == "retours_recettes"

    class TestOpenFoodFactsCache:
        """Tests pour la classe OpenFoodFactsCache."""

        def test_openfoodfactscache_creation(self):
            cache = OpenFoodFactsCache(
                code_barres="3017620422003",
                nom="Nutella",
                marque="Ferrero",
            )
            assert cache.code_barres == "3017620422003"
            assert cache.nom == "Nutella"

        def test_openfoodfactscache_tablename(self):
            assert OpenFoodFactsCache.__tablename__ == "openfoodfacts_cache"
