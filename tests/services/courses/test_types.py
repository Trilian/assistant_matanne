"""
Tests pour src/services/courses/types.py

Tests des modèles Pydantic:
- SuggestionCourses
- ArticleCourse
- ListeCoursesIntelligente
- SuggestionSubstitution
"""

import pytest
from pydantic import ValidationError

from src.services.cuisine.courses.types import (
    ArticleCourse,
    ListeCoursesIntelligente,
    ShoppingItem,
    # Aliases
    ShoppingSuggestion,
    SmartShoppingList,
    SubstitutionSuggestion,
    SuggestionCourses,
    SuggestionSubstitution,
)


class TestSuggestionCourses:
    """Tests pour SuggestionCourses."""

    def test_creation_valide(self):
        """Test création avec données valides."""
        suggestion = SuggestionCourses(
            nom="Tomates", quantite=2.0, unite="kg", priorite="haute", rayon="Fruits & Légumes"
        )
        assert suggestion.nom == "Tomates"
        assert suggestion.quantite == 2.0
        assert suggestion.unite == "kg"
        assert suggestion.priorite == "haute"
        assert suggestion.rayon == "Fruits & Légumes"

    def test_priorite_haute_valide(self):
        """Test priorité haute."""
        suggestion = SuggestionCourses(
            nom="Lait", quantite=1.0, unite="L", priorite="haute", rayon="Crèmerie"
        )
        assert suggestion.priorite == "haute"

    def test_priorite_moyenne_valide(self):
        """Test priorité moyenne."""
        suggestion = SuggestionCourses(
            nom="Pain", quantite=1.0, unite="pièce", priorite="moyenne", rayon="Boulangerie"
        )
        assert suggestion.priorite == "moyenne"

    def test_priorite_basse_valide(self):
        """Test priorité basse."""
        suggestion = SuggestionCourses(
            nom="Sucre", quantite=1.0, unite="kg", priorite="basse", rayon="Épicerie"
        )
        assert suggestion.priorite == "basse"

    def test_priorite_invalide_rejetee(self):
        """Test priorité invalide (ne respecte pas le pattern)."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test", quantite=1.0, unite="kg", priorite="urgente", rayon="Test"
            )
        assert "priorite" in str(exc_info.value)

    def test_nom_trop_court_rejete(self):
        """Test nom < 2 caractères."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(nom="A", quantite=1.0, unite="kg", priorite="haute", rayon="Test")
        assert "nom" in str(exc_info.value)

    def test_quantite_negative_rejetee(self):
        """Test quantité <= 0."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(nom="Test", quantite=-1.0, unite="kg", priorite="haute", rayon="Test")
        assert "quantite" in str(exc_info.value)

    def test_quantite_zero_rejetee(self):
        """Test quantité = 0."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(nom="Test", quantite=0, unite="kg", priorite="haute", rayon="Test")
        assert "quantite" in str(exc_info.value)

    def test_unite_vide_rejetee(self):
        """Test unité vide."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(nom="Test", quantite=1.0, unite="", priorite="haute", rayon="Test")
        assert "unite" in str(exc_info.value)

    def test_rayon_trop_court_rejete(self):
        """Test rayon < 3 caractères."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(nom="Test", quantite=1.0, unite="kg", priorite="haute", rayon="AB")
        assert "rayon" in str(exc_info.value)

    def test_model_validate_alias_article(self):
        """Test normalisation champ 'article' -> 'nom'."""
        data = {
            "article": "Pommes",
            "quantite": 3.0,
            "unite": "kg",
            "priorite": "moyenne",
            "rayon": "Fruits",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Pommes"

    def test_model_validate_alias_name(self):
        """Test normalisation champ 'name' -> 'nom'."""
        data = {
            "name": "Oranges",
            "quantite": 2.0,
            "unite": "kg",
            "priorite": "basse",
            "rayon": "Fruits",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Oranges"

    def test_model_validate_alias_item(self):
        """Test normalisation champ 'item' -> 'nom'."""
        data = {
            "item": "Bananes",
            "quantite": 1.0,
            "unite": "kg",
            "priorite": "haute",
            "rayon": "Fruits",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Bananes"

    def test_model_validate_alias_product(self):
        """Test normalisation champ 'product' -> 'nom'."""
        data = {
            "product": "Raisins",
            "quantite": 0.5,
            "unite": "kg",
            "priorite": "moyenne",
            "rayon": "Fruits",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Raisins"

    def test_model_validate_alias_quantity(self):
        """Test normalisation champ 'quantity' -> 'quantite'."""
        data = {"nom": "Test", "quantity": 5.0, "unite": "kg", "priorite": "haute", "rayon": "Test"}
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.quantite == 5.0

    def test_model_validate_alias_amount(self):
        """Test normalisation champ 'amount' -> 'quantite'."""
        data = {"nom": "Test", "amount": 3.5, "unite": "L", "priorite": "moyenne", "rayon": "Test"}
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.quantite == 3.5

    def test_model_validate_alias_unit(self):
        """Test normalisation champ 'unit' -> 'unite'."""
        data = {
            "nom": "Test",
            "quantite": 1.0,
            "unit": "piece",
            "priorite": "haute",
            "rayon": "Test",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.unite == "piece"

    def test_model_validate_alias_priority(self):
        """Test normalisation champ 'priority' -> 'priorite'."""
        data = {"nom": "Test", "quantite": 1.0, "unite": "kg", "priority": "high", "rayon": "Test"}
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "haute"

    def test_model_validate_alias_section(self):
        """Test normalisation champ 'section' -> 'rayon'."""
        data = {
            "nom": "Test",
            "quantite": 1.0,
            "unite": "kg",
            "priorite": "haute",
            "section": "Épicerie",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.rayon == "Épicerie"

    def test_model_validate_alias_department(self):
        """Test normalisation champ 'department' -> 'rayon'."""
        data = {
            "nom": "Test",
            "quantite": 1.0,
            "unite": "kg",
            "priorite": "haute",
            "department": "Boucherie",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.rayon == "Boucherie"

    def test_model_validate_priorite_high_to_haute(self):
        """Test normalisation priorité 'high' -> 'haute'."""
        data = {"nom": "Test", "quantite": 1.0, "unite": "kg", "priorite": "high", "rayon": "Test"}
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "haute"

    def test_model_validate_priorite_medium_to_moyenne(self):
        """Test normalisation priorité 'medium' -> 'moyenne'."""
        data = {
            "nom": "Test",
            "quantite": 1.0,
            "unite": "kg",
            "priorite": "medium",
            "rayon": "Test",
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "moyenne"

    def test_model_validate_priorite_low_to_basse(self):
        """Test normalisation priorité 'low' -> 'basse'."""
        data = {"nom": "Test", "quantite": 1.0, "unite": "kg", "priorite": "low", "rayon": "Test"}
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.priorite == "basse"

    def test_model_validate_non_dict_passthrough(self):
        """Test que les non-dict passent au parent sans modification."""
        suggestion = SuggestionCourses(
            nom="Direct", quantite=1.0, unite="kg", priorite="haute", rayon="Test"
        )
        validated = SuggestionCourses.model_validate(suggestion)
        assert validated.nom == "Direct"


class TestArticleCourse:
    """Tests pour ArticleCourse."""

    def test_creation_minimale(self):
        """Test création avec champs minimaux."""
        article = ArticleCourse(nom="Pain", quantite=1.0)
        assert article.nom == "Pain"
        assert article.quantite == 1.0
        assert article.unite == ""
        assert article.rayon == "Autre"
        assert article.priorite == 2
        assert article.en_stock == 0
        assert article.a_acheter == 0
        assert article.recettes_source == []
        assert article.notes == ""

    def test_creation_complete(self):
        """Test création avec tous les champs."""
        article = ArticleCourse(
            nom="Tomates",
            quantite=2.5,
            unite="kg",
            rayon="Fruits & Légumes",
            recettes_source=["Salade", "Ratatouille"],
            priorite=1,
            en_stock=0.5,
            a_acheter=2.0,
            notes="Bio de préférence",
        )
        assert article.nom == "Tomates"
        assert article.quantite == 2.5
        assert article.unite == "kg"
        assert article.rayon == "Fruits & Légumes"
        assert article.recettes_source == ["Salade", "Ratatouille"]
        assert article.priorite == 1
        assert article.en_stock == 0.5
        assert article.a_acheter == 2.0
        assert article.notes == "Bio de préférence"

    def test_valeurs_par_defaut(self):
        """Test toutes les valeurs par défaut."""
        article = ArticleCourse(nom="Test", quantite=1.0)
        assert article.unite == ""
        assert article.rayon == "Autre"
        assert article.recettes_source == []
        assert article.priorite == 2
        assert article.en_stock == 0
        assert article.a_acheter == 0
        assert article.notes == ""

    def test_priorite_numerique(self):
        """Test que priorité est numérique (1-3)."""
        article = ArticleCourse(nom="Test", quantite=1.0, priorite=1)
        assert article.priorite == 1

    def test_recettes_source_liste(self):
        """Test liste de recettes."""
        recettes = ["Recette 1", "Recette 2", "Recette 3"]
        article = ArticleCourse(nom="Test", quantite=1.0, recettes_source=recettes)
        assert article.recettes_source == recettes
        assert len(article.recettes_source) == 3


class TestListeCoursesIntelligente:
    """Tests pour ListeCoursesIntelligente."""

    def test_creation_vide(self):
        """Test création sans arguments."""
        liste = ListeCoursesIntelligente()
        assert liste.articles == []
        assert liste.total_articles == 0
        assert liste.recettes_couvertes == []
        assert liste.estimation_budget is None
        assert liste.alertes == []

    def test_creation_avec_articles(self):
        """Test création avec des articles."""
        articles = [
            ArticleCourse(nom="Pain", quantite=1.0),
            ArticleCourse(nom="Lait", quantite=2.0),
        ]
        liste = ListeCoursesIntelligente(
            articles=articles,
            total_articles=2,
            recettes_couvertes=["Petit déj"],
            estimation_budget=15.50,
            alertes=["Stock bas en lait"],
        )
        assert len(liste.articles) == 2
        assert liste.total_articles == 2
        assert liste.recettes_couvertes == ["Petit déj"]
        assert liste.estimation_budget == 15.50
        assert liste.alertes == ["Stock bas en lait"]

    def test_creation_avec_alertes(self):
        """Test création avec alertes."""
        liste = ListeCoursesIntelligente(alertes=["Alerte 1", "Alerte 2"])
        assert len(liste.alertes) == 2
        assert "Alerte 1" in liste.alertes

    def test_estimation_budget_optionnel(self):
        """Test budget None par défaut."""
        liste = ListeCoursesIntelligente()
        assert liste.estimation_budget is None

    def test_estimation_budget_present(self):
        """Test budget avec valeur."""
        liste = ListeCoursesIntelligente(estimation_budget=42.99)
        assert liste.estimation_budget == 42.99


class TestSuggestionSubstitution:
    """Tests pour SuggestionSubstitution."""

    def test_creation_minimale(self):
        """Test création avec champs requis."""
        suggestion = SuggestionSubstitution(
            ingredient_original="Beurre", suggestion="Huile d'olive", raison="Plus sain"
        )
        assert suggestion.ingredient_original == "Beurre"
        assert suggestion.suggestion == "Huile d'olive"
        assert suggestion.raison == "Plus sain"
        assert suggestion.economie_estimee is None

    def test_creation_avec_economie(self):
        """Test création avec économie."""
        suggestion = SuggestionSubstitution(
            ingredient_original="Saumon",
            suggestion="Maquereau",
            raison="Moins cher et local",
            economie_estimee=5.50,
        )
        assert suggestion.economie_estimee == 5.50

    def test_economie_optionnelle(self):
        """Test économie None par défaut."""
        suggestion = SuggestionSubstitution(ingredient_original="A", suggestion="B", raison="Test")
        assert suggestion.economie_estimee is None


class TestAliases:
    """Tests pour les alias anglais."""

    def test_shopping_suggestion_alias(self):
        """Test alias ShoppingSuggestion."""
        assert ShoppingSuggestion is SuggestionCourses
        suggestion = ShoppingSuggestion(
            nom="Test", quantite=1.0, unite="kg", priorite="haute", rayon="Test"
        )
        assert isinstance(suggestion, SuggestionCourses)

    def test_shopping_item_alias(self):
        """Test alias ShoppingItem."""
        assert ShoppingItem is ArticleCourse
        item = ShoppingItem(nom="Test", quantite=1.0)
        assert isinstance(item, ArticleCourse)

    def test_smart_shopping_list_alias(self):
        """Test alias SmartShoppingList."""
        assert SmartShoppingList is ListeCoursesIntelligente
        liste = SmartShoppingList()
        assert isinstance(liste, ListeCoursesIntelligente)

    def test_substitution_suggestion_alias(self):
        """Test alias SubstitutionSuggestion."""
        assert SubstitutionSuggestion is SuggestionSubstitution
        sub = SubstitutionSuggestion(ingredient_original="A", suggestion="B", raison="C")
        assert isinstance(sub, SuggestionSubstitution)
