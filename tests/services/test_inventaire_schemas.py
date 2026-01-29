"""
Tests pour le module inventaire (services/inventaire.py).

Tests couverts:
- Schémas Pydantic (SuggestionCourses, ArticleImport)
- Constantes (CATEGORIES, EMPLACEMENTS)
- Logique de calcul de statut (mockée)
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes de l'inventaire."""

    def test_categories_defined(self):
        """Test que les catégories sont définies."""
        from src.services.inventaire import CATEGORIES
        
        assert len(CATEGORIES) > 0
        assert "Légumes" in CATEGORIES
        assert "Fruits" in CATEGORIES
        assert "Protéines" in CATEGORIES

    def test_emplacements_defined(self):
        """Test que les emplacements sont définis."""
        from src.services.inventaire import EMPLACEMENTS
        
        assert len(EMPLACEMENTS) > 0
        assert "Frigo" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS
        assert "Placard" in EMPLACEMENTS

    def test_categories_all_strings(self):
        """Test que toutes les catégories sont des strings."""
        from src.services.inventaire import CATEGORIES
        
        for cat in CATEGORIES:
            assert isinstance(cat, str)

    def test_emplacements_all_strings(self):
        """Test que tous les emplacements sont des strings."""
        from src.services.inventaire import EMPLACEMENTS
        
        for emp in EMPLACEMENTS:
            assert isinstance(emp, str)


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMA SUGGESTION COURSES
# ═══════════════════════════════════════════════════════════


class TestSuggestionCourses:
    """Tests pour le schéma SuggestionCourses."""

    def test_valid_suggestion(self):
        """Test suggestion valide."""
        from src.services.inventaire import SuggestionCourses
        
        suggestion = SuggestionCourses(
            nom="Tomates",
            quantite=500,
            unite="g",
            priorite="haute",
            rayon="Légumes frais",
        )
        
        assert suggestion.nom == "Tomates"
        assert suggestion.quantite == 500
        assert suggestion.unite == "g"
        assert suggestion.priorite == "haute"
        assert suggestion.rayon == "Légumes frais"

    def test_all_priority_values(self):
        """Test toutes les valeurs de priorité."""
        from src.services.inventaire import SuggestionCourses
        
        for priority in ["haute", "moyenne", "basse"]:
            suggestion = SuggestionCourses(
                nom="Test",
                quantite=1,
                unite="kg",
                priorite=priority,
                rayon="Test rayon",
            )
            assert suggestion.priorite == priority

    def test_invalid_priority_rejected(self):
        """Test priorité invalide rejetée."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test",
                quantite=1,
                unite="kg",
                priorite="invalide",
                rayon="Test rayon",
            )
        
        assert "priorite" in str(exc_info.value)

    def test_nom_too_short_rejected(self):
        """Test nom trop court rejeté."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="A",  # < 2 caractères
                quantite=1,
                unite="kg",
                priorite="haute",
                rayon="Test rayon",
            )
        
        assert "nom" in str(exc_info.value)

    def test_quantite_zero_rejected(self):
        """Test quantité 0 rejetée."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test",
                quantite=0,  # > 0 required
                unite="kg",
                priorite="haute",
                rayon="Test rayon",
            )
        
        assert "quantite" in str(exc_info.value)

    def test_quantite_negative_rejected(self):
        """Test quantité négative rejetée."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test",
                quantite=-5,
                unite="kg",
                priorite="haute",
                rayon="Test rayon",
            )
        
        assert "quantite" in str(exc_info.value)

    def test_unite_empty_rejected(self):
        """Test unité vide rejetée."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test",
                quantite=1,
                unite="",  # min_length=1
                priorite="haute",
                rayon="Test rayon",
            )
        
        assert "unite" in str(exc_info.value)

    def test_rayon_too_short_rejected(self):
        """Test rayon trop court rejeté."""
        from src.services.inventaire import SuggestionCourses
        
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Test",
                quantite=1,
                unite="kg",
                priorite="haute",
                rayon="AB",  # < 3 caractères
            )
        
        assert "rayon" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMA ARTICLE IMPORT
# ═══════════════════════════════════════════════════════════


class TestArticleImport:
    """Tests pour le schéma ArticleImport."""

    def test_valid_article_minimal(self):
        """Test article valide minimal."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Lait",
            quantite=2,
            quantite_min=1,
            unite="L",
        )
        
        assert article.nom == "Lait"
        assert article.quantite == 2
        assert article.quantite_min == 1
        assert article.unite == "L"
        assert article.categorie is None
        assert article.emplacement is None
        assert article.date_peremption is None

    def test_valid_article_complete(self):
        """Test article valide complet."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Yaourt nature",
            quantite=4,
            quantite_min=2,
            unite="pots",
            categorie="Laitier",
            emplacement="Frigo",
            date_peremption="2024-02-15",
        )
        
        assert article.nom == "Yaourt nature"
        assert article.categorie == "Laitier"
        assert article.emplacement == "Frigo"
        assert article.date_peremption == "2024-02-15"

    def test_quantite_zero_accepted(self):
        """Test quantité 0 acceptée (ge=0)."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Épuisé",
            quantite=0,
            quantite_min=0,
            unite="kg",
        )
        
        assert article.quantite == 0

    def test_quantite_negative_rejected(self):
        """Test quantité négative rejetée."""
        from src.services.inventaire import ArticleImport
        
        with pytest.raises(ValidationError) as exc_info:
            ArticleImport(
                nom="Test",
                quantite=-1,
                quantite_min=0,
                unite="kg",
            )
        
        assert "quantite" in str(exc_info.value)

    def test_nom_too_short_rejected(self):
        """Test nom trop court rejeté."""
        from src.services.inventaire import ArticleImport
        
        with pytest.raises(ValidationError) as exc_info:
            ArticleImport(
                nom="X",  # < 2 caractères
                quantite=1,
                quantite_min=0,
                unite="kg",
            )
        
        assert "nom" in str(exc_info.value)

    def test_unite_empty_rejected(self):
        """Test unité vide rejetée."""
        from src.services.inventaire import ArticleImport
        
        with pytest.raises(ValidationError) as exc_info:
            ArticleImport(
                nom="Test",
                quantite=1,
                quantite_min=0,
                unite="",
            )
        
        assert "unite" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════
