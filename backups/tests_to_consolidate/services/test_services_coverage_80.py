"""
Tests exhaustifs pour amÃ©liorer la couverture des services Ã  80%+

Fichiers ciblÃ©s (faible couverture):
- io_service.py (15.13%)
- types.py (9.59%) 
- openfoodfacts.py
- recipe_import.py (10.53%)
- rapports_pdf.py (15.54%)
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
import json


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IOService (Pure static methods)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceFormatValue:
    """Tests pour IOService._format_value"""
    
    def test_format_value_none(self):
        """Test format None"""
        from src.services.io_service import IOService
        assert IOService._format_value(None) == ""
    
    def test_format_value_string(self):
        """Test format string"""
        from src.services.io_service import IOService
        assert IOService._format_value("Hello") == "Hello"
    
    def test_format_value_int(self):
        """Test format int"""
        from src.services.io_service import IOService
        assert IOService._format_value(42) == "42"
    
    def test_format_value_float(self):
        """Test format float"""
        from src.services.io_service import IOService
        assert IOService._format_value(3.14) == "3.14"
    
    def test_format_value_date(self):
        """Test format date"""
        from src.services.io_service import IOService
        d = date(2025, 1, 15)
        assert IOService._format_value(d) == "15/01/2025"
    
    def test_format_value_datetime(self):
        """Test format datetime"""
        from src.services.io_service import IOService
        dt = datetime(2025, 1, 15, 14, 30)
        assert IOService._format_value(dt) == "15/01/2025 14:30"
    
    def test_format_value_bool_true(self):
        """Test format bool True"""
        from src.services.io_service import IOService
        assert IOService._format_value(True) == "Oui"
    
    def test_format_value_bool_false(self):
        """Test format bool False"""
        from src.services.io_service import IOService
        assert IOService._format_value(False) == "Non"
    
    def test_format_value_list(self):
        """Test format list"""
        from src.services.io_service import IOService
        assert IOService._format_value(["a", "b", "c"]) == "a, b, c"
    
    def test_format_value_tuple(self):
        """Test format tuple"""
        from src.services.io_service import IOService
        assert IOService._format_value((1, 2, 3)) == "1, 2, 3"
    
    def test_format_value_empty_list(self):
        """Test format empty list"""
        from src.services.io_service import IOService
        assert IOService._format_value([]) == ""


class TestIOServiceParseValue:
    """Tests pour IOService._parse_value"""
    
    def test_parse_value_empty(self):
        """Test parse empty string"""
        from src.services.io_service import IOService
        assert IOService._parse_value("") is None
    
    def test_parse_value_whitespace(self):
        """Test parse whitespace"""
        from src.services.io_service import IOService
        assert IOService._parse_value("   ") is None
    
    def test_parse_value_oui(self):
        """Test parse 'Oui'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("Oui") is True
    
    def test_parse_value_yes(self):
        """Test parse 'yes'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("yes") is True
    
    def test_parse_value_true(self):
        """Test parse 'true'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("true") is True
    
    def test_parse_value_one(self):
        """Test parse '1' as bool"""
        from src.services.io_service import IOService
        # Note: '1' gets parsed as int first
        result = IOService._parse_value("1")
        assert result == 1  # Parsed as int
    
    def test_parse_value_non(self):
        """Test parse 'Non'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("Non") is False
    
    def test_parse_value_no(self):
        """Test parse 'no'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("no") is False
    
    def test_parse_value_false(self):
        """Test parse 'false'"""
        from src.services.io_service import IOService
        assert IOService._parse_value("false") is False
    
    def test_parse_value_zero(self):
        """Test parse '0'"""
        from src.services.io_service import IOService
        result = IOService._parse_value("0")
        assert result == 0  # Parsed as int
    
    def test_parse_value_integer(self):
        """Test parse integer string"""
        from src.services.io_service import IOService
        assert IOService._parse_value("42") == 42
    
    def test_parse_value_float_dot(self):
        """Test parse float with dot"""
        from src.services.io_service import IOService
        assert IOService._parse_value("3.14") == 3.14
    
    def test_parse_value_float_comma(self):
        """Test parse float with comma (French format)"""
        from src.services.io_service import IOService
        assert IOService._parse_value("3,14") == 3.14
    
    def test_parse_value_date_fr(self):
        """Test parse French date format"""
        from src.services.io_service import IOService
        result = IOService._parse_value("15/01/2025")
        assert result == date(2025, 1, 15)
    
    def test_parse_value_date_iso(self):
        """Test parse ISO date format"""
        from src.services.io_service import IOService
        result = IOService._parse_value("2025-01-15")
        assert result == date(2025, 1, 15)
    
    def test_parse_value_date_dashes(self):
        """Test parse date with dashes (FR)"""
        from src.services.io_service import IOService
        result = IOService._parse_value("15-01-2025")
        assert result == date(2025, 1, 15)
    
    def test_parse_value_string(self):
        """Test parse regular string"""
        from src.services.io_service import IOService
        assert IOService._parse_value("Hello World") == "Hello World"


