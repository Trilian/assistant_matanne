"""
Tests unitaires pour food.py

Module: src.utils.helpers.food
"""

import pytest
from src.utils.helpers.food import (
    convertir_unite,
    multiplier_portion,
    extraire_ingredient,
)


class TestFood:
    """Tests pour le module food."""

    def test_convertir_unite_ml_to_l(self):
        """Test conversion ml vers L."""
        assert convertir_unite(1000, "ml", "L") == 1.0

    def test_convertir_unite_kg_to_g(self):
        """Test conversion kg vers g."""
        assert convertir_unite(1, "kg", "g") == 1000.0

    def test_convertir_unite_g_to_kg(self):
        """Test conversion g vers kg."""
        assert convertir_unite(500, "g", "kg") == 0.5

    def test_convertir_unite_cl_to_l(self):
        """Test conversion cl vers L."""
        assert convertir_unite(100, "cl", "L") == 1.0

    def test_convertir_unite_invalid(self):
        """Test conversion invalide retourne None."""
        assert convertir_unite(100, "kg", "L") is None

    def test_multiplier_portion_double(self):
        """Test doubler les portions."""
        ingredients = {"sucre": 200, "farine": 300}
        result = multiplier_portion(4, 8, ingredients)
        assert result == {"sucre": 400.0, "farine": 600.0}

    def test_multiplier_portion_half(self):
        """Test réduire de moitié."""
        ingredients = {"sucre": 200}
        result = multiplier_portion(4, 2, ingredients)
        assert result == {"sucre": 100.0}

    def test_multiplier_portion_zero_original(self):
        """Test avec portion originale à 0."""
        ingredients = {"sucre": 200}
        result = multiplier_portion(0, 4, ingredients)
        assert result == ingredients

    def test_extraire_ingredient_grammes(self):
        """Test extraction avec grammes."""
        result = extraire_ingredient("200g de farine")
        assert result == {"quantite": 200.0, "unite": "g", "nom": "farine"}

    def test_extraire_ingredient_kilogrammes(self):
        """Test extraction avec kg."""
        result = extraire_ingredient("1.5kg de sucre")
        assert result == {"quantite": 1.5, "unite": "kg", "nom": "sucre"}

    def test_extraire_ingredient_sans_unite(self):
        """Test extraction sans unité explicite."""
        result = extraire_ingredient("3 oeufs")
        assert result is not None
        assert result["quantite"] == 3.0

    def test_extraire_ingredient_invalide(self):
        """Test texte invalide retourne None."""
        result = extraire_ingredient("un peu de sel")
        assert result is None
