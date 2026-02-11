"""
Tests pour src/utils/validators/food.py
"""
import pytest
from datetime import date, timedelta
from src.utils.validators.food import (
    valider_recette,
    valider_ingredient,
    valider_article_inventaire,
)


class TestValiderRecette:
    """Tests pour valider_recette (retourne tuple[bool, list[str]])."""

    def test_valider_recette_valid(self):
        """Recette valide complète."""
        recipe = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is True
        assert errors == []

    def test_valider_recette_missing_name(self):
        """Recette sans nom = invalide."""
        recipe = {
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False
        assert any("nom" in e.lower() for e in errors)

    def test_valider_recette_short_name(self):
        """Nom trop court = invalide."""
        recipe = {
            "nom": "AB",  # < 3 caractères
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False

    def test_valider_recette_negative_time(self):
        """Temps négatif = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": -10,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False

    def test_valider_recette_zero_portions(self):
        """Zero portions = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 0,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False


class TestValiderIngredient:
    """Tests pour valider_ingredient (retourne tuple[bool, list[str]])."""

    def test_valider_ingredient_valid(self):
        """Ingrédient valide."""
        ingredient = {
            "nom": "Farine",
            "unite": "g",  # Unite requise
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is True
        assert errors == []

    def test_valider_ingredient_missing_name(self):
        """Ingrédient sans nom = invalide."""
        ingredient = {
            "unite": "g",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False

    def test_valider_ingredient_missing_unite(self):
        """Ingrédient sans unité = invalide."""
        ingredient = {
            "nom": "Farine",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False

    def test_valider_ingredient_short_name(self):
        """Nom trop court = invalide."""
        ingredient = {
            "nom": "A",  # < 2 caractères
            "unite": "g",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False


class TestValiderArticleInventaire:
    """Tests pour valider_article_inventaire (retourne tuple[bool, list[str]])."""

    def test_valider_inventaire_valid(self):
        """Article inventaire valide."""
        item = {
            "ingredient_id": 1,
            "quantite": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True
        assert errors == []

    def test_valider_inventaire_missing_ingredient_id(self):
        """Article sans ingredient_id = invalide."""
        item = {
            "quantite": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_missing_quantite(self):
        """Article sans quantité = invalide."""
        item = {
            "ingredient_id": 1,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_negative_quantity(self):
        """Quantité négative = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite": -1,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_zero_quantity(self):
        """Quantité zéro = valide (>= 0)."""
        item = {
            "ingredient_id": 1,
            "quantite": 0,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True  # 0 est >= 0

    def test_valider_inventaire_with_min_quantity(self):
        """Article avec quantite_min."""
        item = {
            "ingredient_id": 1,
            "quantite": 5,
            "quantite_min": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True