class TestIOServiceCSV:
    """Tests pour IOService CSV import/export"""
    
    def test_to_csv_empty(self):
        """Test to_csv with empty list"""
        from src.services.io_service import IOService
        result = IOService.to_csv([], {"nom": "Nom"})
        assert result == ""
    
    def test_to_csv_single_item(self):
        """Test to_csv with single item"""
        from src.services.io_service import IOService
        items = [{"nom": "Pomme", "quantite": 5}]
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        result = IOService.to_csv(items, mapping)
        assert "Nom" in result
        assert "QuantitÃ©" in result
        assert "Pomme" in result
        assert "5" in result
    
    def test_to_csv_multiple_items(self):
        """Test to_csv with multiple items"""
        from src.services.io_service import IOService
        items = [
            {"nom": "Pomme", "categorie": "Fruits"},
            {"nom": "Carotte", "categorie": "LÃ©gumes"},
        ]
        mapping = {"nom": "Nom", "categorie": "CatÃ©gorie"}
        result = IOService.to_csv(items, mapping)
        lines = result.strip().split("\n")
        assert len(lines) == 3  # Header + 2 items
    
    def test_to_csv_with_special_values(self):
        """Test to_csv with None, date, bool"""
        from src.services.io_service import IOService
        items = [{"nom": "Test", "date": date(2025, 1, 1), "actif": True}]
        mapping = {"nom": "Nom", "date": "Date", "actif": "Actif"}
        result = IOService.to_csv(items, mapping)
        assert "01/01/2025" in result
        assert "Oui" in result
    
    def test_from_csv_valid(self):
        """Test from_csv with valid data"""
        from src.services.io_service import IOService
        csv_str = "Nom,QuantitÃ©\nPomme,5\nOrange,3"
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        items, errors = IOService.from_csv(csv_str, mapping, ["nom"])
        assert len(items) == 2
        assert len(errors) == 0
        assert items[0]["nom"] == "Pomme"
        assert items[0]["quantite"] == 5
    
    def test_from_csv_missing_required(self):
        """Test from_csv with missing required field"""
        from src.services.io_service import IOService
        csv_str = "Nom,QuantitÃ©\n,5\nOrange,3"
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        items, errors = IOService.from_csv(csv_str, mapping, ["nom"])
        assert len(items) == 1  # Only Orange
        assert len(errors) == 1
        assert "Champs manquants" in errors[0]
    
    def test_from_csv_extra_columns(self):
        """Test from_csv ignores extra columns"""
        from src.services.io_service import IOService
        csv_str = "Nom,Extra,QuantitÃ©\nPomme,ignored,5"
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        items, errors = IOService.from_csv(csv_str, mapping, ["nom"])
        assert len(items) == 1
        assert "extra" not in items[0]


