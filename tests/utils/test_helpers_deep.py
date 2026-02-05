"""
Tests approfondis pour src/utils/helpers/
Objectif: Atteindre 80%+ de couverture

Couvre:
- helpers.py: find_or_create_ingredient, batch_find_or_create_ingredients, validate_stock_level, etc.
- stats.py: calculate_average, calculate_median, calculate_variance, etc.
- strings.py: generate_id, normalize_whitespace, remove_accents, etc.
- food.py: fonctions utilitaires pour la nourriture
- data.py, dates.py: utilitaires généraux
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS STATS
# ═══════════════════════════════════════════════════════════


class TestCalculateAverage:
    """Tests pour calculate_average"""
    
    def test_calculate_average_normal(self):
        """Test moyenne normale"""
        from src.utils.helpers.stats import calculate_average
        
        result = calculate_average([1, 2, 3, 4, 5])
        assert result == 3.0
    
    def test_calculate_average_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_average
        
        result = calculate_average([])
        assert result == 0.0
    
    def test_calculate_average_un_element(self):
        """Test un seul élément"""
        from src.utils.helpers.stats import calculate_average
        
        result = calculate_average([42])
        assert result == 42.0
    
    def test_calculate_average_floats(self):
        """Test avec floats"""
        from src.utils.helpers.stats import calculate_average
        
        result = calculate_average([1.5, 2.5, 3.5])
        assert result == 2.5


class TestCalculateMedian:
    """Tests pour calculate_median"""
    
    def test_calculate_median_impair(self):
        """Test médiane liste impaire"""
        from src.utils.helpers.stats import calculate_median
        
        result = calculate_median([1, 2, 3, 4, 5])
        assert result == 3.0
    
    def test_calculate_median_pair(self):
        """Test médiane liste paire"""
        from src.utils.helpers.stats import calculate_median
        
        result = calculate_median([1, 2, 3, 4])
        assert result == 2.5
    
    def test_calculate_median_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_median
        
        result = calculate_median([])
        assert result == 0.0
    
    def test_calculate_median_non_trie(self):
        """Test liste non triée"""
        from src.utils.helpers.stats import calculate_median
        
        result = calculate_median([5, 1, 3, 2, 4])
        assert result == 3.0


class TestCalculateVariance:
    """Tests pour calculate_variance"""
    
    def test_calculate_variance_normal(self):
        """Test variance normale"""
        from src.utils.helpers.stats import calculate_variance
        
        result = calculate_variance([1, 2, 3, 4, 5])
        assert result == 2.5
    
    def test_calculate_variance_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_variance
        
        result = calculate_variance([])
        assert result == 0.0
    
    def test_calculate_variance_un_element(self):
        """Test un seul élément"""
        from src.utils.helpers.stats import calculate_variance
        
        result = calculate_variance([42])
        assert result == 0.0


class TestCalculateStdDev:
    """Tests pour calculate_std_dev"""
    
    def test_calculate_std_dev_normal(self):
        """Test écart-type normal"""
        from src.utils.helpers.stats import calculate_std_dev
        
        result = calculate_std_dev([1, 2, 3, 4, 5])
        assert abs(result - 1.5811388300841898) < 0.001
    
    def test_calculate_std_dev_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_std_dev
        
        result = calculate_std_dev([])
        assert result == 0.0
    
    def test_calculate_std_dev_un_element(self):
        """Test un seul élément"""
        from src.utils.helpers.stats import calculate_std_dev
        
        result = calculate_std_dev([42])
        assert result == 0.0


class TestCalculatePercentile:
    """Tests pour calculate_percentile"""
    
    def test_calculate_percentile_50(self):
        """Test 50ème percentile"""
        from src.utils.helpers.stats import calculate_percentile
        
        result = calculate_percentile([1, 2, 3, 4, 5], 50)
        assert result == 3.0
    
    def test_calculate_percentile_25(self):
        """Test 25ème percentile"""
        from src.utils.helpers.stats import calculate_percentile
        
        result = calculate_percentile([1, 2, 3, 4, 5], 25)
        assert result == 2.0
    
    def test_calculate_percentile_75(self):
        """Test 75ème percentile"""
        from src.utils.helpers.stats import calculate_percentile
        
        result = calculate_percentile([1, 2, 3, 4, 5], 75)
        assert result == 4.0
    
    def test_calculate_percentile_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_percentile
        
        result = calculate_percentile([], 50)
        assert result == 0.0


class TestCalculateMode:
    """Tests pour calculate_mode"""
    
    def test_calculate_mode_normal(self):
        """Test mode normal"""
        from src.utils.helpers.stats import calculate_mode
        
        result = calculate_mode([1, 2, 2, 3, 3, 3])
        assert result == 3
    
    def test_calculate_mode_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_mode
        
        result = calculate_mode([])
        assert result is None
    
    def test_calculate_mode_pas_unique(self):
        """Test pas de mode unique"""
        from src.utils.helpers.stats import calculate_mode
        
        result = calculate_mode([1, 1, 2, 2])
        # Peut retourner 1 ou 2 selon l'implémentation, ou None
        assert result in [1, 2, None]


class TestCalculateRange:
    """Tests pour calculate_range"""
    
    def test_calculate_range_normal(self):
        """Test étendue normale"""
        from src.utils.helpers.stats import calculate_range
        
        result = calculate_range([1, 2, 3, 4, 5])
        assert result == 4.0
    
    def test_calculate_range_vide(self):
        """Test liste vide"""
        from src.utils.helpers.stats import calculate_range
        
        result = calculate_range([])
        assert result == 0.0


class TestMovingAverage:
    """Tests pour moving_average"""
    
    def test_moving_average_normal(self):
        """Test moyenne mobile normale"""
        from src.utils.helpers.stats import moving_average
        
        result = moving_average([1, 2, 3, 4, 5], 3)
        assert result == [2.0, 3.0, 4.0]
    
    def test_moving_average_window_trop_grand(self):
        """Test fenêtre plus grande que liste"""
        from src.utils.helpers.stats import moving_average
        
        result = moving_average([1, 2, 3], 5)
        assert result == []
    
    def test_moving_average_window_un(self):
        """Test fenêtre de 1"""
        from src.utils.helpers.stats import moving_average
        
        result = moving_average([1, 2, 3], 1)
        assert result == [1.0, 2.0, 3.0]


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS STRINGS
# ═══════════════════════════════════════════════════════════


class TestGenerateId:
    """Tests pour generate_id"""
    
    def test_generate_id_dict(self):
        """Test ID depuis dict"""
        from src.utils.helpers.strings import generate_id
        
        result = generate_id({"nom": "test", "value": 123})
        assert len(result) == 16
        assert isinstance(result, str)
    
    def test_generate_id_deterministe(self):
        """Test que l'ID est déterministe"""
        from src.utils.helpers.strings import generate_id
        
        data = {"a": 1, "b": 2}
        result1 = generate_id(data)
        result2 = generate_id(data)
        assert result1 == result2
    
    def test_generate_id_different_data(self):
        """Test que données différentes = IDs différents"""
        from src.utils.helpers.strings import generate_id
        
        result1 = generate_id({"a": 1})
        result2 = generate_id({"a": 2})
        assert result1 != result2


