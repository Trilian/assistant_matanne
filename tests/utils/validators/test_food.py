"""
Tests pour src/utils/validators/food.py
"""
import pytest
from datetime import date, timedelta
from src.utils.validators.food import (
    valider_recette,
    valider_ingredient,
    valider_article_inventaire,
    valider_article_courses,
    valider_repas,
    valider_quantite,
    valider_allergie,
)


class TestValiderRecette:
    """Tests pour valider_recette (retourne tuple[bool, list[str]])."""

    def test_valider_recette_valid(self):
        """Recette valide complète."""
        recipe = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is True
        assert errors == []

    def test_valider_recette_missing_name(self):
        """Recette sans nom = invalide."""
        recipe = {
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False
        assert any("nom" in e.lower() for e in errors)

    def test_valider_recette_short_name(self):
        """Nom trop court = invalide."""
        recipe = {
            "nom": "AB",  # < 3 caractères
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False

    def test_valider_recette_negative_time(self):
        """Temps négatif = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": -10,
            "temps_cuisson": 45,
            "portions": 4,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False

    def test_valider_recette_zero_portions(self):
        """Zero portions = invalide."""
        recipe = {
            "nom": "Test Recipe",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 0,
        }
        is_valid, errors = valider_recette(recipe)
        assert is_valid is False


class TestValiderIngredient:
    """Tests pour valider_ingredient (retourne tuple[bool, list[str]])."""

    def test_valider_ingredient_valid(self):
        """Ingrédient valide."""
        ingredient = {
            "nom": "Farine",
            "unite": "g",  # Unite requise
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is True
        assert errors == []

    def test_valider_ingredient_missing_name(self):
        """Ingrédient sans nom = invalide."""
        ingredient = {
            "unite": "g",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False

    def test_valider_ingredient_missing_unite(self):
        """Ingrédient sans unité = invalide."""
        ingredient = {
            "nom": "Farine",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False

    def test_valider_ingredient_short_name(self):
        """Nom trop court = invalide."""
        ingredient = {
            "nom": "A",  # < 2 caractères
            "unite": "g",
        }
        is_valid, errors = valider_ingredient(ingredient)
        assert is_valid is False


class TestValiderArticleInventaire:
    """Tests pour valider_article_inventaire (retourne tuple[bool, list[str]])."""

    def test_valider_inventaire_valid(self):
        """Article inventaire valide."""
        item = {
            "ingredient_id": 1,
            "quantite": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True
        assert errors == []

    def test_valider_inventaire_missing_ingredient_id(self):
        """Article sans ingredient_id = invalide."""
        item = {
            "quantite": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_missing_quantite(self):
        """Article sans quantité = invalide."""
        item = {
            "ingredient_id": 1,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_negative_quantity(self):
        """Quantité négative = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite": -1,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_zero_quantity(self):
        """Quantité zéro = valide (>= 0)."""
        item = {
            "ingredient_id": 1,
            "quantite": 0,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True  # 0 est >= 0

    def test_valider_inventaire_with_min_quantity(self):
        """Article avec quantite_min."""
        item = {
            "ingredient_id": 1,
            "quantite": 5,
            "quantite_min": 2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is True

    def test_valider_inventaire_invalid_min_quantity(self):
        """Article avec quantite_min négative = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite": 5,
            "quantite_min": -2,
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False

    def test_valider_inventaire_invalid_quantite_string(self):
        """Article avec quantité texte = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite": "beaucoup",
        }
        is_valid, errors = valider_article_inventaire(item)
        assert is_valid is False


class TestValiderArticleCourses:
    """Tests pour valider_article_courses avec données réelles."""

    def test_article_valide_farine(self):
        """Article courses valide: 500g farine."""
        item = {
            "ingredient_id": 1,
            "quantite_necessaire": 500,
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is True
        assert errors == []

    def test_article_valide_avec_priorite(self):
        """Article avec priorité haute."""
        item = {
            "ingredient_id": 2,
            "quantite_necessaire": 1,
            "priorite": "haute",
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is True

    def test_article_sans_ingredient_id(self):
        """Article sans ingredient_id = invalide."""
        item = {
            "quantite_necessaire": 500,
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is False
        assert any("ingredient_id" in e for e in errors)

    def test_article_sans_quantite(self):
        """Article sans quantité = invalide."""
        item = {
            "ingredient_id": 1,
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is False
        assert any("quantite_necessaire" in e for e in errors)

    def test_article_quantite_zero(self):
        """Quantité zéro = invalide (doit être > 0)."""
        item = {
            "ingredient_id": 1,
            "quantite_necessaire": 0,
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is False

    def test_article_quantite_negative(self):
        """Quantité négative = invalide."""
        item = {
            "ingredient_id": 1,
            "quantite_necessaire": -10,
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is False

    def test_article_priorite_invalide(self):
        """Priorité invalide."""
        item = {
            "ingredient_id": 1,
            "quantite_necessaire": 100,
            "priorite": "urgente",  # pas dans PRIORITES_COURSES
        }
        is_valid, errors = valider_article_courses(item)
        assert is_valid is False


class TestValiderRepas:
    """Tests pour valider_repas avec données planning."""

    def test_repas_valide_dejeuner(self):
        """Repas valide: déjeuner lundi."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 0,  # Lundi
            "date": date.today(),
            "type_repas": "déjeuner",
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is True
        assert errors == []

    def test_repas_valide_diner(self):
        """Repas valide: dîner vendredi."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 4,  # Vendredi
            "date": date.today() + timedelta(days=4),
            "type_repas": "dîner",
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is True

    def test_repas_sans_planning_id(self):
        """Repas sans planning_id = invalide."""
        repas = {
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "déjeuner",
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is False

    def test_repas_jour_negatif(self):
        """Jour semaine négatif = invalide."""
        repas = {
            "planning_id": 1,
            "jour_semaine": -1,
            "date": date.today(),
            "type_repas": "déjeuner",
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is False

    def test_repas_jour_trop_grand(self):
        """Jour semaine > 6 = invalide."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 7,
            "date": date.today(),
            "type_repas": "déjeuner",
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is False

    def test_repas_type_invalide(self):
        """Type repas invalide."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "brunch",  # pas dans TYPES_REPAS
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is False

    def test_repas_avec_portions(self):
        """Repas avec portions valides."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "déjeuner",
            "portions": 4,
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is True

    def test_repas_portions_excessives(self):
        """Portions > 50 = invalide."""
        repas = {
            "planning_id": 1,
            "jour_semaine": 0,
            "date": date.today(),
            "type_repas": "déjeuner",
            "portions": 100,
        }
        is_valid, errors = valider_repas(repas)
        assert is_valid is False


class TestValiderQuantite:
    """Tests pour valider_quantite avec quantités cuisine."""

    def test_quantite_valide_500g(self):
        """500g valide."""
        is_valid, msg = valider_quantite(500)
        assert is_valid is True
        assert msg == ""

    def test_quantite_valide_0_25(self):
        """0.25 valide (quart)."""
        is_valid, msg = valider_quantite(0.25, min_val=0)
        assert is_valid is True

    def test_quantite_valide_string(self):
        """'100' string converti en nombre."""
        is_valid, msg = valider_quantite("100")
        assert is_valid is True

    def test_quantite_negative(self):
        """Quantité négative = invalide."""
        is_valid, msg = valider_quantite(-10)
        assert is_valid is False

    def test_quantite_trop_grande(self):
        """Quantité > max = invalide."""
        is_valid, msg = valider_quantite(50000, max_val=10000)
        assert is_valid is False

    def test_quantite_string_invalide(self):
        """String non numérique = invalide."""
        is_valid, msg = valider_quantite("beaucoup")
        assert is_valid is False
        assert "nombre" in msg

    def test_quantite_none(self):
        """None = invalide."""
        is_valid, msg = valider_quantite(None)
        assert is_valid is False


class TestValiderAllergie:
    """Tests pour valider_allergie avec allergies réelles."""

    def test_allergie_valide_gluten(self):
        """Gluten valide."""
        is_valid, msg = valider_allergie("gluten")
        assert is_valid is True
        assert msg == ""

    def test_allergie_valide_lactose(self):
        """Lactose valide."""
        is_valid, msg = valider_allergie("lactose")
        assert is_valid is True

    def test_allergie_valide_arachides(self):
        """Arachides valide."""
        is_valid, msg = valider_allergie("arachides")
        assert is_valid is True

    def test_allergie_valide_fruits_coque(self):
        """Fruits Ã  coque valide."""
        is_valid, msg = valider_allergie("fruits Ã  coque")
        assert is_valid is True

    def test_allergie_vide(self):
        """Allergie vide = invalide."""
        is_valid, msg = valider_allergie("")
        assert is_valid is False

    def test_allergie_none(self):
        """None = invalide."""
        is_valid, msg = valider_allergie(None)
        assert is_valid is False

    def test_allergie_trop_courte(self):
        """Allergie trop courte < 2 chars = invalide."""
        is_valid, msg = valider_allergie("a")
        assert is_valid is False

    def test_allergie_trop_longue(self):
        """Allergie > 100 chars = invalide."""
        is_valid, msg = valider_allergie("a" * 101)
        assert is_valid is False
        assert "100" in msg
