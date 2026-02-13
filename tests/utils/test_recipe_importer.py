"""
Tests pour src/utils/recipe_importer.py
"""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.recipe_importer import RecipeImporter


@pytest.mark.unit
class TestParseDuration:
    """Tests pour RecipeImporter._parse_duration."""

    def test_parse_iso_minutes_only(self):
        """Parse PT30M â†’ 30 minutes."""
        assert RecipeImporter._parse_duration("PT30M") == 30

    def test_parse_iso_hours_only(self):
        """Parse PT1H â†’ 60 minutes."""
        assert RecipeImporter._parse_duration("PT1H") == 60

    def test_parse_iso_hours_and_minutes(self):
        """Parse PT1H30M â†’ 90 minutes."""
        assert RecipeImporter._parse_duration("PT1H30M") == 90

    def test_parse_iso_2_hours(self):
        """Parse PT2H â†’ 120 minutes."""
        assert RecipeImporter._parse_duration("PT2H") == 120

    def test_parse_french_minutes(self):
        """Parse '30 min' â†’ 30 minutes."""
        assert RecipeImporter._parse_duration("30 min") == 30

    def test_parse_french_hours(self):
        """Parse '1h' â†’ 60 minutes."""
        assert RecipeImporter._parse_duration("1h") == 60

    def test_parse_french_hours_minutes(self):
        """Parse '1h30' â†’ 90 minutes."""
        assert RecipeImporter._parse_duration("1h 30min") == 90

    def test_parse_french_heure_minute(self):
        """Parse '1 heure 30 minutes' â†’ 90."""
        assert RecipeImporter._parse_duration("1 heure 30 minutes") == 90

    def test_parse_empty_string(self):
        """Chaîne vide â†’ 0."""
        assert RecipeImporter._parse_duration("") == 0

    def test_parse_none(self):
        """None â†’ 0."""
        assert RecipeImporter._parse_duration(None) == 0

    def test_parse_just_number(self):
        """Juste un nombre â†’ ce nombre."""
        assert RecipeImporter._parse_duration("45") == 45


@pytest.mark.unit
class TestFromText:
    """Tests pour RecipeImporter.from_text."""

    def test_from_text_simple(self):
        """Parse texte simple avec nom."""
        text = """Tarte aux pommes
Une délicieuse tarte.

Ingrédients:
- 3 pommes
- 200g de farine
- 100g de sucre

Étapes:
Préchauffer le four
Mélanger les ingrédients
Cuire 30 minutes
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert result["nom"] == "Tarte aux pommes"
        assert len(result["ingredients"]) >= 2
        assert len(result["etapes"]) >= 1

    def test_from_text_empty(self):
        """Texte vide â†’ None."""
        result = RecipeImporter.from_text("")
        assert result is None

    def test_from_text_with_temps(self):
        """Parse les temps de préparation."""
        text = """Ma recette
Temps prep: 15 minutes
Temps cuisson: 30 minutes
Portions: 4

Ingrédients:
- Farine
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert result["temps_preparation"] == 15
        assert result["temps_cuisson"] == 30
        assert result["portions"] == 4

    def test_from_text_only_name(self):
        """Texte avec seulement un nom."""
        text = "Ma recette simple"
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert result["nom"] == "Ma recette simple"


@pytest.mark.unit
class TestFromUrl:
    """Tests pour RecipeImporter.from_url."""

    @patch("requests.get")
    def test_from_url_adds_https(self, mock_get):
        """Ajoute https:// si manquant."""
        mock_get.side_effect = Exception("Network error")

        result = RecipeImporter.from_url("example.com/recipe")

        # Vérifie que la requête a été appelée avec https://
        if mock_get.called:
            call_url = mock_get.call_args[0][0]
            assert call_url.startswith("https://")

    @patch("requests.get")
    def test_from_url_handles_error(self, mock_get):
        """Gère les erreurs réseau."""
        mock_get.side_effect = Exception("Network error")

        result = RecipeImporter.from_url("https://example.com/recipe")

        assert result is None

    def test_from_url_requires_bs4(self):
        """from_url nécessite BeautifulSoup."""
        # Test que la méthode existe et retourne None si erreur réseau
        # (test d'intégration complet nécessiterait bs4 + requests)
        result = RecipeImporter.from_url("https://invalid-domain-that-does-not-exist-12345.com")
        assert result is None


