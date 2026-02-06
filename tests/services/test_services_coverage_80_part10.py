"""Tests PART 10 - Recipe Import Service."""
import pytest
from unittest.mock import MagicMock, patch


class TestImportedIngredient:
    def test_import_with_all_fields(self):
        from src.services.recipe_import import ImportedIngredient
        ing = ImportedIngredient(nom="farine", quantite=200.0, unite="g")
        assert ing.nom == "farine"
        assert ing.quantite == 200.0
        assert ing.unite == "g"
    
    def test_import_minimal(self):
        from src.services.recipe_import import ImportedIngredient
        ing = ImportedIngredient(nom="sel")
        assert ing.nom == "sel"
        assert ing.quantite is None
        assert ing.unite == ""


class TestImportedRecipe:
    def test_recipe_defaults(self):
        from src.services.recipe_import import ImportedRecipe
        recipe = ImportedRecipe(nom="Tarte aux pommes")
        assert recipe.nom == "Tarte aux pommes"
        assert recipe.temps_preparation == 0
        assert recipe.portions == 4
    
    def test_recipe_min_length_nom(self):
        from src.services.recipe_import import ImportedRecipe
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ImportedRecipe(nom="ab")


class TestImportResult:
    def test_result_success(self):
        from src.services.recipe_import import ImportResult, ImportedRecipe
        recipe = ImportedRecipe(nom="Test recette")
        result = ImportResult(success=True, message="OK", recipe=recipe)
        assert result.success is True
        assert result.recipe.nom == "Test recette"
    
    def test_result_defaults(self):
        from src.services.recipe_import import ImportResult
        result = ImportResult()
        assert result.success is False
        assert result.recipe is None


class TestRecipeParserCleanText:
    def test_clean_text_normal(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("  Hello   World  ") == "Hello World"
    
    def test_clean_text_none(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text(None) == ""
    
    def test_clean_text_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("") == ""


class TestRecipeParserParseDuration:
    def test_parse_duration_hours(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("2h") == 120
        assert RecipeParser.parse_duration("1h") == 60
    
    def test_parse_duration_minutes(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("30 min") == 30
        assert RecipeParser.parse_duration("45 minutes") == 45
    
    def test_parse_duration_just_number(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("30") == 30
    
    def test_parse_duration_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("") == 0
        assert RecipeParser.parse_duration(None) == 0
    
    def test_parse_duration_combined(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("1h30min") == 90


class TestRecipeParserParsePortions:
    def test_parse_portions_normal(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("4 personnes") == 4
        assert RecipeParser.parse_portions("8") == 8
    
    def test_parse_portions_limits(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("0 portions") == 1
        assert RecipeParser.parse_portions("50 personnes") == 20
    
    def test_parse_portions_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("") == 4


class TestRecipeParserParseIngredient:
    def test_parse_ingredient_full(self):
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.parse_ingredient("200 g de farine")
        assert result.nom == "farine"
        assert result.quantite == 200.0
        assert result.unite == "g"
    
    def test_parse_ingredient_no_quantity(self):
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.parse_ingredient("sel")
        assert result.nom == "sel"
        assert result.quantite is None
    
    def test_parse_ingredient_empty(self):
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.parse_ingredient("")
        assert result.nom == ""


class TestMarmitonParserConfidence:
    def test_calculate_confidence_full(self):
        from src.services.recipe_import import MarmitonParser, ImportedRecipe, ImportedIngredient
        recipe = ImportedRecipe(
            nom="Recette complete",
            temps_preparation=30,
            image_url="https://example.com/img.jpg",
            ingredients=[ImportedIngredient(nom="farine", quantite=200, unite="g")],
            etapes=["Etape 1", "Etape 2"]
        )
        score = MarmitonParser._calculate_confidence(recipe)
        assert score > 0.5
    
    def test_calculate_confidence_empty(self):
        from src.services.recipe_import import MarmitonParser, ImportedRecipe
        recipe = ImportedRecipe(nom="Rec")
        assert MarmitonParser._calculate_confidence(recipe) == 0.0


class TestGenericRecipeParserConfidence:
    def test_calculate_confidence_minimal(self):
        from src.services.recipe_import import GenericRecipeParser, ImportedRecipe
        recipe = ImportedRecipe(nom="Test")
        assert GenericRecipeParser._calculate_confidence(recipe) == 0.2


class TestRecipeImportService:
    def test_init(self):
        with patch('src.services.recipe_import.ClientIA') as mock:
            mock.return_value = MagicMock()
            from src.services.recipe_import import RecipeImportService
            service = RecipeImportService()
            assert service.http_client is not None
    
    def test_get_parser_for_url_marmiton(self):
        with patch('src.services.recipe_import.ClientIA'):
            from src.services.recipe_import import RecipeImportService, MarmitonParser
            service = RecipeImportService()
            parser = service._get_parser_for_url("https://www.marmiton.org/test")
            assert parser == MarmitonParser
    
    def test_get_parser_for_url_generic(self):
        with patch('src.services.recipe_import.ClientIA'):
            from src.services.recipe_import import RecipeImportService, GenericRecipeParser
            service = RecipeImportService()
            parser = service._get_parser_for_url("https://unknown.com/test")
            assert parser == GenericRecipeParser
    
    def test_import_from_url_invalid_scheme(self):
        with patch('src.services.recipe_import.ClientIA'):
            from src.services.recipe_import import RecipeImportService
            service = RecipeImportService()
            result = service.import_from_url("ftp://example.com/recipe")
            assert result.success is False
            assert "invalide" in result.message.lower()
    
    def test_import_from_url_http_error(self):
        with patch('src.services.recipe_import.ClientIA'):
            from src.services.recipe_import import RecipeImportService
            import httpx
            service = RecipeImportService()
            mock_request = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 404
            error = httpx.HTTPStatusError("Not found", request=mock_request, response=mock_response)
            service.http_client.get = MagicMock(side_effect=error)
            result = service.import_from_url("https://example.com/missing")
            assert result.success is False
            assert "404" in result.message
    
    def test_import_batch(self):
        with patch('src.services.recipe_import.ClientIA'):
            from src.services.recipe_import import RecipeImportService, ImportResult
            service = RecipeImportService()
            mock_results = [ImportResult(success=True), ImportResult(success=False)]
            idx = 0
            def mock_import(url):
                nonlocal idx
                r = mock_results[idx]
                idx += 1
                return r
            service.import_from_url = mock_import
            results = service.import_batch(["u1", "u2"])
            assert len(results) == 2


class TestRecipeImportFactory:
    def test_get_recipe_import_service(self):
        with patch('src.services.recipe_import.ClientIA'):
            import src.services.recipe_import as module
            module._import_service = None
            from src.services.recipe_import import get_recipe_import_service
            service = get_recipe_import_service()
            assert service is not None
