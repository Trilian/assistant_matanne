"""
Tests pour src/modules/cuisine/logic/recettes_logic.py
"""

from unittest.mock import Mock


class TestValiderRecette:
    """Tests pour valider_recette (fonction pure)."""

    def test_valider_recette_valide(self):
        """Recette valide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {
            "nom": "Tarte aux pommes",
            "ingredients": ["pommes", "farine", "sucre"],
            "instructions": ["Étape 1", "Étape 2"],
            "temps_preparation": 30,
            "portions": 4,
        }
        valid, error = valider_recette(data)
        assert valid is True
        assert error is None

    def test_valider_recette_sans_nom(self):
        """Recette sans nom = invalide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {"ingredients": ["pommes"], "instructions": ["Étape 1"], "portions": 4}
        valid, error = valider_recette(data)
        assert valid is False
        assert "nom" in error.lower()

    def test_valider_recette_sans_ingredients(self):
        """Recette sans ingrédients = invalide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {"nom": "Test", "ingredients": [], "instructions": ["Étape 1"], "portions": 4}
        valid, error = valider_recette(data)
        assert valid is False
        assert "ingredient" in error.lower()

    def test_valider_recette_sans_instructions(self):
        """Recette sans instructions = invalide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {"nom": "Test", "ingredients": ["pommes"], "instructions": [], "portions": 4}
        valid, error = valider_recette(data)
        assert valid is False
        assert "instruction" in error.lower()

    def test_valider_recette_temps_negatif(self):
        """Temps négatif = invalide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {
            "nom": "Test",
            "ingredients": ["pommes"],
            "instructions": ["Étape 1"],
            "temps_preparation": -10,
            "portions": 4,
        }
        valid, error = valider_recette(data)
        assert valid is False
        assert "temps" in error.lower()

    def test_valider_recette_portions_zero(self):
        """Portions = 0 invalide."""
        from src.modules.cuisine.recettes.utils import valider_recette

        data = {
            "nom": "Test",
            "ingredients": ["pommes"],
            "instructions": ["Étape 1"],
            "portions": 0,
        }
        valid, error = valider_recette(data)
        assert valid is False
        assert "portion" in error.lower()


class TestCalculerCaloriesPortion:
    """Tests pour calculer_calories_portion."""

    def test_calcul_calories_normal(self):
        """Calcul normal de calories par portion."""
        from src.modules.cuisine.recettes.utils import calculer_calories_portion

        recette = Mock()
        recette.calories = 800
        recette.portions = 4

        result = calculer_calories_portion(recette)
        assert result == 200.0

    def test_calcul_calories_sans_calories(self):
        """Pas de calories = None."""
        from src.modules.cuisine.recettes.utils import calculer_calories_portion

        recette = Mock()
        recette.calories = None
        recette.portions = 4

        result = calculer_calories_portion(recette)
        assert result is None

    def test_calcul_calories_sans_portions(self):
        """Pas de portions = None."""
        from src.modules.cuisine.recettes.utils import calculer_calories_portion

        recette = Mock()
        recette.calories = 800
        recette.portions = None

        result = calculer_calories_portion(recette)
        assert result is None


class TestCalculerCoutRecette:
    """Tests pour calculer_cout_recette."""

    def test_calcul_cout_simple(self):
        """Calcul de coût simple."""
        from src.modules.cuisine.recettes.utils import calculer_cout_recette

        recette = Mock()
        recette.ingredients = ["pommes", "farine", "sucre"]

        prix_ingredients = {"pommes": 2.50, "farine": 1.00, "sucre": 0.80}

        result = calculer_cout_recette(recette, prix_ingredients)
        assert result == 4.30

    def test_calcul_cout_ingredient_manquant(self):
        """Ingrédient non trouvé dans les prix."""
        from src.modules.cuisine.recettes.utils import calculer_cout_recette

        recette = Mock()
        recette.ingredients = ["ingrédient_inconnu"]

        prix_ingredients = {"pommes": 2.50}

        result = calculer_cout_recette(recette, prix_ingredients)
        assert result == 0.0

    def test_calcul_cout_vide(self):
        """Liste vide d'ingrédients."""
        from src.modules.cuisine.recettes.utils import calculer_cout_recette

        recette = Mock()
        recette.ingredients = []

        result = calculer_cout_recette(recette, {"pommes": 1.0})
        assert result == 0.0