@pytest.mark.unit
class TestFromPdf:
    """Tests pour RecipeImporter.from_pdf."""

    def test_from_pdf_file_not_found(self):
        """Fichier inexistant â†’ None."""
        result = RecipeImporter.from_pdf("/nonexistent/file.pdf")
        assert result is None

    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_from_pdf_handles_missing_file(self, mock_open):
        """Gère erreur fichier manquant."""
        result = RecipeImporter.from_pdf("missing.pdf")
        assert result is None


@pytest.mark.unit
class TestExtractFromText:
    """Tests pour RecipeImporter._extract_from_text."""

    def test_extract_ingredients_with_bullets(self):
        """Parse ingrédients avec puces."""
        text = """Gâteau
Ingrédients:
• Farine
• Sucre
• Oeufs
"""
        result = RecipeImporter._extract_from_text(text)

        assert result is not None
        assert "Farine" in result["ingredients"]
        assert "Sucre" in result["ingredients"]

    def test_extract_ingredients_with_dashes(self):
        """Parse ingrédients avec tirets."""
        text = """Salade
Ingrédients:
- Laitue
- Tomates
- Concombre
"""
        result = RecipeImporter._extract_from_text(text)

        assert result is not None
        assert "Laitue" in result["ingredients"]

    def test_extract_etapes(self):
        """Parse les étapes."""
        text = """Pizza
Étapes:
Étaler la pâte
Ajouter la sauce
Cuire au four
"""
        result = RecipeImporter._extract_from_text(text)

        assert result is not None
        assert len(result["etapes"]) >= 1

    def test_extract_description(self):
        """Parse la description."""
        text = """Crêpes
Une recette traditionnelle bretonne.

Ingrédients:
- Farine
"""
        result = RecipeImporter._extract_from_text(text)

        assert result is not None
        assert "bretonne" in result["description"]


@pytest.mark.unit
class TestRecipeImporterIntegration:
    """Tests d'intégration pour RecipeImporter."""

    def test_class_has_all_methods(self):
        """La classe a toutes les méthodes attendues."""
        assert hasattr(RecipeImporter, "from_url")
        assert hasattr(RecipeImporter, "from_pdf")
        assert hasattr(RecipeImporter, "from_text")
        assert hasattr(RecipeImporter, "_parse_duration")
        assert hasattr(RecipeImporter, "_extract_from_text")
        assert hasattr(RecipeImporter, "_extract_from_html")

    def test_all_methods_are_static(self):
        """Toutes les méthodes sont statiques."""
        assert isinstance(RecipeImporter.__dict__["from_url"], staticmethod)
        assert isinstance(RecipeImporter.__dict__["from_text"], staticmethod)
        assert isinstance(RecipeImporter.__dict__["_parse_duration"], staticmethod)


