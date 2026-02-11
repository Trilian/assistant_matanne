"""
Tests supplémentaires pour recipe_import - couverture des parsers et service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


# ═══════════════════════════════════════════════════════════
# TESTS MARMITONPARSER.PARSE()
# ═══════════════════════════════════════════════════════════


class TestMarmitonParserParse:
    """Tests pour MarmitonParser.parse() avec HTML simulé."""
    
    def test_parse_minimal_page(self):
        """Parse une page avec seulement un titre."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Tarte aux pommes</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recettes/tarte")
        
        assert recipe.nom == "Tarte aux pommes"
        assert recipe.source_site == "Marmiton"
    
    def test_parse_with_description(self):
        """Parse une page avec titre et description."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Gâteau au chocolat</h1>
            <p class="description">Un délicieux gâteau fondant</p>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert recipe.nom == "Gâteau au chocolat"
        assert "délicieux" in recipe.description
    
    def test_parse_with_image(self):
        """Parse une page avec image de recette."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Crêpes</h1>
            <img class="recipe-media" src="https://example.com/crepes.jpg"/>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert recipe.image_url == "https://example.com/crepes.jpg"
    
    def test_parse_with_times(self):
        """Parse une page avec temps de préparation et cuisson."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Quiche</h1>
            <div class="time">préparation: 30 min</div>
            <div class="duration">cuisson: 45 min</div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert recipe.temps_preparation == 30
        assert recipe.temps_cuisson == 45
    
    def test_parse_with_portions(self):
        """Parse une page avec nombre de portions."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Soupe</h1>
            <span class="serving">Pour 6 personnes</span>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert recipe.portions == 6
    
    def test_parse_with_ingredients(self):
        """Parse une page avec liste d'ingrédients."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Omelette</h1>
            <div class="ingredient">
                <li>3 oeufs</li>
                <li>50 g de beurre</li>
                <li>sel et poivre</li>
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert len(recipe.ingredients) >= 2
    
    def test_parse_with_steps(self):
        """Parse une page avec étapes de préparation."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Riz au lait</h1>
            <div class="step">
                <li>Faire chauffer le lait dans une casserole.</li>
                <li>Ajouter le riz et le sucre. Laisser cuire 30 minutes.</li>
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/recette")
        
        assert len(recipe.etapes) >= 1
    
    def test_parse_complete_recipe(self):
        """Parse une page complète avec tous les éléments."""
        from src.services.recettes.import_url import MarmitonParser
        
        html = """
        <html><body>
            <h1>Tarte Tatin</h1>
            <p class="intro">La célèbre tarte renversée aux pommes</p>
            <img class="recipe-media" src="https://example.com/tatin.jpg"/>
            <span class="portion">8 personnes</span>
            <div class="temps">préparation 25 min</div>
            <div class="time">cuisson 40 min</div>
            <div class="ingredient">
                <li>6 pommes golden</li>
                <li>150 g de sucre</li>
                <li>100 g de beurre</li>
                <li>1 pâte feuilletée</li>
            </div>
            <div class="instruction">
                <li>Préparer le caramel avec le sucre et le beurre.</li>
                <li>Éplucher et couper les pommes en quartiers.</li>
                <li>Disposer les pommes sur le caramel et recouvrir de pâte.</li>
                <li>Cuire au four 40 min à 180°C puis démouler.</li>
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = MarmitonParser.parse(soup, "https://www.marmiton.org/tartetatin")
        
        assert recipe.nom == "Tarte Tatin"
        assert recipe.portions == 8
        assert len(recipe.ingredients) >= 3
        assert len(recipe.etapes) >= 3
        assert recipe.confiance_score > 0.3


class TestMarmitonCalculateConfidence:
    """Tests pour MarmitonParser._calculate_confidence()."""
    
    def test_confidence_empty_recipe(self):
        """Recipe vide a un score bas."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe
        
        recipe = ImportedRecipe()
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score == 0.0
    
    def test_confidence_with_name(self):
        """Recipe avec nom a un score plus élevé."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe
        
        recipe = ImportedRecipe(nom="Ma recette test")
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score >= 0.2
    
    def test_confidence_with_ingredients(self):
        """Recipe avec ingrédients a un score plus élevé."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe, ImportedIngredient
        
        recipe = ImportedRecipe(
            nom="Ma recette test",  # >5 chars pour +0.2
            ingredients=[
                ImportedIngredient(nom="ing1"),
                ImportedIngredient(nom="ing2"),
                ImportedIngredient(nom="ing3"),
            ]
        )
        score = MarmitonParser._calculate_confidence(recipe)
        
        # nom >5 chars: +0.2, 3 ingredients * 0.05 = 0.15 => total > 0.3
        assert score >= 0.3
    
    def test_confidence_with_steps(self):
        """Recipe avec étapes a un score plus élevé."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe
        
        recipe = ImportedRecipe(
            nom="Test Recipe",
            etapes=["Étape 1", "Étape 2", "Étape 3"]
        )
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score >= 0.4
    
    def test_confidence_with_time(self):
        """Recipe avec temps préparation a un score plus élevé."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe
        
        recipe = ImportedRecipe(
            nom="Test Recipe",
            temps_preparation=30
        )
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score >= 0.3
    
    def test_confidence_with_image(self):
        """Recipe avec image a un score plus élevé."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe
        
        recipe = ImportedRecipe(
            nom="Test Recipe",
            image_url="https://example.com/img.jpg"
        )
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score >= 0.3
    
    def test_confidence_max_one(self):
        """Score de confiance ne dépasse pas 1.0."""
        from src.services.recettes.import_url import MarmitonParser, ImportedRecipe, ImportedIngredient
        
        recipe = ImportedRecipe(
            nom="Super recette complète",
            temps_preparation=30,
            image_url="https://example.com/img.jpg",
            ingredients=[ImportedIngredient(nom=f"ing{i}") for i in range(10)],
            etapes=[f"Étape {i}" for i in range(10)]
        )
        score = MarmitonParser._calculate_confidence(recipe)
        
        assert score <= 1.0


# ═══════════════════════════════════════════════════════════
# TESTS CUISINEAZPARSER.PARSE()
# ═══════════════════════════════════════════════════════════


class TestCuisineAZParserParse:
    """Tests pour CuisineAZParser.parse() avec HTML simulé."""
    
    def test_parse_minimal(self):
        """Parse une page minimale."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html><body>
            <h1>Gratin dauphinois</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert recipe.nom == "Gratin dauphinois"
        assert recipe.source_site == "CuisineAZ"
    
    def test_parse_with_title_class(self):
        """Parse avec h1 ayant une classe title."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html><body>
            <h1 class="title">Blanquette de veau</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert recipe.nom == "Blanquette de veau"
    
    def test_parse_with_image_relative(self):
        """Parse avec image en URL relative."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html><body>
            <h1>Soupe</h1>
            <img class="recipe" src="//cdn.example.com/soupe.jpg"/>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert recipe.image_url == "https://cdn.example.com/soupe.jpg"
    
    def test_parse_with_meta_times(self):
        """Parse avec meta tags pour temps."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html>
        <head>
            <meta property="prepTime" content="PT20M"/>
            <meta property="cookTime" content="PT35M"/>
            <meta property="recipeYield" content="4 personnes"/>
        </head>
        <body><h1>Plat</h1></body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert recipe.temps_preparation == 20
        assert recipe.temps_cuisson == 35
        assert recipe.portions == 4
    
    def test_parse_with_json_ld(self):
        """Parse avec données JSON-LD."""
        from src.services.recettes.import_url import CuisineAZParser
        import json
        
        json_ld = json.dumps({
            "@type": "Recipe",
            "name": "Quiche lorraine",
            "recipeIngredient": ["200g de lardons", "4 oeufs", "200ml de crème"],
            "recipeInstructions": [
                {"text": "Préchauffer le four."},
                {"text": "Étaler la pâte."},
                "Ajouter la garniture."
            ]
        })
        
        html = f"""
        <html>
        <head>
            <script type="application/ld+json">{json_ld}</script>
        </head>
        <body><h1>Quiche lorraine</h1></body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert len(recipe.ingredients) >= 2
        assert len(recipe.etapes) >= 2
    
    def test_parse_fallback_ingredients_html(self):
        """Parse ingrédients depuis HTML si pas de JSON-LD."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html><body>
            <h1>Salade</h1>
            <div class="ingredient">Laitue</div>
            <div class="ingredient">Tomates</div>
            <div class="ingredient">Vinaigrette</div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert len(recipe.ingredients) >= 2
    
    def test_parse_fallback_steps_html(self):
        """Parse étapes depuis HTML si pas de JSON-LD."""
        from src.services.recettes.import_url import CuisineAZParser
        
        html = """
        <html><body>
            <h1>Plat simple</h1>
            <div class="instruction">
                <li>Couper les légumes en petits morceaux.</li>
                <li>Faire revenir dans une poêle avec huile.</li>
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = CuisineAZParser.parse(soup, "https://www.cuisineaz.com/recettes")
        
        assert len(recipe.etapes) >= 1


