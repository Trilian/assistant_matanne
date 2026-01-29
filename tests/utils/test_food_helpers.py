"""
Tests pour src/utils/helpers/food.py - Fonctions utilitaires pour la nourriture.
"""

import pytest

from src.utils.helpers.food import (
    batch_find_or_create_ingredients,
    calculate_recipe_cost,
    consolidate_duplicates,
    enrich_with_ingredient_info,
    find_or_create_ingredient,
    format_inventory_summary,
    format_recipe_summary,
    get_all_ingredients_cached,
    suggest_ingredient_substitutes,
    validate_stock_level,
)


# ═══════════════════════════════════════════════════════════
# TESTS BATCH FIND OR CREATE INGREDIENTS
# ═══════════════════════════════════════════════════════════


class TestBatchFindOrCreateIngredients:
    """Tests pour batch_find_or_create_ingredients."""

    def test_returns_same_list(self):
        """Test retourne la même liste."""
        data = [{"name": "Tomate"}, {"name": "Oignon"}]
        result = batch_find_or_create_ingredients(data)
        assert result == data

    def test_empty_list(self):
        """Test avec liste vide."""
        result = batch_find_or_create_ingredients([])
        assert result == []

    def test_preserves_data(self):
        """Test préserve les données."""
        data = [{"name": "Carotte", "quantity": 5, "extra": "info"}]
        result = batch_find_or_create_ingredients(data)
        assert result[0]["name"] == "Carotte"
        assert result[0]["quantity"] == 5


# ═══════════════════════════════════════════════════════════
# TESTS CALCULATE RECIPE COST
# ═══════════════════════════════════════════════════════════


class TestCalculateRecipeCost:
    """Tests pour calculate_recipe_cost."""

    def test_returns_zero(self):
        """Test retourne 0.0."""
        result = calculate_recipe_cost([])
        assert result == 0.0

    def test_with_ingredients(self):
        """Test avec des ingrédients."""
        ingredients = [{"name": "Farine", "cost": 2.5}]
        result = calculate_recipe_cost(ingredients)
        assert result == 0.0  # Implementation actuelle retourne toujours 0


# ═══════════════════════════════════════════════════════════
# TESTS CONSOLIDATE DUPLICATES
# ═══════════════════════════════════════════════════════════


class TestConsolidateDuplicates:
    """Tests pour consolidate_duplicates."""

    def test_returns_same_list(self):
        """Test retourne la même liste."""
        items = [{"id": 1}, {"id": 2}]
        result = consolidate_duplicates(items)
        assert result == items

    def test_empty_list(self):
        """Test avec liste vide."""
        result = consolidate_duplicates([])
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS ENRICH WITH INGREDIENT INFO
# ═══════════════════════════════════════════════════════════


class TestEnrichWithIngredientInfo:
    """Tests pour enrich_with_ingredient_info."""

    def test_returns_same_list(self):
        """Test retourne la même liste."""
        items = [{"name": "Sel"}]
        result = enrich_with_ingredient_info(items)
        assert result == items

    def test_empty_list(self):
        """Test avec liste vide."""
        result = enrich_with_ingredient_info([])
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS FIND OR CREATE INGREDIENT
# ═══════════════════════════════════════════════════════════


class TestFindOrCreateIngredient:
    """Tests pour find_or_create_ingredient."""

    def test_returns_dict_with_name(self):
        """Test retourne un dict avec le nom."""
        result = find_or_create_ingredient("Tomate")
        assert result == {"name": "Tomate"}

    def test_preserves_name(self):
        """Test préserve le nom."""
        result = find_or_create_ingredient("Oignon Rouge")
        assert result["name"] == "Oignon Rouge"

    def test_empty_name(self):
        """Test avec nom vide."""
        result = find_or_create_ingredient("")
        assert result == {"name": ""}


# ═══════════════════════════════════════════════════════════
# TESTS FORMAT INVENTORY SUMMARY
# ═══════════════════════════════════════════════════════════


class TestFormatInventorySummary:
    """Tests pour format_inventory_summary."""

    def test_returns_default_message(self):
        """Test retourne message par défaut."""
        result = format_inventory_summary({})
        assert result == "Inventaire vide"

    def test_with_data(self):
        """Test avec données."""
        data = {"items": 10, "value": 100}
        result = format_inventory_summary(data)
        assert result == "Inventaire vide"  # Implementation actuelle


# ═══════════════════════════════════════════════════════════
# TESTS FORMAT RECIPE SUMMARY
# ═══════════════════════════════════════════════════════════


class TestFormatRecipeSummary:
    """Tests pour format_recipe_summary."""

    def test_with_name(self):
        """Test avec nom."""
        result = format_recipe_summary({"name": "Tarte aux pommes"})
        assert result == "Recette: Tarte aux pommes"

    def test_without_name(self):
        """Test sans nom."""
        result = format_recipe_summary({})
        assert result == "Recette: sans titre"

    def test_with_empty_name(self):
        """Test avec nom vide."""
        result = format_recipe_summary({"name": ""})
        assert result == "Recette: "


# ═══════════════════════════════════════════════════════════
# TESTS GET ALL INGREDIENTS CACHED
# ═══════════════════════════════════════════════════════════


class TestGetAllIngredientsCached:
    """Tests pour get_all_ingredients_cached."""

    def test_returns_empty_list(self):
        """Test retourne liste vide."""
        result = get_all_ingredients_cached()
        assert result == []

    def test_returns_list_type(self):
        """Test retourne type list."""
        result = get_all_ingredients_cached()
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS SUGGEST INGREDIENT SUBSTITUTES
# ═══════════════════════════════════════════════════════════


class TestSuggestIngredientSubstitutes:
    """Tests pour suggest_ingredient_substitutes."""

    def test_returns_empty_list(self):
        """Test retourne liste vide."""
        result = suggest_ingredient_substitutes("Beurre")
        assert result == []

    def test_any_ingredient(self):
        """Test avec n'importe quel ingrédient."""
        result = suggest_ingredient_substitutes("Farine")
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATE STOCK LEVEL
# ═══════════════════════════════════════════════════════════


class TestValidateStockLevel:
    """Tests pour validate_stock_level."""

    def test_stock_above_minimum(self):
        """Test stock au-dessus du minimum."""
        result = validate_stock_level(10, 5)
        assert result is True

    def test_stock_equal_minimum(self):
        """Test stock égal au minimum."""
        result = validate_stock_level(5, 5)
        assert result is True

    def test_stock_below_minimum(self):
        """Test stock sous le minimum."""
        result = validate_stock_level(3, 5)
        assert result is False

    def test_zero_stock_zero_min(self):
        """Test stock 0 et min 0."""
        result = validate_stock_level(0, 0)
        assert result is True

    def test_zero_stock_positive_min(self):
        """Test stock 0 et min positif."""
        result = validate_stock_level(0, 1)
        assert result is False

    def test_float_values(self):
        """Test avec valeurs décimales."""
        result = validate_stock_level(5.5, 5.0)
        assert result is True

    def test_float_below(self):
        """Test décimal sous le minimum."""
        result = validate_stock_level(4.9, 5.0)
        assert result is False