class TestIOServiceJSON:
    """Tests pour IOService JSON import/export"""
    
    def test_to_json_empty(self):
        """Test to_json with empty list"""
        from src.services.io_service import IOService
        result = IOService.to_json([])
        assert result == "[]"
    
    def test_to_json_single(self):
        """Test to_json with single item"""
        from src.services.io_service import IOService
        items = [{"nom": "Pomme", "quantite": 5}]
        result = IOService.to_json(items)
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["nom"] == "Pomme"
    
    def test_to_json_indent(self):
        """Test to_json with custom indent"""
        from src.services.io_service import IOService
        items = [{"nom": "Pomme"}]
        result = IOService.to_json(items, indent=4)
        assert "    " in result  # 4 spaces
    
    def test_from_json_valid_array(self):
        """Test from_json with valid array"""
        from src.services.io_service import IOService
        json_str = '[{"nom": "Pomme", "quantite": 5}]'
        items, errors = IOService.from_json(json_str, ["nom"])
        assert len(items) == 1
        assert len(errors) == 0
    
    def test_from_json_single_object(self):
        """Test from_json with single object (auto-wrapped)"""
        from src.services.io_service import IOService
        json_str = '{"nom": "Pomme", "quantite": 5}'
        items, errors = IOService.from_json(json_str, ["nom"])
        assert len(items) == 1
    
    def test_from_json_invalid(self):
        """Test from_json with invalid JSON"""
        from src.services.io_service import IOService
        json_str = '{invalid json}'
        items, errors = IOService.from_json(json_str, ["nom"])
        assert len(items) == 0
        assert len(errors) == 1
        assert "JSON invalide" in errors[0]
    
    def test_from_json_missing_required(self):
        """Test from_json with missing required field"""
        from src.services.io_service import IOService
        json_str = '[{"quantite": 5}, {"nom": "Pomme"}]'
        items, errors = IOService.from_json(json_str, ["nom"])
        assert len(items) == 1  # Only second item
        assert len(errors) == 1
        assert "Champs manquants" in errors[0]


class TestIOServiceFieldMappings:
    """Tests pour les templates de field mappings"""
    
    def test_recette_field_mapping(self):
        """Test RECETTE_FIELD_MAPPING exists"""
        from src.services.io_service import RECETTE_FIELD_MAPPING
        assert "nom" in RECETTE_FIELD_MAPPING
        assert "description" in RECETTE_FIELD_MAPPING
        assert RECETTE_FIELD_MAPPING["nom"] == "Nom"
    
    def test_inventaire_field_mapping(self):
        """Test INVENTAIRE_FIELD_MAPPING exists"""
        from src.services.io_service import INVENTAIRE_FIELD_MAPPING
        assert "nom" in INVENTAIRE_FIELD_MAPPING
        assert "categorie" in INVENTAIRE_FIELD_MAPPING
        assert "quantite" in INVENTAIRE_FIELD_MAPPING
    
    def test_courses_field_mapping(self):
        """Test COURSES_FIELD_MAPPING exists"""
        from src.services.io_service import COURSES_FIELD_MAPPING
        assert "nom" in COURSES_FIELD_MAPPING
        assert "quantite" in COURSES_FIELD_MAPPING
        assert "priorite" in COURSES_FIELD_MAPPING


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OpenFoodFacts Service (Dataclasses + parsing)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNutritionInfoDataclass:
    """Tests pour la dataclass NutritionInfo"""
    
    def test_nutrition_info_default(self):
        """Test default values"""
        from src.services.openfoodfacts import NutritionInfo
        info = NutritionInfo()
        assert info.energie_kcal is None
        assert info.proteines_g is None
        assert info.nutriscore is None
    
    def test_nutrition_info_with_values(self):
        """Test with actual values"""
        from src.services.openfoodfacts import NutritionInfo
        info = NutritionInfo(
            energie_kcal=250.0,
            proteines_g=10.5,
            glucides_g=30.0,
            lipides_g=8.0,
            nutriscore="B",
            nova_group=3
        )
        assert info.energie_kcal == 250.0
        assert info.nutriscore == "B"
        assert info.nova_group == 3