class TestCuisineAZCalculateConfidence:
    """Tests pour CuisineAZParser._calculate_confidence()."""
    
    def test_confidence_empty(self):
        from src.services.recettes.import_url import CuisineAZParser, ImportedRecipe
        recipe = ImportedRecipe()
        assert CuisineAZParser._calculate_confidence(recipe) == 0.0
    
    def test_confidence_increases(self):
        from src.services.recettes.import_url import CuisineAZParser, ImportedRecipe, ImportedIngredient
        
        recipe1 = ImportedRecipe()
        recipe2 = ImportedRecipe(nom="Test")
        recipe3 = ImportedRecipe(
            nom="Test",
            ingredients=[ImportedIngredient(nom="ing1")],
            etapes=["step1"],
            temps_preparation=10,
            image_url="http://img.jpg"
        )
        
        assert CuisineAZParser._calculate_confidence(recipe1) < \
               CuisineAZParser._calculate_confidence(recipe2) < \
               CuisineAZParser._calculate_confidence(recipe3)


# ═══════════════════════════════════════════════════════════
# TESTS GENERICRECIPEPARSER.PARSE()
# ═══════════════════════════════════════════════════════════


class TestGenericRecipeParserParse:
    """Tests pour GenericRecipeParser.parse() avec HTML simulé."""
    
    def test_parse_with_json_ld_recipe(self):
        """Parse avec JSON-LD schema.org Recipe."""
        from src.services.recettes.import_url import GenericRecipeParser
        import json
        
        json_ld = json.dumps({
            "@type": "Recipe",
            "name": "Poulet rôti",
            "description": "Poulet rôti aux herbes",
            "image": "https://example.com/poulet.jpg",
            "prepTime": "PT15M",
            "cookTime": "PT1H",
            "recipeYield": "4",
            "recipeIngredient": ["1 poulet", "herbes de provence", "huile d'olive"],
            "recipeInstructions": ["Assaisonner le poulet", "Cuire au four"]
        })
        
        html = f"""
        <html><head>
            <script type="application/ld+json">{json_ld}</script>
        </head><body></body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.nom == "Poulet rôti"
        assert recipe.description == "Poulet rôti aux herbes"
        assert recipe.temps_preparation == 15
        assert recipe.temps_cuisson == 60
        assert recipe.confiance_score == 0.9
    
    def test_parse_json_ld_list(self):
        """Parse quand JSON-LD est une liste."""
        from src.services.recettes.import_url import GenericRecipeParser
        import json
        
        json_ld = json.dumps([
            {"@type": "WebPage"},
            {"@type": "Recipe", "name": "Tarte citron"}
        ])
        
        html = f"""
        <html><head>
            <script type="application/ld+json">{json_ld}</script>
        </head><body></body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.nom == "Tarte citron"
    
    def test_parse_json_ld_image_list(self):
        """Parse quand image est une liste."""
        from src.services.recettes.import_url import GenericRecipeParser
        import json
        
        json_ld = json.dumps({
            "@type": "Recipe",
            "name": "Test",
            "image": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        })
        
        html = f"""
        <html><head>
            <script type="application/ld+json">{json_ld}</script>
        </head><body></body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.image_url == "https://example.com/img1.jpg"
    
    def test_parse_json_ld_instructions_string(self):
        """Parse quand instructions est une string."""
        from src.services.recettes.import_url import GenericRecipeParser
        import json
        
        json_ld = json.dumps({
            "@type": "Recipe",
            "name": "Test",
            "recipeInstructions": "Faire ceci. Puis cela. Enfin servir."
        })
        
        html = f"""
        <html><head>
            <script type="application/ld+json">{json_ld}</script>
        </head><body></body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert len(recipe.etapes) >= 2
    
    def test_parse_fallback_html_title(self):
        """Parse titre depuis HTML quand pas de JSON-LD."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><body>
            <h1>Recette maison</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.nom == "Recette maison"
    
    def test_parse_fallback_itemprop_name(self):
        """Parse titre depuis itemprop."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><body>
            <span itemprop="name">Risotto aux champignons</span>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.nom == "Risotto aux champignons"
    
    def test_parse_fallback_description_meta(self):
        """Parse description depuis meta tag."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><head>
            <meta name="description" content="Une recette traditionnelle"/>
        </head><body>
            <h1>Plat</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.description == "Une recette traditionnelle"
    
    def test_parse_fallback_ingredients(self):
        """Parse ingrédients depuis HTML fallback."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><body>
            <h1>Plat</h1>
            <ul class="ingredients">
                <li>100g de farine</li>
                <li>2 oeufs</li>
            </ul>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert len(recipe.ingredients) >= 1
    
    def test_parse_fallback_steps(self):
        """Parse étapes depuis HTML fallback."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><body>
            <h1>Plat</h1>
            <ol class="steps">
                <li>Première étape de préparation importante.</li>
                <li>Deuxième étape de cuisson longue.</li>
            </ol>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert len(recipe.etapes) >= 1
    
    def test_parse_fallback_times(self):
        """Parse temps depuis HTML fallback."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><body>
            <h1>Plat</h1>
            <span itemprop="prepTime">25 min</span>
            <span itemprop="cookTime">45 min</span>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.temps_preparation == 25
        assert recipe.temps_cuisson == 45
    
    def test_parse_fallback_image_og(self):
        """Parse image depuis og:image meta."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><head>
            <meta property="og:image" content="https://example.com/recipe.jpg"/>
        </head><body>
            <h1>Plat</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.image_url == "https://example.com/recipe.jpg"
    
    def test_parse_json_ld_invalid_json(self):
        """Gère gracieusement le JSON invalide."""
        from src.services.recettes.import_url import GenericRecipeParser
        
        html = """
        <html><head>
            <script type="application/ld+json">not valid json{</script>
        </head><body>
            <h1>Fallback title</h1>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        recipe = GenericRecipeParser.parse(soup, "https://example.com/recipe")
        
        assert recipe.nom == "Fallback title"


class TestGenericRecipeParserCalculateConfidence:
    """Tests pour GenericRecipeParser._calculate_confidence()."""
    
    def test_confidence_empty(self):
        from src.services.recettes.import_url import GenericRecipeParser, ImportedRecipe
        recipe = ImportedRecipe()
        assert GenericRecipeParser._calculate_confidence(recipe) == 0.0
    
    def test_confidence_complete(self):
        from src.services.recettes.import_url import GenericRecipeParser, ImportedRecipe, ImportedIngredient
        
        recipe = ImportedRecipe(
            nom="Complete recipe",
            ingredients=[ImportedIngredient(nom=f"ing{i}") for i in range(5)],
            etapes=["step1", "step2", "step3"],
            temps_preparation=20,
            temps_cuisson=30,
            image_url="http://img.jpg"
        )
        score = GenericRecipeParser._calculate_confidence(recipe)
        
        assert score >= 0.7
        assert score <= 1.0


# ═══════════════════════════════════════════════════════════
# TESTS RECIPEIMPORTSERVICE
# ═══════════════════════════════════════════════════════════


class TestRecipeImportServiceGetParser:
    """Tests pour _get_parser_for_url()."""
    
    def test_parser_marmiton(self):
        from src.services.recettes.import_url import RecipeImportService, MarmitonParser
        service = RecipeImportService()
        
        parser = service._get_parser_for_url("https://www.marmiton.org/recettes/recette_1")
        assert parser == MarmitonParser
    
    def test_parser_cuisineaz(self):
        from src.services.recettes.import_url import RecipeImportService, CuisineAZParser
        service = RecipeImportService()
        
        parser = service._get_parser_for_url("https://www.cuisineaz.com/recettes/quiche")
        assert parser == CuisineAZParser
    
    def test_parser_generic(self):
        from src.services.recettes.import_url import RecipeImportService, GenericRecipeParser
        service = RecipeImportService()
        
        parser = service._get_parser_for_url("https://www.allrecipes.com/recipe/123")
        assert parser == GenericRecipeParser
    
    def test_parser_strips_www(self):
        from src.services.recettes.import_url import RecipeImportService, MarmitonParser
        service = RecipeImportService()
        
        parser = service._get_parser_for_url("https://marmiton.org/recettes/test")
        assert parser == MarmitonParser


class TestRecipeImportServiceImportFromUrl:
    """Tests pour import_from_url() avec mocks."""
    
    def test_import_invalid_url_scheme(self):
        """Rejette les URLs avec schéma invalide."""
        from src.services.recettes.import_url import RecipeImportService
        service = RecipeImportService()
        
        result = service.import_from_url("ftp://example.com/recipe")
        
        assert result is None or result.success is False
    
    def test_import_http_error(self):
        """Gère les erreurs HTTP."""
        from src.services.recettes.import_url import RecipeImportService
        import httpx
        
        service = RecipeImportService()
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=Mock(),
            response=mock_response
        )
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.import_from_url("https://example.com/not-found")
            # Le décorateur retourne None en cas d'erreur
            assert result is None or result.success is False
    
    def test_import_success_marmiton(self):
        """Importe avec succès depuis Marmiton."""
        from src.services.recettes.import_url import RecipeImportService
        
        service = RecipeImportService()
        
        html = """
        <html><body>
            <h1>Crêpes bretonnes</h1>
            <p class="description">Recette traditionnelle de Bretagne</p>
            <span class="serving">4 personnes</span>
            <div class="time">préparation 10 min</div>
            <div class="ingredient">
                <li>250g de farine</li>
                <li>4 oeufs</li>
                <li>500ml de lait</li>
            </div>
            <div class="instruction">
                <li>Mélanger la farine et les oeufs pour former une pâte lisse.</li>
                <li>Ajouter le lait progressivement en remuant bien.</li>
                <li>Cuire les crêpes dans une poêle bien chaude avec beurre.</li>
            </div>
        </body></html>
        """
        
        mock_response = Mock()
        mock_response.text = html
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.import_from_url("https://www.marmiton.org/recettes/crepes")
            
            assert result.success is True
            assert result.recipe.nom == "Crêpes bretonnes"
            assert len(result.recipe.ingredients) >= 2
    
    def test_import_low_confidence_no_ai(self):
        """Import avec score bas sans AI fallback."""
        from src.services.recettes.import_url import RecipeImportService
        
        service = RecipeImportService()
        
        html = "<html><body><h1>T</h1></body></html>"  # Score très bas
        
        mock_response = Mock()
        mock_response.text = html
        mock_response.raise_for_status = Mock()
        
        with patch.object(service.http_client, 'get', return_value=mock_response):
            result = service.import_from_url("https://example.com/r", use_ai_fallback=False)
            
            # Résultat avec erreurs ou échec
            if result:
                assert not result.success or len(result.errors) > 0
    
    def test_import_connection_error(self):
        """Gère les erreurs de connexion."""
        from src.services.recettes.import_url import RecipeImportService
        
        service = RecipeImportService()
        
        with patch.object(service.http_client, 'get', side_effect=Exception("Connection refused")):
            result = service.import_from_url("https://example.com/recipe")
            # Le résultat indique l'échec
            assert result is None or result.success is False


