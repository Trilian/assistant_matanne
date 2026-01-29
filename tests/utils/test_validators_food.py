"""
Tests pour les validators de données cuisine
"""

import pytest

from src.utils.validators.food import (
    validate_recipe,
    validate_ingredient,
    validate_inventory_item,
    validate_shopping_item,
    validate_meal,
)


class TestValidateRecipe:
    """Tests pour validate_recipe"""

    def test_validate_recipe_valid(self):
        """Test recette valide"""
        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is True
        assert errors == []

    def test_validate_recipe_missing_nom(self):
        """Test nom manquant"""
        data = {
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is False
        assert any("nom" in e for e in errors)

    def test_validate_recipe_nom_too_short(self):
        """Test nom trop court"""
        data = {
            "nom": "ab",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is False
        assert any("3 caractères" in e for e in errors)

    def test_validate_recipe_temps_invalid(self):
        """Test temps invalide"""
        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": -10,
            "temps_cuisson": 45,
            "portions": 6,
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is False

    def test_validate_recipe_portions_invalid(self):
        """Test portions invalides"""
        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 100,
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is False
        assert any("portions" in e for e in errors)

    def test_validate_recipe_invalid_difficulte(self):
        """Test difficulté invalide"""
        data = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "impossible",
        }
        is_valid, errors = validate_recipe(data)
        assert is_valid is False
        assert any("difficulte" in e for e in errors)


class TestValidateIngredient:
    """Tests pour validate_ingredient"""

    def test_validate_ingredient_valid(self):
        """Test ingrédient valide"""
        data = {"nom": "Pomme", "unite": "pcs"}  # pcs = pièces
        is_valid, errors = validate_ingredient(data)
        assert is_valid is True
        assert errors == []

    def test_validate_ingredient_missing_nom(self):
        """Test nom manquant"""
        data = {"unite": "pièce"}
        is_valid, errors = validate_ingredient(data)
        assert is_valid is False
        assert any("nom" in e for e in errors)

    def test_validate_ingredient_nom_too_short(self):
        """Test nom trop court"""
        data = {"nom": "a", "unite": "pièce"}
        is_valid, errors = validate_ingredient(data)
        assert is_valid is False
        assert any("2 caractères" in e for e in errors)

    def test_validate_ingredient_missing_unite(self):
        """Test unité manquante"""
        data = {"nom": "Pomme"}
        is_valid, errors = validate_ingredient(data)
        assert is_valid is False
        assert any("unite" in e for e in errors)

    def test_validate_ingredient_invalid_unite(self):
        """Test unité invalide"""
        data = {"nom": "Pomme", "unite": "invalid"}
        is_valid, errors = validate_ingredient(data)
        assert is_valid is False
        assert any("unite" in e for e in errors)


class TestValidateInventoryItem:
    """Tests pour validate_inventory_item"""

    def test_validate_inventory_item_valid(self):
        """Test article inventaire valide"""
        data = {"ingredient_id": 1, "quantite": 10}
        is_valid, errors = validate_inventory_item(data)
        assert is_valid is True
        assert errors == []

    def test_validate_inventory_item_missing_ingredient_id(self):
        """Test ingredient_id manquant"""
        data = {"quantite": 10}
        is_valid, errors = validate_inventory_item(data)
        assert is_valid is False
        assert any("ingredient_id" in e for e in errors)

    def test_validate_inventory_item_negative_quantite(self):
        """Test quantité négative"""
        data = {"ingredient_id": 1, "quantite": -5}
        is_valid, errors = validate_inventory_item(data)
        assert is_valid is False
        assert any("quantite" in e for e in errors)

    def test_validate_inventory_item_invalid_quantite_min(self):
        """Test quantite_min invalide"""
        data = {"ingredient_id": 1, "quantite": 10, "quantite_min": -1}
        is_valid, errors = validate_inventory_item(data)
        assert is_valid is False
        assert any("quantite_min" in e for e in errors)


class TestValidateShoppingItem:
    """Tests pour validate_shopping_item"""

    def test_validate_shopping_item_valid(self):
        """Test article courses valide"""
        data = {"ingredient_id": 1, "quantite_necessaire": 5}
        is_valid, errors = validate_shopping_item(data)
        assert is_valid is True
        assert errors == []

    def test_validate_shopping_item_missing_ingredient_id(self):
        """Test ingredient_id manquant"""
        data = {"quantite_necessaire": 5}
        is_valid, errors = validate_shopping_item(data)
        assert is_valid is False
        assert any("ingredient_id" in e for e in errors)

    def test_validate_shopping_item_zero_quantite(self):
        """Test quantité à zéro"""
        data = {"ingredient_id": 1, "quantite_necessaire": 0}
        is_valid, errors = validate_shopping_item(data)
        assert is_valid is False
        assert any("quantite_necessaire" in e for e in errors)

    def test_validate_shopping_item_invalid_priorite(self):
        """Test priorité invalide"""
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 5,
            "priorite": "invalid",
        }
        is_valid, errors = validate_shopping_item(data)
        assert is_valid is False
        assert any("priorite" in e for e in errors)


class TestValidateMeal:
    """Tests pour validate_meal"""

    def test_validate_meal_valid(self):
        """Test repas valide"""
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": "2025-01-15",
            "type_repas": "déjeuner",
        }
        is_valid, errors = validate_meal(data)
        assert is_valid is True
        assert errors == []

    def test_validate_meal_missing_planning_id(self):
        """Test planning_id manquant"""
        data = {
            "jour_semaine": 0,
            "date": "2025-01-15",
            "type_repas": "déjeuner",
        }
        is_valid, errors = validate_meal(data)
        assert is_valid is False
        assert any("planning_id" in e for e in errors)

    def test_validate_meal_invalid_jour_semaine(self):
        """Test jour_semaine invalide"""
        data = {
            "planning_id": 1,
            "jour_semaine": 10,
            "date": "2025-01-15",
            "type_repas": "déjeuner",
        }
        is_valid, errors = validate_meal(data)
        assert is_valid is False
        assert any("jour_semaine" in e for e in errors)

    def test_validate_meal_invalid_type_repas(self):
        """Test type_repas invalide"""
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": "2025-01-15",
            "type_repas": "invalid",
        }
        is_valid, errors = validate_meal(data)
        assert is_valid is False
        assert any("type_repas" in e for e in errors)

    def test_validate_meal_invalid_portions(self):
        """Test portions invalides"""
        data = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": "2025-01-15",
            "type_repas": "déjeuner",
            "portions": 100,
        }
        is_valid, errors = validate_meal(data)
        assert is_valid is False
        assert any("portions" in e for e in errors)

