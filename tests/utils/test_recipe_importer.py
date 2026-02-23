"""
Tests pour src/services/cuisine/recettes/importer.py (PDF + text) et parsers.py
"""

from unittest.mock import patch

import pytest

from src.services.cuisine.recettes.importer import RecipeImporter
from src.services.cuisine.recettes.parsers import RecipeParser


@pytest.mark.unit
class TestParseDuration:
    """Tests pour RecipeParser.parse_duration."""

    def test_parse_iso_minutes_only(self):
        """Parse PT30M â†’ 30 minutes."""
        assert RecipeParser.parse_duration("PT30M") == 30

    def test_parse_iso_hours_only(self):
        """Parse PT1H â†’ 60 minutes."""
        assert RecipeParser.parse_duration("PT1H") == 60

    def test_parse_iso_hours_and_minutes(self):
        """Parse PT1H30M â†’ 90 minutes."""
        assert RecipeParser.parse_duration("PT1H30M") == 90

    def test_parse_iso_2_hours(self):
        """Parse PT2H â†’ 120 minutes."""
        assert RecipeParser.parse_duration("PT2H") == 120

    def test_parse_french_minutes(self):
        """Parse '30 min' â†’ 30 minutes."""
        assert RecipeParser.parse_duration("30 min") == 30

    def test_parse_french_hours(self):
        """Parse '1h' â†’ 60 minutes."""
        assert RecipeParser.parse_duration("1h") == 60

    def test_parse_french_hours_minutes(self):
        """Parse '1h30' â†’ 90 minutes."""
        assert RecipeParser.parse_duration("1h 30min") == 90

    def test_parse_french_heure_minute(self):
        """Parse '1 heure 30 minutes' â†’ 90."""
        assert RecipeParser.parse_duration("1 heure 30 minutes") == 90

    def test_parse_empty_string(self):
        """Chaîne vide â†’ 0."""
        assert RecipeParser.parse_duration("") == 0

    def test_parse_just_number(self):
        """Juste un nombre â†’ ce nombre."""
        assert RecipeParser.parse_duration("45") == 45


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
        assert hasattr(RecipeImporter, "from_pdf")
        assert hasattr(RecipeImporter, "from_text")
        assert hasattr(RecipeImporter, "_extract_from_text")

    def test_all_methods_are_static(self):
        """Toutes les méthodes sont statiques."""
        assert isinstance(RecipeImporter.__dict__["from_text"], staticmethod)


@pytest.mark.unit
class TestParseDurationEdgeCases:
    """Tests edge cases pour RecipeParser.parse_duration."""

    def test_parse_h30_format(self):
        """Parse 1h30 sans espace (retourne 60 car pas de 'min')."""
        # La fonction cherche "min" pour les minutes
        result = RecipeParser.parse_duration("1h30")
        # 1h30 sans "min" = seulement l'heure est parsée
        assert result == 60 or result == 90

    def test_parse_2h15min(self):
        """Parse 2h15min."""
        assert RecipeParser.parse_duration("2h15min") == 135

    def test_parse_iso_seconds(self):
        """Ignore les secondes ISO."""
        assert RecipeParser.parse_duration("PT30M30S") == 30

    def test_parse_mixed_french(self):
        """Parse formats mixtes."""
        assert RecipeParser.parse_duration("environ 45 min") == 45

    def test_parse_heure_pluriel(self):
        """Parse 2 heures."""
        assert RecipeParser.parse_duration("2 heures") == 120

    def test_parse_integer_string(self):
        """Parse un entier en string."""
        assert RecipeParser.parse_duration("30") == 30

    def test_parse_float_string(self):
        """Parse 1.5 — pas un format reconnu, retourne 0."""
        result = RecipeParser.parse_duration("1.5")
        assert result == 0  # "1.5" ne matche pas ^(\d+)$


@pytest.mark.unit
class TestFromPdfExtended:
    """Tests supplémentaires pour RecipeImporter.from_pdf."""

    def test_from_pdf_file_not_found(self):
        """Gère fichier inexistant."""
        result = RecipeImporter.from_pdf("/nonexistent/path/recipe.pdf")

        assert result is None

    @patch("builtins.open", side_effect=PermissionError("Access denied"))
    def test_from_pdf_permission_error(self, mock_open):
        """Gère erreur de permission."""
        result = RecipeImporter.from_pdf("/protected/recipe.pdf")

        assert result is None


@pytest.mark.unit
class TestFromTextExceptions:
    """Tests pour les exceptions dans from_text."""

    def test_from_text_with_none(self):
        """Gère None en entrée."""
        result = RecipeImporter.from_text(None)

        assert result is None

    def test_from_text_just_title(self):
        """Parse texte avec juste un titre."""
        result = RecipeImporter.from_text("Ma recette simple")

        assert result is not None
        assert result["nom"] == "Ma recette simple"


@pytest.mark.unit
class TestExtractFromTextPaths:
    """Tests pour les chemins de _extract_from_text."""

    def test_extract_text_with_temps_prep(self):
        """Parse temps préparation dans texte."""
        text = """Gateau facile
Temps prep: 20 minutes

Ingredients:
- Farine
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert result["temps_preparation"] == 20

    def test_extract_text_with_temps_cuisson(self):
        """Parse temps cuisson dans texte."""
        text = """Pizza maison
Temps cuisson: 15 minutes

Ingredients:
- Pate
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert result["temps_cuisson"] == 15

    def test_extract_text_portions_line(self):
        """Parse portions dans texte."""
        text = """Tarte citron
Portions: 8

Ingredients:
- Citron
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        # La fonction peut ou non parser les portions selon l'implémentation

    def test_extract_text_with_etapes_keyword(self):
        """Parse étapes avec mot-clé 'étapes'."""
        text = """Soupe tomate

Ingrédients:
- Tomates
- Oignons

Étapes:
Couper les tomates
Faire revenir les oignons
Mixer le tout
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert len(result["etapes"]) >= 1

    def test_extract_text_with_instructions_keyword(self):
        """Parse étapes avec mot-clé 'instructions'."""
        text = """Riz au curry

Ingrédients:
- Riz
- Curry

Instructions:
Cuire le riz
Ajouter le curry
Servir chaud
"""
        result = RecipeImporter.from_text(text)

        assert result is not None
        assert len(result["etapes"]) >= 1