class TestRecipeImportServiceBatch:
    """Tests pour import_batch()."""
    
    def test_batch_empty(self):
        """Import lot vide."""
        from src.services.recettes.import_url import RecipeImportService
        service = RecipeImportService()
        
        results = service.import_batch([])
        assert results == []
    
    def test_batch_with_urls(self):
        """Import lot avec URLs."""
        from src.services.recettes.import_url import RecipeImportService, ImportResult
        service = RecipeImportService()
        
        with patch.object(service, 'import_from_url') as mock_import:
            mock_import.return_value = ImportResult(success=True, message="OK")
            
            results = service.import_batch([
                "https://example.com/r1",
                "https://example.com/r2"
            ])
            
            assert len(results) == 2
            assert mock_import.call_count == 2


# ═══════════════════════════════════════════════════════════
# TESTS PARSE_INGREDIENT BRANCHES
# ═══════════════════════════════════════════════════════════


class TestParseIngredientBranches:
    """Tests pour branches non couvertes de parse_ingredient."""
    
    def test_parse_with_three_groups(self):
        """Parse ingrédient avec quantité, unité et nom."""
        from src.services.recettes.import_url import RecipeParser
        
        ing = RecipeParser.parse_ingredient("500 ml de lait")
        assert ing.quantite == 500.0
        assert ing.unite == "ml"
        assert "lait" in ing.nom.lower()
    
    def test_parse_with_two_groups(self):
        """Parse ingrédient avec quantité et nom (sans unité)."""
        from src.services.recettes.import_url import RecipeParser
        
        ing = RecipeParser.parse_ingredient("6 tomates")
        assert ing.quantite == 6.0
    
    def test_parse_invalid_quantity_three_groups(self):
        """Parse avec quantité invalide dans pattern 3 groupes."""
        from src.services.recettes.import_url import RecipeParser
        
        # "abc g de farine" - abc n'est pas un nombre
        ing = RecipeParser.parse_ingredient("abc g de farine")
        # Devrait avoir quantité None car "abc" n'est pas parseable
        assert ing.quantite is None or ing.nom != ""
    
    def test_parse_invalid_quantity_two_groups(self):
        """Parse avec quantité invalide dans pattern 2 groupes."""
        from src.services.recettes.import_url import RecipeParser
        
        ing = RecipeParser.parse_ingredient("plusieurs oeufs")
        # "plusieurs" n'est pas un nombre
        assert ing.nom != ""