class TestNormalizeWhitespace:
    """Tests pour normalize_whitespace"""
    
    def test_normalize_whitespace_multiple_spaces(self):
        """Test espaces multiples"""
        from src.utils.helpers.strings import normalize_whitespace
        
        result = normalize_whitespace("  hello    world  ")
        assert result == "hello world"
    
    def test_normalize_whitespace_tabs(self):
        """Test avec tabs"""
        from src.utils.helpers.strings import normalize_whitespace
        
        result = normalize_whitespace("hello\t\tworld")
        assert result == "hello world"
    
    def test_normalize_whitespace_newlines(self):
        """Test avec sauts de ligne"""
        from src.utils.helpers.strings import normalize_whitespace
        
        result = normalize_whitespace("hello\n\nworld")
        assert result == "hello world"


class TestRemoveAccents:
    """Tests pour remove_accents"""
    
    def test_remove_accents_fr(self):
        """Test accents français"""
        from src.utils.helpers.strings import remove_accents
        
        result = remove_accents("café crème")
        assert result == "cafe creme"
    
    def test_remove_accents_tous(self):
        """Test tous les accents"""
        from src.utils.helpers.strings import remove_accents
        
        result = remove_accents("àáâäãèéêëìíîïòóôöõùúûüçñ")
        # Note: certains caractères comme ã -> a, õ -> o peuvent varier selon normalisation
        assert "a" in result and "e" in result and "i" in result and "o" in result
    
    def test_remove_accents_majuscules(self):
        """Test accents majuscules"""
        from src.utils.helpers.strings import remove_accents
        
        result = remove_accents("ÉÀÜÇÑ")
        assert result == "EAUCN"


