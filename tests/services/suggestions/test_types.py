"""
Tests for src/services/suggestions/types.py

Pydantic models for suggestions.
"""

from src.services.cuisine.suggestions.types import (
    ContexteSuggestion,
    ProfilCulinaire,
    SuggestionRecette,
)


class TestProfilCulinaire:
    """Tests for ProfilCulinaire."""

    def test_default_values(self):
        """Test valeurs par défaut."""
        profil = ProfilCulinaire()
        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []
        assert profil.ingredients_evites == []
        assert profil.difficulte_moyenne == "moyen"
        assert profil.temps_moyen_minutes == 45
        assert profil.nb_portions_habituel == 4
        assert profil.recettes_favorites == []
        assert profil.jours_depuis_derniere_recette == {}

    def test_custom_values(self):
        """Test valeurs personnalisées."""
        profil = ProfilCulinaire(
            categories_preferees=["italien", "français"],
            ingredients_frequents=["tomate", "oignon"],
            ingredients_evites=["coriandre"],
            difficulte_moyenne="facile",
            temps_moyen_minutes=30,
            nb_portions_habituel=2,
            recettes_favorites=[1, 2, 3],
            jours_depuis_derniere_recette={1: 5, 2: 10},
        )
        assert len(profil.categories_preferees) == 2
        assert "coriandre" in profil.ingredients_evites
        assert profil.difficulte_moyenne == "facile"
        assert profil.nb_portions_habituel == 2
        assert 3 in profil.recettes_favorites

    def test_serialization(self):
        """Test sérialisation."""
        profil = ProfilCulinaire(
            categories_preferees=["italien"],
            temps_moyen_minutes=30,
        )
        data = profil.model_dump()
        assert data["categories_preferees"] == ["italien"]
        assert data["temps_moyen_minutes"] == 30


class TestContexteSuggestion:
    """Tests for ContexteSuggestion."""

    def test_default_values(self):
        """Test valeurs par défaut."""
        contexte = ContexteSuggestion()
        assert contexte.type_repas == "dîner"
        assert contexte.nb_personnes == 4
        assert contexte.temps_disponible_minutes == 60
        assert contexte.ingredients_disponibles == []
        assert contexte.ingredients_a_utiliser == []
        assert contexte.contraintes == []
        assert contexte.saison == ""
        assert contexte.budget == "normal"

    def test_custom_values(self):
        """Test valeurs personnalisées."""
        contexte = ContexteSuggestion(
            type_repas="déjeuner",
            nb_personnes=2,
            temps_disponible_minutes=30,
            ingredients_disponibles=["tomate", "oignon", "poulet"],
            ingredients_a_utiliser=["tomate"],
            contraintes=["sans gluten"],
            saison="été",
            budget="économique",
        )
        assert contexte.type_repas == "déjeuner"
        assert contexte.nb_personnes == 2
        assert contexte.temps_disponible_minutes == 30
        assert len(contexte.ingredients_disponibles) == 3
        assert "tomate" in contexte.ingredients_a_utiliser
        assert "sans gluten" in contexte.contraintes
        assert contexte.saison == "été"
        assert contexte.budget == "économique"

    def test_serialization(self):
        """Test sérialisation."""
        contexte = ContexteSuggestion(
            type_repas="brunch",
            nb_personnes=6,
        )
        data = contexte.model_dump()
        assert data["type_repas"] == "brunch"
        assert data["nb_personnes"] == 6


class TestSuggestionRecette:
    """Tests for SuggestionRecette."""

    def test_default_values(self):
        """Test valeurs par défaut."""
        suggestion = SuggestionRecette()
        assert suggestion.recette_id is None
        assert suggestion.nom == ""
        assert suggestion.raison == ""
        assert suggestion.score == 0.0
        assert suggestion.tags == []
        assert suggestion.temps_preparation == 0
        assert suggestion.difficulte == ""
        assert suggestion.ingredients_manquants == []
        assert suggestion.est_nouvelle is False

    def test_custom_values(self):
        """Test valeurs personnalisées."""
        suggestion = SuggestionRecette(
            recette_id=42,
            nom="Pâtes carbonara",
            raison="Rapide et économique",
            score=95.5,
            tags=["rapide", "italien", "économique"],
            temps_preparation=25,
            difficulte="facile",
            ingredients_manquants=["guanciale"],
            est_nouvelle=True,
        )
        assert suggestion.recette_id == 42
        assert suggestion.nom == "Pâtes carbonara"
        assert suggestion.raison == "Rapide et économique"
        assert suggestion.score == 95.5
        assert len(suggestion.tags) == 3
        assert "italien" in suggestion.tags
        assert suggestion.temps_preparation == 25
        assert suggestion.difficulte == "facile"
        assert "guanciale" in suggestion.ingredients_manquants
        assert suggestion.est_nouvelle is True

    def test_serialization(self):
        """Test sérialisation."""
        suggestion = SuggestionRecette(
            recette_id=1,
            nom="Test",
            score=80.0,
        )
        data = suggestion.model_dump()
        assert data["recette_id"] == 1
        assert data["nom"] == "Test"
        assert data["score"] == 80.0

    def test_score_precision(self):
        """Test précision du score."""
        suggestion = SuggestionRecette(score=75.123456)
        assert suggestion.score == 75.123456


class TestAllExport:
    """Test __all__ exports."""

    def test_all_exports(self):
        """Test tous les exports."""
        from src.services.cuisine.suggestions import types

        assert "ProfilCulinaire" in types.__all__
        assert "ContexteSuggestion" in types.__all__
        assert "SuggestionRecette" in types.__all__
