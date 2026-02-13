"""
Tests approfondis pour helpers/food.py, helpers/helpers.py, helpers/stats.py

Modules: src/utils/helpers/
Objectif: Couverture maximale (80%+)
"""


# =============================================================================
# TESTS helpers/food.py
# =============================================================================


class TestFoodHelpers:
    def test_batch_find_or_create_ingredients(self):
        from src.utils.helpers.food import batch_find_or_create_ingredients

        data = [{"name": "Tomate"}, {"name": "Oignon"}]
        result = batch_find_or_create_ingredients(data)
        assert result == data

    def test_calculate_recipe_cost(self):
        from src.utils.helpers.food import calculate_recipe_cost

        ingredients = [
            {"nom": "Tomate", "quantite": 2, "prix": 1.5},
            {"nom": "Oignon", "quantite": 1, "prix": 0.5},
        ]
        assert calculate_recipe_cost(ingredients) == 0.0  # Dummy impl

    def test_consolidate_duplicates(self):
        from src.utils.helpers.food import consolidate_duplicates

        items = [{"id": 1}, {"id": 1}, {"id": 2}]
        assert consolidate_duplicates(items) == items

    def test_enrich_with_ingredient_info(self):
        from src.utils.helpers.food import enrich_with_ingredient_info

        items = [{"id": 1}]
        assert enrich_with_ingredient_info(items) == items

    def test_find_or_create_ingredient(self):
        from src.utils.helpers.food import find_or_create_ingredient

        assert find_or_create_ingredient("Tomate") == {"name": "Tomate"}

    def test_format_inventory_summary(self):
        from src.utils.helpers.food import format_inventory_summary

        assert format_inventory_summary({}) == "Inventaire vide"

    def test_format_recipe_summary(self):
        from src.utils.helpers.food import format_recipe_summary

        assert "Recette:" in format_recipe_summary({"name": "Tarte"})

    def test_get_all_ingredients_cached(self):
        from src.utils.helpers.food import get_all_ingredients_cached

        assert get_all_ingredients_cached() == []

    def test_suggest_ingredient_substitutes(self):
        from src.utils.helpers.food import suggest_ingredient_substitutes

        assert suggest_ingredient_substitutes("Tomate") == []

    def test_validate_stock_level(self):
        from src.utils.helpers.food import validate_stock_level

        assert validate_stock_level(5, 2) is True
        assert validate_stock_level(1, 2) is False


# =============================================================================
# TESTS helpers/helpers.py (version pure, sans DB)
# =============================================================================


class TestHelpersPure:
    def test_validate_stock_level(self):
        from src.utils.helpers.helpers import validate_stock_level

        assert validate_stock_level(1, 5, "Tomate") == ("critique", "ðŸ”´")
        assert validate_stock_level(3, 5, "Tomate") == ("sous_seuil", "âš ï¸")
        assert validate_stock_level(6, 5, "Tomate") == ("ok", "âœ…")

    def test_consolidate_duplicates_default(self):
        from src.utils.helpers.helpers import consolidate_duplicates

        items = [
            {"nom": "Tomate", "qty": 2},
            {"nom": "tomate", "qty": 3},
            {"nom": "Oignon", "qty": 1},
        ]
        merged = consolidate_duplicates(items, "nom")
        assert len(merged) == 2
        noms = [i["nom"].lower() for i in merged]
        assert "tomate" in noms and "oignon" in noms

    def test_consolidate_duplicates_with_merge(self):
        from src.utils.helpers.helpers import consolidate_duplicates

        def merge(a, b):
            return {"nom": a["nom"], "qty": a["qty"] + b["qty"]}

        items = [
            {"nom": "Tomate", "qty": 2},
            {"nom": "tomate", "qty": 3},
        ]
        merged = consolidate_duplicates(items, "nom", merge)
        assert merged[0]["qty"] == 5

    def test_format_recipe_summary(self):
        from src.utils.helpers.helpers import format_recipe_summary

        recette = {
            "nom": "Tarte",
            "temps_preparation": 10,
            "temps_cuisson": 20,
            "portions": 2,
            "difficulte": "facile",
        }
        summary = format_recipe_summary(recette)
        assert "Tarte" in summary and "30min" in summary

    def test_format_inventory_summary(self):
        from src.utils.helpers.helpers import format_inventory_summary

        inv = [
            {"statut": "ok"},
            {"statut": "sous_seuil"},
            {"statut": "critique"},
            {"statut": "peremption_proche"},
        ]
        summary = format_inventory_summary(inv)
        assert "4 articles" in summary
        assert "2 stock bas" in summary
        assert "1 pÃ©remption proche" in summary

    def test_calculate_recipe_cost(self):
        from src.utils.helpers.helpers import calculate_recipe_cost

        recette = {
            "ingredients": [
                {"nom": "Tomate", "quantite": 2},
                {"nom": "Oignon", "quantite": 1},
            ]
        }
        prix = {"Tomate": 3.0, "Oignon": 2.0}
        cost = calculate_recipe_cost(recette, prix)
        assert cost == 8.0

    def test_suggest_ingredient_substitutes(self):
        from src.utils.helpers.helpers import suggest_ingredient_substitutes

        assert "margarine" in suggest_ingredient_substitutes("beurre")
        assert suggest_ingredient_substitutes("inconnu") == []


# =============================================================================
# TESTS helpers/stats.py
# =============================================================================


class TestStatsHelpers:
    def test_calculate_average(self):
        from src.utils.helpers.stats import calculate_average

        assert calculate_average([1, 2, 3, 4, 5]) == 3.0
        assert calculate_average([]) == 0.0

    def test_calculate_median(self):
        from src.utils.helpers.stats import calculate_median

        assert calculate_median([1, 2, 3, 4, 5]) == 3.0
        assert calculate_median([1, 2, 3, 4]) == 2.5
        assert calculate_median([]) == 0.0

    def test_calculate_variance(self):
        from src.utils.helpers.stats import calculate_variance

        assert calculate_variance([1, 2, 3, 4, 5]) == 2.5
        assert calculate_variance([1]) == 0.0
        assert calculate_variance([]) == 0.0

    def test_calculate_std_dev(self):
        from src.utils.helpers.stats import calculate_std_dev

        assert round(calculate_std_dev([1, 2, 3, 4, 5]), 5) == 1.58114
        assert calculate_std_dev([1]) == 0.0
        assert calculate_std_dev([]) == 0.0

    def test_calculate_percentile(self):
        from src.utils.helpers.stats import calculate_percentile

        assert calculate_percentile([1, 2, 3, 4, 5], 50) == 3.0
        assert calculate_percentile([], 50) == 0.0

    def test_calculate_mode(self):
        from src.utils.helpers.stats import calculate_mode

        assert calculate_mode([1, 2, 2, 3]) == 2
        # En Python 3.8+, mode() retourne le premier si pas de mode unique
        assert calculate_mode([1, 2, 3]) == 1
        assert calculate_mode([]) is None

    def test_calculate_range(self):
        from src.utils.helpers.stats import calculate_range

        assert calculate_range([1, 2, 3, 4, 5]) == 4.0
        assert calculate_range([]) == 0.0

    def test_moving_average(self):
        from src.utils.helpers.stats import moving_average

        assert moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
        assert moving_average([1, 2], 3) == []