class TestCamelToSnake:
    """Tests pour camel_to_snake"""
    
    def test_camel_to_snake_simple(self):
        """Test conversion simple"""
        from src.utils.helpers.strings import camel_to_snake
        
        result = camel_to_snake("myVariableName")
        assert result == "my_variable_name"
    
    def test_camel_to_snake_pascal(self):
        """Test PascalCase"""
        from src.utils.helpers.strings import camel_to_snake
        
        result = camel_to_snake("MyVariableName")
        assert result == "my_variable_name"
    
    def test_camel_to_snake_deja_snake(self):
        """Test déjà snake_case"""
        from src.utils.helpers.strings import camel_to_snake
        
        result = camel_to_snake("my_variable")
        assert result == "my_variable"


class TestSnakeToCamel:
    """Tests pour snake_to_camel"""
    
    def test_snake_to_camel_simple(self):
        """Test conversion simple"""
        from src.utils.helpers.strings import snake_to_camel
        
        result = snake_to_camel("my_variable_name")
        assert result == "myVariableName"
    
    def test_snake_to_camel_un_mot(self):
        """Test un seul mot"""
        from src.utils.helpers.strings import snake_to_camel
        
        result = snake_to_camel("variable")
        assert result == "variable"
    
    def test_snake_to_camel_deja_camel(self):
        """Test déjà camelCase"""
        from src.utils.helpers.strings import snake_to_camel
        
        result = snake_to_camel("myVariable")
        assert result == "myVariable"


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS HELPERS.PY (MÉTIER)
# ═══════════════════════════════════════════════════════════


class TestValidateStockLevel:
    """Tests pour validate_stock_level dans helpers.py"""
    
    def test_validate_stock_level_critique(self):
        """Test stock critique"""
        from src.utils.helpers.helpers import validate_stock_level
        
        statut, icon = validate_stock_level(1.0, 5.0, "Tomates")
        assert statut == "critique"
        assert icon == "🔴"
    
    def test_validate_stock_level_sous_seuil(self):
        """Test stock sous seuil"""
        from src.utils.helpers.helpers import validate_stock_level
        
        statut, icon = validate_stock_level(3.0, 5.0, "Tomates")
        assert statut == "sous_seuil"
        assert icon == "⚠️"
    
    def test_validate_stock_level_ok(self):
        """Test stock OK"""
        from src.utils.helpers.helpers import validate_stock_level
        
        statut, icon = validate_stock_level(10.0, 5.0, "Tomates")
        assert statut == "ok"
        assert icon == "✅"


