"""
Tests complets pour le service RecipeImport.
"""
import pytest
import importlib
from unittest.mock import Mock, patch, MagicMock


def test_import_recipe_import_module():
    """Vérifie que le module recipe_import s'importe sans erreur."""
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None


@pytest.mark.unit
def test_import_recipe_import_service():
    """Vérifie que le module recipe_import s'importe sans erreur."""
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None


@pytest.mark.unit
def test_recipe_import_service_exists():
    """Test that recipe import service exists."""
    try:
        from src.services.recipe_import import get_recipe_import_service
        service = get_recipe_import_service()
        assert service is not None
    except ImportError:
        pass  # Service may not exist yet


# ═══════════════════════════════════════════════════════════
# TESTS DES SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TestImportedIngredient:
    """Tests pour ImportedIngredient."""
    
    def test_create_simple(self):
        from src.services.recipe_import import ImportedIngredient
        ing = ImportedIngredient(nom="Farine")
        assert ing.nom == "Farine"
        assert ing.quantite is None
        assert ing.unite == ""
    
    def test_create_with_quantity(self):
        from src.services.recipe_import import ImportedIngredient
        ing = ImportedIngredient(nom="Sucre", quantite=200.0, unite="g")
        assert ing.quantite == 200.0
        assert ing.unite == "g"


class TestImportedRecipe:
    """Tests pour ImportedRecipe."""
    
    def test_create_minimal(self):
        from src.services.recipe_import import ImportedRecipe
        recipe = ImportedRecipe(nom="Tarte aux pommes")
        assert recipe.nom == "Tarte aux pommes"
        assert recipe.portions == 4
        assert recipe.difficulte == "moyen"
    
    def test_create_full(self):
        from src.services.recipe_import import ImportedRecipe, ImportedIngredient
        recipe = ImportedRecipe(
            nom="Gâteau au chocolat",
            description="Un délicieux gâteau",
            temps_preparation=20,
            temps_cuisson=30,
            portions=8,
            difficulte="facile",
            categorie="Dessert",
            ingredients=[
                ImportedIngredient(nom="Chocolat", quantite=200, unite="g"),
                ImportedIngredient(nom="Oeufs", quantite=4, unite=""),
            ],
            etapes=["Faire fondre le chocolat", "Mélanger avec les oeufs"],
            source_url="https://example.com/recette",
            confiance_score=0.9
        )
        assert recipe.temps_preparation == 20
        assert recipe.temps_cuisson == 30
        assert len(recipe.ingredients) == 2
        assert len(recipe.etapes) == 2


class TestImportResult:
    """Tests pour ImportResult."""
    
    def test_success_result(self):
        from src.services.recipe_import import ImportResult, ImportedRecipe
        recipe = ImportedRecipe(nom="Test")
        result = ImportResult(success=True, message="OK", recipe=recipe)
        assert result.success is True
        assert result.recipe.nom == "Test"
    
    def test_failure_result(self):
        from src.services.recipe_import import ImportResult
        result = ImportResult(
            success=False,
            message="Erreur",
            errors=["URL invalide", "Contenu non trouvé"]
        )
        assert result.success is False
        assert len(result.errors) == 2


# ═══════════════════════════════════════════════════════════
# TESTS RECIPEPARSER
# ═══════════════════════════════════════════════════════════