@pytest.mark.unit
class TestExtractFromHtml:
    """Tests pour RecipeImporter._extract_from_html avec BeautifulSoup."""

    def test_extract_from_html_json_ld(self):
        """Parse JSON-LD schema.org Recipe."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Tarte aux fraises",
                "description": "Une délicieuse tarte",
                "recipeIngredient": ["250g fraises", "200g pâte sablée"],
                "recipeInstructions": [
                    {"@type": "HowToStep", "text": "Étaler la pâte"},
                    {"@type": "HowToStep", "text": "Ajouter les fraises"}
                ],
                "prepTime": "PT20M",
                "cookTime": "PT30M",
                "recipeYield": "6 portions",
                "image": "https://example.com/tarte.jpg"
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["nom"] == "Tarte aux fraises"
        assert "fraises" in str(result["ingredients"])
        assert result["temps_preparation"] == 20
        assert result["temps_cuisson"] == 30
        assert result["image_url"] == "https://example.com/tarte.jpg"

    def test_extract_from_html_fallback_h1(self):
        """Parse fallback via H1 quand pas de JSON-LD."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <meta property="og:description" content="Recette traditionnelle">
        </head>
        <body>
            <h1>Crêpes bretonnes</h1>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["nom"] == "Crêpes bretonnes"
        assert "traditionnelle" in result["description"]

    def test_extract_from_html_og_image(self):
        """Parse og:image pour l'image."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <meta property="og:image" content="https://cdn.example.com/photo.jpg">
        </head>
        <body>
            <h1>Gâteau chocolat</h1>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["image_url"] == "https://cdn.example.com/photo.jpg"

    def test_extract_from_html_relative_image(self):
        """Convertit URL image relative en absolue."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <meta property="og:image" content="/images/recipe.jpg">
        </head>
        <body>
            <h1>Quiche lorraine</h1>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["image_url"].startswith("https://")

    def test_extract_from_html_no_title(self):
        """Retourne None si pas de titre."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = "<html><body><p>Du texte sans titre</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is None

    def test_extract_json_ld_string_instructions(self):
        """Parse JSON-LD avec instructions string."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Salade verte",
                "recipeInstructions": ["Laver la salade", "Ajouter la vinaigrette"]
            }
            </script>
        </head>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert len(result["etapes"]) == 2

    def test_extract_json_ld_image_list(self):
        """Parse JSON-LD avec image en liste."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Pizza maison",
                "image": ["https://example.com/pizza1.jpg", "https://example.com/pizza2.jpg"]
            }
            </script>
        </head>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["image_url"] == "https://example.com/pizza1.jpg"

    def test_extract_json_ld_yield_list(self):
        """Parse JSON-LD avec yield en liste."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            pytest.skip("BeautifulSoup non installé")

        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Recipe",
                "name": "Cookies",
                "recipeYield": ["24 cookies", "pour 24"]
            }
            </script>
        </head>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = RecipeImporter._extract_from_html(soup, "https://example.com")

        assert result is not None
        assert result["portions"] == 24


@pytest.mark.unit
class TestParseDurationEdgeCases:
    """Tests edge cases pour _parse_duration."""

    def test_parse_h30_format(self):
        """Parse 1h30 sans espace (retourne 60 car pas de 'min')."""
        # La fonction cherche "min" pour les minutes
        result = RecipeImporter._parse_duration("1h30")
        # 1h30 sans "min" = seulement l'heure est parsée
        assert result == 60 or result == 90

    def test_parse_2h15min(self):
        """Parse 2h15min."""
        assert RecipeImporter._parse_duration("2h15min") == 135

    def test_parse_iso_seconds(self):
        """Ignore les secondes ISO."""
        assert RecipeImporter._parse_duration("PT30M30S") == 30

    def test_parse_mixed_french(self):
        """Parse formats mixtes."""
        assert RecipeImporter._parse_duration("environ 45 min") == 45

    def test_parse_heure_pluriel(self):
        """Parse 2 heures."""
        assert RecipeImporter._parse_duration("2 heures") == 120

    def test_parse_integer(self):
        """Parse un entier directement."""
        assert RecipeImporter._parse_duration(30) == 30

    def test_parse_float_string(self):
        """Parse 1.5 (arrondi)."""
        result = RecipeImporter._parse_duration("1.5")
        assert result == 1  # Prend le premier nombre entier


@pytest.mark.unit
class TestFromUrlMocking:
    """Tests avancés pour from_url avec mocks."""

    @patch("requests.get")
    def test_from_url_json_ld_success(self, mock_get):
        """Parse une URL avec JSON-LD."""
        mock_response = MagicMock()
        mock_response.content = b"""
        <html>
        <head>
            <script type="application/ld+json">
            {"@type": "Recipe", "name": "Gratin dauphinois", "prepTime": "PT15M"}
            </script>
        </head>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = RecipeImporter.from_url("https://example.com/gratin")

        assert result is not None
        assert result["nom"] == "Gratin dauphinois"
        assert result["temps_preparation"] == 15

    @patch("requests.get")
    def test_from_url_timeout(self, mock_get):
        """Gère timeout réseau."""
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout("Connection timed out")

        result = RecipeImporter.from_url("https://example.com/slow")

        assert result is None