class TestProduitOpenFoodFactsDataclass:
    """Tests pour la dataclass ProduitOpenFoodFacts"""
    
    def test_produit_minimal(self):
        """Test with minimal required fields"""
        from src.services.openfoodfacts import ProduitOpenFoodFacts
        produit = ProduitOpenFoodFacts(
            code_barres="3017620422003",
            nom="Nutella"
        )
        assert produit.code_barres == "3017620422003"
        assert produit.nom == "Nutella"
        assert produit.marque is None
        assert produit.categories == []
    
    def test_produit_full(self):
        """Test with all fields"""
        from src.services.openfoodfacts import ProduitOpenFoodFacts, NutritionInfo
        nutrition = NutritionInfo(energie_kcal=539.0, nutriscore="E")
        produit = ProduitOpenFoodFacts(
            code_barres="3017620422003",
            nom="Nutella",
            marque="Ferrero",
            quantite="400g",
            categories=["PÃ¢tes Ã  tartiner", "Chocolat"],
            nutrition=nutrition,
            labels=["Sans huile de palme"],
            confiance=0.95
        )
        assert produit.marque == "Ferrero"
        assert produit.nutrition.nutriscore == "E"
        assert len(produit.categories) == 2
        assert produit.confiance == 0.95


class TestOpenFoodFactsServiceInit:
    """Tests pour OpenFoodFactsService initialization"""
    
    def test_service_init(self):
        """Test service instantiation"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        assert service.timeout == 10.0
        assert "AssistantMatanne" in service.user_agent


class TestOpenFoodFactsServiceParser:
    """Tests pour OpenFoodFactsService._parser_produit"""
    
    def test_parser_produit_minimal(self):
        """Test parsing minimal product data"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        
        data = {
            "product_name_fr": "Pain de mie",
            "brands": "Harry's"
        }
        result = service._parser_produit("123456789", data)
        
        assert result.nom == "Pain de mie"
        assert result.marque == "Harry's"
        assert result.code_barres == "123456789"
    
    def test_parser_produit_fallback_name(self):
        """Test parsing with fallback product name"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        
        data = {
            "product_name": "Bread",
            "generic_name_fr": "Pain"
        }
        result = service._parser_produit("123", data)
        assert result.nom == "Bread"  # product_name takes precedence
    
    def test_parser_produit_unknown_name(self):
        """Test parsing with no name"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        
        data = {}
        result = service._parser_produit("123", data)
        assert result.nom == "Produit inconnu"
    
    def test_parser_produit_with_nutrition(self):
        """Test parsing with nutrition data"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        
        data = {
            "product_name_fr": "Yaourt",
            "nutriments": {
                "energy-kcal_100g": 85.0,
                "proteins_100g": 4.0,
                "carbohydrates_100g": 12.0,
                "sugars_100g": 10.0,
                "fat_100g": 2.0,
                "salt_100g": 0.1
            },
            "nutriscore_grade": "a",
            "nova_group": 1
        }
        result = service._parser_produit("123", data)
        
        assert result.nutrition.energie_kcal == 85.0
        assert result.nutrition.proteines_g == 4.0
        assert result.nutrition.nutriscore == "A"
        assert result.nutrition.nova_group == 1
    
    def test_parser_produit_with_categories(self):
        """Test parsing with categories"""
        from src.services.openfoodfacts import OpenFoodFactsService
        service = OpenFoodFactsService()
        
        data = {
            "product_name_fr": "Jus d'orange",
            "categories_tags_fr": ["en:beverages", "fr:jus-de-fruits"]
        }
        result = service._parser_produit("123", data)
        
        assert len(result.categories) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RecipeImport (Pure methods)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRecipeParserCleanText:
    """Tests pour RecipeParser.clean_text"""
    
    def test_clean_text_none(self):
        """Test clean_text avec None"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text(None) == ""
    
    def test_clean_text_empty(self):
        """Test clean_text avec string vide"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("") == ""
    
    def test_clean_text_whitespace(self):
        """Test clean_text avec espaces multiples"""
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.clean_text("  hello   world  ")
        assert result == "hello world"
    
    def test_clean_text_newlines(self):
        """Test clean_text avec newlines"""
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.clean_text("hello\n\nworld")
        assert result == "hello world"


class TestRecipeParserParseDuration:
    """Tests pour RecipeParser.parse_duration"""
    
    def test_parse_duration_none(self):
        """Test parse_duration avec None"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration(None) == 0
    
    def test_parse_duration_empty(self):
        """Test parse_duration avec string vide"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("") == 0
    
    def test_parse_duration_minutes(self):
        """Test parse_duration avec minutes"""
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("30 min") == 30
        assert RecipeParser.parse_duration("15 minutes") == 15
    
    def test_parse_duration_hours(self):
        """Test parse_duration avec heures"""
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.parse_duration("2h")
        assert result == 120
    
    def test_parse_duration_hours_and_minutes(self):
        """Test parse_duration avec heures et minutes"""
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.parse_duration("1h 30min")
        assert result == 90


class TestImportedIngredient:
    """Tests pour le modÃ¨le ImportedIngredient"""
    
    def test_ingredient_minimal(self):
        """Test with minimal data"""
        from src.services.recipe_import import ImportedIngredient
        ingredient = ImportedIngredient(nom="Farine")
        assert ingredient.nom == "Farine"
        assert ingredient.quantite is None
        assert ingredient.unite == ""
    
    def test_ingredient_full(self):
        """Test with full data"""
        from src.services.recipe_import import ImportedIngredient
        ingredient = ImportedIngredient(
            nom="Farine",
            quantite=250.0,
            unite="g"
        )
        assert ingredient.quantite == 250.0
        assert ingredient.unite == "g"


class TestImportedRecipe:
    """Tests pour le modÃ¨le ImportedRecipe"""
    
    def test_recipe_minimal(self):
        """Test with minimal data"""
        from src.services.recipe_import import ImportedRecipe
        recipe = ImportedRecipe(nom="Tarte aux pommes")
        assert recipe.nom == "Tarte aux pommes"
        assert recipe.portions == 4
        assert recipe.difficulte == "moyen"
        assert recipe.ingredients == []
    
    def test_recipe_full(self):
        """Test with full data"""
        from src.services.recipe_import import ImportedRecipe, ImportedIngredient
        recipe = ImportedRecipe(
            nom="Tarte aux pommes",
            description="Une dÃ©licieuse tarte",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            difficulte="facile",
            categorie="Dessert",
            ingredients=[ImportedIngredient(nom="Pommes", quantite=4.0)],
            etapes=["Ã‰plucher les pommes", "Faire la pÃ¢te"],
            source_url="https://example.com/recette",
            confiance_score=0.85
        )
        assert recipe.temps_preparation == 30
        assert recipe.temps_cuisson == 45
        assert len(recipe.ingredients) == 1


class TestImportResult:
    """Tests pour le modÃ¨le ImportResult"""
    
    def test_import_result_default(self):
        """Test default values"""
        from src.services.recipe_import import ImportResult
        result = ImportResult()
        assert result.success is False
        assert result.message == ""
        assert result.recipe is None
        assert result.errors == []
    
    def test_import_result_success(self):
        """Test success result"""
        from src.services.recipe_import import ImportResult, ImportedRecipe
        recipe = ImportedRecipe(nom="Test")
        result = ImportResult(
            success=True,
            message="Import rÃ©ussi",
            recipe=recipe
        )
        assert result.success is True
        assert result.recipe is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS rapports_pdf Schemas
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRapportStocksSchema:
    """Tests pour RapportStocks schema"""
    
    def test_rapport_stocks_default(self):
        """Test default values"""
        from src.services.rapports_pdf import RapportStocks
        rapport = RapportStocks()
        assert rapport.periode_jours == 7
        assert rapport.articles_total == 0
        assert rapport.articles_faible_stock == []
    
    def test_rapport_stocks_custom(self):
        """Test with custom values"""
        from src.services.rapports_pdf import RapportStocks
        rapport = RapportStocks(
            periode_jours=30,
            articles_total=150,
            valeur_stock_total=1500.50
        )
        assert rapport.periode_jours == 30
        assert rapport.valeur_stock_total == 1500.50


class TestRapportBudgetSchema:
    """Tests pour RapportBudget schema"""
    
    def test_rapport_budget_default(self):
        """Test default values"""
        from src.services.rapports_pdf import RapportBudget
        rapport = RapportBudget()
        assert rapport.periode_jours == 30
        assert rapport.depenses_total == 0.0
    
    def test_rapport_budget_custom(self):
        """Test with custom values"""
        from src.services.rapports_pdf import RapportBudget
        rapport = RapportBudget(
            depenses_total=850.0,
            depenses_par_categorie={"Alimentation": 500.0, "HygiÃ¨ne": 150.0}
        )
        assert rapport.depenses_total == 850.0
        assert len(rapport.depenses_par_categorie) == 2


class TestAnalyseGaspillageSchema:
    """Tests pour AnalyseGaspillage schema"""
    
    def test_analyse_gaspillage_default(self):
        """Test default values"""
        from src.services.rapports_pdf import AnalyseGaspillage
        analyse = AnalyseGaspillage()
        assert analyse.periode_jours == 30
        assert analyse.articles_perimes_total == 0
        assert analyse.recommandations == []
    
    def test_analyse_gaspillage_custom(self):
        """Test with custom values"""
        from src.services.rapports_pdf import AnalyseGaspillage
        analyse = AnalyseGaspillage(
            articles_perimes_total=5,
            valeur_perdue=25.50,
            recommandations=["RÃ©duire les achats de fruits"]
        )
        assert analyse.articles_perimes_total == 5
        assert analyse.valeur_perdue == 25.50


class TestRapportPlanningSchema:
    """Tests pour RapportPlanning schema"""
    
    def test_rapport_planning_default(self):
        """Test default values"""
        from src.services.rapports_pdf import RapportPlanning
        rapport = RapportPlanning()
        assert rapport.planning_id == 0
        assert rapport.nom_planning == ""
        assert rapport.total_repas == 0
    
    def test_rapport_planning_custom(self):
        """Test with custom values"""
        from src.services.rapports_pdf import RapportPlanning
        rapport = RapportPlanning(
            planning_id=1,
            nom_planning="Semaine 1",
            total_repas=14
        )
        assert rapport.planning_id == 1
        assert rapport.nom_planning == "Semaine 1"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS types.py BaseService (avec mock DB)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBaseServiceInit:
    """Tests pour BaseService initialization"""
    
    def test_base_service_init(self):
        """Test BaseService initialization"""
        from src.services.types import BaseService
        
        # Create a mock model class
        class MockModel:
            __name__ = "MockModel"
            id = None
        
        service = BaseService(MockModel, cache_ttl=120)
        assert service.model == MockModel
        assert service.model_name == "MockModel"
        assert service.cache_ttl == 120


class TestBaseServiceHelpers:
    """Tests pour BaseService helper methods"""
    
    def test_invalider_cache(self):
        """Test _invalider_cache method"""
        from src.services.types import BaseService
        
        class MockModel:
            __name__ = "MockModel"
        
        service = BaseService(MockModel)
        # Should not raise
        service._invalider_cache()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS Constants et imports
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOpenFoodFactsConstants:
    """Tests pour les constantes OpenFoodFacts"""
    
    def test_api_url(self):
        """Test API URL exists"""
        from src.services.openfoodfacts import OPENFOODFACTS_API
        assert "openfoodfacts.org" in OPENFOODFACTS_API
    
    def test_search_url(self):
        """Test Search URL exists"""
        from src.services.openfoodfacts import OPENFOODFACTS_SEARCH
        assert "openfoodfacts.org" in OPENFOODFACTS_SEARCH
    
    def test_cache_ttl(self):
        """Test Cache TTL value"""
        from src.services.openfoodfacts import CACHE_TTL
        assert CACHE_TTL == 86400  # 24 hours


class TestServiceFactories:
    """Tests pour les factory functions"""
    
    def test_get_openfoodfacts_service(self):
        """Test get_openfoodfacts_service factory"""
        from src.services.openfoodfacts import get_openfoodfacts_service
        service1 = get_openfoodfacts_service()
        service2 = get_openfoodfacts_service()
        # Singleton pattern
        assert service1 is service2