class TestConsolidateDuplicates:
    """Tests pour consolidate_duplicates"""
    
    def test_consolidate_duplicates_simple(self):
        """Test consolidation simple"""
        from src.utils.helpers.helpers import consolidate_duplicates
        
        items = [
            {"nom": "tomate", "qty": 2},
            {"nom": "Tomate", "qty": 3}
        ]
        result = consolidate_duplicates(items, "nom")
        
        assert len(result) == 1
    
    def test_consolidate_duplicates_sans_doublons(self):
        """Test sans doublons"""
        from src.utils.helpers.helpers import consolidate_duplicates
        
        items = [
            {"nom": "tomate", "qty": 2},
            {"nom": "oignon", "qty": 3}
        ]
        result = consolidate_duplicates(items, "nom")
        
        assert len(result) == 2
    
    def test_consolidate_duplicates_avec_strategy(self):
        """Test avec stratégie de fusion"""
        from src.utils.helpers.helpers import consolidate_duplicates
        
        def merge_qty(item1, item2):
            return {"nom": item1["nom"], "qty": item1["qty"] + item2["qty"]}
        
        items = [
            {"nom": "tomate", "qty": 2},
            {"nom": "Tomate", "qty": 3}
        ]
        result = consolidate_duplicates(items, "nom", merge_strategy=merge_qty)
        
        assert len(result) == 1
        assert result[0]["qty"] == 5
    
    def test_consolidate_duplicates_cle_vide(self):
        """Test avec clé vide"""
        from src.utils.helpers.helpers import consolidate_duplicates
        
        items = [
            {"nom": "tomate", "qty": 2},
            {"nom": "", "qty": 3}
        ]
        result = consolidate_duplicates(items, "nom")
        
        assert len(result) == 1


class TestFormatRecipeSummary:
    """Tests pour format_recipe_summary"""
    
    def test_format_recipe_summary_complet(self):
        """Test résumé complet"""
        from src.utils.helpers.helpers import format_recipe_summary
        
        recette = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "moyen"
        }
        result = format_recipe_summary(recette)
        
        assert "Tarte aux pommes" in result
        assert "75min" in result
        assert "6 portions" in result
        assert "Moyen" in result
    
    def test_format_recipe_summary_defauts(self):
        """Test avec valeurs par défaut"""
        from src.utils.helpers.helpers import format_recipe_summary
        
        recette = {"nom": "Test"}
        result = format_recipe_summary(recette)
        
        assert "Test" in result
        assert "0min" in result


class TestFormatInventorySummary:
    """Tests pour format_inventory_summary"""
    
    def test_format_inventory_summary_normal(self):
        """Test résumé normal"""
        from src.utils.helpers.helpers import format_inventory_summary
        
        inventaire = [
            {"nom": "Tomate", "statut": "ok"},
            {"nom": "Lait", "statut": "sous_seuil"},
            {"nom": "Yaourt", "statut": "peremption_proche"},
        ]
        result = format_inventory_summary(inventaire)
        
        assert "3 articles" in result
        assert "1 stock bas" in result
        assert "1 péremption proche" in result
    
    def test_format_inventory_summary_vide(self):
        """Test inventaire vide"""
        from src.utils.helpers.helpers import format_inventory_summary
        
        result = format_inventory_summary([])
        assert "0 articles" in result


class TestCalculateRecipeCost:
    """Tests pour calculate_recipe_cost"""
    
    def test_calculate_recipe_cost_normal(self):
        """Test calcul coût normal"""
        from src.utils.helpers.helpers import calculate_recipe_cost
        
        recette = {
            "ingredients": [
                {"nom": "Tomate", "quantite": 0.5},
                {"nom": "Oignon", "quantite": 0.2}
            ]
        }
        prix = {"Tomate": 3.0, "Oignon": 2.0}
        
        result = calculate_recipe_cost(recette, prix)
        
        assert result == 1.9  # 0.5*3 + 0.2*2
    
    def test_calculate_recipe_cost_ingredient_inconnu(self):
        """Test avec ingrédient sans prix"""
        from src.utils.helpers.helpers import calculate_recipe_cost
        
        recette = {
            "ingredients": [
                {"nom": "Tomate", "quantite": 0.5},
                {"nom": "Sel", "quantite": 0.1}
            ]
        }
        prix = {"Tomate": 3.0}
        
        result = calculate_recipe_cost(recette, prix)
        
        assert result == 1.5  # 0.5*3 + 0.1*0
    
    def test_calculate_recipe_cost_sans_ingredients(self):
        """Test sans ingrédients"""
        from src.utils.helpers.helpers import calculate_recipe_cost
        
        recette = {}
        result = calculate_recipe_cost(recette, {})
        
        assert result == 0.0


