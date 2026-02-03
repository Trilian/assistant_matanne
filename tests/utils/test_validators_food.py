"""
Tests pour src/utils/validators/food.py
"""
import pytest
from datetime import date, timedelta
from src.utils.validators.food import (
    validate_recipe,
    validate_ingredient,
    validate_inventory_item,
)


class TestValidateRecipe:
    """Tests pour validate_recipe (retourne tuple[bool, list[str]])."""

    def test_validate_recipe_valid(self):
        """Recette valide complète."""
        recipe = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = validate_recipe(recipe)
        assert is_valid is True
        assert errors == []

    def test_validate_recipe_missing_name(self):
        """Recette sans nom = invalide."""
        recipe = {
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = validate_recipe(recipe)
        assert is_valid is False
        assert any("nom" in e.lower() for e in errors)

    def test_validate_recipe_short_name(self):
        """Nom trop court = invalide."""
        recipe = {
            "nom": "AB",  # < 3 caractères
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = validate_recipe(recipe)
        assert is_valid is False

    def test_validate_recipe_negative_time(self):
        """Temps négatif = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": -10,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = validate_recipe(recipe)
        assert is_valid is False

    def test_validate_recipe_zero_portions(self):
        """Zero portions = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 0,
        }
        is_valid, errors = validate_recipe(recipe)
        assert is_valid is False


class TestValidateIngredient:
    """Tests pour validate_ingredient (retourne tuple[bool, list[str]])."""

    def test_validate_ingredient_valid(self):
        """Ingrédient valide."""
        ingredient = {
            "nom": "Farine",
            "unite": "g",  # Unite requise
        }
        is_valid, errors = validate_ingredient(ingredient)
        assert is_valid is True
        assert errors == []

    def test_validate_ingredient_missing_name(self):
        """Ingrédient sans nom = invalide."""
        ingredient = {
            "unite": "g",
        }
        is_valid, errors = validate_ingredient(ingredient)
        assert is_valid is False

    def test_validate_ingredient_missing_unite(self):
        """Ingrédient sans unité = invalide."""
        ingredient = {
            "nom": "Farine",
        }
        is_valid, errors = validate_ingredient(ingredient)
        assert is_valid is False

    def test_validate_ingredient_short_name(self):
        """Nom trop court = invalide."""
        ingredient = {
            "nom": "A",  # < 2 caractères
            "unite": "g",
        }
        is_valid, errors = validate_ingredient(ingredient)
        assert is_valid is False


class TestValidateInventoryItem:
    """Tests pour validate_inventory_item (retourne tuple[bool, list[str]])."""

    def test_validate_inventory_valid(self):
        """Article inventaire valide."""
        item = {
            "ingredient_id": 1,
            "quantite": 2,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is True
        assert errors == []

    def test_validate_inventory_missing_ingredient_id(self):
        """Article sans ingredient_id = invalide."""
        item = {
            "quantite": 2,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is False

    def test_validate_inventory_missing_quantite(self):
        """Article sans quantité = invalide."""
        item = {
            "ingredient_id": 1,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is False

    def test_validate_inventory_negative_quantity(self):
        """Quantité négative = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite": -1,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is False

    def test_validate_inventory_zero_quantity(self):
        """Quantité zéro = valide (>= 0)."""
        item = {
            "ingredient_id": 1,
            "quantite": 0,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is True  # 0 est >= 0

    def test_validate_inventory_with_min_quantity(self):
        """Article avec quantite_min."""
        item = {
            "ingredient_id": 1,
            "quantite": 5,
            "quantite_min": 2,
        }
        is_valid, errors = validate_inventory_item(item)
        assert is_valid is True
