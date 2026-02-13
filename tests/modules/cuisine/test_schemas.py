"""
Tests pour schemas.py - Dataclasses du domaine Cuisine
Couverture cible: 80%+
"""

from datetime import date

from src.modules.cuisine.schemas import (
    FeedbackRecette,
    PreferencesUtilisateur,
)

# ═══════════════════════════════════════════════════════════
# TESTS PREFERENCES UTILISATEUR
# ═══════════════════════════════════════════════════════════


class TestPreferencesUtilisateur:
    """Tests de la dataclass PreferencesUtilisateur."""

    def test_creation_default(self):
        """Création avec valeurs par défaut."""
        prefs = PreferencesUtilisateur()

        assert prefs.nb_adultes == 2
        assert prefs.jules_present is True
        assert prefs.jules_age_mois == 19
        assert prefs.temps_semaine == "normal"
        assert prefs.temps_weekend == "long"

    def test_creation_custom(self):
        """Création avec valeurs personnalisées."""
        prefs = PreferencesUtilisateur(
            nb_adultes=3, jules_present=False, poisson_par_semaine=3, budget_semaine=150.0
        )

        assert prefs.nb_adultes == 3
        assert prefs.jules_present is False
        assert prefs.poisson_par_semaine == 3
        assert prefs.budget_semaine == 150.0

    def test_aliments_exclus_modifiables(self):
        """Les listes sont modifiables."""
        prefs = PreferencesUtilisateur(
            aliments_exclus=["gluten", "lactose"], aliments_favoris=["pâtes", "riz"]
        )

        assert "gluten" in prefs.aliments_exclus
        assert "pâtes" in prefs.aliments_favoris

    def test_robots_default(self):
        """Robots par défaut."""
        prefs = PreferencesUtilisateur()
        assert "four" in prefs.robots
        assert "poele" in prefs.robots

    def test_magasins_preferes_default(self):
        """Magasins par défaut."""
        prefs = PreferencesUtilisateur()
        assert len(prefs.magasins_preferes) > 0
        assert "Carrefour" in prefs.magasins_preferes

    def test_to_dict(self):
        """Conversion en dictionnaire."""
        prefs = PreferencesUtilisateur(nb_adultes=4, budget_semaine=200.0)
        d = prefs.to_dict()

        assert isinstance(d, dict)
        assert d["nb_adultes"] == 4
        assert d["budget_semaine"] == 200.0
        assert "jules_present" in d
        assert "poisson_par_semaine" in d

    def test_from_dict(self):
        """Création depuis dictionnaire."""
        data = {
            "nb_adultes": 5,
            "jules_present": False,
            "temps_semaine": "express",
            "budget_semaine": 180.0,
        }
        prefs = PreferencesUtilisateur.from_dict(data)

        assert prefs.nb_adultes == 5
        assert prefs.jules_present is False
        assert prefs.temps_semaine == "express"
        assert prefs.budget_semaine == 180.0

    def test_from_dict_ignore_extra_keys(self):
        """Les clés inconnues sont ignorées."""
        data = {"nb_adultes": 2, "cle_inconnue": "valeur", "autre_cle": 123}
        prefs = PreferencesUtilisateur.from_dict(data)

        assert prefs.nb_adultes == 2
        assert not hasattr(prefs, "cle_inconnue")

    def test_roundtrip_dict(self):
        """Aller-retour to_dict/from_dict."""
        original = PreferencesUtilisateur(
            nb_adultes=3, aliments_exclus=["poisson"], budget_semaine=100.0
        )

        data = original.to_dict()
        restored = PreferencesUtilisateur.from_dict(data)

        assert restored.nb_adultes == original.nb_adultes
        assert restored.aliments_exclus == original.aliments_exclus
        assert restored.budget_semaine == original.budget_semaine


# ═══════════════════════════════════════════════════════════
# TESTS FEEDBACK RECETTE
# ═══════════════════════════════════════════════════════════


class TestFeedbackRecette:
    """Tests de la dataclass FeedbackRecette."""

    def test_creation_simple(self):
        """Création d'un feedback."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Tarte aux pommes", feedback="like")

        assert fb.recette_id == 1
        assert fb.recette_nom == "Tarte aux pommes"
        assert fb.feedback == "like"

    def test_date_feedback_default(self):
        """Date de feedback par défaut = aujourd'hui."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="neutral")

        assert fb.date_feedback == date.today()

    def test_contexte_optionnel(self):
        """Contexte est optionnel."""
        fb = FeedbackRecette(
            recette_id=1, recette_nom="Test", feedback="dislike", contexte="Jules n'a pas aimé"
        )

        assert fb.contexte == "Jules n'a pas aimé"

    def test_score_like(self):
        """Score pour 'like' = 1."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="like")
        assert fb.score == 1

    def test_score_dislike(self):
        """Score pour 'dislike' = -1."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="dislike")
        assert fb.score == -1

    def test_score_neutral(self):
        """Score pour 'neutral' = 0."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="neutral")
        assert fb.score == 0

    def test_score_inconnu(self):
        """Score pour feedback inconnu = 0."""
        fb = FeedbackRecette(recette_id=1, recette_nom="Test", feedback="inconnu")
        assert fb.score == 0

    def test_multiple_feedbacks(self):
        """Plusieurs feedbacks pour une même recette."""
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Test", feedback="like"),
            FeedbackRecette(recette_id=1, recette_nom="Test", feedback="like"),
            FeedbackRecette(recette_id=1, recette_nom="Test", feedback="dislike"),
        ]

        total_score = sum(fb.score for fb in feedbacks)
        assert total_score == 1  # 1 + 1 - 1 = 1


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION SCHEMAS
# ═══════════════════════════════════════════════════════════


class TestSchemasIntegration:
    """Tests d'intégration entre les schemas."""

    def test_preferences_avec_feedbacks(self):
        """Utilisation combinée des schémas."""
        prefs = PreferencesUtilisateur(aliments_exclus=["poisson"])

        # Simuler des feedbacks
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Pâtes carbo", feedback="like"),
            FeedbackRecette(recette_id=2, recette_nom="Saumon grillé", feedback="dislike"),
        ]

        # Filtrer les feedbacks négatifs
        negatifs = [fb for fb in feedbacks if fb.score < 0]
        assert len(negatifs) == 1
        assert negatifs[0].recette_nom == "Saumon grillé"

    def test_preferences_serialization_complete(self):
        """Sérialisation complète des préférences."""
        import json

        prefs = PreferencesUtilisateur(
            nb_adultes=2, aliments_exclus=["fruits de mer"], robots=["four", "cookeo", "thermomix"]
        )

        # Doit être sérialisable en JSON
        json_str = json.dumps(prefs.to_dict())
        assert len(json_str) > 0

        # Doit être désérialisable
        data = json.loads(json_str)
        restored = PreferencesUtilisateur.from_dict(data)
        assert restored.nb_adultes == prefs.nb_adultes
