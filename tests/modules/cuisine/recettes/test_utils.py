"""
Tests pour src/modules/cuisine/recettes/utils.py

Tests complets pour la logique métier des recettes.
"""

from unittest.mock import MagicMock

import pytest

from src.modules.cuisine.recettes.utils import (
    calculer_calories_portion,
    calculer_cout_recette,
    formater_quantite,
    valider_recette,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def recette_mock():
    """Mock d'une recette SQLAlchemy."""
    recette = MagicMock()
    recette.id = 1
    recette.nom = "Tarte aux pommes"
    recette.ingredients = ["pommes", "sucre", "pâte brisée", "beurre"]
    recette.instructions = ["Préparer la pâte", "Couper les pommes", "Cuire"]
    recette.categorie = "dessert"
    recette.difficulte = "facile"
    recette.temps_preparation = 30
    recette.temps_cuisson = 45
    recette.portions = 8
    recette.calories = 2400
    recette.favorite = False
    return recette


@pytest.fixture
def recette_sans_calories():
    """Mock d'une recette sans calories."""
    recette = MagicMock()
    recette.id = 2
    recette.nom = "Salade verte"
    recette.ingredients = ["laitue", "tomates"]
    recette.instructions = ["Laver", "Couper", "Servir"]
    recette.portions = 4
    recette.calories = None
    return recette


@pytest.fixture
def prix_ingredients():
    """Dictionnaire de prix des ingrédients."""
    return {
        "pommes": 2.50,
        "sucre": 1.20,
        "beurre": 2.00,
        "farine": 0.80,
        "lait": 1.10,
        "oeufs": 2.40,
        "poulet": 8.50,
        "riz": 1.50,
    }


@pytest.fixture
def donnees_recette_valide():
    """Données valides pour créer une recette."""
    return {
        "nom": "Quiche lorraine",
        "ingredients": ["oeufs", "lardons", "crème", "pâte brisée"],
        "instructions": ["Étaler la pâte", "Préparer l'appareil", "Cuire au four"],
        "temps_preparation": 20,
        "portions": 6,
    }


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL COÛT RECETTE
# ═══════════════════════════════════════════════════════════


class TestCalculerCoutRecette:
    """Tests pour calculer_cout_recette."""

    def test_cout_basique(self, recette_mock, prix_ingredients):
        """Calcule le coût d'une recette avec des ingrédients connus."""
        cout = calculer_cout_recette(recette_mock, prix_ingredients)
        # pommes (2.50) + sucre (1.20) + beurre (2.00) = 5.70
        assert cout == 5.70

    def test_cout_arrondi(self, prix_ingredients):
        """Le coût est arrondi à 2 décimales."""
        recette = MagicMock()
        recette.ingredients = ["pommes", "sucre"]

        cout = calculer_cout_recette(recette, prix_ingredients)
        # 2.50 + 1.20 = 3.70
        assert cout == 3.70

    def test_ingredient_inconnu(self, prix_ingredients):
        """Les ingrédients inconnus ne sont pas comptés."""
        recette = MagicMock()
        recette.ingredients = ["pommes", "chocolat"]  # chocolat pas dans prix

        cout = calculer_cout_recette(recette, prix_ingredients)
        assert cout == 2.50  # Seulement pommes

    def test_recette_sans_ingredients(self, prix_ingredients):
        """Recette sans ingrédients = coût 0."""
        recette = MagicMock()
        recette.ingredients = []

        cout = calculer_cout_recette(recette, prix_ingredients)
        assert cout == 0.0

    def test_correspondance_partielle(self, prix_ingredients):
        """Correspondance partielle des noms d'ingrédients."""
        recette = MagicMock()
        recette.ingredients = ["2 pommes Golden", "100g de sucre en poudre"]

        cout = calculer_cout_recette(recette, prix_ingredients)
        # Devrait trouver pommes et sucre
        assert cout == 3.70


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL CALORIES PAR PORTION
# ═══════════════════════════════════════════════════════════


class TestCalculerCaloriesPortion:
    """Tests pour calculer_calories_portion."""

    def test_calories_normales(self, recette_mock):
        """Calcule les calories par portion."""
        calories = calculer_calories_portion(recette_mock)
        # 2400 / 8 = 300
        assert calories == 300.0

    def test_sans_calories(self, recette_sans_calories):
        """Retourne None si pas de calories définies."""
        assert calculer_calories_portion(recette_sans_calories) is None

    def test_sans_portions(self):
        """Retourne None si pas de portions définies."""
        recette = MagicMock()
        recette.calories = 1000
        recette.portions = None

        assert calculer_calories_portion(recette) is None

    def test_portions_zero(self):
        """Retourne None si portions = 0."""
        recette = MagicMock()
        recette.calories = 1000
        recette.portions = 0

        assert calculer_calories_portion(recette) is None

    def test_arrondi(self):
        """Le résultat est arrondi à 2 décimales."""
        recette = MagicMock()
        recette.calories = 1000
        recette.portions = 3

        calories = calculer_calories_portion(recette)
        # 1000 / 3 = 333.333...
        assert calories == 333.33


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION RECETTE
# ═══════════════════════════════════════════════════════════


class TestValiderRecette:
    """Tests pour valider_recette."""

    def test_recette_valide(self, donnees_recette_valide):
        """Une recette valide retourne True."""
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is True
        assert erreur is None

    def test_nom_manquant(self, donnees_recette_valide):
        """Le nom est requis."""
        donnees_recette_valide["nom"] = ""
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False
        assert "nom" in erreur.lower()

    def test_nom_none(self, donnees_recette_valide):
        """Un nom None est invalide."""
        donnees_recette_valide["nom"] = None
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False

    def test_ingredients_manquants(self, donnees_recette_valide):
        """Au moins un ingrédient est requis."""
        donnees_recette_valide["ingredients"] = []
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False
        assert "ingredient" in erreur.lower()

    def test_ingredients_none(self, donnees_recette_valide):
        """Ingredients None est invalide."""
        donnees_recette_valide["ingredients"] = None
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False

    def test_instructions_manquantes(self, donnees_recette_valide):
        """Au moins une instruction est requise."""
        donnees_recette_valide["instructions"] = []
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False
        assert "instruction" in erreur.lower()

    def test_temps_preparation_negatif(self, donnees_recette_valide):
        """Le temps de préparation doit être positif."""
        donnees_recette_valide["temps_preparation"] = -10
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False
        assert "temps" in erreur.lower()

    def test_temps_preparation_zero(self, donnees_recette_valide):
        """Temps de préparation à 0 est valide."""
        donnees_recette_valide["temps_preparation"] = 0
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is True

    def test_portions_zero(self, donnees_recette_valide):
        """Le nombre de portions doit être supérieur à 0."""
        donnees_recette_valide["portions"] = 0
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False
        assert "portions" in erreur.lower()

    def test_portions_negatives(self, donnees_recette_valide):
        """Portions négatives invalides."""
        donnees_recette_valide["portions"] = -4
        est_valide, erreur = valider_recette(donnees_recette_valide)
        assert est_valide is False

    def test_champs_optionnels_absents(self):
        """Les champs optionnels peuvent être absents."""
        donnees = {
            "nom": "Simple",
            "ingredients": ["un"],
            "instructions": ["faire"],
            "portions": 4,  # Portions est requis et doit être > 0
        }
        est_valide, erreur = valider_recette(donnees)
        assert est_valide is True


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER QUANTITÉ
# ═══════════════════════════════════════════════════════════


class TestFormaterQuantite:
    """Tests pour formater_quantite."""

    def test_entier(self):
        """Un entier reste un entier."""
        assert formater_quantite(5) == "5"

    def test_float_entier(self):
        """Un float qui est un entier s'affiche sans décimales."""
        assert formater_quantite(5.0) == "5"

    def test_float_decimal(self):
        """Un float avec décimales les conserve."""
        assert formater_quantite(2.5) == "2.5"

    def test_string_entier(self):
        """Une string représentant un entier."""
        assert formater_quantite("3") == "3"

    def test_string_float(self):
        """Une string représentant un float."""
        assert formater_quantite("2.5") == "2.5"

    def test_string_invalide(self):
        """Une string non numérique reste une string."""
        assert formater_quantite("une pincée") == "une pincée"

    def test_zero(self):
        """Zéro s'affiche correctement."""
        assert formater_quantite(0) == "0"

    def test_float_zero(self):
        """Float zéro."""
        assert formater_quantite(0.0) == "0"