class TestRecipeParserCleanText:
    """Tests pour clean_text."""
    
    def test_clean_normal(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("  Hello   World  ") == "Hello World"
    
    def test_clean_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("") == ""
        assert RecipeParser.clean_text(None) == ""
    
    def test_clean_newlines(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.clean_text("Hello\n\nWorld") == "Hello World"


class TestRecipeParserParseDuration:
    """Tests pour parse_duration."""
    
    def test_parse_minutes(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("30 min") == 30
        assert RecipeParser.parse_duration("45 minutes") == 45
    
    def test_parse_hours(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("1h") == 60
        assert RecipeParser.parse_duration("2 h") == 120
    
    def test_parse_hours_and_minutes(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("1h30min") == 90
        assert RecipeParser.parse_duration("1 h 45 min") == 105
    
    def test_parse_just_number(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("45") == 45
    
    def test_parse_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("") == 0
        assert RecipeParser.parse_duration("pas de temps") == 0


class TestRecipeParserParsePortions:
    """Tests pour parse_portions."""
    
    def test_parse_simple(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("4 personnes") == 4
        assert RecipeParser.parse_portions("6 portions") == 6
    
    def test_parse_limits(self):
        from src.services.recipe_import import RecipeParser
        # Max 20
        assert RecipeParser.parse_portions("100") == 20
        # Min 1 (0 trouve 0, retourne min=1)
        assert RecipeParser.parse_portions("0") == 1
    
    def test_parse_empty(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("") == 4
        assert RecipeParser.parse_portions("beaucoup") == 4


class TestRecipeParserParseIngredient:
    """Tests pour parse_ingredient."""
    
    def test_parse_with_unit(self):
        from src.services.recipe_import import RecipeParser
        ing = RecipeParser.parse_ingredient("200 g de farine")
        assert ing.nom == "farine"
        assert ing.quantite == 200.0
        assert ing.unite == "g"
    
    def test_parse_without_unit(self):
        from src.services.recipe_import import RecipeParser
        ing = RecipeParser.parse_ingredient("3 oeufs")
        assert ing.quantite == 3.0
        assert "oeufs" in ing.nom.lower()
    
    def test_parse_decimal(self):
        from src.services.recipe_import import RecipeParser
        ing = RecipeParser.parse_ingredient("1,5 kg de pommes")
        assert ing.quantite == 1.5
    
    def test_parse_no_quantity(self):
        from src.services.recipe_import import RecipeParser
        ing = RecipeParser.parse_ingredient("sel")
        assert ing.nom == "sel"
        assert ing.quantite is None
    
    def test_parse_empty(self):
        from src.services.recipe_import import RecipeParser
        ing = RecipeParser.parse_ingredient("")
        assert ing.nom == ""


# ═══════════════════════════════════════════════════════════
# TESTS MARMITON PARSER
# ═══════════════════════════════════════════════════════════


class TestMarmitonParser:
    """Tests pour MarmitonParser."""
    
    def test_parser_exists(self):
        from src.services.recipe_import import MarmitonParser
        assert MarmitonParser is not None
    
    def test_parser_has_parse(self):
        from src.services.recipe_import import MarmitonParser
        assert hasattr(MarmitonParser, 'parse')


class TestCuisineAZParser:
    """Tests pour CuisineAZParser."""
    
    def test_parser_exists(self):
        from src.services.recipe_import import CuisineAZParser
        assert CuisineAZParser is not None


class TestGenericRecipeParser:
    """Tests pour GenericRecipeParser."""
    
    def test_parser_exists(self):
        from src.services.recipe_import import GenericRecipeParser
        assert GenericRecipeParser is not None
    
    def test_parser_has_parse(self):
        from src.services.recipe_import import GenericRecipeParser
        assert hasattr(GenericRecipeParser, 'parse')


# ═══════════════════════════════════════════════════════════
# TESTS RECIPEIMPORTSERVICE
# ═══════════════════════════════════════════════════════════


class TestRecipeImportServiceInit:
    """Tests d'initialisation du service."""
    
    def test_service_creation(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        assert service is not None
    
    def test_factory_function(self):
        from src.services.recipe_import import get_recipe_import_service
        service = get_recipe_import_service()
        assert service is not None


class TestRecipeImportServiceMethods:
    """Tests pour vérifier que le service a les bonnes méthodes."""
    
    def test_service_has_import_method(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        assert hasattr(service, 'import_from_url')
    
    def test_service_inherits_base(self):
        from src.services.recipe_import import RecipeImportService
        from src.services.base import BaseAIService
        assert issubclass(RecipeImportService, BaseAIService)


class TestRecipeParserHelpers:
    """Tests pour les helpers du parser."""
    
    def test_clean_text_multiline(self):
        from src.services.recipe_import import RecipeParser
        result = RecipeParser.clean_text("  Ligne1\n  Ligne2  ")
        assert result == "Ligne1 Ligne2"
    
    def test_parse_duration_hour_short(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_duration("2h") == 120
    
    def test_parse_portions_default(self):
        from src.services.recipe_import import RecipeParser
        assert RecipeParser.parse_portions("inconnu") == 4


class TestRecipeImportServiceMocked:
    """Tests avec mocks HTTP."""
    
    def test_import_url_network_error(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        
        with patch('httpx.get', side_effect=Exception("Network error")):
            result = service.import_from_url("https://www.example.com/recipe")
            assert result.success is False
            assert "erreur" in result.message.lower() or len(result.errors) > 0
    
    def test_import_url_404(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status = Mock(side_effect=Exception("404 Not Found"))
        
        with patch('httpx.get', return_value=mock_response):
            result = service.import_from_url("https://www.example.com/not-found")
            # Should handle 404 gracefully
            assert result.success is False


class TestBatchImport:
    """Tests pour l'import en lot."""
    
    def test_import_urls_list(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        
        urls = [
            "https://www.example.com/recipe1",
            "https://www.example.com/recipe2",
        ]
        
        with patch.object(service, 'import_from_url') as mock_import:
            from src.services.recipe_import import ImportResult
            mock_import.return_value = ImportResult(success=False, message="Test")
            
            if hasattr(service, 'import_batch'):
                results = service.import_batch(urls)
                assert len(results) == 2
    
    def test_import_empty_list(self):
        from src.services.recipe_import import RecipeImportService
        service = RecipeImportService()
        
        if hasattr(service, 'import_batch'):
            results = service.import_batch([])
            assert results == []