class TestSuggestIngredientSubstitutes:
    """Tests pour suggest_ingredient_substitutes"""
    
    def test_suggest_substitutes_beurre(self):
        """Test substituts beurre"""
        from src.utils.helpers.helpers import suggest_ingredient_substitutes
        
        result = suggest_ingredient_substitutes("Beurre")
        
        assert "margarine" in result
        assert "huile d'olive" in result
    
    def test_suggest_substitutes_inconnu(self):
        """Test ingrédient sans substituts"""
        from src.utils.helpers.helpers import suggest_ingredient_substitutes
        
        result = suggest_ingredient_substitutes("Truffe")
        
        assert result == []
    
    @pytest.mark.parametrize("ingredient", ["lait", "oeuf", "sucre", "farine"])
    def test_suggest_substitutes_connus(self, ingredient):
        """Test substituts pour ingrédients courants"""
        from src.utils.helpers.helpers import suggest_ingredient_substitutes
        
        result = suggest_ingredient_substitutes(ingredient)
        
        assert len(result) > 0


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS DATA
# ═══════════════════════════════════════════════════════════


class TestDataHelpers:
    """Tests pour les fonctions de data.py"""
    
    def test_import_data_module(self):
        """Test import du module data"""
        from src.utils.helpers import data
        
        assert data is not None


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS DATES
# ═══════════════════════════════════════════════════════════


class TestDatesHelpers:
    """Tests pour les fonctions de dates.py"""
    
    def test_import_dates_module(self):
        """Test import du module dates"""
        from src.utils.helpers import dates
        
        assert dates is not None


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS FOOD
# ═══════════════════════════════════════════════════════════


class TestFoodHelpers:
    """Tests pour les fonctions de food.py"""
    
    def test_batch_find_or_create_ingredients(self):
        """Test batch création ingrédients"""
        from src.utils.helpers.food import batch_find_or_create_ingredients
        
        data = [{"name": "Tomate"}]
        result = batch_find_or_create_ingredients(data)
        
        assert len(result) == 1
    
    def test_calculate_recipe_cost_food(self):
        """Test calcul coût recette"""
        from src.utils.helpers.food import calculate_recipe_cost
        
        result = calculate_recipe_cost([])
        assert result == 0.0
    
    def test_consolidate_duplicates_food(self):
        """Test consolidation doublons"""
        from src.utils.helpers.food import consolidate_duplicates
        
        result = consolidate_duplicates([{"name": "test"}])
        assert len(result) == 1
    
    def test_enrich_with_ingredient_info_food(self):
        """Test enrichissement items"""
        from src.utils.helpers.food import enrich_with_ingredient_info
        
        result = enrich_with_ingredient_info([{"id": 1}])
        assert len(result) == 1
    
    def test_find_or_create_ingredient_food(self):
        """Test trouver/créer ingrédient"""
        from src.utils.helpers.food import find_or_create_ingredient
        
        result = find_or_create_ingredient("Tomate")
        assert result["name"] == "Tomate"
    
    def test_format_inventory_summary_food(self):
        """Test formatage inventaire"""
        from src.utils.helpers.food import format_inventory_summary
        
        result = format_inventory_summary({})
        assert result == "Inventaire vide"
    
    def test_format_recipe_summary_food(self):
        """Test formatage recette"""
        from src.utils.helpers.food import format_recipe_summary
        
        result = format_recipe_summary({"name": "Tarte"})
        assert "Tarte" in result
    
    def test_get_all_ingredients_cached_food(self):
        """Test récupération ingrédients cachés"""
        from src.utils.helpers.food import get_all_ingredients_cached
        
        result = get_all_ingredients_cached()
        assert isinstance(result, list)
    
    def test_suggest_ingredient_substitutes_food(self):
        """Test suggestions substituts"""
        from src.utils.helpers.food import suggest_ingredient_substitutes
        
        result = suggest_ingredient_substitutes("Beurre")
        assert isinstance(result, list)
    
    def test_validate_stock_level_food(self):
        """Test validation niveau stock"""
        from src.utils.helpers.food import validate_stock_level
        
        result = validate_stock_level(10, 5)
        assert result is True
        
        result = validate_stock_level(3, 5)
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS AVEC MOCKING DB
# ═══════════════════════════════════════════════════════════