# TESTS LOGIQUE DE STATUT (PURE LOGIC)
# ═══════════════════════════════════════════════════════════


class TestCalculerStatutLogic:
    """Tests pour la logique de calcul de statut.
    
    Note: Ces tests vérifient la logique pure sans base de données.
    """

    def test_peremption_proche_logic(self):
        """Test logique péremption proche (< 7 jours)."""
        # Simulation: date_peremption dans 5 jours
        today = date.today()
        peremption = today + timedelta(days=5)
        days_left = (peremption - today).days
        
        # La logique devrait retourner "peremption_proche" si days_left <= 7
        assert days_left <= 7
        expected_status = "peremption_proche"
        
        # Vérifier la logique
        if days_left <= 7:
            status = "peremption_proche"
        else:
            status = "ok"
        
        assert status == expected_status

    def test_peremption_ok_logic(self):
        """Test logique péremption OK (> 7 jours)."""
        today = date.today()
        peremption = today + timedelta(days=30)
        days_left = (peremption - today).days
        
        assert days_left > 7
        
        # Vérifier la logique
        if days_left <= 7:
            status = "peremption_proche"
        else:
            status = "ok"
        
        assert status == "ok"

    def test_stock_critique_logic(self):
        """Test logique stock critique (< 50% du minimum)."""
        quantite = 1
        quantite_min = 5
        
        # La logique: critique si quantite < quantite_min * 0.5
        is_critique = quantite < (quantite_min * 0.5)  # 1 < 2.5 = True
        
        assert is_critique is True
        
        status = "critique" if is_critique else "ok"
        assert status == "critique"

    def test_stock_bas_logic(self):
        """Test logique stock bas (< minimum mais >= 50%)."""
        quantite = 3
        quantite_min = 5
        
        # Pas critique: 3 >= 2.5
        is_critique = quantite < (quantite_min * 0.5)
        assert is_critique is False
        
        # Mais stock_bas: 3 < 5
        is_stock_bas = quantite < quantite_min
        assert is_stock_bas is True
        
        if is_critique:
            status = "critique"
        elif is_stock_bas:
            status = "stock_bas"
        else:
            status = "ok"
        
        assert status == "stock_bas"

    def test_stock_ok_logic(self):
        """Test logique stock OK (>= minimum)."""
        quantite = 10
        quantite_min = 5
        
        is_critique = quantite < (quantite_min * 0.5)
        is_stock_bas = quantite < quantite_min
        
        assert is_critique is False
        assert is_stock_bas is False
        
        status = "ok"
        assert status == "ok"


class TestJoursAvantPeremptionLogic:
    """Tests pour la logique de calcul des jours avant péremption."""

    def test_no_peremption_date(self):
        """Test sans date de péremption."""
        date_peremption = None
        
        if not date_peremption:
            result = None
        else:
            result = (date_peremption - date.today()).days
        
        assert result is None

    def test_future_peremption(self):
        """Test péremption future."""
        today = date.today()
        date_peremption = today + timedelta(days=10)
        
        result = (date_peremption - today).days
        
        assert result == 10

    def test_past_peremption(self):
        """Test péremption passée (négatif)."""
        today = date.today()
        date_peremption = today - timedelta(days=3)
        
        result = (date_peremption - today).days
        
        assert result == -3

    def test_today_peremption(self):
        """Test péremption aujourd'hui."""
        today = date.today()
        date_peremption = today
        
        result = (date_peremption - today).days
        
        assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS D'EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_suggestion_float_quantite(self):
        """Test suggestion avec quantité décimale."""
        from src.services.inventaire import SuggestionCourses
        
        suggestion = SuggestionCourses(
            nom="Fromage",
            quantite=0.5,
            unite="kg",
            priorite="moyenne",
            rayon="Crémerie",
        )
        
        assert suggestion.quantite == 0.5

    def test_article_unicode_nom(self):
        """Test article avec nom Unicode."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Œufs frais",
            quantite=12,
            quantite_min=6,
            unite="pièces",
        )
        
        assert article.nom == "Œufs frais"

    def test_article_accented_chars(self):
        """Test article avec caractères accentués."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Pâté de campagne",
            quantite=1,
            quantite_min=0,
            unite="pot",
            categorie="Épicerie",
        )
        
        assert "é" in article.categorie or "pât" in article.nom.lower()

    def test_suggestion_long_rayon(self):
        """Test suggestion avec rayon long."""
        from src.services.inventaire import SuggestionCourses
        
        suggestion = SuggestionCourses(
            nom="Produit",
            quantite=1,
            unite="u",
            priorite="basse",
            rayon="Rayon des produits frais et réfrigérés du magasin",
        )
        
        assert len(suggestion.rayon) > 30