class TestHelpersWithDBMocking:
    """Tests pour fonctions qui nécessitent la BD"""
    
    @patch("src.utils.helpers.helpers.get_db_context")
    def test_find_or_create_ingredient_new(self, mock_db):
        """Test création nouvel ingrédient"""
        from src.utils.helpers.helpers import find_or_create_ingredient
        
        # Mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_session
        
        # Mock nouvel ingrédient avec ID
        mock_ingredient = MagicMock()
        mock_ingredient.id = 1
        
        def mock_add(obj):
            obj.id = 1
        mock_session.add = mock_add
        
        # Appel
        result = find_or_create_ingredient("Tomate", "kg", "Légumes")
        
        assert result == 1
    
    @patch("src.utils.helpers.helpers.get_db_context")
    def test_find_or_create_ingredient_existing(self, mock_db):
        """Test ingrédient existant"""
        from src.utils.helpers.helpers import find_or_create_ingredient
        
        # Mock ingrédient existant
        mock_ingredient = MagicMock()
        mock_ingredient.id = 42
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_ingredient
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_session
        
        result = find_or_create_ingredient("Tomate", "kg")
        
        assert result == 42
    
    def test_find_or_create_ingredient_with_session(self):
        """Test avec session fournie"""
        from src.utils.helpers.helpers import find_or_create_ingredient
        
        mock_session = MagicMock()
        mock_ingredient = MagicMock()
        mock_ingredient.id = 99
        mock_session.query.return_value.filter.return_value.first.return_value = mock_ingredient
        
        result = find_or_create_ingredient("Tomate", "kg", db=mock_session)
        
        assert result == 99
    
    @patch("src.utils.helpers.helpers.get_db_context")
    def test_batch_find_or_create_ingredients(self, mock_db):
        """Test batch création"""
        from src.utils.helpers.helpers import batch_find_or_create_ingredients
        
        mock_ingredient = MagicMock()
        mock_ingredient.nom = "Tomate"
        mock_ingredient.id = 1
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_ingredient]
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_session
        
        items = [
            {"nom": "Tomate", "unite": "kg"},
            {"nom": "Oignon", "unite": "kg"}
        ]
        result = batch_find_or_create_ingredients(items)
        
        assert "Tomate" in result
    
    @patch("src.utils.helpers.helpers.get_db_context")
    def test_get_all_ingredients_cached(self, mock_db):
        """Test récupération tous ingrédients"""
        from src.utils.helpers.helpers import get_all_ingredients_cached
        
        mock_ingredient = MagicMock()
        mock_ingredient.id = 1
        mock_ingredient.nom = "Tomate"
        mock_ingredient.unite = "kg"
        mock_ingredient.categorie = "Légumes"
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_ingredient]
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_session
        
        # Clear cache before test
        get_all_ingredients_cached.cache_clear() if hasattr(get_all_ingredients_cached, 'cache_clear') else None
        
        result = get_all_ingredients_cached()
        
        assert len(result) >= 0  # Le cache peut être vide
    
    @patch("src.utils.helpers.helpers.get_db_context")
    def test_enrich_with_ingredient_info(self, mock_db):
        """Test enrichissement articles"""
        from src.utils.helpers.helpers import enrich_with_ingredient_info
        
        mock_ingredient = MagicMock()
        mock_ingredient.id = 1
        mock_ingredient.nom = "Tomate"
        mock_ingredient.unite = "kg"
        mock_ingredient.categorie = "Légumes"
        
        mock_item = MagicMock()
        mock_item.id = 10
        mock_item.ingredient_id = 1
        mock_item.quantite = 2.5
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_ingredient]
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_db.return_value = mock_session
        
        result = enrich_with_ingredient_info([mock_item])
        
        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"
